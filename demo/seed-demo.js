// Datos de DEMOSTRACIÓN para grabar el video. Todo lo que crea tiene DNI que empieza con 9900
// y se borra por completo con: node demo/limpiar-demo.js
// Uso: node demo/seed-demo.js
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

for (const line of fs.readFileSync(path.join(__dirname, '..', '.env'), 'utf8').split(/\r?\n/)) {
  const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
  if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
}
const s = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);

const HOUR = 3600e3;
const limaDate = (ms) => new Date(ms - 5 * HOUR).toISOString().slice(0, 10);
const daysAgo = (n) => limaDate(Date.now() - n * 24 * HOUR);
const YEAR = limaDate(Date.now()).slice(0, 4);
const MAIL = (tag) => `hemocax26+${tag}@gmail.com`; // llega a tu propia bandeja

const ACCOUNTS = [
  { dni: '99000001', name: 'Enfermera Demo', role: 'STAFF', release: false, password: 'Demo-Enfermera-26' },
  { dni: '99000002', name: 'Médico Demo', role: 'STAFF', release: true, password: 'Demo-Medico-2026' },
  { dni: '99000003', name: 'Administrador Demo', role: 'ADMIN', release: true, password: 'Demo-Admin-2026x' },
];

// donations: [fecha, resultado]. resultado: {h: horas hasta liberar} | {pendingHours: horas esperando} | null
const DONORS = [
  { dni: '99000101', first: 'Ana', last: 'Quispe Demo', g: 'F', blood: 'O-', birth: '1992-03-14', email: MAIL('ana'), consent: true, donations: [[daysAgo(200), { h: 25 }]] },
  { dni: '99000102', first: 'Luis', last: 'Mendoza Demo', g: 'M', blood: 'A+', birth: '1988-07-02', email: MAIL('luis'), consent: true, donations: [[daysAgo(20), { h: 30 }]] },
  { dni: '99000103', first: 'Rosa', last: 'Cueva Demo', g: 'F', blood: 'O-', birth: '1995-11-21', email: MAIL('rosa'), consent: true, donations: [[`${YEAR}-01-12`, { h: 20 }], [`${YEAR}-04-10`, { h: 40 }], [`${YEAR}-07-14`, { h: 70 }]] },
  { dni: '99000104', first: 'Carlos', last: 'Pérez Demo', g: 'M', blood: 'B+', birth: '1990-01-30', email: null, consent: false, donations: [[null, { pendingHours: 40 }]] },
  { dni: '99000105', first: 'Elena', last: 'Torres Demo', g: 'F', blood: 'AB-', birth: '1993-09-09', email: MAIL('elena'), consent: false, donations: [[null, { pendingHours: 75 }]] },
  { dni: '99000106', first: 'Jorge', last: 'Salas Demo', g: 'M', blood: 'O+', birth: '1985-05-17', email: 'jorge.demo@ejemplo.com', consent: false, status: 'INACTIVE', donations: [[daysAgo(400), { h: 28 }]] },
  { dni: '99000107', first: 'Marta', last: 'Díaz Demo', g: 'F', blood: null, birth: '1991-12-03', email: MAIL('marta'), consent: true, donations: [[null, { pendingHours: 3 }]] },
  { dni: '99000108', first: 'Pedro', last: 'Quispe Demo', g: 'M', blood: 'A-', birth: '1999-02-25', email: MAIL('pedro'), consent: true, donations: [[null, { pendingHours: 1 }]] },
  { dni: '99000109', first: 'Lucía', last: 'Rojas Demo', g: 'F', blood: 'O-', birth: '1997-06-18', email: MAIL('lucia'), consent: true, donations: [[daysAgo(300), { h: 50 }]] },
  { dni: '99000110', first: 'Diego', last: 'Vargas Demo', g: 'M', blood: 'B-', birth: '1994-08-08', email: MAIL('diego'), consent: true, donations: [[daysAgo(300), { h: 18 }], [daysAgo(130), { h: 26 }]] },
  // Donantes con cuenta propia para mostrar el portal del donante
  { dni: '99000011', first: 'Carmen', last: 'Flores Demo', g: 'F', blood: 'O+', birth: '1989-04-04', email: MAIL('carmen'), consent: false, account: 'demo-sol-rio-11', donations: [[daysAgo(100), { h: 22, msg: 'Tus resultados están normales. Gracias por donar.' }]] },
  { dni: '99000012', first: 'Juan', last: 'Ramos Demo', g: 'M', blood: 'A+', birth: '1986-10-10', email: MAIL('juan'), consent: true, account: 'demo-luna-mar-12', donations: [[daysAgo(15), { h: 27, msg: 'Tus resultados están normales. Gracias por donar.' }]] },
];

