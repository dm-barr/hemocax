export function parseCsv(text: string): string[][] {
  const clean = text.replace(/^﻿/, '');
  const firstLine = clean.split(/\r?\n/)[0] || '';
  const delimiter = (firstLine.match(/;/g)?.length ?? 0) > (firstLine.match(/,/g)?.length ?? 0) ? ';' : ',';
  const rows: string[][] = [];
  let row: string[] = [];
  let cur = '';
  let quoted = false;
  const endRow = () => {
    row.push(cur);
    cur = '';
    if (row.some((c) => c.trim() !== '')) rows.push(row);
    row = [];
  };
  for (let i = 0; i < clean.length; i++) {
    const ch = clean[i];
    if (quoted) {
      if (ch === '"') {
        if (clean[i + 1] === '"') { cur += '"'; i++; } else quoted = false;
      } else cur += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === delimiter) { row.push(cur); cur = ''; }
    else if (ch === '\n' || ch === '\r') { if (ch === '\r' && clean[i + 1] === '\n') i++; endRow(); }
    else cur += ch;
  }
  endRow();
  return rows;
}

const norm = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');

const ALIASES: Record<string, string> = {
  dni: 'dni', documento: 'dni',
  nombres: 'first_name', nombre: 'first_name',
  apellidos: 'last_name', apellido: 'last_name',
  sexo: 'gender', genero: 'gender',
  fecha_nacimiento: 'birth_date', nacimiento: 'birth_date', fecha_de_nacimiento: 'birth_date',
  telefono: 'phone', celular: 'phone',
  correo: 'email', email: 'email', correo_electronico: 'email',
  grupo_sanguineo: 'blood', grupo: 'blood', sangre: 'blood', tipo_de_sangre: 'blood',
};

export type DonorImportRow = {
  dni: string; first_name: string; last_name: string; gender: 'M' | 'F'; birth_date: string;
  phone: string; email: string | null; blood_type: string | null; rh_factor: string | null;
};

function parseDate(raw: string): string | null {
  const t = raw.trim();
  let y: number, m: number, d: number;
  let match = t.match(/^(\d{4})[-/.\s](\d{1,2})[-/.\s](\d{1,2})$/);
  if (match) { y = +match[1]; m = +match[2]; d = +match[3]; }
  else {
    match = t.match(/^(\d{1,2})[-/.\s](\d{1,2})[-/.\s](\d{4})$/);
    if (!match) return null;
    d = +match[1]; m = +match[2]; y = +match[3];
  }
  const date = new Date(Date.UTC(y, m - 1, d));
  if (date.getUTCFullYear() !== y || date.getUTCMonth() !== m - 1 || date.getUTCDate() !== d) return null;
  if (y < 1900 || date.getTime() > Date.now()) return null;
  return date.toISOString().slice(0, 10);
}

export function mapDonorRows(rows: string[][]): { valid: { line: number; row: DonorImportRow }[]; errors: { line: number; message: string }[] } {
  const valid: { line: number; row: DonorImportRow }[] = [];
  const errors: { line: number; message: string }[] = [];
  if (rows.length < 2) return { valid, errors: [{ line: 1, message: 'El archivo no tiene filas de datos.' }] };

  const headers = rows[0].map((h) => ALIASES[norm(h)] ?? '');
  const required = ['dni', 'first_name', 'last_name', 'gender', 'birth_date', 'phone'];
  const labels: Record<string, string> = { dni: 'dni', first_name: 'nombres', last_name: 'apellidos', gender: 'sexo', birth_date: 'fecha_nacimiento', phone: 'telefono' };
  const missing = required.filter((r) => !headers.includes(r));
  if (missing.length) return { valid, errors: [{ line: 1, message: `Faltan columnas: ${missing.map((m) => labels[m]).join(', ')}.` }] };

  const seen = new Set<string>();
  rows.slice(1).forEach((cells, index) => {
    const line = index + 2;
    const get = (key: string) => (cells[headers.indexOf(key)] ?? '').trim();
    const dni = get('dni').replace(/\D/g, '');
    const gender = { m: 'M', h: 'M', hombre: 'M', masculino: 'M', f: 'F', mujer: 'F', femenino: 'F' }[norm(get('gender'))] as 'M' | 'F' | undefined;
    const birth = parseDate(get('birth_date'));
    const phone = get('phone').replace(/\D/g, '');
    const email = get('email').toLowerCase();
    const unknownBlood = ['', 'no_se', 'ni_idea', 'desconocido', 'sin_dato', 'na', 'n_a'].includes(norm(get('blood')));
    const bloodRaw = unknownBlood ? '' : get('blood').toUpperCase().replace(/\s/g, '');
    const bloodOk = bloodRaw === '' || /^(O|A|B|AB)[+-]$/.test(bloodRaw);

    const problem =
      !/^\d{8}$/.test(dni) ? 'DNI inválido (8 números)' :
      seen.has(dni) ? 'DNI repetido en el archivo' :
      !get('first_name') || !get('last_name') ? 'Falta nombre o apellido' :
      !gender ? 'Sexo debe ser M o F' :
      !birth ? 'Fecha de nacimiento inválida' :
      phone.length < 7 ? 'Teléfono inválido' :
      email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ? 'Correo inválido' :
      !bloodOk ? 'Grupo sanguíneo inválido (ej. O+, A-)' : '';
    if (problem) { errors.push({ line, message: problem }); return; }

    seen.add(dni);
    valid.push({
      line,
      row: {
        dni, first_name: get('first_name'), last_name: get('last_name'), gender: gender!, birth_date: birth!, phone,
        email: email || null,
        blood_type: bloodRaw ? bloodRaw.slice(0, -1) : null, rh_factor: bloodRaw ? bloodRaw.slice(-1) : null,
      },
    });
  });
  return { valid, errors };
}
