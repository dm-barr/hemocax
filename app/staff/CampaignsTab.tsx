'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { callApi } from './api';
import { Badge, Empty, Field, Modal, Notify, PageHeader, friendlyError } from './ui';

type Campaign = { id: number; name: string; description: string | null; message_template: string; status: string };
type Target = { id: number; first_name: string; email: string; blood_type: string; rh_factor: string };

const GROUPS = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'];
const DEFAULT_MESSAGE = 'Hola {{nombre}}, el Banco de Sangre del HRDC te invita a donar sangre. ¡Tu ayuda salva vidas!';

export default function CampaignsTab({ notify }: { notify: Notify }) {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [sending, setSending] = useState<Campaign | null>(null);

  const load = useCallback(async () => {
    const { data, error } = await getBrowserSupabaseClient().from('campaigns').select('id,name,description,message_template,status').order('created_at', { ascending: false });
    if (error) notify(friendlyError(error.message), 'error');
    else setCampaigns((data || []) as Campaign[]);
    setLoading(false);
  }, [notify]);

  useEffect(() => { load(); }, [load]);

  return (
    <>
      <PageHeader
        title="Campañas"
        help="Una campaña es un mensaje que se envía por correo a varios donantes a la vez, por ejemplo: «Necesitamos sangre O negativo». Solo lo reciben los donantes que autorizaron correos."
        action={<button className="primary" onClick={() => setCreating(true)}>+ Crear campaña</button>}
      />
      {loading ? <p className="muted">Cargando campañas…</p> : campaigns.length === 0 ? (
        <div className="card">
          <Empty title="Todavía no hay campañas" hint="Crea la primera y luego elige a quién enviarla." action={<button className="primary" onClick={() => setCreating(true)}>Crear mi primera campaña</button>} />
        </div>
      ) : (
        <div className="cards">
          {campaigns.map((c) => (
            <div className="card campaign" key={c.id}>
              <div className="campaign-head"><h3>{c.name}</h3><Badge tone={c.status === 'ACTIVE' ? 'ok' : 'muted'}>{c.status === 'ACTIVE' ? 'Activa' : 'Cerrada'}</Badge></div>
              {c.description && <p className="muted">{c.description}</p>}
              <p className="quote">{c.message_template}</p>
              <button className="primary small" onClick={() => setSending(c)}>Enviar campaña</button>
            </div>
          ))}
        </div>
      )}
      {creating && <CreateModal notify={notify} onClose={() => setCreating(false)} onSaved={() => { setCreating(false); load(); }} />}
      {sending && <SendModal campaign={sending} notify={notify} onClose={() => setSending(null)} />}
    </>
  );
}

function CreateModal({ notify, onClose, onSaved }: { notify: Notify; onClose: () => void; onSaved: () => void }) {
  const [form, setForm] = useState({ name: '', description: '', message_template: DEFAULT_MESSAGE });
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    const { error } = await getBrowserSupabaseClient().from('campaigns').insert({ ...form, status: 'ACTIVE' });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Campaña creada. Ya puedes enviarla.');
    onSaved();
  }

  return (
    <Modal title="Crear campaña" onClose={onClose}>
      <form onSubmit={submit}>
        <Field label="Nombre de la campaña" hint="Solo para que tú la reconozcas."><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></Field>
        <Field label="Descripción (opcional)"><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></Field>
        <Field label="Mensaje que recibirá cada donante" hint="Escribe {{nombre}} y se cambiará por el nombre de cada persona.">
          <textarea required rows={4} value={form.message_template} onChange={(e) => setForm({ ...form, message_template: e.target.value })} />
        </Field>
        <p className="quote">Vista previa: {form.message_template.replaceAll('{{nombre}}', 'Ana')}</p>
        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose}>Cancelar</button>
          <button className="primary" disabled={busy}>{busy ? 'Guardando…' : 'Crear campaña'}</button>
        </div>
      </form>
    </Modal>
  );
}

function SendModal({ campaign, notify, onClose }: { campaign: Campaign; notify: Notify; onClose: () => void }) {
  const [group, setGroup] = useState('');
  const [candidates, setCandidates] = useState<Target[] | null>(null);
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);

  useEffect(() => {
    (async () => {
      const supabase = getBrowserSupabaseClient();
      const [donors, already] = await Promise.all([
        supabase.from('donors').select('id,first_name,email,blood_type,rh_factor').eq('status', 'ACTIVE').eq('consent_email', true).eq('opted_out', false).not('email', 'is', null),
        supabase.from('campaign_recipients').select('donor_id').eq('campaign_id', campaign.id),
      ]);
      const received = new Set((already.data || []).map((r) => r.donor_id));
      setCandidates(((donors.data || []) as Target[]).filter((d) => !received.has(d.id)));
    })();
  }, [campaign.id]);

  const targets = (candidates ?? []).filter((d) => !group || `${d.blood_type}${d.rh_factor}` === group);

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
    notify(failed ? `Campaña enviada a ${ok} donante(s). ${failed} no se pudieron enviar (revisa Correos enviados).` : `Campaña enviada a ${ok} donante(s).`, failed ? 'error' : 'ok');
    onClose();
  }

  return (
    <Modal title={`Enviar «${campaign.name}»`} onClose={progress ? () => undefined : onClose}>
      <Field label="¿A quién se la enviamos?">
        <select value={group} onChange={(e) => setGroup(e.target.value)} disabled={!!progress}>
          <option value="">A todos los donantes con correo autorizado</option>
          {GROUPS.map((g) => <option key={g} value={g}>Solo grupo {g}</option>)}
        </select>
      </Field>
      <p className="quote">{campaign.message_template.replaceAll('{{nombre}}', 'Ana')}</p>
      {candidates === null ? <p className="muted">Calculando destinatarios…</p> : targets.length === 0 ? (
        <p className="notice-box warn">No hay donantes a quienes enviarla: deben tener correo autorizado y no haber recibido ya esta campaña.</p>
      ) : (
        <p className="notice-box">Se enviará a <b>{targets.length}</b> donante(s). Este paso no se puede deshacer.</p>
      )}
      {progress && <p className="muted">Enviando… {progress.done} de {progress.total}</p>}
      <div className="modal-actions">
        <button className="secondary" onClick={onClose} disabled={!!progress}>Cancelar</button>
        <button className="primary" disabled={!!progress || targets.length === 0} onClick={send}>{progress ? 'Enviando…' : `Enviar a ${targets.length}`}</button>
      </div>
    </Modal>
  );
}
