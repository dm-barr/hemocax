'use client';

import { FormEvent, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import StaffPanel from './staff/StaffPanel';

type UserProfile = { dni: string; full_name: string; role: 'ADMIN' | 'STAFF' | 'DONOR'; can_release_results: boolean };
type Donor = { id: number; first_name: string; last_name: string; gender: 'M' | 'F'; blood_type: string; rh_factor: string; consent_email: boolean; opted_out: boolean };
type Donation = { id: number; donation_date: string; donation_type: string };
type Result = { id: number; status: string; available_at: string | null; donor_message: string | null; donations: { donation_date: string } | null };

const db = getBrowserSupabaseClient;

export default function Home() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [donor, setDonor] = useState<Donor | null>(null);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [results, setResults] = useState<Result[]>([]);
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
      const { data: d, error: donorError } = await supabase.from('donors').select('id,first_name,last_name,gender,blood_type,rh_factor,consent_email,opted_out').eq('auth_user_id', auth.user.id).single();
      if (donorError) throw donorError;
      setDonor(d as Donor);
      const [{ data: ds, error: donationError }, { data: rs, error: resultError }] = await Promise.all([
        supabase.from('donations').select('id,donation_date,donation_type').eq('donor_id', d.id).order('donation_date', { ascending: false }),
        supabase.from('donation_results').select('id,status,available_at,donor_message,donations(donation_date)').order('created_at', { ascending: false }),
      ]);
      if (donationError) throw donationError;
      if (resultError) throw resultError;
      setDonations((ds ?? []) as Donation[]); setResults((rs ?? []) as unknown as Result[]);
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
    const now = enabled ? new Date().toISOString() : null;
    const { error: updateError } = await db().from('donors').update({ consent_email: enabled, consent_at: now, consent_version: enabled ? 'piloto-v1' : null, opted_out: !enabled }).eq('id', donor.id);
    if (updateError) { setError('No se pudo actualizar tu consentimiento.'); return; }
    setDonor({ ...donor, consent_email: enabled, opted_out: !enabled });
  }

  async function logout() { await db().auth.signOut(); setProfile(null); setDonor(null); }

  if (!profile) return <main className="login-wrap"><form className="login" onSubmit={login}>
    <div className="brand"><span className="brand-icon">H</span><span>HEMO<span className="accent">CAX</span></span></div>
    <p className="eyebrow">BANCO DE SANGRE · HRDC</p><h1>Bienvenido</h1><p className="muted">Entra con tu DNI y tu contraseña. Sirve tanto para donantes como para el personal del Banco de Sangre.</p>
    <label>DNI<input inputMode="numeric" autoComplete="username" maxLength={8} value={dni} onChange={e => setDni(e.target.value.replace(/\D/g, ''))} placeholder="8 dígitos" required /></label>
    <label>Contraseña<input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
    {error && <p className="error" role="alert">{error}</p>}<button className="primary" disabled={busy}>{busy ? 'Ingresando…' : 'Ingresar'}</button>
    <p className="privacy">¿No tienes cuenta o olvidaste tu contraseña? Pídela al personal del Banco de Sangre.</p>
  </form></main>;

  const year = new Date().getFullYear();
  const currentYearDonations = donations.filter(d => new Date(`${d.donation_date}T00:00:00`).getFullYear() === year).length;
  const annualLimit = donor?.gender === 'M' ? 4 : 3;
  if (profile.role !== 'DONOR') return <StaffPanel profile={profile} onLogout={logout} />;

  return <main className="portal"><aside className="sidebar"><Brand /><div className="nav-active">◉　 Mi portal</div><div className="side-note">HRDC · Banco de Sangre</div></aside><section className="content"><header className="topbar"><div><span className="eyebrow">PORTAL DEL DONANTE</span><div className="greeting">Hola, {donor?.first_name ?? profile.full_name}</div></div><button onClick={logout}>Cerrar sesión</button></header>
    <div className="intro"><div><h1>Tu donación, en un solo lugar</h1><p className="muted">Consulta tu historial y mantén tus datos al día.</p></div><div className="blood">{donor?.blood_type}{donor?.rh_factor}<small>GRUPO SANGUÍNEO</small></div></div>
    {error && <p className="error" role="alert">{error}</p>}
    <div className="metrics"><article><span className="eyebrow">DONACIONES ESTE AÑO</span><strong>{currentYearDonations}<span className="metric-total"> / {annualLimit}</span></strong><small>máximo anual de sangre total</small></article><article><span className="eyebrow">HISTORIAL TOTAL</span><strong>{donations.length}</strong><small>donaciones registradas</small></article><article><span className="eyebrow">RESULTADOS</span><strong>{results.filter(r => ['AVAILABLE','NOTIFIED','CONSULTED'].includes(r.status)).length}</strong><small>disponibles en el portal</small></article></div>
    <div className="columns"><section className="panel"><div className="panel-head"><div><h2>Mis donaciones</h2><p>Tu historial reciente</p></div></div>{donations.length ? <div className="rows">{donations.map(d => <div className="row" key={d.id}><span className="row-icon">＋</span><span><b>Donación de sangre</b><small>{new Date(`${d.donation_date}T00:00:00`).toLocaleDateString('es-PE',{day:'numeric',month:'long',year:'numeric'})}</small></span><span className="tag">Registrada</span></div>)}</div> : <p className="empty">Aún no hay donaciones en tu historial.</p>}</section>
      <section className="panel"><div className="panel-head"><div><h2>Mis resultados</h2><p>Solo se muestran cuando el equipo autorizado los libera.</p></div></div>{results.filter(r => ['AVAILABLE','NOTIFIED','CONSULTED'].includes(r.status)).length ? <div className="rows">{results.filter(r => ['AVAILABLE','NOTIFIED','CONSULTED'].includes(r.status)).map(r => <div className="row" key={r.id}><span className="row-icon result-icon">✓</span><span><b>Resultado disponible</b><small>{r.donor_message || 'Consulta con el Banco de Sangre para orientación.'}</small></span><span className="tag">Disponible</span></div>)}</div> : <p className="empty">No tienes resultados liberados por el momento.</p>}</section></div>
    <section className="panel consent"><div><h2>Mensajes por correo</h2><p>Recibe recordatorios y avisos del Banco de Sangre. Puedes cambiar tu decisión cuando quieras.</p><small>Al activarlo, autorizas mensajes informativos del piloto de HEMOCAX por correo electrónico.</small></div><button className={donor?.consent_email && !donor.opted_out ? 'secondary' : 'primary'} onClick={() => consent(!(donor?.consent_email && !donor.opted_out))}>{donor?.consent_email && !donor.opted_out ? 'Dejar de recibir' : 'Dar consentimiento'}</button></section>
    <footer>HEMOCAX · HRDC <span>Tu información es confidencial.</span></footer></section></main>;
}

function Brand() { return <div className="brand"><span className="brand-icon">H</span><span>HEMO<span className="accent">CAX</span></span></div>; }
