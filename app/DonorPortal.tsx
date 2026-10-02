'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Params, loadParams } from '@/lib/params';
import { computeEligibility } from '@/lib/eligibility';
import { Modal, downloadFile } from './staff/ui';

type Profile = { dni: string; full_name: string };
type Donor = { id: number; first_name: string; last_name: string; gender: 'M' | 'F'; blood_type: string | null; rh_factor: string | null; consent_email: boolean; opted_out: boolean; status: string; email: string | null };
type Donation = { id: number; donation_date: string };
type Result = { id: number; status: string; available_at: string | null; donor_message: string | null; donations: { donation_date: string } | null };
type Campaign = { id: number; name: string; message_template: string; kind: 'CAMPAIGN' | 'INFO' };

const RELEASED = ['AVAILABLE', 'NOTIFIED', 'CONSULTED'];
const longDate = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString('es-PE', { day: 'numeric', month: 'long', year: 'numeric' });

export default function DonorPortal({ profile, onLogout }: { profile: Profile; onLogout: () => void }) {
  const [donor, setDonor] = useState<Donor | null>(null);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [results, setResults] = useState<Result[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [params, setParams] = useState<Params | null>(null);
  const [consentText, setConsentText] = useState<{ version: string; body: string } | null>(null);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [askConsent, setAskConsent] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [message, setMessage] = useState('');

  const load = useCallback(async () => {
    setState('loading');
    try {
      const supabase = getBrowserSupabaseClient();
      const { data: auth } = await supabase.auth.getUser();
      if (!auth.user) throw new Error('sin sesión');
      const { data: d, error } = await supabase.from('donors')
        .select('id,first_name,last_name,gender,blood_type,rh_factor,consent_email,opted_out,status,email').eq('auth_user_id', auth.user.id).single();
      if (error) throw error;
      setDonor(d as Donor);
      const [ds, rs, cs, cv, prm] = await Promise.all([
        supabase.from('donations').select('id,donation_date').eq('donor_id', d.id).order('donation_date', { ascending: false }),
        supabase.from('donation_results').select('id,status,available_at,donor_message,donations(donation_date)').order('created_at', { ascending: false }),
        supabase.from('campaigns').select('id,name,message_template,kind').eq('status', 'ACTIVE').order('created_at', { ascending: false }),
        supabase.from('consent_versions').select('version,body').eq('active', true).maybeSingle(),
        loadParams(supabase),
      ]);
      setDonations((ds.data ?? []) as Donation[]);
      setResults((rs.data ?? []) as unknown as Result[]);
      setCampaigns((cs.data ?? []) as Campaign[]);
      if (cv.data) setConsentText(cv.data);
      setParams(prm);
      setState('ready');
    } catch {
      setState('error');
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function setConsent(enabled: boolean) {
    if (!donor) return;
    const patch = enabled
      ? { consent_email: true, consent_at: new Date().toISOString(), consent_version: consentText?.version ?? 'piloto-v1', opted_out: false }
      : { consent_email: false, opted_out: true };
    const { error } = await getBrowserSupabaseClient().from('donors').update(patch).eq('id', donor.id);
    if (error) { setMessage('No se pudo guardar. Inténtalo de nuevo.'); return; }
    setDonor({ ...donor, consent_email: enabled, opted_out: !enabled });
    setAskConsent(false);
    setAccepted(false);
    setMessage(enabled ? 'Listo. Ahora recibirás avisos por correo.' : 'Listo. Ya no recibirás avisos por correo.');
  }

  async function downloadMyData() {
    if (!donor) return;
    const supabase = getBrowserSupabaseClient();
    const [me, ev] = await Promise.all([
      supabase.from('donors').select('*').eq('id', donor.id).single(),
      supabase.from('consent_events').select('action,version,recorded_via,created_at').eq('donor_id', donor.id),
    ]);
    const { auth_user_id: _omit, ...personal } = (me.data ?? {}) as Record<string, unknown>;
    void _omit;
    downloadFile('mis-datos-hemocax.json', JSON.stringify({ datos_personales: personal, donaciones: donations, resultados: results, consentimiento: ev.data }, null, 2), 'application/json');
  }

  if (state === 'loading') return <main className="dp"><DpTop onLogout={onLogout} /><p className="dp-status">Cargando tus datos…</p></main>;
  if (state === 'error' || !donor || !params) {
    return (
      <main className="dp">
        <DpTop onLogout={onLogout} />
        <section className="dp-card">
          <h2>No pudimos cargar tus datos</h2>
          <p>Revisa tu conexión a internet e inténtalo otra vez.</p>
          <button className="dp-btn" onClick={load}>Intentar de nuevo</button>
        </section>
      </main>
    );
  }

  const eligibility = computeEligibility({ gender: donor.gender, active: donor.status === 'ACTIVE', donationDates: donations.map((d) => d.donation_date), params });
  const released = results.filter((r) => RELEASED.includes(r.status));
  const authorized = donor.consent_email && !donor.opted_out;
  const campaignList = campaigns.filter((c) => c.kind === 'CAMPAIGN');
  const infoList = campaigns.filter((c) => c.kind === 'INFO');

  const hero = {
    APTO: { tone: 'ok', title: donations.length ? 'Ya puedes volver a donar' : 'Puedes donar sangre', text: 'Acércate al Banco de Sangre. El personal de salud te atenderá y te evaluará ese día.' },
    ESPERA: { tone: 'wait', title: `Podrás donar desde el ${eligibility.eligibleFrom ? longDate(eligibility.eligibleFrom) : ''}`, text: 'Todavía no pasó el tiempo mínimo desde tu última donación. Gracias por esperar.' },
    MAXIMO: { tone: 'wait', title: 'Ya donaste todas las veces permitidas este año', text: `Podrás donar de nuevo desde el ${eligibility.eligibleFrom ? longDate(eligibility.eligibleFrom) : ''}.` },
    INACTIVO: { tone: 'wait', title: 'Tu registro está inactivo', text: 'Habla con el Banco de Sangre si quieres volver a donar.' },
  }[eligibility.state];

  return (
    <main className="dp">
      <DpTop onLogout={onLogout} />

      <section className={`dp-hero ${hero.tone}`}>
        <div className="dp-hero-text">
          <p className="dp-hello">Hola, {donor.first_name}</p>
          <h1>{hero.title}</h1>
          <p>{hero.text}</p>
        </div>
        <div className="dp-blood"><span>Tu grupo de sangre</span><b>{donor.blood_type ? `${donor.blood_type}${donor.rh_factor}` : 'Aún no registrado'}</b></div>
      </section>

      {message && <p className="dp-message" role="status">{message}</p>}

      <div className="dp-grid">
      <div className="dp-col">
      <section className="dp-card">
        <h2>Tu resultado</h2>
        {released.length === 0 ? (
          <p>Todavía no tienes un resultado nuevo. Cuando el médico lo revise, aparecerá aquí.</p>
        ) : (
          <>
            {released.slice(0, 3).map((r) => (
              <div className="dp-result" key={r.id}>
                <b>✓ Tu resultado está listo</b>
                {r.donations && <span>Donación del {longDate(r.donations.donation_date)}</span>}
                <p>{r.donor_message || 'Consulta con el Banco de Sangre si tienes dudas.'}</p>
              </div>
            ))}
            {params.recommendations && <div className="dp-reco"><b>Qué hacer ahora</b><p>{params.recommendations}</p></div>}
          </>
        )}
      </section>

      {(campaignList.length > 0 || infoList.length > 0) && (
        <section className="dp-card">
          <h2>{campaignList.length > 0 ? 'El Banco de Sangre te invita' : 'Información útil'}</h2>
          {[...campaignList, ...infoList].map((c) => (
            <div className="dp-item" key={c.id}><b>{c.name}</b><p>{c.message_template.replaceAll('{{nombre}}', donor.first_name)}</p></div>
          ))}
        </section>
      )}

      <section className="dp-card">
        <h2>Tus donaciones</h2>
        <p>{donations.length === 0 ? 'Todavía no tienes donaciones registradas.' : <>Has donado <b>{donations.length} {donations.length === 1 ? 'vez' : 'veces'}</b>. La última fue el <b>{longDate(donations[0].donation_date)}</b>.</>}</p>
        <p className="dp-small">Este año llevas {eligibility.thisYear} de {eligibility.limit} donaciones permitidas.</p>
        {donations.length > 1 && (
          <details className="dp-more"><summary>Ver todas mis donaciones</summary>
            <ul>{donations.map((d) => <li key={d.id}>{longDate(d.donation_date)}</li>)}</ul>
          </details>
        )}
      </section>

      </div>
      <div className="dp-col">
      {params.contactInfo && (
        <section className="dp-card">
          <h2>¿Dónde donar?</h2>
          <p className="dp-pre">{params.contactInfo}</p>
        </section>
      )}

      <section className="dp-card">
        <h2>Avisos por correo</h2>
        {!donor.email ? (
          <p>Para recibir avisos necesitamos tu correo electrónico. Pídele al personal del Banco de Sangre que lo anote.</p>
        ) : authorized ? (
          <>
            <p>✓ <b>Estás recibiendo avisos</b> en {donor.email}: recordatorios, resultados y campañas.</p>
            <button className="dp-btn light" onClick={() => setConsent(false)}>Dejar de recibir avisos</button>
          </>
        ) : (
          <>
            <p>Ahora <b>no estás recibiendo avisos</b>. Si quieres, te avisaremos cuando puedas volver a donar y cuando tu resultado esté listo.</p>
            <button className="dp-btn" onClick={() => setAskConsent(true)}>Quiero recibir avisos</button>
          </>
        )}
      </section>

      <details className="dp-card dp-options">
        <summary>Más opciones</summary>
        <PasswordForm onDone={setMessage} />
        <div className="dp-opt">
          <h3>Mis datos personales</h3>
          <p>Tienes derecho a conocer, corregir y pedir que se eliminen tus datos. Para corregirlos o eliminarlos, pídelo en el Banco de Sangre.</p>
          <button className="dp-btn light" onClick={downloadMyData}>Descargar una copia de mis datos</button>
        </div>
      </details>
      </div>
      </div>

      <p className="dp-footer">HEMOCAX · Banco de Sangre HRDC<br />Tus datos son confidenciales (Ley N.° 29733). DNI {profile.dni}</p>

      {askConsent && (
        <Modal title="Avisos por correo" onClose={() => { setAskConsent(false); setAccepted(false); }}>
          <div className="consent-text"><p>{consentText?.body ?? 'Cargando…'}</p></div>
          <label className="check"><input type="checkbox" checked={accepted} onChange={(e) => setAccepted(e.target.checked)} /><span>He leído y acepto recibir correos del Banco de Sangre del HRDC</span></label>
          <div className="modal-actions">
            <button className="secondary" onClick={() => { setAskConsent(false); setAccepted(false); }}>Cancelar</button>
            <button className="primary" disabled={!accepted || !consentText} onClick={() => setConsent(true)}>Aceptar</button>
          </div>
        </Modal>
      )}
    </main>
  );
}

function DpTop({ onLogout }: { onLogout: () => void }) {
  return (
    <header className="dp-top">
      <div className="brand"><span className="brand-icon">H</span><span>HEMO<span className="accent">CAX</span></span></div>
      <button className="dp-exit" onClick={onLogout}>Salir</button>
    </header>
  );
}

function PasswordForm({ onDone }: { onDone: (m: string) => void }) {
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (password.length < 8) { setError('Escribe al menos 8 letras o números.'); return; }
    setBusy(true);
    const { error: err } = await getBrowserSupabaseClient().auth.updateUser({ password });
    setBusy(false);
    if (err) { setError('No se pudo cambiar. Prueba con otra contraseña.'); return; }
    setPassword('');
    onDone('Listo. Tu contraseña nueva ya está guardada. Anótala en un lugar seguro.');
  }

  return (
    <form className="dp-opt" onSubmit={submit}>
      <h3>Cambiar mi contraseña</h3>
      <p>Si te dieron una contraseña temporal, cámbiala por una que recuerdes. Mínimo 8 letras o números.</p>
      <input className="dp-input" type={show ? 'text' : 'password'} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Contraseña nueva" aria-label="Contraseña nueva" />
      <label className="dp-check"><input type="checkbox" checked={show} onChange={(e) => setShow(e.target.checked)} /> Mostrar lo que escribo</label>
      {error && <p className="dp-error" role="alert">{error}</p>}
      <button className="dp-btn" disabled={busy}>{busy ? 'Guardando…' : 'Guardar contraseña nueva'}</button>
    </form>
  );
}
