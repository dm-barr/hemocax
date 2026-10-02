'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { callApi } from './api';
import { Badge, EMAIL_STATUS_LABEL, EMAIL_TYPE_LABEL, Empty, Field, Notify, PageHeader, friendlyError } from './ui';

type Mail = { id: number; type: string; status: string; message: string; created_at: string; error_message: string | null; created_by_name: string | null; donors: { first_name: string; last_name: string } | null };
type Target = { id: number; first_name: string; last_name: string; dni: string };

const DEFAULT_MESSAGE = 'Hola {{nombre}}, gracias por ser parte de HEMOCAX.';

export default function EmailsTab({ notify }: { notify: Notify }) {
  const [mails, setMails] = useState<Mail[]>([]);
  const [targets, setTargets] = useState<Target[]>([]);
  const [loading, setLoading] = useState(true);
  const [donorId, setDonorId] = useState('');
  const [message, setMessage] = useState(DEFAULT_MESSAGE);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const supabase = getBrowserSupabaseClient();
    const [m, t] = await Promise.all([
      supabase.from('communications').select('id,type,status,message,created_at,error_message,created_by_name,donors(first_name,last_name)').order('created_at', { ascending: false }).limit(100),
      supabase.from('donors').select('id,first_name,last_name,dni').eq('status', 'ACTIVE').eq('consent_email', true).eq('opted_out', false).not('email', 'is', null).order('last_name'),
    ]);
    if (m.error) notify(friendlyError(m.error.message), 'error');
    else setMails((m.data || []) as unknown as Mail[]);
    setTargets((t.data || []) as Target[]);
    setLoading(false);
  }, [notify]);

  useEffect(() => { load(); }, [load]);

  async function send(e: FormEvent) {
    e.preventDefault();
    const donor = targets.find((t) => String(t.id) === donorId);
    if (!donor) return;
    setBusy(true);
    try {
      const row = await callApi('/api/communications/send', { donor_id: donor.id, type: 'MANUAL', message: message.replaceAll('{{nombre}}', donor.first_name) });
      if (row.status === 'FAILED') notify('El correo no se pudo enviar. Mira el detalle abajo en la lista.', 'error');
      else notify(`Correo enviado a ${donor.first_name}.`);
      setDonorId('');
      load();
    } catch (err) {
      notify(friendlyError(err instanceof Error ? err.message : 'No se pudo enviar el correo.'), 'error');
    }
    setBusy(false);
  }

  return (
    <>
      <PageHeader
        title="Correos enviados"
        help="Aquí puedes escribirle un correo a un donante y ver el historial de todo lo que se ha enviado, incluidos los avisos automáticos de cumpleaños y recordatorios."
      />

      <div className="card">
        <h3>Enviar un correo a un donante</h3>
        {targets.length === 0 && !loading ? (
          <p className="muted">Todavía no hay donantes con correo autorizado. Ve a <b>Donantes</b>, pulsa «Correos» en la fila del donante y registra su autorización.</p>
        ) : (
          <form onSubmit={send}>
            <Field label="Donante">
              <select required value={donorId} onChange={(e) => setDonorId(e.target.value)}>
                <option value="">Elige un donante…</option>
                {targets.map((t) => <option key={t.id} value={t.id}>{t.first_name} {t.last_name} — DNI {t.dni}</option>)}
              </select>
            </Field>
            <Field label="Mensaje" hint="Escribe {{nombre}} y se cambiará por el nombre del donante.">
              <textarea required rows={3} value={message} onChange={(e) => setMessage(e.target.value)} />
            </Field>
            <button className="primary" disabled={busy || !donorId}>{busy ? 'Enviando…' : 'Enviar correo'}</button>
          </form>
        )}
      </div>

      <h2 className="section-title">Historial</h2>
      {loading ? <p className="muted">Cargando…</p> : mails.length === 0 ? (
        <div className="card"><Empty title="Todavía no se ha enviado ningún correo" hint="Cuando envíes uno, o cuando se envíe uno automático, aparecerá aquí." /></div>
      ) : (
        <div className="card table-card">
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Fecha</th><th>Donante</th><th>Tipo</th><th>Canal</th><th>Enviado por</th><th>Estado</th><th>Mensaje</th></tr></thead>
              <tbody>
                {mails.map((c) => {
                  const status = EMAIL_STATUS_LABEL[c.status] ?? { text: c.status, tone: 'muted' as const };
                  return (
                    <tr key={c.id}>
                      <td>{new Date(c.created_at).toLocaleString('es-PE', { dateStyle: 'medium', timeStyle: 'short' })}</td>
                      <td>{c.donors ? `${c.donors.first_name} ${c.donors.last_name}` : '—'}</td>
                      <td>{EMAIL_TYPE_LABEL[c.type] ?? c.type}</td>
                      <td>Correo</td>
                      <td>{c.created_by_name ?? <span className="muted">—</span>}</td>
                      <td><Badge tone={status.tone}>{status.text}</Badge>{c.status === 'FAILED' && c.error_message && <><br /><small className="error">{c.error_message}</small></>}</td>
                      <td>{c.message}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}
