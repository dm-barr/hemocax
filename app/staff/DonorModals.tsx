'use client';

import { FormEvent, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Params } from '@/lib/params';
import { daysBetween } from '@/lib/eligibility';
import { callApi } from './api';
import { DonationRow } from './useDirectory';
import { Donor, Field, Modal, Notify, downloadFile, fullName, friendlyError, isAuthorized, todayISO } from './ui';

type ConsentEvent = { id: number; action: 'GRANTED' | 'REVOKED'; version: string | null; recorded_via: string; created_at: string };

export const BLOOD_GROUPS = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'];
const EMPTY_FORM = { dni: '', first_name: '', last_name: '', gender: 'F', birth_date: '', phone: '', email: '', blood: '', status: 'ACTIVE', consent: false };

export function DonorForm({ donor, initialDni, notify, onClose, onSaved }: { donor: Donor | null; initialDni?: string; notify: Notify; onClose: () => void; onSaved: (id?: number) => void }) {
  const [form, setForm] = useState(donor ? {
    dni: donor.dni, first_name: donor.first_name, last_name: donor.last_name, gender: donor.gender as string, birth_date: donor.birth_date,
    phone: donor.phone, email: donor.email ?? '', blood: donor.blood_type ? `${donor.blood_type}${donor.rh_factor}` : '', status: donor.status, consent: false,
  } : { ...EMPTY_FORM, dni: initialDni ?? '' });
  const [busy, setBusy] = useState(false);
  const set = (patch: Partial<typeof form>) => setForm((f) => ({ ...f, ...patch }));

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!/^\d{8}$/.test(form.dni)) { notify('El DNI debe tener exactamente 8 números.', 'error'); return; }
    setBusy(true);
    const supabase = getBrowserSupabaseClient();
    const data = {
      first_name: form.first_name.trim(), last_name: form.last_name.trim(), gender: form.gender, birth_date: form.birth_date,
      phone: form.phone.trim(), email: form.email.trim() || null,
      blood_type: form.blood ? form.blood.slice(0, -1) : null, rh_factor: form.blood ? form.blood.slice(-1) : null,
    };
    let newId: number | undefined;
    let error;
    if (donor) {
      ({ error } = await supabase.from('donors').update({ ...data, status: form.status, ...(data.email ? {} : { consent_email: false }) }).eq('id', donor.id));
    } else {
      const res = await supabase.from('donors').insert({
        ...data, dni: form.dni,
        ...(form.consent && data.email ? { consent_email: true, consent_at: new Date().toISOString(), consent_version: 'piloto-v1', opted_out: false } : {}),
      }).select('id').single();
      error = res.error;
      newId = res.data?.id;
    }
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify(donor ? 'Datos actualizados.' : `${data.first_name} quedó registrado como donante.`);
    onSaved(newId ?? donor?.id);
  }

  return (
    <Modal title={donor ? 'Editar datos del donante' : 'Registrar donante nuevo'} onClose={onClose}>
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
        <Field label="Grupo sanguíneo" hint="Si el donante no lo sabe, déjalo en «No sé» y complétalo cuando se lo midan.">
          <select value={form.blood} onChange={(e) => set({ blood: e.target.value })}>
            <option value="">No sé</option>
            {BLOOD_GROUPS.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </Field>

        {donor && (
          <Field label="Estado" hint="Un donante inactivo no recibe correos ni aparece como apto.">
            <select value={form.status} onChange={(e) => set({ status: e.target.value })}><option value="ACTIVE">Activo</option><option value="INACTIVE">Inactivo</option></select>
          </Field>
        )}

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

export function DonationModal({ donor, donations, params, notify, onClose, onSaved }: { donor: Donor; donations: DonationRow[]; params: Params; notify: Notify; onClose: () => void; onSaved: () => void }) {
  const [date, setDate] = useState(todayISO());
  const [notes, setNotes] = useState('');
  const [override, setOverride] = useState(false);
  const [busy, setBusy] = useState(false);

  const mine = donations.filter((x) => x.donor_id === donor.id);
  const limit = params.limits[donor.gender];
  const interval = params.intervals[donor.gender];
  const countInYear = mine.filter((x) => x.donation_date.slice(0, 4) === date.slice(0, 4)).length;
  const reached = countInYear >= limit;
  const previous = mine.filter((x) => x.donation_date <= date).reduce<string | null>((max, x) => (!max || x.donation_date > max ? x.donation_date : max), null);
  const elapsed = previous ? daysBetween(previous, date) : null;
  const tooSoon = elapsed !== null && elapsed < interval;

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    const supabase = getBrowserSupabaseClient();
    const { data: auth } = await supabase.auth.getUser();
    const { error } = await supabase.from('donations').insert({
      donor_id: donor.id, donation_date: date, donation_type: 'WHOLE_BLOOD',
      notes: [tooSoon ? 'Registrada antes del intervalo, autorizada por el médico.' : '', notes.trim()].filter(Boolean).join(' ') || null,
      created_by: auth.user?.id ?? null,
    });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Donación registrada. El resultado quedó pendiente de revisión del médico.');
    onSaved();
  }

  return (
    <Modal title="Registrar donación" onClose={onClose}>
      <form onSubmit={submit}>
        <p className="modal-lead">Donante: <b>{fullName(donor)}</b>{donor.blood_type ? ` · ${donor.blood_type}${donor.rh_factor}` : ''}</p>
        <Field label="Fecha de la donación" hint="Por defecto es hoy."><input required type="date" max={todayISO()} value={date} onChange={(e) => { setDate(e.target.value); setOverride(false); }} /></Field>
        <Field label="Notas (opcional)"><textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} /></Field>
        <p className={reached ? 'notice-box warn' : 'notice-box'}>
          {reached
            ? `Este donante ya llegó al máximo de ${limit} donaciones en ${date.slice(0, 4)}. No se puede registrar otra en ese año.`
            : `En ${date.slice(0, 4)} lleva ${countInYear} de ${limit} donaciones permitidas.`}
        </p>
        {tooSoon && !reached && (
          <>
            <p className="notice-box warn">Solo han pasado {elapsed} días desde su donación anterior; el intervalo establecido es de {interval} días.</p>
            <label className="check">
              <input type="checkbox" checked={override} onChange={(e) => setOverride(e.target.checked)} />
              <span>Registrar de todos modos: lo autorizó el médico responsable</span>
            </label>
          </>
        )}
        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose}>Cancelar</button>
          <button className="primary" disabled={busy || reached || (tooSoon && !override)}>{busy ? 'Guardando…' : 'Registrar donación'}</button>
        </div>
      </form>
    </Modal>
  );
}

