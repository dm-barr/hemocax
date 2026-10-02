'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { loadParams } from '@/lib/params';
import { computeEligibility } from '@/lib/eligibility';
import { callApi } from './api';
import { Badge, Empty, Field, Modal, Notify, PageHeader, friendlyError } from './ui';

type Campaign = { id: number; name: string; description: string | null; message_template: string; status: string; kind: 'CAMPAIGN' | 'INFO' };
type Target = { id: number; first_name: string; last_name: string; email: string; blood_type: string | null; rh_factor: string | null; gender: 'M' | 'F'; apto: boolean };

const GROUPS = ['O-', 'A-', 'B-', 'AB-', 'O+', 'A+', 'B+', 'AB+'];
const DEFAULT_MESSAGE = 'Hola {{nombre}}, el Banco de Sangre del HRDC te invita a donar sangre. ¡Tu ayuda salva vidas!';
const groupOf = (d: { blood_type: string | null; rh_factor: string | null }) => (d.blood_type ? `${d.blood_type}${d.rh_factor}` : '');

export default function CampaignsTab({ notify }: { notify: Notify }) {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Campaign | 'new' | null>(null);
  const [sending, setSending] = useState<Campaign | null>(null);

  const load = useCallback(async () => {
    const { data, error } = await getBrowserSupabaseClient().from('campaigns').select('id,name,description,message_template,status,kind').order('created_at', { ascending: false });
    if (error) notify(friendlyError(error.message), 'error');
    else setCampaigns((data || []) as Campaign[]);
    setLoading(false);
  }, [notify]);

  useEffect(() => { load(); }, [load]);

  async function toggle(c: Campaign) {
    const status = c.status === 'ACTIVE' ? 'CLOSED' : 'ACTIVE';
    const { error } = await getBrowserSupabaseClient().from('campaigns').update({ status }).eq('id', c.id);
    if (error) notify(friendlyError(error.message), 'error');
    else { notify(status === 'CLOSED' ? 'Campaña cerrada.' : 'Campaña reabierta.'); load(); }
  }

  return (
    <>
      <PageHeader
        title="Campañas e información"
        help="Una campaña es un mensaje que se envía por correo a varios donantes a la vez, por ejemplo: «Necesitamos sangre O negativo». La información educativa se publica además en el portal del donante. Solo reciben correos los donantes que lo autorizaron."
        action={<button className="primary" onClick={() => setEditing('new')}>+ Crear</button>}
      />
      {loading ? <p className="muted">Cargando…</p> : campaigns.length === 0 ? (
        <div className="card">
          <Empty title="Todavía no hay campañas" hint="Crea la primera y luego elige a quién enviarla." action={<button className="primary" onClick={() => setEditing('new')}>Crear mi primera campaña</button>} />
        </div>
      ) : (
        <div className="cards">
          {campaigns.map((c) => (
            <div className="card campaign" key={c.id}>
              <div className="campaign-head">
                <h3>{c.name}</h3>
                <span><Badge tone="info">{c.kind === 'INFO' ? 'Información' : 'Campaña'}</Badge> <Badge tone={c.status === 'ACTIVE' ? 'ok' : 'muted'}>{c.status === 'ACTIVE' ? 'Activa' : 'Cerrada'}</Badge></span>
              </div>
              {c.description && <p className="muted">{c.description}</p>}
              <p className="quote">{c.message_template}</p>
              <div className="card-actions">
                {c.status === 'ACTIVE' && <button className="primary small" onClick={() => setSending(c)}>Enviar por correo</button>}
                <button className="secondary small" onClick={() => setEditing(c)}>Editar</button>
                <button className="secondary small" onClick={() => toggle(c)}>{c.status === 'ACTIVE' ? 'Cerrar' : 'Reabrir'}</button>
              </div>
            </div>
          ))}
        </div>
      )}
      {editing && <EditModal campaign={editing === 'new' ? null : editing} notify={notify} onClose={() => setEditing(null)} onSaved={() => { setEditing(null); load(); }} />}
      {sending && <SendModal campaign={sending} notify={notify} onClose={() => setSending(null)} />}
    </>
  );
}

function EditModal({ campaign, notify, onClose, onSaved }: { campaign: Campaign | null; notify: Notify; onClose: () => void; onSaved: () => void }) {
  const [form, setForm] = useState({
    name: campaign?.name ?? '', description: campaign?.description ?? '', message_template: campaign?.message_template ?? DEFAULT_MESSAGE, kind: campaign?.kind ?? 'CAMPAIGN',
  });
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    const supabase = getBrowserSupabaseClient();
    const { error } = campaign
      ? await supabase.from('campaigns').update(form).eq('id', campaign.id)
      : await supabase.from('campaigns').insert({ ...form, status: 'ACTIVE' });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify(campaign ? 'Cambios guardados.' : 'Creada. Ya puedes enviarla.');
    onSaved();
  }

  return (
    <Modal title={campaign ? 'Editar' : 'Crear campaña o información'} onClose={onClose}>
      <form onSubmit={submit}>
        <Field label="Tipo" hint={form.kind === 'INFO' ? 'Se publica en el portal del donante y puede enviarse por correo.' : 'Se envía por correo a los donantes que elijas.'}>
          <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value as 'CAMPAIGN' | 'INFO' })}>
            <option value="CAMPAIGN">Campaña (convocatoria por correo)</option>
            <option value="INFO">Información educativa (consejos, requisitos…)</option>
          </select>
        </Field>
        <Field label="Título" hint="Es lo que ve el donante en su portal."><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></Field>
        <Field label="Descripción (opcional)"><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></Field>
        <Field label="Mensaje" hint="Escribe {{nombre}} y se cambiará por el nombre de cada persona.">
          <textarea required rows={4} value={form.message_template} onChange={(e) => setForm({ ...form, message_template: e.target.value })} />
        </Field>
        <p className="quote">Vista previa: {form.message_template.replaceAll('{{nombre}}', 'Ana')}</p>
        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose}>Cancelar</button>
          <button className="primary" disabled={busy}>{busy ? 'Guardando…' : 'Guardar'}</button>
        </div>
      </form>
    </Modal>
  );
}