// 18 donantes adicionales: junto con los 12 anteriores suman 30 donantes DEMO.
// 15 tienen 1 donación (con las 15 anteriores suman 30 donaciones y 30 resultados) y 3 son registros nuevos sin donar.
// Ninguno es O negativo con consentimiento, para que la campaña «O negativo» siga llegando solo a los donantes del guion.
const EXTRA = [
  ['Marco', 'Chávez', 'M', 'A+', '1984-01-19', 'marco', true, 260], ['Sofía', 'Alva', 'F', 'O+', '1996-02-11', 'sofia', true, 240],
  ['Raúl', 'Tello', 'M', 'B+', '1979-09-23', 'raul', true, 220], ['Camila', 'Huamán', 'F', 'A-', '1998-04-30', 'camila', true, 200],
  ['Daniel', 'Zelada', 'M', 'O+', '1991-12-12', 'daniel', true, 180], ['Valeria', 'Cieza', 'F', 'AB+', '1993-06-06', 'valeria', true, 165],
  ['Hugo', 'Sánchez', 'M', 'A+', '1987-03-27', 'hugo', true, 150], ['Paola', 'Becerra', 'F', 'B-', '1990-10-15', 'paola', true, 135],
  ['Iván', 'Calderón', 'M', 'O+', '1982-08-04', 'ivan', true, 120], ['Lorena', 'Ríos', 'F', 'A+', '1994-05-21', 'lorena', true, 105],
  ['Sergio', 'Vásquez', 'M', 'B+', '2000-07-09', 'sergio', true, 90], ['Natalia', 'Llamo', 'F', 'O+', '1989-11-02', 'natalia', true, 75],
  ['Óscar', 'Mejía', 'M', 'AB-', '1976-02-28', null, false, 60], ['Gabriela', 'Terrones', 'F', 'A+', '1995-09-17', null, false, 45],
  ['Andrés', 'Cabrera', 'M', 'B+', '1992-12-25', null, false, 30],
  ['Fiorella', 'Paredes', 'F', null, '1999-01-08', 'fiorella', true, null], ['Kevin', 'Sarmiento', 'M', null, '2001-03-14', null, false, null],
  ['Milagros', 'Ordóñez', 'F', 'O+', '1988-06-29', 'milagros', true, null],
];
EXTRA.forEach(([first, last, g, blood, birth, tag, consent, ago], i) => {
  DONORS.push({
    dni: String(99000111 + i), first, last: `${last} Demo`, g, blood, birth, email: tag ? MAIL(tag) : null, consent: !!(consent && tag), extra: true,
    donations: ago ? [[daysAgo(ago), { h: 20 + ((i * 7) % 30) }]] : [],
  });
});

async function mkUser(dni, name, role, release, password) {
  const { data, error } = await s.auth.admin.createUser({ email: `dni-${dni}@login.hemocax.org`, password, email_confirm: true, user_metadata: { dni, full_name: name } });
  if (error) throw new Error(`${dni}: ${error.message}`);
  const { error: pe } = await s.from('profiles').insert({ user_id: data.user.id, dni, full_name: name, role, can_release_results: release, active: true });
  if (pe) throw pe;
  return data.user.id;
}

