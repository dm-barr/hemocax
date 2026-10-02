'use client';

import { useCallback, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { loadParams } from '@/lib/params';
import { Badge, EMAIL_TYPE_LABEL, Field, Notify, PageHeader, Profile, friendlyError } from './ui';

type Template = { type: string; subject: string; body: string; approved: boolean; approved_by: string | null; approved_at: string | null };

export default function ParamsTab({ notify, profile }: { notify: Notify; profile: Profile }) {
  const [loading, setLoading] = useState(true);
  const [nums, setNums] = useState({ male_interval_days: '90', female_interval_days: '90', male_annual_limit: '4', female_annual_limit: '3' });
  const [recs, setRecs] = useState('');
  const [contact, setContact] = useState('');
  const [consent, setConsent] = useState<{ version: string; body: string } | null>(null);
  const [consentDraft, setConsentDraft] = useState('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [drafts, setDrafts] = useState<Record<string, { subject: string; body: string }>>({});
  const [busy, setBusy] = useState('');

  const load = useCallback(async () => {
    const supabase = getBrowserSupabaseClient();
    const [p, c, t] = await Promise.all([
      loadParams(supabase),
      supabase.from('consent_versions').select('version,body').eq('active', true).maybeSingle(),
      supabase.from('message_templates').select('type,subject,body,approved,approved_by,approved_at').order('type'),
    ]);
    setNums({
      male_interval_days: String(p.intervals.M), female_interval_days: String(p.intervals.F),
      male_annual_limit: String(p.limits.M), female_annual_limit: String(p.limits.F),
    });
    setRecs(p.recommendations);
    setContact(p.contactInfo);
    if (c.data) { setConsent(c.data); setConsentDraft(c.data.body); }
    const list = (t.data || []) as Template[];
    setTemplates(list);
    setDrafts(Object.fromEntries(list.map((x) => [x.type, { subject: x.subject, body: x.body }])));
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function saveConfig(values: Record<string, number | string>, label: string) {
    setBusy(label);
    const supabase = getBrowserSupabaseClient();
    for (const [key, value] of Object.entries(values)) {
      const { error } = await supabase.from('system_config').update({ value, updated_at: new Date().toISOString() }).eq('key', key);
      if (error) { notify(friendlyError(error.message), 'error'); setBusy(''); return; }
    }
    notify('Guardado.');
    setBusy('');
  }

  async function saveDonation() {
    const entries = Object.entries(nums).map(([k, v]) => [k, Number(v)] as const);
    if (entries.some(([, v]) => !Number.isInteger(v) || v < 1 || v > 400)) { notify('Los valores deben ser números enteros entre 1 y 400.', 'error'); return; }
    await saveConfig(Object.fromEntries(entries), 'donation');
  }

  async function publishConsent() {
    setBusy('consent');
    const { data, error } = await getBrowserSupabaseClient().rpc('publish_consent_version', { p_body: consentDraft });
    setBusy('');
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify(`Se publicó el texto ${data}. Los próximos consentimientos usarán esta versión.`);
    load();
  }

  async function saveTemplate(t: Template) {
    setBusy(t.type);
    const d = drafts[t.type];
    const { error } = await getBrowserSupabaseClient().from('message_templates').update({ subject: d.subject.trim(), body: d.body.trim() }).eq('type', t.type);
    setBusy('');
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Mensaje guardado. Falta aprobarlo para que se envíe.');
    load();
  }

  async function approveTemplate(t: Template) {
    setBusy(t.type);
    const { error } = await getBrowserSupabaseClient().from('message_templates')
      .update({ approved: true, approved_by: profile.full_name, approved_at: new Date().toISOString() }).eq('type', t.type);
    setBusy('');
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Mensaje aprobado: ya puede enviarse en los recordatorios automáticos.');
    load();
  }

  if (loading) return <p className="muted">Cargando parámetros…</p>;

  return (
    <>
      <PageHeader title="Parámetros" help="Aquí se ajustan las reglas del sistema y los textos que ve el donante. Los valores de donación son provisionales hasta que el médico responsable los valide." />

      <div className="card">
        <h3>Reglas de donación</h3>
        <p className="muted">Cada cuántos días puede volver a donar una persona y cuántas donaciones de sangre total se permiten por año.</p>
        <div className="form-grid">
          <Field label="Intervalo hombres (días)"><input type="number" min={1} value={nums.male_interval_days} onChange={(e) => setNums({ ...nums, male_interval_days: e.target.value })} /></Field>
          <Field label="Intervalo mujeres (días)"><input type="number" min={1} value={nums.female_interval_days} onChange={(e) => setNums({ ...nums, female_interval_days: e.target.value })} /></Field>
          <Field label="Máximo anual hombres"><input type="number" min={1} value={nums.male_annual_limit} onChange={(e) => setNums({ ...nums, male_annual_limit: e.target.value })} /></Field>
          <Field label="Máximo anual mujeres"><input type="number" min={1} value={nums.female_annual_limit} onChange={(e) => setNums({ ...nums, female_annual_limit: e.target.value })} /></Field>
        </div>
        <button className="primary" disabled={busy === 'donation'} onClick={saveDonation}>{busy === 'donation' ? 'Guardando…' : 'Guardar reglas'}</button>
      </div>

      <div className="card">
        <h3>Recomendaciones junto al resultado</h3>
        <p className="muted">Este texto lo ve el donante en su portal junto con su resultado liberado y la fecha de su próxima donación. Debe validarlo la Jefatura del Banco de Sangre.</p>
        <Field label="Recomendaciones"><textarea rows={4} value={recs} onChange={(e) => setRecs(e.target.value)} /></Field>
        <button className="primary" disabled={busy === 'recs' || !recs.trim()} onClick={() => saveConfig({ result_recommendations: recs.trim() }, 'recs')}>{busy === 'recs' ? 'Guardando…' : 'Guardar recomendaciones'}</button>
      </div>

      <div className="card">
        <h3>Dónde y cuándo donar</h3>
        <p className="muted">Este texto lo ve el donante en su portal, en «¿Dónde donar?». Escribe la dirección, el horario y un teléfono del Banco de Sangre, en lenguaje sencillo.</p>
        <Field label="Dirección, horario y teléfono"><textarea rows={4} value={contact} onChange={(e) => setContact(e.target.value)} /></Field>
        <button className="primary" disabled={busy === 'contact' || !contact.trim()} onClick={() => saveConfig({ contact_info: contact.trim() }, 'contact')}>{busy === 'contact' ? 'Guardando…' : 'Guardar datos de contacto'}</button>
      </div>

      <div className="card">
        <h3>Texto del consentimiento</h3>
        <p className="muted">Es lo que se le lee o muestra al donante antes de autorizar los correos. Cada cambio crea una versión nueva; los consentimientos ya dados conservan la versión que aceptaron.</p>
        {consent && <p><Badge tone="info">Versión vigente: {consent.version}</Badge></p>}
        <Field label="Texto"><textarea rows={7} value={consentDraft} onChange={(e) => setConsentDraft(e.target.value)} /></Field>
        <button className="primary" disabled={busy === 'consent' || consentDraft.trim() === (consent?.body ?? '').trim()} onClick={publishConsent}>{busy === 'consent' ? 'Publicando…' : 'Publicar nueva versión'}</button>
      </div>

      <div className="card">
        <h3>Mensajes automáticos</h3>
        <p className="notice-box warn">Un mensaje automático solo se envía si está <b>aprobado</b>. Si lo editas, vuelve a quedar sin aprobar hasta que la Jefatura lo valide. Usa {'{{nombre}}'} para el nombre del donante.</p>
        {templates.map((t) => {
          const d = drafts[t.type] ?? { subject: t.subject, body: t.body };
          const dirty = d.subject.trim() !== t.subject || d.body.trim() !== t.body;
          return (
            <div className="template" key={t.type}>
              <div className="campaign-head">
                <h4>{EMAIL_TYPE_LABEL[t.type] ?? t.type}</h4>
                {t.approved ? <Badge tone="ok">Aprobado por {t.approved_by}</Badge> : <Badge tone="warn">Sin aprobar</Badge>}
              </div>
              <Field label="Asunto"><input value={d.subject} onChange={(e) => setDrafts({ ...drafts, [t.type]: { ...d, subject: e.target.value } })} /></Field>
              <Field label="Mensaje"><textarea rows={3} value={d.body} onChange={(e) => setDrafts({ ...drafts, [t.type]: { ...d, body: e.target.value } })} /></Field>
              <div className="card-actions">
                <button className="secondary small" disabled={!dirty || busy === t.type || !d.subject.trim() || !d.body.trim()} onClick={() => saveTemplate(t)}>Guardar cambios</button>
                <button className="primary small" disabled={t.approved || dirty || busy === t.type} onClick={() => approveTemplate(t)}>Aprobar mensaje</button>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
