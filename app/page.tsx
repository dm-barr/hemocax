'use client';

import dynamic from 'next/dynamic';
import { FormEvent, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';

type UserProfile = { dni: string; full_name: string; role: 'ADMIN' | 'STAFF' | 'DONOR'; can_release_results: boolean };

// Cada tipo de usuario descarga solo su parte: así el portal del donante es liviano en celulares y conexiones lentas.
const StaffPanel = dynamic(() => import('./staff/StaffPanel'), { ssr: false, loading: () => <p className="dp-status">Cargando…</p> });
const DonorPortal = dynamic(() => import('./DonorPortal'), { ssr: false, loading: () => <p className="dp-status">Cargando…</p> });

const db = getBrowserSupabaseClient;

export default function Home() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [checking, setChecking] = useState(true);
  const [dni, setDni] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function loadProfile() {
    const supabase = db();
    const { data: auth } = await supabase.auth.getUser();
    if (!auth.user) { setProfile(null); return; }
    const { data: p, error: profileError } = await supabase.from('profiles').select('dni,full_name,role,can_release_results').eq('user_id', auth.user.id).single();
    if (profileError) throw profileError;
    setProfile(p as UserProfile);
  }

  useEffect(() => {
    loadProfile().catch(() => setError('No pudimos abrir tu cuenta. Revisa tu conexión e inténtalo otra vez.')).finally(() => setChecking(false));
  }, []);

  async function login(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      if (!/^\d{8}$/.test(dni)) throw new Error('Escribe tu DNI completo: son 8 números.');
      const { error: authError } = await db().auth.signInWithPassword({ email: `dni-${dni}@login.hemocax.org`, password });
      if (authError) throw new Error('El DNI o la contraseña no son correctos. Revisa y vuelve a escribir.');
      await loadProfile();
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo entrar. Inténtalo otra vez.'); }
    finally { setBusy(false); }
  }

  async function logout() { await db().auth.signOut(); setProfile(null); setPassword(''); }

  if (checking) return <main className="login-wrap"><p className="dp-status">Cargando…</p></main>;

  if (!profile) return <main className="login-wrap"><form className="login" onSubmit={login}>
    <div className="brand"><span className="brand-icon">H</span><span>HEMO<span className="accent">CAX</span></span></div>
    <p className="eyebrow">BANCO DE SANGRE · HRDC</p>
    <h1>Entrar</h1>
    <p className="muted">Escribe tu DNI y tu contraseña.</p>
    <label>Tu DNI (8 números)<input inputMode="numeric" autoComplete="username" maxLength={8} value={dni} onChange={e => setDni(e.target.value.replace(/\D/g, ''))} required /></label>
    <label>Tu contraseña<input type={showPassword ? 'text' : 'password'} autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
    <label className="login-show"><input type="checkbox" checked={showPassword} onChange={e => setShowPassword(e.target.checked)} /> Mostrar lo que escribo</label>
    {error && <p className="error" role="alert">{error}</p>}
    <button className="primary" disabled={busy}>{busy ? 'Entrando…' : 'Entrar'}</button>
    <p className="privacy">¿No tienes cuenta o olvidaste tu contraseña? Pídela en el Banco de Sangre del hospital.<br />Tus datos se tratan conforme a la Ley N.° 29733 de Protección de Datos Personales.</p>
  </form></main>;

  if (profile.role !== 'DONOR') return <StaffPanel profile={profile} onLogout={logout} />;
  return <DonorPortal profile={profile} onLogout={logout} />;
}
