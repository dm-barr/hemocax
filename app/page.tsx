'use client';

import { FormEvent, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Params, loadParams } from '@/lib/params';
import { computeEligibility, formatDate } from '@/lib/eligibility';
import StaffPanel from './staff/StaffPanel';
import { Modal, downloadFile } from './staff/ui';

type UserProfile = { dni: string; full_name: string; role: 'ADMIN' | 'STAFF' | 'DONOR'; can_release_results: boolean };
type Donor = { id: number; first_name: string; last_name: string; gender: 'M' | 'F'; blood_type: string | null; rh_factor: string | null; consent_email: boolean; opted_out: boolean; status: string };
type Donation = { id: number; donation_date: string; donation_type: string };
type Result = { id: number; status: string; available_at: string | null; donor_message: string | null; donations: { donation_date: string } | null };
type Campaign = { id: number; name: string; description: string | null; message_template: string; kind: 'CAMPAIGN' | 'INFO' };

const db = getBrowserSupabaseClient;
const RELEASED = ['AVAILABLE', 'NOTIFIED', 'CONSULTED'];

export default function Home() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [donor, setDonor] = useState<Donor | null>(null);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [results, setResults] = useState<Result[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [params, setParams] = useState<Params | null>(null);
  const [consentText, setConsentText] = useState<{ version: string; body: string } | null>(null);
  const [askConsent, setAskConsent] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [dni, setDni] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function loadPortal() {
    const supabase = db();
    const { data: auth } = await supabase.auth.getUser();
    if (!auth.user) { setProfile(null); return; }
    const { data: p, error: profileError } = await supabase.from('profiles').select('dni,full_name,role,can_release_results').eq('user_id', auth.user.id).single();
    if (profileError) throw profileError;
    setProfile(p as UserProfile);
    if (p.role === 'DONOR') {
      const { data: d, error: donorError } = await supabase.from('donors').select('id,first_name,last_name,gender,blood_type,rh_factor,consent_email,opted_out,status').eq('auth_user_id', auth.user.id).single();
      if (donorError) throw donorError;
      setDonor(d as Donor);
      const [{ data: ds, error: donationError }, { data: rs, error: resultError }, cs, cv, prm] = await Promise.all([
        supabase.from('donations').select('id,donation_date,donation_type').eq('donor_id', d.id).order('donation_date', { ascending: false }),
        supabase.from('donation_results').select('id,status,available_at,donor_message,donations(donation_date)').order('created_at', { ascending: false }),
        supabase.from('campaigns').select('id,name,description,message_template,kind').eq('status', 'ACTIVE').order('created_at', { ascending: false }),
        supabase.from('consent_versions').select('version,body').eq('active', true).maybeSingle(),
        loadParams(supabase),
      ]);
      if (donationError) throw donationError;
      if (resultError) throw resultError;
      setDonations((ds ?? []) as Donation[]); setResults((rs ?? []) as unknown as Result[]);
      setCampaigns((cs.data ?? []) as Campaign[]);
      if (cv.data) setConsentText(cv.data);
      setParams(prm);
    }
  }

  useEffect(() => { loadPortal().catch(e => setError(e.message)); }, []);

  async function login(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      if (!/^\d{8}$/.test(dni)) throw new Error('Ingresa un DNI válido de 8 dígitos.');
      const { error: authError } = await db().auth.signInWithPassword({ email: `dni-${dni}@login.hemocax.org`, password });
      if (authError) throw new Error('DNI o contraseña incorrectos.');
      await loadPortal();
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo iniciar sesión.'); }
    finally { setBusy(false); }
  }

  async function consent(enabled: boolean) {
    if (!donor) return;
    setError('');
    const patch = enabled
      ? { consent_email: true, consent_at: new Date().toISOString(), consent_version: consentText?.version ?? 'piloto-v1', opted_out: false }
      : { consent_email: false, opted_out: true };
    const { error: updateError } = await db().from('donors').update(patch).eq('id', donor.id);
    if (updateError) { setError('No se pudo actualizar tu consentimiento.'); return; }
    setDonor({ ...donor, consent_email: enabled, opted_out: !enabled });
    setAskConsent(false); setAccepted(false);
  }

  async function downloadMyData() {
    if (!donor) return;
    const supabase = db();
    const [me, ev] = await Promise.all([
      supabase.from('donors').select('*').eq('id', donor.id).single(),
      supabase.from('consent_events').select('action,version,recorded_via,created_at').eq('donor_id', donor.id),
    ]);
    const { auth_user_id: _omit, ...personal } = (me.data ?? {}) as Record<string, unknown>;
    void _omit;
    downloadFile('mis-datos-hemocax.json', JSON.stringify({ datos_personales: personal, donaciones: donations, resultados: results, consentimiento: ev.data }, null, 2), 'application/json');
  }

  async function logout() { await db().auth.signOut(); setProfile(null); setDonor(null); }

  if (!profile) return <main className="login-wrap"><form className="login" onSubmit={login}>
    <div className="brand"><span className="brand-icon">H</span><span>HEMO<span className="accent">CAX</span></span></div>
    <p className="eyebrow">BANCO DE SANGRE · HRDC</p><h1>Bienvenido</h1><p className="muted">Entra con tu DNI y tu contraseña. Sirve tanto para donantes como para el personal del Banco de Sangre.</p>
    <label>DNI<input inputMode="numeric" autoComplete="username" maxLength={8} value={dni} onChange={e => setDni(e.target.value.replace(/\D/g, ''))} placeholder="8 dígitos" required /></label>
    <label>Contraseña<input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
    {error && <p className="error" role="alert">{error}</p>}<button className="primary" disabled={busy}>{busy ? 'Ingresando…' : 'Ingresar'}</button>
    <p className="privacy">¿No tienes cuenta o olvidaste tu contraseña? Pídela al personal del Banco de Sangre.<br />Tus datos se tratan conforme a la Ley N.° 29733 de Protección de Datos Personales.</p>
  </form></main>;

  if (profile.role !== 'DONOR') return <StaffPanel profile={profile} onLogout={logout} />;

  const year = new Date().getFullYear();
  const currentYearDonations = donations.filter(d => new Date(`${d.donation_date}T00:00:00`).getFullYear() === year).length;
  const annualLimit = donor ? (params?.limits[donor.gender] ?? (donor.gender === 'M' ? 4 : 3)) : 3;
  const released = results.filter(r => RELEASED.includes(r.status));
  const eligibility = donor && params ? computeEligibility({ gender: donor.gender, active: donor.status === 'ACTIVE', donationDates: donations.map(d => d.donation_date), params }) : null;
  const authorized = !!donor?.consent_email && !donor.opted_out;
  const campaignList = campaigns.filter(c => c.kind === 'CAMPAIGN');
  const infoList = campaigns.filter(c => c.kind === 'INFO');

  return <main className="portal"><aside className="sidebar"><Brand /><div className="nav-active">◉　 Mi portal</div><div className="side-note">HRDC · Banco de Sangre</div></aside><section className="content"><header className="topbar"><div><span className="eyebrow">PORTAL DEL DONANTE</span><div className="greeting">Hola, {donor?.first_name ?? profile.full_name}</div></div><button onClick={logout}>Cerrar sesión</button></header>
    <div className="intro"><div><h1>Tu donación, en un solo lugar</h1><p className="muted">Consulta tu historial y mantén tus datos al día.</p></div><div className="blood">{donor?.blood_type ? `${donor.blood_type}${donor.rh_factor}` : '—'}<small>GRUPO SANGUÍNEO</small></div></div>
    {error && <p className="error" role="alert">{error}</p>}
    <div className="metrics"><article><span className="eyebrow">DONACIONES ESTE AÑO</span><strong>{currentYearDonations}<span className="metric-total"> / {annualLimit}</span></strong><small>máximo anual de sangre total</small></article><article><span className="eyebrow">HISTORIAL TOTAL</span><strong>{donations.length}</strong><small>donaciones registradas</small></article><article><span className="eyebrow">RESULTADOS</span><strong>{released.length}</strong><small>disponibles en el portal</small></article></div>

    {eligibility && <section className="panel next-donation"><div className="panel-head"><div><h2>Tu próxima donación</h2>
      <p>{eligibility.state === 'APTO' ? (donations.length ? 'Ya cumpliste el intervalo desde tu última donación: puedes volver a donar. La evaluación final la hace el personal de salud.' : 'Cuando quieras, acércate al Banco de Sangre. La evaluación final la hace el personal de salud.')
        : eligibility.state === 'INACTIVO' ? 'Tu registro está inactivo. Comunícate con el Banco de Sangre si quieres volver a donar.'
        : eligibility.state === 'MAXIMO' ? `Llegaste al máximo de ${eligibility.limit} donaciones este año. Podrás volver a donar desde el ${formatDate(eligibility.eligibleFrom!)}.`
        : `Podrás volver a donar desde el ${formatDate(eligibility.eligibleFrom!)}.`}</p></div></div></section>}

    <div className="columns"><section className="panel"><div className="panel-head"><div><h2>Mis donaciones</h2><p>Tu historial reciente</p></div></div>{donations.length ? <div className="rows">{donations.map(d => <div className="row" key={d.id}><span className="row-icon">＋</span><span><b>Donación de sangre</b><small>{new Date(`${d.donation_date}T00:00:00`).toLocaleDateString('es-PE',{day:'numeric',month:'long',year:'numeric'})}</small></span><span className="tag">Registrada</span></div>)}</div> : <p className="empty">Aún no hay donaciones en tu historial.</p>}</section>
      <section className="panel"><div className="panel-head"><div><h2>Mis resultados</h2><p>Solo se muestran cuando el equipo autorizado los libera. Si necesitas orientación, consulta con el Banco de Sangre.</p></div></div>{released.length ? <><div className="rows">{released.map(r => <div className="row" key={r.id}><span className="row-icon result-icon">✓</span><span><b>Resultado disponible</b><small>{r.donor_message || 'Consulta con el Banco de Sangre para orientación.'}</small></span><span className="tag">Disponible</span></div>)}</div>{params?.recommendations && <div className="recommendations"><b>Recomendaciones</b><p>{params.recommendations}</p></div>}</> : <p className="empty">No tienes resultados liberados por el momento.</p>}</section></div>

    {(campaignList.length > 0 || infoList.length > 0) && <div className="columns">
      {campaignList.length > 0 && <section className="panel"><div className="panel-head"><div><h2>Campañas activas</h2><p>Convocatorias del Banco de Sangre</p></div></div><div className="rows">{campaignList.map(c => <div className="row" key={c.id}><span><b>{c.name}</b><small>{c.message_template.replaceAll('{{nombre}}', donor?.first_name ?? '')}</small></span></div>)}</div></section>}
      {infoList.length > 0 && <section className="panel"><div className="panel-head"><div><h2>Información útil</h2><p>Consejos del Banco de Sangre</p></div></div><div className="rows">{infoList.map(c => <div className="row" key={c.id}><span><b>{c.name}</b><small>{c.message_template.replaceAll('{{nombre}}', donor?.first_name ?? '')}</small></span></div>)}</div></section>}
    </div>}

    <section className="panel consent"><div><h2>Mensajes por correo</h2><p>Recibe recordatorios y avisos del Banco de Sangre. Puedes cambiar tu decisión cuando quieras.</p><small>{authorized ? 'Tienes activados los mensajes por correo electrónico.' : 'Antes de activarlos te mostraremos el texto completo del consentimiento.'}</small></div><button className={authorized ? 'secondary' : 'primary'} onClick={() => authorized ? consent(false) : setAskConsent(true)}>{authorized ? 'Dejar de recibir' : 'Dar consentimiento'}</button></section>

    <section className="panel consent"><div><h2>Tus datos</h2><p>Tienes derecho a conocer, corregir y pedir la eliminación de tus datos personales. Puedes descargar una copia aquí; para corregirlos o eliminarlos, solicítalo al personal del Banco de Sangre.</p></div><button className="secondary" onClick={downloadMyData}>Descargar mis datos</button></section>

    <footer>HEMOCAX · HRDC <span>Tu información es confidencial (Ley N.° 29733).</span></footer>

    {askConsent && <Modal title="Consentimiento para recibir correos" onClose={() => { setAskConsent(false); setAccepted(false); }}>
      <div className="consent-text"><small>Texto {consentText?.version ?? ''}</small><p>{consentText?.body ?? 'Cargando…'}</p></div>
      <label className="check"><input type="checkbox" checked={accepted} onChange={e => setAccepted(e.target.checked)} /><span>He leído y acepto recibir correos del Banco de Sangre del HRDC</span></label>
      <div className="modal-actions"><button className="secondary" onClick={() => { setAskConsent(false); setAccepted(false); }}>Cancelar</button><button className="primary" disabled={!accepted || !consentText} onClick={() => consent(true)}>Aceptar</button></div>
    </Modal>}
  </section></main>;
}

function Brand() { return <div className="brand"><span className="brand-icon">H</span><span>HEMO<span className="accent">CAX</span></span></div>; }
