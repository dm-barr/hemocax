// Borra TODO lo creado por seed-demo.js y lo que se haya registrado durante la grabación con DNI 9900xxxx.
// Uso: node demo/limpiar-demo.js
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

for (const line of fs.readFileSync(path.join(__dirname, '..', '.env'), 'utf8').split(/\r?\n/)) {
  const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
  if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
}
const s = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);

async function deleteDonors(donors) {
  for (const d of donors) {
    const { data: dons } = await s.from('donations').select('id').eq('donor_id', d.id);
    const ids = (dons || []).map((x) => x.id);
    let rids = [];
    await s.from('campaign_recipients').delete().eq('donor_id', d.id);
    await s.from('communications').delete().eq('donor_id', d.id);
    await s.from('notifications').delete().eq('donor_id', d.id);
    if (ids.length) {
      const { data: res } = await s.from('donation_results').select('id').in('donation_id', ids);
      rids = (res || []).map((x) => x.id);
      await s.from('donation_results').delete().in('donation_id', ids);
      await s.from('donations').delete().in('id', ids);
    }
    const r = await s.from('donors').delete().eq('id', d.id);
    if (r.error) throw new Error('donante ' + d.id + ': ' + r.error.message);
    // La bitácora se limpia DESPUÉS de borrar, porque los triggers registran el borrado.
    if (rids.length) await s.from('audit_logs').delete().eq('entity', 'donation_result').in('entity_id', rids);
    if (ids.length) await s.from('audit_logs').delete().eq('entity', 'donation').in('entity_id', ids);
    await s.from('audit_logs').delete().eq('entity', 'donor').eq('entity_id', d.id);
  }
}

async function main() {
  // 1) Donantes de demostración (y los registrados o importados durante la grabación con DNI 9900…)
  const { data: donors } = await s.from('donors').select('id').like('dni', '9900%');
  await deleteDonors(donors || []);

  // 2) Donantes anonimizados durante la grabación (su DNI pasa a 9000000N): solo los creados desde el seed
  const markerFile = path.join(__dirname, '.seed-time');
  if (fs.existsSync(markerFile)) {
    const since = fs.readFileSync(markerFile, 'utf8').trim();
    const { data: anon } = await s.from('donors').select('id').eq('last_name', 'anonimizado').gte('created_at', since);
    await deleteDonors(anon || []);
  }

  // 3) Campañas DEMO
  const { data: camps } = await s.from('campaigns').select('id').like('name', 'DEMO%');
  for (const c of camps || []) {
    await s.from('campaign_recipients').delete().eq('campaign_id', c.id);
    await s.from('communications').delete().eq('campaign_id', c.id);
    await s.from('campaigns').delete().eq('id', c.id);
    await s.from('audit_logs').delete().eq('entity', 'campaign').eq('entity_id', c.id);
  }

  // 3b) Plantillas aprobadas durante la grabación por una cuenta DEMO: se desaprueban para que no salgan correos reales
  await s.from('message_templates').update({ approved: false, approved_by: null, approved_at: null }).like('approved_by', '%Demo%');

  // 4) Cuentas DEMO (personal, donantes y las creadas en la grabación con DNI 9900…)
  const { data: profs } = await s.from('profiles').select('user_id').like('dni', '9900%');
  for (const p of profs || []) {
    await s.from('audit_logs').delete().eq('actor_id', p.user_id);
    await s.from('communications').update({ created_by: null }).eq('created_by', p.user_id);
    await s.from('donations').update({ created_by: null }).eq('created_by', p.user_id);
    await s.from('consent_events').update({ recorded_by: null }).eq('recorded_by', p.user_id);
    await s.from('consent_versions').update({ created_by: null }).eq('created_by', p.user_id);
    await s.from('campaigns').update({ created_by: null }).eq('created_by', p.user_id);
    const r = await s.auth.admin.deleteUser(p.user_id);
    if (r.error) throw new Error(`cuenta ${p.user_id}: ${r.error.message}`);
  }
  await s.from('audit_logs').delete().like('actor_dni', '9900%');

  for (const f of ['.seed-time', 'CREDENCIALES_DEMO.txt']) { try { fs.unlinkSync(path.join(__dirname, f)); } catch { /* no existía */ } }

  const { data: left } = await s.from('profiles').select('dni').order('dni');
  const { count } = await s.from('donors').select('id', { count: 'exact', head: true });
  console.log('Listo. Cuentas que quedan:', left.map((x) => x.dni).join(', '), '| donantes que quedan:', count);
}

main().catch((e) => { console.error('FAIL', e.message || e); process.exitCode = 1; });
