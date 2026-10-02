'use client';

import { useCallback, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { callApi } from './api';
import { Badge, Empty, Field, Modal, Notify, PageHeader, RESULT_LABEL, friendlyError, isAuthorized } from './ui';

type ResultRow = {
  id: number; status: string; critical: boolean; created_at: string;
  donations: { donation_date: string; donors: { id: number; first_name: string; last_name: string; email: string | null; consent_email: boolean; opted_out: boolean } };
};

const hoursSince = (iso: string) => Math.floor((Date.now() - new Date(iso).getTime()) / 3_600_000);

export default function ResultsTab({ canRelease, notify }: { canRelease: boolean; notify: Notify }) {
  const [rows, setRows] = useState<ResultRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [releasing, setReleasing] = useState<ResultRow | null>(null);
  const [flagging, setFlagging] = useState<ResultRow | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    const { data, error } = await getBrowserSupabaseClient()
      .from('donation_results')
      .select('id,status,critical,created_at,donations!inner(donation_date,donors!inner(id,first_name,last_name,email,consent_email,opted_out))')
      .order('created_at', { ascending: false })
      .limit(200);
    if (error) notify(friendlyError(error.message), 'error');
    else setRows((data || []) as unknown as ResultRow[]);
    setLoading(false);
  }, [notify]);

  useEffect(() => { load(); }, [load]);

  async function notifyDonor(r: ResultRow) {
    const donor = r.donations.donors;
    setBusyId(r.id);
    try {
      const message = `Hola ${donor.first_name}. Hay información disponible sobre tu proceso de donación. Ingresa a ${window.location.origin} con tu DNI para revisarla.`;
      const sent = await callApi('/api/communications/send', { donor_id: donor.id, type: 'RESULT', result_id: r.id, message });
      notify(sent.status === 'FAILED' ? 'No se pudo enviar el correo. Revisa la pestaña Correos enviados.' : 'Correo enviado al donante.', sent.status === 'FAILED' ? 'error' : 'ok');
      load();
    } catch (e) {
      notify(friendlyError(e instanceof Error ? e.message : 'No se pudo enviar el correo.'), 'error');
    }
    setBusyId(null);
  }

  async function clearCritical(r: ResultRow) {
    setBusyId(r.id);
    const { error } = await getBrowserSupabaseClient().rpc('clear_result_critical', { p_result_id: r.id });
    setBusyId(null);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Se quitó la marca de crítico: vuelve a quedar pendiente de revisión.');
    load();
  }

  const pending = rows.filter((r) => r.status === 'PENDING' || r.critical);
  const released = rows.filter((r) => !(r.status === 'PENDING' || r.critical));

  const table = (list: ResultRow[], showAge: boolean) => (
    <div className="card table-card">
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Donante</th><th>Fecha de donación</th><th>Estado</th>{showAge && <th>Tiempo esperando</th>}<th>Acción</th></tr></thead>
          <tbody>
            {list.map((r) => {
              const donor = r.donations.donors;
              const label = r.critical ? RESULT_LABEL.CRITICAL_PENDING : RESULT_LABEL[r.status] ?? { text: r.status, tone: 'muted' as const };
              const hours = hoursSince(r.created_at);
              return (
                <tr key={r.id}>
                  <td><b>{donor.first_name} {donor.last_name}</b></td>
                  <td>{new Date(`${r.donations.donation_date}T00:00:00`).toLocaleDateString('es-PE', { day: 'numeric', month: 'long', year: 'numeric' })}</td>
                  <td><Badge tone={label.tone}>{label.text}</Badge></td>
                  {showAge && (
                    <td>{r.critical ? <span className="muted">—</span> : <Badge tone={hours >= 48 ? 'danger' : hours >= 36 ? 'warn' : 'muted'}>{hours >= 48 ? `${hours} h · pasó la meta` : hours >= 36 ? `${hours} h · por vencer` : `${hours} h`}</Badge>}</td>
                  )}
                  <td className="actions">
                    {r.critical && <p className="muted small-note">No se muestra en el portal. Comunícate con el donante por teléfono o cita presencial.</p>}
                    {r.critical && canRelease && <button className="secondary small" disabled={busyId === r.id} onClick={() => clearCritical(r)}>Quitar marca de crítico</button>}
                    {!r.critical && r.status === 'PENDING' && (
                      <>
                        {canRelease
                          ? <button className="primary small" onClick={() => setReleasing(r)}>Liberar resultado</button>
                          : <span className="muted">Solo personal autorizado puede liberarlo</span>}
                        <button className="danger small" onClick={() => setFlagging(r)}>Marcar como crítico</button>
                      </>
                    )}
                    {!r.critical && r.status === 'AVAILABLE' && (isAuthorized(donor) && donor.email
                      ? <button className="secondary small" disabled={busyId === r.id} onClick={() => notifyDonor(r)}>{busyId === r.id ? 'Enviando…' : 'Avisar por correo'}</button>
                      : <span className="muted">Sin correo autorizado para avisarle</span>)}
                    {!r.critical && (r.status === 'NOTIFIED' || r.status === 'CONSULTED') && <span className="muted">Listo</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <>
      <PageHeader
        title="Resultados"
        help="Cada vez que registras una donación se crea un resultado pendiente. Si es normal, libéralo para que el donante lo vea en su portal (la meta es hacerlo dentro de 48 horas) y avísale por correo. Si es reactivo o dudoso, márcalo como crítico: nunca se muestra en el portal."
      />
      {!canRelease && <p className="notice-box warn">Tu cuenta no tiene permiso para liberar resultados. Pídele a un administrador que te lo active.</p>}
      {loading ? <p className="muted">Cargando resultados…</p> : rows.length === 0 ? (
        <div className="card"><Empty title="Todavía no hay resultados" hint="Aparecen aquí automáticamente cuando registras una donación en la pestaña Donantes." /></div>
      ) : (
        <>
          <h2 className="section-title">Pendientes de revisión ({pending.length})</h2>
          {pending.length ? table(pending, true) : <div className="card"><p className="muted">No hay resultados pendientes.</p></div>}
          <h2 className="section-title">Ya liberados ({released.length})</h2>
          {released.length ? table(released, false) : <div className="card"><p className="muted">Todavía no has liberado ninguno.</p></div>}
        </>
      )}
      {releasing && <ReleaseModal row={releasing} notify={notify} onClose={() => setReleasing(null)} onDone={() => { setReleasing(null); load(); }} />}
      {flagging && <CriticalModal row={flagging} notify={notify} onClose={() => setFlagging(null)} onDone={() => { setFlagging(null); load(); }} />}
    </>
  );
}

function ReleaseModal({ row, notify, onClose, onDone }: { row: ResultRow; notify: Notify; onClose: () => void; onDone: () => void }) {
  const [message, setMessage] = useState('Tus resultados están disponibles. Gracias por donar.');
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const donor = row.donations.donors;

  async function release() {
    setBusy(true);
    const { error } = await getBrowserSupabaseClient().rpc('release_noncritical_result', { p_result_id: row.id, p_donor_message: message.trim() });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Resultado liberado. Ahora puedes avisarle por correo.');
    onDone();
  }

  return (
    <Modal title="Liberar resultado" onClose={onClose}>
      <p className="modal-lead">Donante: <b>{donor.first_name} {donor.last_name}</b></p>
      <p className="muted">Al liberarlo, el donante podrá verlo en su portal junto con las recomendaciones generales y la fecha en que podrá volver a donar. Hazlo solo si ya revisaste el resultado y es normal (no crítico).</p>
      <Field label="Mensaje para el donante" hint="No escribas datos médicos sensibles aquí.">
        <textarea rows={3} value={message} onChange={(e) => setMessage(e.target.value)} />
      </Field>
      <label className="check">
        <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
        <span>Confirmo que revisé el resultado y no es crítico</span>
      </label>
      <div className="modal-actions">
        <button className="secondary" onClick={onClose}>Cancelar</button>
        <button className="primary" disabled={busy || !confirmed || !message.trim()} onClick={release}>{busy ? 'Liberando…' : 'Liberar resultado'}</button>
      </div>
    </Modal>
  );
}

function CriticalModal({ row, notify, onClose, onDone }: { row: ResultRow; notify: Notify; onClose: () => void; onDone: () => void }) {
  const [busy, setBusy] = useState(false);
  const donor = row.donations.donors;

  async function flag() {
    setBusy(true);
    const { error } = await getBrowserSupabaseClient().rpc('mark_result_critical', { p_result_id: row.id });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Resultado marcado como crítico. No se mostrará al donante.');
    onDone();
  }

  return (
    <Modal title="Marcar como crítico" onClose={onClose}>
      <p className="modal-lead">Donante: <b>{donor.first_name} {donor.last_name}</b></p>
      <p className="notice-box warn">Un resultado crítico no se muestra en el portal ni se avisa por correo: el donante debe ser contactado por teléfono o en consulta presencial con el médico del Banco de Sangre.</p>
      <div className="modal-actions">
        <button className="secondary" onClick={onClose}>Cancelar</button>
        <button className="danger" disabled={busy} onClick={flag}>{busy ? 'Guardando…' : 'Sí, marcar como crítico'}</button>
      </div>
    </Modal>
  );
}