export function ConsentModal({ donor, notify, onClose, onSaved }: { donor: Donor; notify: Notify; onClose: () => void; onSaved: () => void }) {
  const authorized = isAuthorized(donor);
  const [email, setEmail] = useState(donor.email ?? '');
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [text, setText] = useState<{ version: string; body: string } | null>(null);
  const [events, setEvents] = useState<ConsentEvent[]>([]);

  useEffect(() => {
    (async () => {
      const supabase = getBrowserSupabaseClient();
      const [v, ev] = await Promise.all([
        supabase.from('consent_versions').select('version,body').eq('active', true).maybeSingle(),
        supabase.from('consent_events').select('id,action,version,recorded_via,created_at').eq('donor_id', donor.id).order('created_at', { ascending: false }).limit(8),
      ]);
      if (v.data) setText(v.data);
      setEvents((ev.data || []) as ConsentEvent[]);
    })();
  }, [donor.id]);

  async function save(patch: object, okMessage: string) {
    setBusy(true);
    const { error } = await getBrowserSupabaseClient().from('donors').update(patch).eq('id', donor.id);
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify(okMessage);
    onSaved();
  }

  const history = events.length > 0 && (
    <>
      <p className="form-section">Historial de consentimiento</p>
      <ul className="history">
        {events.map((e) => (
          <li key={e.id}>
            <b>{e.action === 'GRANTED' ? 'Autorizó' : 'Revocó'}</b> · {new Date(e.created_at).toLocaleString('es-PE', { dateStyle: 'medium', timeStyle: 'short' })}
            {' '}· {e.recorded_via === 'DONOR' ? 'desde su portal' : e.recorded_via === 'STAFF' ? 'registrado por el personal' : 'sistema'}{e.version ? ` · texto ${e.version}` : ''}
          </li>
        ))}
      </ul>
    </>
  );

  return (
    <Modal title="Correos del donante" onClose={onClose}>
      <p className="modal-lead"><b>{fullName(donor)}</b> · {donor.email || 'sin correo registrado'}</p>
      {authorized ? (
        <>
          <p className="notice-box ok">Este donante autorizó recibir correos del Banco de Sangre (recordatorios, avisos de resultados y campañas).</p>
          <p className="muted">Si pidió dejar de recibirlos, quita la autorización. Podrás volver a activarla si cambia de opinión.</p>
          {history}
          <div className="modal-actions">
            <button className="secondary" onClick={onClose}>Cerrar</button>
            <button className="danger" disabled={busy} onClick={() => save({ consent_email: false, opted_out: true }, 'Listo: ya no recibirá correos.')}>Quitar autorización</button>
          </div>
        </>
      ) : (
        <>
          <p className="muted">El Banco de Sangre solo puede escribirle si el donante lo aceptó. Léele este texto y marca la casilla únicamente si lo aceptó.</p>
          {text && <div className="consent-text"><small>Texto {text.version}</small><p>{text.body}</p></div>}
          {!donor.email && (
            <Field label="Correo del donante" hint="Hace falta un correo para poder escribirle."><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
          )}
          <label className="check">
            <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
            <span>Confirmo que el donante conoce este texto y aceptó recibir correos del Banco de Sangre</span>
          </label>
          {history}
          <div className="modal-actions">
            <button className="secondary" onClick={onClose}>Cancelar</button>
            <button
              className="primary"
              disabled={busy || !confirmed || !text || !(donor.email || email.trim())}
              onClick={() => save(
                { consent_email: true, consent_at: new Date().toISOString(), consent_version: text?.version, opted_out: false, ...(donor.email ? {} : { email: email.trim() }) },
                'Listo: el donante ya puede recibir correos.',
              )}
            >Autorizar correos</button>
          </div>
        </>
      )}
    </Modal>
  );
}

