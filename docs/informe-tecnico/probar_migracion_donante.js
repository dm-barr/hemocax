// Prueba la migración 20261004000400 dentro de una transacción y la DESHACE (no deja cambios en la base).
// Uso: node docs/informe-tecnico/probar_migracion_donante.js   (requiere DATABASE_URL en .env y las cuentas DEMO)
const fs = require('fs');
const path = require('path');
const { Client } = require('pg');
const raiz = path.join(__dirname, '..', '..');
for (const l of fs.readFileSync(path.join(raiz, '.env'), 'utf8').split(/\r?\n/)) {
  const m = l.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
  if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
}
const sql = fs.readFileSync(path.join(raiz, 'supabase/migrations/20261004000400_restrict_donor_self_update.sql'), 'utf8');

(async () => {
  const c = new Client({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } });
  await c.connect();
  const uid = async (dni) => (await c.query('select id from auth.users where email=$1', [`dni-${dni}@login.hemocax.org`])).rows[0]?.id;
  const donante = await uid('99000011'), enfermera = await uid('99000001');
  if (!donante || !enfermera) throw new Error('Faltan las cuentas DEMO');
  const como = async (id, consulta, params = []) => {
    await c.query('savepoint s');
    try {
      await c.query('set local role authenticated');
      await c.query(`select set_config('request.jwt.claims', $1, true)`, [JSON.stringify({ sub: id, role: 'authenticated' })]);
      const r = await c.query(consulta, params);
      await c.query('reset role');
      await c.query('release savepoint s');
      return `OK (${r.rowCount} fila)`;
    } catch (e) {
      await c.query('rollback to savepoint s');
      await c.query('reset role');
      return `RECHAZADO: ${e.message}`;
    }
  };
  try {
    await c.query('begin');
    console.log('--- ANTES de la migración');
    console.log('donante cambia teléfono   :', await como(donante, `update public.donors set phone='900000002' where auth_user_id='${donante}'`));
    await c.query('rollback'); await c.query('begin');
    await c.query(sql);
    console.log('--- DESPUÉS de la migración');
    console.log('donante cambia teléfono   :', await como(donante, `update public.donors set phone='900000002' where auth_user_id='${donante}'`));
    console.log('donante cambia estado     :', await como(donante, `update public.donors set status='INACTIVE' where auth_user_id='${donante}'`));
    console.log('donante cambia grupo      :', await como(donante, `update public.donors set blood_type='A' where auth_user_id='${donante}'`));
    console.log('donante activa consent.   :', await como(donante, `update public.donors set consent_email=true, consent_at=now(), consent_version='piloto-v1', opted_out=false where auth_user_id='${donante}'`));
    console.log('donante revoca consent.   :', await como(donante, `update public.donors set consent_email=false, opted_out=true where auth_user_id='${donante}'`));
    console.log('enfermería edita teléfono :', await como(enfermera, `update public.donors set phone='900000003' where auth_user_id='${donante}'`));
    console.log('servidor (sin sesión)     :', await (async () => { try { await c.query(`update public.donors set phone='900000004' where auth_user_id='${donante}'`); return 'OK'; } catch (e) { return 'RECHAZADO ' + e.message; } })());
  } finally {
    await c.query('rollback');
    await c.end();
    console.log('--- transacción deshecha: la base no se modificó');
  }
})().catch((e) => { console.error('FAIL', e.message); process.exitCode = 1; });
