'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { callApi } from './api';
import { Badge, Donor, Empty, Field, Modal, Notify, PageHeader, ROLE_LABEL, Role, fullName, friendlyError } from './ui';

type Account = { user_id: string; dni: string; full_name: string; role: Role; can_release_results: boolean; active: boolean };
type Created = { dni: string; password: string; name: string; reset?: boolean };

const KINDS: { role: Role; title: string; text: string }[] = [
  { role: 'STAFF', title: 'Personal del Banco de Sangre', text: 'Registra donantes y donaciones, revisa resultados y envía correos.' },
  { role: 'ADMIN', title: 'Administrador', text: 'Lo mismo que el personal, y además crea cuentas y ve la actividad.' },
  { role: 'DONOR', title: 'Donante', text: 'Entra a su portal para ver sus donaciones y resultados.' },
];

function generatePassword(): string {
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789';
  const bytes = crypto.getRandomValues(new Uint32Array(14));
  return Array.from(bytes, (b) => chars[b % chars.length]).join('');
}

export default function AccountsTab({ notify, intent }: { notify: Notify; intent?: string }) {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [free, setFree] = useState<Donor[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(intent === 'new');
  const [created, setCreated] = useState<Created | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const supabase = getBrowserSupabaseClient();
    const [a, d] = await Promise.all([
      supabase.from('profiles').select('user_id,dni,full_name,role,can_release_results,active').order('full_name'),
      supabase.from('donors').select('id,dni,first_name,last_name,gender,birth_date,phone,email,blood_type,rh_factor,status,consent_email,opted_out,auth_user_id').is('auth_user_id', null).order('last_name'),
    ]);
    if (a.error) notify(friendlyError(a.error.message), 'error');
    else setAccounts((a.data || []) as Account[]);
    setFree((d.data || []) as Donor[]);
    setLoading(false);
  }, [notify]);

  useEffect(() => { load(); }, [load]);

  async function manage(a: Account, action: string, extra: object = {}) {
    setBusyId(a.user_id);
    try {
      const res = await callApi('/api/admin/users/manage', { user_id: a.user_id, action, ...extra });
      if (action === 'reset_password') setCreated({ dni: a.dni, password: res.password, name: a.full_name, reset: true });
      else notify('Cambio guardado.');
      load();
    } catch (e) {
      notify(friendlyError(e instanceof Error ? e.message : 'No se pudo completar la acción.'), 'error');
    }
    setBusyId(null);
  }

  return (
    <>
      <PageHeader
        title="Cuentas de acceso"
        help="Cada persona que entre al portal necesita una cuenta. Entra con su DNI y una contraseña que tú le entregas la primera vez; luego puede cambiarla."
        action={<button className="primary" onClick={() => setCreating(true)}>+ Crear cuenta</button>}
      />
      {loading ? <p className="muted">Cargando cuentas…</p> : accounts.length === 0 ? (
        <div className="card"><Empty title="Todavía no hay cuentas" /></div>
      ) : (
        <div className="card table-card">
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Nombre</th><th>DNI</th><th>Tipo de cuenta</th><th>Puede liberar resultados</th><th>Estado</th><th>Acciones</th></tr></thead>
              <tbody>
                {accounts.map((a) => (
                  <tr key={a.user_id}>
                    <td><b>{a.full_name}</b></td>
                    <td>{a.dni}</td>
                    <td>{ROLE_LABEL[a.role]}</td>
                    <td>{a.role === 'DONOR' ? <span className="muted">—</span> : a.can_release_results ? <Badge tone="ok">Sí</Badge> : <Badge>No</Badge>}</td>
                    <td>{a.active ? <Badge tone="ok">Activa</Badge> : <Badge tone="warn">Inactiva</Badge>}</td>
                    <td className="actions">
                      <button className="secondary small" disabled={busyId === a.user_id} onClick={() => manage(a, 'reset_password')}>Nueva contraseña</button>
                      {a.role !== 'DONOR' && <button className="secondary small" disabled={busyId === a.user_id} onClick={() => manage(a, 'set_release', { value: !a.can_release_results })}>{a.can_release_results ? 'Quitar permiso de liberar' : 'Dar permiso de liberar'}</button>}
                      <button className={a.active ? 'danger small' : 'secondary small'} disabled={busyId === a.user_id} onClick={() => manage(a, 'set_active', { active: !a.active })}>{a.active ? 'Desactivar' : 'Activar'}</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {creating && <CreateModal free={free} notify={notify} onClose={() => setCreating(false)} onCreated={(c) => { setCreating(false); setCreated(c); load(); }} />}
      {created && <CreatedModal created={created} onClose={() => setCreated(null)} />}
    </>
  );
}

function CreateModal({ free, notify, onClose, onCreated }: { free: Donor[]; notify: Notify; onClose: () => void; onCreated: (c: Created) => void }) {
  const [role, setRole] = useState<Role>('STAFF');
  const [dni, setDni] = useState('');
  const [name, setName] = useState('');
  const [donorId, setDonorId] = useState('');
  const [canRelease, setCanRelease] = useState(false);
  const [password, setPassword] = useState(generatePassword());
  const [show, setShow] = useState(true);
  const [busy, setBusy] = useState(false);

  const donor = free.find((d) => String(d.id) === donorId);
  const finalDni = role === 'DONOR' ? donor?.dni ?? '' : dni;
  const finalName = role === 'DONOR' ? (donor ? fullName(donor) : '') : name.trim();

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await callApi('/api/admin/users', {
        dni: finalDni, full_name: finalName, role, password,
        can_release_results: role !== 'DONOR' && canRelease,
        donor_id: role === 'DONOR' ? Number(donorId) : undefined,
      });
      onCreated({ dni: finalDni, password, name: finalName });
    } catch (err) {
      notify(friendlyError(err instanceof Error ? err.message : 'No se pudo crear la cuenta.'), 'error');
    }
    setBusy(false);
  }

  return (
    <Modal title="Crear cuenta de acceso" onClose={onClose}>
      <form onSubmit={submit}>
        <p className="form-section">1. ¿Para quién es la cuenta?</p>
        <div className="kinds">
          {KINDS.map((k) => (
            <label key={k.role} className={role === k.role ? 'kind active' : 'kind'}>
              <input type="radio" name="kind" checked={role === k.role} onChange={() => setRole(k.role)} />
              <b>{k.title}</b>
              <span>{k.text}</span>
            </label>
          ))}
        </div>

        <p className="form-section">2. Sus datos</p>
        {role === 'DONOR' ? (
          <Field label="Elige al donante" hint={free.length === 0 ? 'No hay donantes sin cuenta. Primero regístralo en la pestaña Donantes.' : 'Solo aparecen donantes que aún no tienen cuenta.'}>
            <select required value={donorId} onChange={(e) => setDonorId(e.target.value)}>
              <option value="">Elige un donante…</option>
              {free.map((d) => <option key={d.id} value={d.id}>{fullName(d)} — DNI {d.dni}</option>)}
            </select>
          </Field>
        ) : (
          <div className="form-grid">
            <Field label="DNI" hint="Con este número entrará al portal."><input required maxLength={8} inputMode="numeric" value={dni} onChange={(e) => setDni(e.target.value.replace(/\D/g, ''))} /></Field>
            <Field label="Nombre completo"><input required value={name} onChange={(e) => setName(e.target.value)} /></Field>
          </div>
        )}
        {role !== 'DONOR' && (
          <label className="check">
            <input type="checkbox" checked={canRelease} onChange={(e) => setCanRelease(e.target.checked)} />
            <span>Puede liberar resultados no críticos (solo para médicos o responsables)</span>
          </label>
        )}

        <p className="form-section">3. Contraseña inicial</p>
        <Field label="Contraseña" hint="Ya generamos una segura. Anótala o cópiala: luego ya no se vuelve a mostrar.">
          <div className="password-row">
            <input required minLength={12} type={show ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} />
            <button type="button" className="secondary small" onClick={() => setShow((s) => !s)}>{show ? 'Ocultar' : 'Mostrar'}</button>
            <button type="button" className="secondary small" onClick={() => setPassword(generatePassword())}>Generar otra</button>
          </div>
        </Field>

        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose}>Cancelar</button>
          <button className="primary" disabled={busy || !finalDni || !finalName}>{busy ? 'Creando…' : 'Crear cuenta'}</button>
        </div>
      </form>
    </Modal>
  );
}

function CreatedModal({ created, onClose }: { created: Created; onClose: () => void }) {
  const [copied, setCopied] = useState(false);
  const text = `Portal HEMOCAX: ${window.location.origin}\nDNI: ${created.dni}\nContraseña temporal: ${created.password}`;

  return (
    <Modal title={created.reset ? 'Contraseña nueva' : 'Cuenta creada'} onClose={onClose}>
      <p className="notice-box ok">{created.reset ? <>Se cambió la contraseña de <b>{created.name}</b>. La anterior ya no sirve.</> : <>La cuenta de <b>{created.name}</b> ya está lista.</>} Entrégale estos datos; esta es la única vez que se muestra la contraseña.</p>
      <pre className="credentials">{text}</pre>
      <p className="muted">Pídele que entre y cambie su contraseña en <b>Mi cuenta</b>.</p>
      <div className="modal-actions">
        <button className="secondary" onClick={async () => { await navigator.clipboard.writeText(text); setCopied(true); }}>{copied ? 'Copiado' : 'Copiar datos'}</button>
        <button className="primary" onClick={onClose}>Listo</button>
      </div>
    </Modal>
  );
}
