'use client';

import { FormEvent, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Field, Notify, PageHeader, Profile, ROLE_LABEL, friendlyError } from './ui';

export default function MyAccountTab({ profile, notify }: { profile: Profile; notify: Notify }) {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [busy, setBusy] = useState(false);

  async function change(e: FormEvent) {
    e.preventDefault();
    if (password !== confirm) { notify('Las dos contraseñas no coinciden.', 'error'); return; }
    setBusy(true);
    const { error } = await getBrowserSupabaseClient().auth.updateUser({ password });
    setBusy(false);
    if (error) { notify(friendlyError(error.message), 'error'); return; }
    notify('Contraseña actualizada. Úsala la próxima vez que entres.');
    setPassword('');
    setConfirm('');
  }

  return (
    <>
      <PageHeader title="Mi cuenta" help="Tus datos de acceso y el cambio de contraseña." />
      <div className="card">
        <h3>{profile.full_name}</h3>
        <p className="muted">DNI {profile.dni} · {ROLE_LABEL[profile.role]}{profile.can_release_results ? ' · puede liberar resultados' : ''}</p>
      </div>
      <form className="card" onSubmit={change}>
        <h3>Cambiar mi contraseña</h3>
        <p className="muted">Usa al menos 12 caracteres. Si tu contraseña fue temporal, cámbiala ahora.</p>
        <div className="form-grid">
          <Field label="Contraseña nueva"><input required type="password" minLength={12} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} /></Field>
          <Field label="Repite la contraseña nueva"><input required type="password" minLength={12} autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} /></Field>
        </div>
        <button className="primary" disabled={busy}>{busy ? 'Guardando…' : 'Cambiar contraseña'}</button>
      </form>
    </>
  );
}
