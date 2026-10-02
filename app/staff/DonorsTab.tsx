'use client';

import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Badge, Donor, Empty, Field, Modal, Notify, PageHeader, fullName, friendlyError, isAuthorized, todayISO } from './ui';

type DonationRow = { donor_id: number; donation_date: string };
type Filter = 'all' | 'authorized' | 'unauthorized';

const EMPTY_FORM = { dni: '', first_name: '', last_name: '', gender: 'F', birth_date: '', phone: '', email: '', blood_type: 'O', rh_factor: '+', consent: false };

export default function DonorsTab({ notify, intent }: { notify: Notify; intent?: string }) {
  const [donors, setDonors] = useState<Donor[]>([]);
  const [donations, setDonations] = useState<DonationRow[]>([]);
  const [limits, setLimits] = useState({ M: 4, F: 3 });
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<Filter>('all');
  const [editing, setEditing] = useState<Donor | 'new' | null>(intent === 'new' ? 'new' : null);
  const [donating, setDonating] = useState<Donor | null>(null);
  const [consenting, setConsenting] = useState<Donor | null>(null);

  const load = useCallback(async () => {
    const supabase = getBrowserSupabaseClient();
    const [d, ds, cfg] = await Promise.all([
      supabase.from('donors')
        .select('id,dni,first_name,last_name,gender,birth_date,phone,email,blood_type,rh_factor,status,consent_email,opted_out,auth_user_id')
        .order('last_name'),
      supabase.from('donations').select('donor_id,donation_date').eq('donation_type', 'WHOLE_BLOOD'),
      supabase.from('system_config').select('key,value').in('key', ['male_annual_limit', 'female_annual_limit']),
    ]);
    if (d.error) notify(friendlyError(d.error.message), 'error');
    else setDonors((d.data || []) as Donor[]);
    if (ds.data) setDonations(ds.data as DonationRow[]);
    if (cfg.data) {
      const map = Object.fromEntries(cfg.data.map((r) => [r.key, Number(r.value)]));
      setLimits({ M: map.male_annual_limit || 4, F: map.female_annual_limit || 3 });
    }
    setLoading(false);
  }, [notify]);

  useEffect(() => { load(); }, [load]);

  const year = String(new Date().getFullYear());
  const perDonor = useMemo(() => {
    const map = new Map<number, { thisYear: number; last: string }>();
    for (const x of donations) {
      const cur = map.get(x.donor_id) ?? { thisYear: 0, last: '' };
      if (x.donation_date.slice(0, 4) === year) cur.thisYear += 1;
      if (x.donation_date > cur.last) cur.last = x.donation_date;
      map.set(x.donor_id, cur);
    }
    return map;
  }, [donations, year]);

  const filtered = donors.filter((d) => {
    const text = `${fullName(d)} ${d.dni} ${d.email ?? ''}`.toLowerCase();
    if (!text.includes(query.toLowerCase())) return false;
    if (filter === 'all') return true;
    return filter === 'authorized' ? isAuthorized(d) : !isAuthorized(d);
  });

  return (
    <>
      <PageHeader
        title="Donantes"
        help="Aquí están todas las personas registradas como donantes. Desde aquí registras una donación nueva o anotas si el donante autorizó recibir correos."
        action={<button className="primary" onClick={() => setEditing('new')}>+ Registrar donante</button>}
      />

      <div className="toolbar">
        <input className="search" placeholder="Buscar por nombre, DNI o correo" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Buscar donante" />
        <div className="chips" role="group" aria-label="Filtrar">
          {([['all', 'Todos'], ['authorized', 'Con correo autorizado'], ['unauthorized', 'Sin autorizar']] as [Filter, string][]).map(([key, label]) => (
            <button key={key} className={filter === key ? 'chip active' : 'chip'} onClick={() => setFilter(key)}>{label}</button>
          ))}
        </div>
      </div>

      {loading ? <p className="muted">Cargando donantes…</p> : filtered.length === 0 ? (
        <div className="card">
          <Empty
            title={donors.length === 0 ? 'Todavía no hay donantes registrados' : 'No encontramos donantes con ese filtro'}
            hint={donors.length === 0 ? 'Empieza registrando al primero: solo necesitas su DNI, nombre, fecha de nacimiento y tipo de sangre.' : 'Prueba con otro nombre o cambia el filtro.'}
            action={donors.length === 0 ? <button className="primary" onClick={() => setEditing('new')}>Registrar el primer donante</button> : undefined}
          />
        </div>
      ) : (
        <div className="card table-card">
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Donante</th><th>Sangre</th><th>Contacto</th><th>Correos</th><th>Donaciones</th><th>Acciones</th></tr></thead>
              <tbody>
                {filtered.map((d) => {
                  const info = perDonor.get(d.id);
                  const limit = limits[d.gender];
                  return (
                    <tr key={d.id}>
                      <td><b>{fullName(d)}</b><br /><small>DNI {d.dni}{d.auth_user_id ? ' · tiene cuenta' : ''}</small></td>
                      <td><span className="blood-type">{d.blood_type}{d.rh_factor}</span></td>
                      <td>{d.email || <span className="muted">Sin correo</span>}<br /><small>{d.phone}</small></td>
                      <td>{d.opted_out ? <Badge tone="warn">No quiere correos</Badge> : d.consent_email ? <Badge tone="ok">Autorizado</Badge> : <Badge>Sin autorizar</Badge>}</td>
                      <td>
                        {info?.thisYear ?? 0} de {limit} este año<br />
                        <small>Última: {info?.last ? new Date(`${info.last}T00:00:00`).toLocaleDateString('es-PE', { day: 'numeric', month: 'short', year: 'numeric' }) : 'ninguna'}</small>
                      </td>
                      <td className="actions">
                        <button className="primary small" onClick={() => setDonating(d)}>Registrar donación</button>
                        <button className="secondary small" onClick={() => setConsenting(d)}>Correos</button>
                        <button className="secondary small" onClick={() => setEditing(d)}>Editar</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {editing && <DonorForm donor={editing === 'new' ? null : editing} notify={notify} onClose={() => setEditing(null)} onSaved={() => { setEditing(null); load(); }} />}
      {donating && <DonationModal donor={donating} donations={donations} limit={limits[donating.gender]} notify={notify} onClose={() => setDonating(null)} onSaved={() => { setDonating(null); load(); }} />}
      {consenting && <ConsentModal donor={consenting} notify={notify} onClose={() => setConsenting(null)} onSaved={() => { setConsenting(null); load(); }} />}
    </>
  );
}

function DonorForm({ donor, notify, onClose, onSaved }: { donor: Donor | null; notify: Notify; onClose: () => void; onSaved: () => void }) {
  const [form, setForm] = useState(donor ? {
    dni: donor.dni, first_name: donor.first_name, last_name: donor.last_name, gender: donor.gender as string, birth_date: donor.birth_date,
    phone: donor.phone, email: donor.email ?? '', blood_type: donor.blood_type, rh_factor: donor.rh_factor, consent: false,
  } : EMPTY_FORM);
  const [busy, setBusy] = useState(false);
  const set = (patch: Partial<typeof form>) => setForm((f) => ({ ...f, ...patch }));

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!/^\d{8}$/.test(form.dni)) { notify('El DNI debe tener exactamente 8 números.', 'error'); return; }
    setBusy(true);
    const supabase = getBrowserSupabaseClient();
    const data = {
      first_name: form.first_name.trim(), last_name: form.last_name.trim(), gender: form.gender, birth_date: form.birth_date,
      phone: form.phone.trim(), email: form.email.trim() || null, blood_type: form.blood_type, rh_factor: form.rh_factor,
    };
    const { error } = donor
      ? await supabase.from('donors').update({ ...data, ...(data.email ? {} : { consent_email: false }) }).eq('id', donor.id)
      : await supabase.from('donors').insert({
          ...data, dni: form.dni,
          ...(form.consent && data.email ? { consent_email: true, consent_at: new Date().toISOString(), consent_version: 'piloto-v1-personal', opted_out: false } : {}),
        });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify(donor ? 'Datos actualizados.' : `${data.first_name} quedó registrado como donante.`);
    onSaved();
  }

  return (
    <Modal title={donor ? 'Editar donante' : 'Registrar donante'} onClose={onClose}>
      <form onSubmit={submit}>
        <p className="form-section">Datos personales</p>
        <div className="form-grid">
          <Field label="DNI" hint={donor ? 'El DNI no se puede cambiar.' : '8 números'}>
            <input required maxLength={8} inputMode="numeric" disabled={!!donor} value={form.dni} onChange={(e) => set({ dni: e.target.value.replace(/\D/g, '') })} />
          </Field>
          <Field label="Fecha de nacimiento"><input required type="date" max={todayISO()} value={form.birth_date} onChange={(e) => set({ birth_date: e.target.value })} /></Field>
          <Field label="Nombres"><input required value={form.first_name} onChange={(e) => set({ first_name: e.target.value })} /></Field>
          <Field label="Apellidos"><input required value={form.last_name} onChange={(e) => set({ last_name: e.target.value })} /></Field>
          <Field label="Sexo" hint="Define el máximo de donaciones por año."><select value={form.gender} onChange={(e) => set({ gender: e.target.value })}><option value="F">Mujer</option><option value="M">Hombre</option></select></Field>
        </div>

        <p className="form-section">Contacto</p>
        <div className="form-grid">
          <Field label="Correo electrónico" hint="Recomendado: sin correo no podemos avisarle de sus resultados.">
            <input type="email" value={form.email} onChange={(e) => set({ email: e.target.value })} />
          </Field>
          <Field label="Teléfono"><input required inputMode="tel" value={form.phone} onChange={(e) => set({ phone: e.target.value })} /></Field>
        </div>

        <p className="form-section">Tipo de sangre</p>
        <div className="form-grid">
          <Field label="Grupo"><select value={form.blood_type} onChange={(e) => set({ blood_type: e.target.value })}>{['O', 'A', 'B', 'AB'].map((x) => <option key={x}>{x}</option>)}</select></Field>
          <Field label="Factor RH"><select value={form.rh_factor} onChange={(e) => set({ rh_factor: e.target.value })}><option value="+">Positivo (+)</option><option value="-">Negativo (−)</option></select></Field>
        </div>

        {!donor && (
          <label className="check">
            <input type="checkbox" checked={form.consent} disabled={!form.email.trim()} onChange={(e) => set({ consent: e.target.checked })} />
            <span>El donante aceptó recibir correos del Banco de Sangre {!form.email.trim() && <em>(escribe su correo para marcar esto)</em>}</span>
          </label>
        )}

        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose}>Cancelar</button>
          <button className="primary" disabled={busy}>{busy ? 'Guardando…' : donor ? 'Guardar cambios' : 'Registrar donante'}</button>
        </div>
      </form>
    </Modal>
  );
}

function DonationModal({ donor, donations, limit, notify, onClose, onSaved }: { donor: Donor; donations: DonationRow[]; limit: number; notify: Notify; onClose: () => void; onSaved: () => void }) {
  const [date, setDate] = useState(todayISO());
  const [notes, setNotes] = useState('');
  const [busy, setBusy] = useState(false);
  const countInYear = donations.filter((x) => x.donor_id === donor.id && x.donation_date.slice(0, 4) === date.slice(0, 4)).length;
  const reached = countInYear >= limit;

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    const supabase = getBrowserSupabaseClient();
    const { data: auth } = await supabase.auth.getUser();
    const { error } = await supabase.from('donations').insert({
      donor_id: donor.id, donation_date: date, donation_type: 'WHOLE_BLOOD', notes: notes.trim() || null, created_by: auth.user?.id ?? null,
    });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Donación registrada. Quedó un resultado pendiente de revisión en la pestaña Resultados.');
    onSaved();
  }

  return (
    <Modal title="Registrar donación" onClose={onClose}>
      <form onSubmit={submit}>
        <p className="modal-lead">Donante: <b>{fullName(donor)}</b> · {donor.blood_type}{donor.rh_factor}</p>
        <Field label="Fecha de la donación"><input required type="date" max={todayISO()} value={date} onChange={(e) => setDate(e.target.value)} /></Field>
        <Field label="Notas (opcional)"><textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} /></Field>
        <p className={reached ? 'notice-box warn' : 'notice-box'}>
          {reached
            ? `Este donante ya llegó al máximo de ${limit} donaciones en ${date.slice(0, 4)}. No se puede registrar otra en ese año.`
            : `En ${date.slice(0, 4)} lleva ${countInYear} de ${limit} donaciones permitidas.`}
        </p>
        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose}>Cancelar</button>
          <button className="primary" disabled={busy || reached}>{busy ? 'Guardando…' : 'Registrar donación'}</button>
        </div>
      </form>
    </Modal>
  );
}

