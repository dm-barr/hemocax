'use client';

import { useCallback, useState } from 'react';
import AccountsTab from './AccountsTab';
import AuditTab from './AuditTab';
import CampaignsTab from './CampaignsTab';
import DonorsTab from './DonorsTab';
import EmailsTab from './EmailsTab';
import HomeTab from './HomeTab';
import MyAccountTab from './MyAccountTab';
import ParamsTab from './ParamsTab';
import ReportsTab from './ReportsTab';
import ResultsTab from './ResultsTab';
import { Go, Notify, Profile, ROLE_LABEL, TabKey } from './ui';

const NAV: { group: string; adminOnly?: boolean; items: { key: TabKey; label: string }[] }[] = [
  { group: 'Trabajo diario', items: [{ key: 'home', label: 'Inicio' }, { key: 'donors', label: 'Donantes' }, { key: 'results', label: 'Resultados' }] },
  { group: 'Comunicación', items: [{ key: 'campaigns', label: 'Campañas e información' }, { key: 'emails', label: 'Correos enviados' }] },
  { group: 'Seguimiento', items: [{ key: 'reports', label: 'Reportes' }] },
  { group: 'Administración', adminOnly: true, items: [{ key: 'accounts', label: 'Cuentas de acceso' }, { key: 'params', label: 'Parámetros' }, { key: 'audit', label: 'Actividad' }] },
  { group: 'Mi perfil', items: [{ key: 'account', label: 'Mi cuenta' }] },
];

type Toast = { id: number; message: string; kind: 'ok' | 'error' };

export default function StaffPanel({ profile, onLogout }: { profile: Profile; onLogout: () => void }) {
  const [nav, setNav] = useState<{ tab: TabKey; intent?: string }>({ tab: 'home' });
  const [toasts, setToasts] = useState<Toast[]>([]);

  const notify = useCallback<Notify>((message, kind = 'ok') => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, message, kind }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), kind === 'error' ? 8000 : 5000);
  }, []);
  const go = useCallback<Go>((tab, intent) => setNav({ tab, intent }), []);

  const isAdmin = profile.role === 'ADMIN';

  return (
    <div className="shell">
      <aside className="side">
        <div className="brand"><span className="brand-icon">H</span><span>HEMO<span className="accent">CAX</span></span></div>
        <nav aria-label="Secciones">
          {NAV.filter((g) => !g.adminOnly || isAdmin).map((g) => (
            <div key={g.group} className="nav-section">
              <div className="nav-group">{g.group}</div>
              {g.items.map((i) => (
                <button key={i.key} className={nav.tab === i.key ? 'nav-item active' : 'nav-item'} onClick={() => go(i.key)} aria-current={nav.tab === i.key ? 'page' : undefined}>{i.label}</button>
              ))}
            </div>
          ))}
        </nav>
        <div className="side-user">
          <b>{profile.full_name}</b>
          <span>{ROLE_LABEL[profile.role]}</span>
          <button className="secondary small" onClick={onLogout}>Cerrar sesión</button>
        </div>
      </aside>

      <main className="main">
        {nav.tab === 'home' && <HomeTab profile={profile} go={go} />}
        {nav.tab === 'donors' && <DonorsTab notify={notify} intent={nav.intent} isAdmin={isAdmin} />}
        {nav.tab === 'results' && <ResultsTab canRelease={profile.can_release_results} notify={notify} />}
        {nav.tab === 'campaigns' && <CampaignsTab notify={notify} />}
        {nav.tab === 'emails' && <EmailsTab notify={notify} />}
        {nav.tab === 'reports' && <ReportsTab notify={notify} />}
        {nav.tab === 'params' && isAdmin && <ParamsTab notify={notify} profile={profile} />}
        {nav.tab === 'accounts' && isAdmin && <AccountsTab notify={notify} intent={nav.intent} />}
        {nav.tab === 'audit' && isAdmin && <AuditTab notify={notify} />}
        {nav.tab === 'account' && <MyAccountTab profile={profile} notify={notify} />}
      </main>

      <div className="toasts" aria-live="polite">
        {toasts.map((t) => <div key={t.id} className={`toast ${t.kind}`}>{t.message}</div>)}
      </div>
    </div>
  );
}