async function main() {
  const { count } = await s.from('donors').select('id', { count: 'exact', head: true }).like('dni', '9900%');
  if (count) throw new Error('Ya hay datos de demostración. Ejecuta primero: node demo/limpiar-demo.js');
  fs.writeFileSync(path.join(__dirname, '.seed-time'), new Date().toISOString());

  for (const a of ACCOUNTS) await mkUser(a.dni, a.name, a.role, a.release, a.password);

  const ids = {};
  for (const d of DONORS) {
    const { data: donor, error } = await s.from('donors').insert({
      dni: d.dni, first_name: d.first, last_name: d.last, gender: d.g, birth_date: d.birth, phone: '9' + d.dni.slice(-8),
      email: d.email, blood_type: d.blood ? d.blood.slice(0, -1) : null, rh_factor: d.blood ? d.blood.slice(-1) : null,
      status: d.status || 'ACTIVE',
      ...(d.consent && d.email ? { consent_email: true, consent_at: new Date().toISOString(), consent_version: 'piloto-v1', opted_out: false } : {}),
    }).select('id').single();
    if (error) throw new Error(`${d.dni}: ${error.message}`);
    ids[d.dni] = { id: donor.id, donations: [] };

    if (d.account) {
      const uid = await mkUser(d.dni, `${d.first} ${d.last}`, 'DONOR', false, d.account);
      await s.from('donors').update({ auth_user_id: uid }).eq('id', donor.id);
    }

    for (const [dateIn, res] of d.donations) {
      const createdMs = res.pendingHours !== undefined ? Date.now() - res.pendingHours * HOUR : new Date(`${dateIn}T15:00:00Z`).getTime();
      const date = dateIn || limaDate(createdMs);
      const { data: don, error: de } = await s.from('donations').insert({ donor_id: donor.id, donation_date: date, donation_type: 'WHOLE_BLOOD' }).select('id').single();
      if (de) throw new Error(`${d.dni} donación: ${de.message}`);
      ids[d.dni].donations.push(don.id);
      const patch = { created_at: new Date(createdMs).toISOString() };
      if (res.h !== undefined) {
        patch.status = 'AVAILABLE';
        patch.available_at = new Date(createdMs + res.h * HOUR).toISOString();
        patch.donor_message = res.msg || 'Tus resultados están disponibles. Gracias por donar.';
      }
      const { error: re } = await s.from('donation_results').update(patch).eq('donation_id', don.id);
      if (re) throw new Error(`${d.dni} resultado: ${re.message}`);
    }
  }

  // Campañas
  const camp = async (row) => (await s.from('campaigns').insert(row).select('id').single()).data.id;
  await camp({ name: 'DEMO · Se necesita sangre O negativo', description: 'Convocatoria para donantes O negativo', message_template: 'Hola {{nombre}}, el Banco de Sangre del HRDC necesita donantes de sangre O negativo. Si ya puedes donar, acércate: tu ayuda salva vidas.', kind: 'CAMPAIGN', status: 'ACTIVE' });
  await camp({ name: 'DEMO · Requisitos para donar', description: 'Información educativa', message_template: 'Para donar sangre debes ser mayor de edad, pesar más de 50 kg, estar en buen estado de salud y haber desayunado. Trae tu DNI.', kind: 'INFO', status: 'ACTIVE' });
  const oldCampaign = await camp({ name: 'DEMO · Campaña anterior', description: 'Ya cerrada', message_template: 'Hola {{nombre}}, gracias por apoyar nuestra campaña.', kind: 'CAMPAIGN', status: 'CLOSED' });

  // Historial de correos (solo registros de ejemplo: no se envía nada)
  const iso = (daysBack) => new Date(Date.now() - daysBack * 24 * HOUR).toISOString();
  const comm = async (dni, type, status, by, daysBack, extra = {}) => {
    const d = DONORS.find((x) => x.dni === dni);
    const { data } = await s.from('communications').insert({
      donor_id: ids[dni].id, type, channel: 'EMAIL', email: d.email || 'demo@ejemplo.com', message: extra.message || 'Mensaje de ejemplo.', status,
      created_by_name: by, created_at: iso(daysBack), sent_at: status === 'SENT' ? iso(daysBack) : null, ...extra.fields,
    }).select('id').single();
    return data?.id;
  };
  await comm('99000101', 'MANUAL', 'SENT', 'Enfermera Demo', 12, { message: 'Hola Ana, gracias por ser parte de HEMOCAX.' });
  for (const dni of ['99000101', '99000109', '99000110']) {
    const cid = await comm(dni, 'CAMPAIGN', 'SENT', 'Médico Demo', 9, { message: 'Hola, gracias por apoyar nuestra campaña.', fields: { campaign_id: oldCampaign } });
    if (cid) await s.from('campaign_recipients').insert({ campaign_id: oldCampaign, donor_id: ids[dni].id, communication_id: cid, status: 'SENT' });
  }
  await comm('99000102', 'RESULT', 'SENT', 'Médico Demo', 18, { message: 'Hola Luis. Hay información disponible sobre tu proceso de donación.' });
  await comm('99000110', 'DONATION_THANKS', 'SENT', 'Sistema (automático)', 128, { message: 'Hola Diego. Gracias por tu donación voluntaria.', fields: { related_donation_id: ids['99000110'].donations[1] } });
  await comm('99000107', 'BIRTHDAY', 'SENT', 'Sistema (automático)', 30, { message: 'Feliz cumpleaños, Marta.' });
  await comm('99000101', 'RETURN_REMINDER', 'FAILED', 'Sistema (automático)', 3, { message: 'Hola Ana. Ya puedes volver a donar.', fields: { related_donation_id: ids['99000101'].donations[0], error_message: 'Ejemplo: la bandeja del destinatario está llena' } });

  // Historial adicional para completar 30 correos de ejemplo (solo registros: no se envía nada)
  const conCorreo = DONORS.filter((d) => d.extra && d.consent && d.donations.length);
  for (const d of conCorreo) {
    await comm(d.dni, 'DONATION_THANKS', 'SENT', 'Sistema (automático)', 5 + Math.floor(Math.random() * 40), { message: `Hola ${d.first}. Gracias por tu donación voluntaria.`, fields: { related_donation_id: ids[d.dni].donations[0] } });
  }
  for (const d of conCorreo.slice(0, 4)) await comm(d.dni, 'BIRTHDAY', 'SENT', 'Sistema (automático)', 20 + Math.floor(Math.random() * 60), { message: `Feliz cumpleaños, ${d.first}.` });
  const manuales = conCorreo.slice(4, 11);
  for (const [i, d] of manuales.entries()) {
    await comm(d.dni, 'MANUAL', i === 2 || i === 5 ? 'FAILED' : 'SENT', i % 2 ? 'Médico Demo' : 'Enfermera Demo', 2 + i * 4,
      { message: `Hola ${d.first}, gracias por ser parte de HEMOCAX.`, fields: i === 2 || i === 5 ? { error_message: 'Ejemplo: el buzón del destinatario no existe' } : {} });
  }
  const totales = {};
  for (const [tabla, filtro] of [['donors', ['dni', '9900%']]]) {
    const r = await s.from(tabla).select('id', { count: 'exact', head: true }).like(filtro[0], filtro[1]);
    totales[tabla] = r.count;
  }
  const ds = (await s.from('donors').select('id').like('dni', '9900%')).data.map((x) => x.id);
  totales.donaciones = (await s.from('donations').select('id', { count: 'exact', head: true }).in('donor_id', ds)).count;
  totales.correos = (await s.from('communications').select('id', { count: 'exact', head: true }).in('donor_id', ds)).count;
  console.log('Totales DEMO:', JSON.stringify(totales));

  let credentials = 'CUENTAS DE DEMOSTRACIÓN (portal: https://hemocax.vercel.app)\r\n\r\nPERSONAL\r\n';
  for (const a of ACCOUNTS) credentials += `  ${a.name.padEnd(20)} DNI ${a.dni}   contraseña: ${a.password}\r\n`;
  credentials += '\r\nDONANTES CON CUENTA\r\n';
  for (const d of DONORS.filter((x) => x.account)) credentials += `  ${(d.first + ' ' + d.last).padEnd(20)} DNI ${d.dni}   contraseña: ${d.account}\r\n`;
  credentials += '\r\nDONANTES PARA ATENDER (busca por DNI o escribe «Demo» en Donantes)\r\n';
  for (const d of DONORS.filter((x) => !x.account && !x.extra)) credentials += `  ${(d.first + ' ' + d.last).padEnd(20)} DNI ${d.dni}\r\n`;
  credentials += `
(+ ${DONORS.filter((x) => x.extra).length} donantes adicionales DNI 99000111 a 99000128, para que el listado tenga 30)
`;
  fs.writeFileSync(path.join(__dirname, 'CREDENCIALES_DEMO.txt'), credentials);
  console.log(credentials);
}

main().catch((e) => { console.error('FAIL', e.message || e); process.exitCode = 1; });