function ConsentModal({ donor, notify, onClose, onSaved }: { donor: Donor; notify: Notify; onClose: () => void; onSaved: () => void }) {
  const authorized = isAuthorized(donor);
  const [email, setEmail] = useState(donor.email ?? '');
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);

  async function save(patch: object, okMessage: string) {
    setBusy(true);
    const { error } = await getBrowserSupabaseClient().from('donors').update(patch).eq('id', donor.id);
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify(okMessage);
    onSaved();
  }

  return (
    <Modal title="Correos del donante" onClose={onClose}>
      <p className="modal-lead"><b>{fullName(donor)}</b> · {donor.email || 'sin correo registrado'}</p>
      {authorized ? (
        <>
          <p className="notice-box ok">Este donante autorizó recibir correos del Banco de Sangre (recordatorios, avisos de resultados y campañas).</p>
          <p className="muted">Si pidió dejar de recibirlos, quita la autorización. Podrás volver a activarla si cambia de opinión.</p>
          <div className="modal-actions">
            <button className="secondary" onClick={onClose}>Cerrar</button>
            <button className="danger" disabled={busy} onClick={() => save({ consent_email: false, opted_out: true }, 'Listo: ya no recibirá correos.')}>Quitar autorización</button>
          </div>
        </>
      ) : (
        <>
          <p className="muted">El Banco de Sangre solo puede escribirle si el donante lo aceptó. Marca la casilla únicamente si te lo confirmó él mismo.</p>
          {!donor.email && (
            <Field label="Correo del donante" hint="Hace falta un correo para poder escribirle."><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
          )}
          <label className="check">
            <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
            <span>Confirmo que el donante aceptó recibir correos del Banco de Sangre</span>
          </label>
          <div className="modal-actions">
            <button className="secondary" onClick={onClose}>Cancelar</button>
            <button
              className="primary"
              disabled={busy || !confirmed || !(donor.email || email.trim())}
              onClick={() => save(
                { consent_email: true, consent_at: new Date().toISOString(), consent_version: 'piloto-v1-personal', opted_out: false, ...(donor.email ? {} : { email: email.trim() }) },
                'Listo: el donante ya puede recibir correos.',
              )}
            >Autorizar correos</button>
          </div>
        </>
      )}
    </Modal>
  );
}