function SendModal({ campaign, notify, onClose }: { campaign: Campaign; notify: Notify; onClose: () => void }) {
  const [group, setGroup] = useState('');
  const [onlyApto, setOnlyApto] = useState(true);
  const [candidates, setCandidates] = useState<Target[] | null>(null);
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);

  useEffect(() => {
    (async () => {
      const supabase = getBrowserSupabaseClient();
      const [donors, already, params] = await Promise.all([
        supabase.from('donors').select('id,first_name,last_name,email,blood_type,rh_factor,gender').eq('status', 'ACTIVE').eq('consent_email', true).eq('opted_out', false).not('email', 'is', null),
        supabase.from('campaign_recipients').select('donor_id').eq('campaign_id', campaign.id),
        loadParams(supabase),
      ]);
      const ids = (donors.data || []).map((d) => d.id);
      const dons = ids.length ? await supabase.from('donations').select('donor_id,donation_date').eq('donation_type', 'WHOLE_BLOOD').in('donor_id', ids) : { data: [] };
      const byDonor = new Map<number, string[]>();
      for (const x of dons.data || []) byDonor.set(x.donor_id, [...(byDonor.get(x.donor_id) || []), x.donation_date]);
      const received = new Set((already.data || []).map((r) => r.donor_id));
      setCandidates((donors.data || [])
        .filter((d) => !received.has(d.id))
        .map((d) => ({
          ...(d as Omit<Target, 'apto'>),
          apto: computeEligibility({ gender: d.gender, active: true, donationDates: byDonor.get(d.id) || [], params }).state === 'APTO',
        })));
    })();
  }, [campaign.id]);

  const pool = (candidates ?? []).filter((d) => !onlyApto || d.apto);
  const targets = pool.filter((d) => !group || groupOf(d) === group);
  const countByGroup = (g: string) => pool.filter((d) => groupOf(d) === g).length;

  async function send() {
    const supabase = getBrowserSupabaseClient();
    let ok = 0;
    let failed = 0;
    setProgress({ done: 0, total: targets.length });
    for (const donor of targets) {
      try {
        const row = await callApi('/api/communications/send', {
          donor_id: donor.id, type: 'CAMPAIGN', campaign_id: campaign.id,
          message: campaign.message_template.replaceAll('{{nombre}}', donor.first_name),
        });
        await supabase.from('campaign_recipients').insert({ campaign_id: campaign.id, donor_id: donor.id, communication_id: row.id, status: row.status });
        if (row.status === 'FAILED') failed += 1; else ok += 1;
      } catch {
        failed += 1;
      }
      setProgress({ done: ok + failed, total: targets.length });
    }
    notify(failed ? `Enviada a ${ok} donante(s). ${failed} no se pudieron enviar (revisa Correos enviados).` : `Enviada a ${ok} donante(s).`, failed ? 'error' : 'ok');
    onClose();
  }

  return (
    <Modal title={`Enviar «${campaign.name}»`} onClose={progress ? () => undefined : onClose}>
      <p className="muted">Elige a quién convocar. Solo se incluyen donantes activos con correo autorizado que aún no recibieron esta campaña.</p>
      <label className="check">
        <input type="checkbox" checked={onlyApto} onChange={(e) => setOnlyApto(e.target.checked)} disabled={!!progress} />
        <span>Solo donantes que pueden donar hoy (cumplieron el intervalo y no llegaron al máximo anual)</span>
      </label>
      <p className="form-section">Prioridad por grupo sanguíneo</p>
      <div className="chips group-chips">
        <button className={group === '' ? 'chip active' : 'chip'} onClick={() => setGroup('')} disabled={!!progress}>Todos ({pool.length})</button>
        {GROUPS.map((g) => <button key={g} className={group === g ? 'chip active' : 'chip'} onClick={() => setGroup(g)} disabled={!!progress}>{g} ({candidates ? countByGroup(g) : '…'})</button>)}
      </div>
      <p className="quote">{campaign.message_template.replaceAll('{{nombre}}', 'Ana')}</p>
      {candidates === null ? <p className="muted">Calculando destinatarios…</p> : targets.length === 0 ? (
        <p className="notice-box warn">No hay donantes para este filtro. Prueba otro grupo o quita la restricción de aptitud.</p>
      ) : (
        <>
          <p className="notice-box">Se enviará a <b>{targets.length}</b> donante(s). Revisa la lista y confirma: este paso no se puede deshacer.</p>
          <details><summary>Ver destinatarios</summary><ul className="recipients">{targets.map((d) => <li key={d.id}>{d.first_name} {d.last_name} · {groupOf(d) || 'sin grupo'}</li>)}</ul></details>
        </>
      )}
      {progress && <p className="muted">Enviando… {progress.done} de {progress.total}</p>}
      <div className="modal-actions">
        <button className="secondary" onClick={onClose} disabled={!!progress}>Cancelar</button>
        <button className="primary" disabled={!!progress || targets.length === 0} onClick={send}>{progress ? 'Enviando…' : `Confirmar y enviar a ${targets.length}`}</button>
      </div>
    </Modal>
  );
}
