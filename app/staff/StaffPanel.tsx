'use client';

import { useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';

type Profile = { dni: string; full_name: string; role: 'ADMIN' | 'STAFF' | 'DONOR'; can_release_results: boolean };
type Donor = {
  id: number; dni: string; first_name: string; last_name: string; gender: 'M' | 'F'; birth_date: string;
  phone: string; email: string | null; blood_type: string; rh_factor: string; status: string;
  consent_email: boolean; opted_out: boolean;
};
type ResultRow = {
  id: number; status: string; critical: boolean; donor_message: string | null; created_at: string;
  donations: { donation_date: string; donor_id: number; donors: { first_name: string; last_name: string } } | null;
};
type Campaign = { id: number; name: string; description: string | null; message_template: string; status: string; blood_groups: string[] };
type Communication = { id: number; type: string; channel: string; email: string | null; status: string; message: string; created_at: string; donors: { first_name: string; last_name: string } | null };
type AuditLog = { id: number; created_at: string; action: string; entity: string; entity_id: number | null; actor_dni: string | null; detail: Record<string, unknown> };
type AccountRow = { user_id: string; dni: string; full_name: string; role: string; can_release_results: boolean; active: boolean };

async function accessToken(): Promise<string> {
  const { data } = await getBrowserSupabaseClient().auth.getSession();
  const token = data.session?.access_token;
  if (!token) throw new Error('Tu sesión expiró. Vuelve a iniciar sesión.');
  return token;
}

async function callApi(path: string, body: object) {
  const token = await accessToken();
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  const json = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(json.error || `Error ${response.status}`);
  return json;
}

type TabKey = 'donors' | 'results' | 'campaigns' | 'communications' | 'accounts' | 'audit' | 'account';
const TABS: { key: TabKey; label: string; roles: Profile['role'][] }[] = [
  { key: 'donors', label: 'Donantes', roles: ['ADMIN', 'STAFF'] },
  { key: 'results', label: 'Resultados', roles: ['ADMIN', 'STAFF'] },
  { key: 'campaigns', label: 'Campañas', roles: ['ADMIN', 'STAFF'] },
  { key: 'communications', label: 'Comunicaciones', roles: ['ADMIN', 'STAFF'] },
  { key: 'accounts', label: 'Cuentas', roles: ['ADMIN'] },
  { key: 'audit', label: 'Auditoría', roles: ['ADMIN'] },
  { key: 'account', label: 'Mi cuenta', roles: ['ADMIN', 'STAFF'] },
];

export default function StaffPanel({ profile, onLogout }: { profile: Profile; onLogout: () => void }) {
  const [tab, setTab] = useState<TabKey>('donors');
  const visibleTabs = TABS.filter((t) => t.roles.includes(profile.role));

  return (
    <main className="staff">
      <header className="topbar">
        <div>
          <span className="eyebrow">ÁREA DE PERSONAL</span>
          <div className="greeting">Hola, {profile.full_name}</div>
        </div>
        <button onClick={onLogout}>Cerrar sesión</button>
      </header>
      <nav className="tabs">
        {visibleTabs.map((t) => (
          <button key={t.key} className={tab === t.key ? 'tab active' : 'tab'} onClick={() => setTab(t.key)}>{t.label}</button>
        ))}
      </nav>
      {tab === 'donors' && <DonorsTab />}
      {tab === 'results' && <ResultsTab canRelease={profile.can_release_results} />}
      {tab === 'campaigns' && <CampaignsTab />}
      {tab === 'communications' && <CommunicationsTab />}
      {tab === 'accounts' && profile.role === 'ADMIN' && <AccountsTab />}
      {tab === 'audit' && profile.role === 'ADMIN' && <AuditTab />}
      {tab === 'account' && <MyAccountTab />}
    </main>
  );
}

function DonorsTab() {
  const [donors, setDonors] = useState<Donor[]>([]);
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ dni: '', first_name: '', last_name: '', gender: 'F', birth_date: '', phone: '', email: '', blood_type: 'O', rh_factor: '+' });

  async function load() {
    const { data, error: err } = await getBrowserSupabaseClient()
      .from('donors')
      .select('id,dni,first_name,last_name,gender,birth_date,phone,email,blood_type,rh_factor,status,consent_email,opted_out')
      .order('last_name');
    if (err) setError(err.message); else setDonors((data || []) as Donor[]);
  }

  useEffect(() => { load(); }, []);

  async function createDonor(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const { error: err } = await getBrowserSupabaseClient().from('donors').insert({
        dni: form.dni, first_name: form.first_name, last_name: form.last_name, gender: form.gender,
        birth_date: form.birth_date, phone: form.phone, email: form.email || null,
        blood_type: form.blood_type, rh_factor: form.rh_factor,
      });
      if (err) throw new Error(err.message);
      setShowForm(false);
      setForm({ dni: '', first_name: '', last_name: '', gender: 'F', birth_date: '', phone: '', email: '', blood_type: 'O', rh_factor: '+' });
      load();
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo registrar al donante.'); }
  }

  async function registerDonation(donorId: number) {
    const date = window.prompt('Fecha de la donación (AAAA-MM-DD)', new Date().toISOString().slice(0, 10));
    if (!date) return;
    const { error: err } = await getBrowserSupabaseClient().from('donations').insert({ donor_id: donorId, donation_date: date, donation_type: 'WHOLE_BLOOD' });
    if (err) alert(err.message); else alert('Donación registrada.');
  }

  const filtered = donors.filter((d) => `${d.first_name} ${d.last_name} ${d.dni} ${d.email || ''}`.toLowerCase().includes(query.toLowerCase()));

  return (
    <section className="panel">
      <div className="panel-head">
        <div><h2>Donantes</h2><p>Búsqueda, alta y registro de donaciones.</p></div>
        <button className="primary" onClick={() => setShowForm((v) => !v)}>{showForm ? 'Cancelar' : '+ Registrar donante'}</button>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      {showForm && (
        <form className="form-grid" onSubmit={createDonor}>
          <label>DNI<input required maxLength={8} value={form.dni} onChange={(e) => setForm({ ...form, dni: e.target.value.replace(/\D/g, '') })} /></label>
          <label>Nombres<input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></label>
          <label>Apellidos<input required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></label>
          <label>Género<select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })}><option value="F">F</option><option value="M">M</option></select></label>
          <label>Fecha de nacimiento<input required type="date" value={form.birth_date} onChange={(e) => setForm({ ...form, birth_date: e.target.value })} /></label>
          <label>Teléfono<input required value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
          <label>Correo<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Tipo de sangre<select value={form.blood_type} onChange={(e) => setForm({ ...form, blood_type: e.target.value })}>{['O', 'A', 'B', 'AB'].map((x) => <option key={x}>{x}</option>)}</select></label>
          <label>Factor RH<select value={form.rh_factor} onChange={(e) => setForm({ ...form, rh_factor: e.target.value })}><option value="+">+</option><option value="-">-</option></select></label>
          <button className="primary" type="submit">Guardar donante</button>
        </form>
      )}
      <input className="search" placeholder="Buscar por nombre, DNI o correo" value={query} onChange={(e) => setQuery(e.target.value)} />
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Donante</th><th>Grupo</th><th>Correo</th><th>Correo autorizado</th><th>Acciones</th></tr></thead>
          <tbody>
            {filtered.map((d) => (
              <tr key={d.id}>
                <td><b>{d.first_name} {d.last_name}</b><br /><small>{d.dni}</small></td>
                <td>{d.blood_type}{d.rh_factor}</td>
                <td>{d.email || '—'}</td>
                <td><span className={`tag ${d.consent_email && !d.opted_out ? '' : 'warn'}`}>{d.consent_email && !d.opted_out ? 'Sí' : 'No'}</span></td>
                <td><button onClick={() => registerDonation(d.id)}>Registrar donación</button></td>
              </tr>
            ))}
            {!filtered.length && <tr><td colSpan={5} className="empty">Sin donantes para mostrar.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ResultsTab({ canRelease }: { canRelease: boolean }) {
  const [results, setResults] = useState<ResultRow[]>([]);
  const [error, setError] = useState('');

  async function load() {
    const { data, error: err } = await getBrowserSupabaseClient()
      .from('donation_results')
      .select('id,status,critical,donor_message,created_at,donations!inner(donation_date,donor_id,donors!inner(first_name,last_name))')
      .order('created_at', { ascending: false })
      .limit(200);
    if (err) setError(err.message); else setResults((data || []) as unknown as ResultRow[]);
  }

  useEffect(() => { load(); }, []);

  async function release(id: number) {
    const message = window.prompt('Mensaje no sensible que verá el donante', 'Tus resultados no críticos están disponibles en HEMOCAX.');
    if (message === null) return;
    const { error: err } = await getBrowserSupabaseClient().rpc('release_noncritical_result', { p_result_id: id, p_donor_message: message });
    if (err) alert(err.message); else load();
  }

  return (
    <section className="panel">
      <div className="panel-head"><div><h2>Resultados</h2><p>Solo cuentas autorizadas pueden liberar resultados no críticos.</p></div></div>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Donante</th><th>Donación</th><th>Estado</th><th>Acción</th></tr></thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.id}>
                <td>{r.donations?.donors.first_name} {r.donations?.donors.last_name}</td>
                <td>{r.donations?.donation_date}</td>
                <td><span className="tag">{r.critical ? 'CRÍTICO' : r.status}</span></td>
                <td>{r.status === 'PENDING' && !r.critical && canRelease ? <button onClick={() => release(r.id)}>Liberar</button> : '—'}</td>
              </tr>
            ))}
            {!results.length && <tr><td colSpan={4} className="empty">Sin resultados registrados.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function CampaignsTab() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', message_template: 'Hola {{nombre}}, te invitamos a donar sangre.' });

  async function load() {
    const { data, error: err } = await getBrowserSupabaseClient().from('campaigns').select('id,name,description,message_template,status,blood_groups').order('created_at', { ascending: false });
    if (err) setError(err.message); else setCampaigns((data || []) as Campaign[]);
  }

  useEffect(() => { load(); }, []);

  async function createCampaign(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const { error: err } = await getBrowserSupabaseClient().from('campaigns').insert({ ...form, status: 'ACTIVE' });
      if (err) throw new Error(err.message);
      setShowForm(false);
      setForm({ name: '', description: '', message_template: 'Hola {{nombre}}, te invitamos a donar sangre.' });
      load();
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo crear la campaña.'); }
  }

  async function send(campaign: Campaign) {
    const bloodType = window.prompt('Filtrar por grupo sanguíneo (vacío = todos): O, A, B, AB', '');
    if (bloodType === null) return;
    try {
      const supabase = getBrowserSupabaseClient();
      let query = supabase.from('donors').select('id,first_name,email,blood_type').eq('status', 'ACTIVE').eq('consent_email', true).eq('opted_out', false).not('email', 'is', null);
      if (bloodType.trim()) query = query.eq('blood_type', bloodType.trim().toUpperCase());
      const { data: targets, error: targetsError } = await query;
      if (targetsError) throw new Error(targetsError.message);
      const { data: already } = await supabase.from('campaign_recipients').select('donor_id').eq('campaign_id', campaign.id);
      const sentTo = new Set((already || []).map((r) => r.donor_id));
      const pending = (targets || []).filter((d) => !sentTo.has(d.id));
      let sent = 0;
      for (const donor of pending) {
        const message = campaign.message_template.replaceAll('{{nombre}}', donor.first_name);
        const comm = await callApi('/api/communications/send', { donor_id: donor.id, type: 'CAMPAIGN', campaign_id: campaign.id, message });
        await supabase.from('campaign_recipients').insert({ campaign_id: campaign.id, donor_id: donor.id, communication_id: comm.id, status: comm.status });
        sent += 1;
      }
      alert(`Enviado a ${sent} donante(s) con consentimiento vigente.`);
    } catch (e) { alert(e instanceof Error ? e.message : 'No se pudo enviar la campaña.'); }
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <div><h2>Campañas</h2><p>Convocatorias para donantes con consentimiento vigente.</p></div>
        <button className="primary" onClick={() => setShowForm((v) => !v)}>{showForm ? 'Cancelar' : '+ Crear campaña'}</button>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      {showForm && (
        <form className="form-grid" onSubmit={createCampaign}>
          <label>Nombre<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
          <label>Descripción<input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
          <label>Mensaje (usa {'{{nombre}}'})<input required value={form.message_template} onChange={(e) => setForm({ ...form, message_template: e.target.value })} /></label>
          <button className="primary" type="submit">Guardar campaña</button>
        </form>
      )}
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Campaña</th><th>Estado</th><th>Mensaje</th><th>Acción</th></tr></thead>
          <tbody>
            {campaigns.map((c) => (
              <tr key={c.id}>
                <td><b>{c.name}</b><br /><small>{c.description}</small></td>
                <td><span className="tag">{c.status}</span></td>
                <td>{c.message_template}</td>
                <td><button onClick={() => send(c)}>Enviar</button></td>
              </tr>
            ))}
            {!campaigns.length && <tr><td colSpan={4} className="empty">Sin campañas registradas.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function CommunicationsTab() {
  const [rows, setRows] = useState<Communication[]>([]);
  const [error, setError] = useState('');
  const [donorDni, setDonorDni] = useState('');
  const [message, setMessage] = useState('Hola {{nombre}}, gracias por ser parte de HEMOCAX.');

  async function load() {
    const { data, error: err } = await getBrowserSupabaseClient()
      .from('communications')
      .select('id,type,channel,email,status,message,created_at,donors(first_name,last_name)')
      .order('created_at', { ascending: false })
      .limit(100);
    if (err) setError(err.message); else setRows((data || []) as unknown as Communication[]);
  }

  useEffect(() => { load(); }, []);

  async function sendManual(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const { data: donor, error: donorError } = await getBrowserSupabaseClient().from('donors').select('id,first_name').eq('dni', donorDni.trim()).single();
      if (donorError || !donor) throw new Error('No se encontró un donante con ese DNI.');
      await callApi('/api/communications/send', { donor_id: donor.id, type: 'MANUAL', message: message.replaceAll('{{nombre}}', donor.first_name) });
      setDonorDni('');
      load();
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo enviar el correo.'); }
  }

  return (
    <section className="panel">
      <div className="panel-head"><div><h2>Comunicaciones</h2><p>Trazabilidad de correos enviados.</p></div></div>
      {error && <p className="error" role="alert">{error}</p>}
      <form className="form-grid" onSubmit={sendManual}>
        <label>DNI del donante<input required maxLength={8} value={donorDni} onChange={(e) => setDonorDni(e.target.value.replace(/\D/g, ''))} /></label>
        <label>Mensaje (usa {'{{nombre}}'})<input required value={message} onChange={(e) => setMessage(e.target.value)} /></label>
        <button className="primary" type="submit">Enviar correo manual</button>
      </form>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Fecha</th><th>Donante</th><th>Tipo</th><th>Estado</th><th>Mensaje</th></tr></thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id}>
                <td>{new Date(c.created_at).toLocaleString('es-PE')}</td>
                <td>{c.donors ? `${c.donors.first_name} ${c.donors.last_name}` : '—'}</td>
                <td>{c.type}</td>
                <td><span className={`tag ${c.status === 'FAILED' ? 'warn' : ''}`}>{c.status}</span></td>
                <td>{c.message}</td>
              </tr>
            ))}
            {!rows.length && <tr><td colSpan={5} className="empty">No hay comunicaciones.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AccountsTab() {
  const [accounts, setAccounts] = useState<AccountRow[]>([]);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ dni: '', full_name: '', role: 'STAFF', can_release_results: false, password: '', donor_id: '' });

  async function load() {
    const { data, error: err } = await getBrowserSupabaseClient().from('profiles').select('user_id,dni,full_name,role,can_release_results,active').order('full_name');
    if (err) setError(err.message); else setAccounts((data || []) as AccountRow[]);
  }

  useEffect(() => { load(); }, []);

  async function createAccount(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      await callApi('/api/admin/users', { ...form, donor_id: form.donor_id || undefined });
      setShowForm(false);
      setForm({ dni: '', full_name: '', role: 'STAFF', can_release_results: false, password: '', donor_id: '' });
      load();
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo crear la cuenta.'); }
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <div><h2>Cuentas</h2><p>Aprovisionamiento de accesos para personal y donantes.</p></div>
        <button className="primary" onClick={() => setShowForm((v) => !v)}>{showForm ? 'Cancelar' : '+ Crear cuenta'}</button>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      {showForm && (
        <form className="form-grid" onSubmit={createAccount}>
          <label>DNI<input required maxLength={8} value={form.dni} onChange={(e) => setForm({ ...form, dni: e.target.value.replace(/\D/g, '') })} /></label>
          <label>Nombre completo<input required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /></label>
          <label>Rol<select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="STAFF">STAFF</option><option value="ADMIN">ADMIN</option><option value="DONOR">DONOR</option></select></label>
          {form.role !== 'DONOR' && (
            <label className="checkbox"><input type="checkbox" checked={form.can_release_results} onChange={(e) => setForm({ ...form, can_release_results: e.target.checked })} /> Puede liberar resultados no críticos</label>
          )}
          {form.role === 'DONOR' && (
            <label>ID del donante a vincular<input required type="number" value={form.donor_id} onChange={(e) => setForm({ ...form, donor_id: e.target.value })} /></label>
          )}
          <label>Contraseña inicial (mín. 12 caracteres)<input required type="password" minLength={12} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="primary" type="submit">Crear cuenta</button>
        </form>
      )}
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Nombre</th><th>DNI</th><th>Rol</th><th>Libera resultados</th><th>Estado</th></tr></thead>
          <tbody>
            {accounts.map((a) => (
              <tr key={a.user_id}>
                <td>{a.full_name}</td><td>{a.dni}</td><td>{a.role}</td>
                <td>{a.can_release_results ? 'Autorizado' : 'No'}</td>
                <td>{a.active ? 'Activo' : 'Inactivo'}</td>
              </tr>
            ))}
            {!accounts.length && <tr><td colSpan={5} className="empty">Sin cuentas registradas.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AuditTab() {
  const [rows, setRows] = useState<AuditLog[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    getBrowserSupabaseClient().from('audit_logs').select('*').order('created_at', { ascending: false }).limit(200)
      .then(({ data, error: err }) => { if (err) setError(err.message); else setRows((data || []) as AuditLog[]); });
  }, []);

  return (
    <section className="panel">
      <div className="panel-head"><div><h2>Auditoría</h2><p>Registro de cambios y accesos.</p></div></div>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Fecha</th><th>Actor</th><th>Acción</th><th>Entidad</th><th>Detalle</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{new Date(r.created_at).toLocaleString('es-PE')}</td>
                <td>{r.actor_dni || '—'}</td>
                <td>{r.action}</td>
                <td>{r.entity} {r.entity_id ?? ''}</td>
                <td>{JSON.stringify(r.detail || {})}</td>
              </tr>
            ))}
            {!rows.length && <tr><td colSpan={5} className="empty">Aún no hay actividad.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function MyAccountTab() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [status, setStatus] = useState('');

  async function changePassword(e: React.FormEvent) {
    e.preventDefault();
    setStatus('');
    if (password.length < 12) { setStatus('La contraseña debe tener al menos 12 caracteres.'); return; }
    if (password !== confirmPassword) { setStatus('Las contraseñas no coinciden.'); return; }
    const { error } = await getBrowserSupabaseClient().auth.updateUser({ password });
    if (error) setStatus(error.message); else { setStatus('Contraseña actualizada.'); setPassword(''); setConfirmPassword(''); }
  }

  return (
    <section className="panel">
      <div className="panel-head"><div><h2>Mi cuenta</h2><p>Cambia tu contraseña de acceso.</p></div></div>
      {status && <p className={status === 'Contraseña actualizada.' ? 'muted' : 'error'}>{status}</p>}
      <form className="form-grid" onSubmit={changePassword}>
        <label>Nueva contraseña<input required type="password" minLength={12} value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <label>Confirmar contraseña<input required type="password" minLength={12} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} /></label>
        <button className="primary" type="submit">Actualizar contraseña</button>
      </form>
    </section>
  );
}