export function DataModal({ donor, isAdmin, notify, onClose, onChanged }: { donor: Donor; isAdmin: boolean; notify: Notify; onClose: () => void; onChanged: () => void }) {
  const [typed, setTyped] = useState('');
  const [busy, setBusy] = useState(false);

  async function exportData() {
    setBusy(true);
    const supabase = getBrowserSupabaseClient();
    const [don, comm, ev] = await Promise.all([
      supabase.from('donations').select('*').eq('donor_id', donor.id),
      supabase.from('communications').select('type,channel,status,message,created_at').eq('donor_id', donor.id),
      supabase.from('consent_events').select('action,version,recorded_via,created_at').eq('donor_id', donor.id),
    ]);
    const ids = (don.data || []).map((x) => x.id);
    const res = ids.length ? await supabase.from('donation_results').select('status,critical,available_at,created_at').in('donation_id', ids) : { data: [] };
    const { auth_user_id: _omit, ...personal } = donor;
    void _omit;
    downloadFile(`datos-donante-${donor.dni}.json`, JSON.stringify({ donante: personal, donaciones: don.data, resultados: res.data, correos: comm.data, consentimiento: ev.data }, null, 2), 'application/json');
    setBusy(false);
  }

  async function deactivate() {
    setBusy(true);
    const { error } = await getBrowserSupabaseClient().from('donors').update({ status: 'INACTIVE', opted_out: true, consent_email: false }).eq('id', donor.id);
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('El donante quedó inactivo y ya no recibirá mensajes.');
    onChanged();
  }

  async function anonymize() {
    setBusy(true);
    try {
      await callApi('/api/admin/donors/anonymize', { donor_id: donor.id });
      notify('Datos personales eliminados. Se conservan las donaciones sin identificar a la persona.');
      onChanged();
    } catch (e) {
      notify(friendlyError(e instanceof Error ? e.message : 'No se pudo eliminar.'), 'error');
    }
    setBusy(false);
  }

  return (
    <Modal title="Datos y privacidad del donante" onClose={onClose}>
      <p className="modal-lead"><b>{fullName(donor)}</b> · DNI {donor.dni}</p>
      <div className="data-actions">
        <div><b>Descargar sus datos</b><p className="muted">Un archivo con todo lo que el sistema guarda de esta persona (derecho de acceso).</p><button className="secondary small" disabled={busy} onClick={exportData}>Descargar archivo</button></div>
        <div><b>Dar de baja</b><p className="muted">Pasa a inactivo y deja de recibir mensajes. Se conserva su historial.</p><button className="secondary small" disabled={busy || donor.status === 'INACTIVE'} onClick={deactivate}>{donor.status === 'INACTIVE' ? 'Ya está inactivo' : 'Dar de baja'}</button></div>
        {isAdmin && (
          <div>
            <b>Eliminar sus datos personales</b>
            <p className="muted">Borra su nombre, DNI, contacto y cuenta. Las donaciones quedan sin identificar. No se puede deshacer. Escribe su DNI para confirmar.</p>
            <input className="confirm-input" value={typed} onChange={(e) => setTyped(e.target.value.replace(/\D/g, ''))} placeholder={donor.dni} maxLength={8} aria-label="Escribe el DNI para confirmar" />
            <button className="danger small" disabled={busy || typed !== donor.dni} onClick={anonymize}>Eliminar datos personales</button>
          </div>
        )}
      </div>
      <div className="modal-actions"><button className="secondary" onClick={onClose}>Cerrar</button></div>
    </Modal>
  );
}
