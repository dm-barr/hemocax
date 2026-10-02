'use client';

import { useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Go, PageHeader, Profile, ROLE_LABEL } from './ui';

type Counts = { donors: number; donations: number; pending: number; sent: number; unauthorized: number };

const ROLE_HELP: Record<string, string> = {
  ADMIN: 'Puedes hacer todo: registrar donantes y donaciones, liberar resultados, enviar correos y crear cuentas de acceso para tu equipo.',
  STAFF: 'Puedes registrar donantes y donaciones, revisar resultados y enviar correos a los donantes.',
};

export default function HomeTab({ profile, go }: { profile: Profile; go: Go }) {
  const [counts, setCounts] = useState<Counts | null>(null);

  useEffect(() => {
    (async () => {
      const supabase = getBrowserSupabaseClient();
      const head = { count: 'exact', head: true } as const;
      const year = new Date().getFullYear();
      const [donors, donations, pending, sent, unauthorized] = await Promise.all([
        supabase.from('donors').select('id', head),
        supabase.from('donations').select('id', head).gte('donation_date', `${year}-01-01`),
        supabase.from('donation_results').select('id', head).eq('status', 'PENDING'),
        supabase.from('communications').select('id', head).in('status', ['SENT', 'DELIVERED', 'READ']),
        supabase.from('donors').select('id', head).eq('consent_email', false),
      ]);
      setCounts({
        donors: donors.count ?? 0,
        donations: donations.count ?? 0,
        pending: pending.count ?? 0,
        sent: sent.count ?? 0,
        unauthorized: unauthorized.count ?? 0,
      });
    })();
  }, []);

  const firstName = profile.full_name.split(' ')[0];
  const attention: { text: string; action: string; tab: 'results' | 'donors' }[] = [];
  if (counts && counts.pending > 0) attention.push({ text: `${counts.pending} resultado(s) esperan tu revisión.`, action: 'Ver resultados', tab: 'results' });
  if (counts && counts.unauthorized > 0) attention.push({ text: `${counts.unauthorized} donante(s) todavía no autorizan recibir correos.`, action: 'Ver donantes', tab: 'donors' });

  return (
    <>
      <PageHeader
        title={`Hola, ${firstName}`}
        help={`Tu perfil: ${ROLE_LABEL[profile.role]}. ${ROLE_HELP[profile.role] ?? ''}`}
      />

      <h2 className="section-title">Así funciona HEMOCAX, paso a paso</h2>
      <div className="steps">
        <div className="card step">
          <span className="step-num">1</span>
          <h3>Registra al donante</h3>
          <p>Guarda sus datos y su tipo de sangre. Pídele su correo y si acepta que le escribamos.</p>
          <button className="primary small" onClick={() => go('donors', 'new')}>Registrar donante</button>
        </div>
        <div className="card step">
          <span className="step-num">2</span>
          <h3>Anota su donación</h3>
          <p>Cuando done sangre, registra la fecha. El sistema cuida el máximo de donaciones por año.</p>
          <button className="secondary small" onClick={() => go('donors')}>Ir a donantes</button>
        </div>
        <div className="card step">
          <span className="step-num">3</span>
          <h3>Libera su resultado</h3>
          <p>Si el resultado es normal, libéralo para que el donante lo vea en su portal.</p>
          <button className="secondary small" onClick={() => go('results')}>
            Ver resultados{counts && counts.pending > 0 ? ` (${counts.pending} pendientes)` : ''}
          </button>
        </div>
        <div className="card step">
          <span className="step-num">4</span>
          <h3>Avísale por correo</h3>
          <p>Avisa de un resultado o convoca a varios donantes a la vez con una campaña.</p>
          <button className="secondary small" onClick={() => go('campaigns')}>Ir a campañas</button>
        </div>
      </div>

      <h2 className="section-title">Resumen</h2>
      <div className="stats">
        <div className="card stat"><span>Donantes registrados</span><strong>{counts?.donors ?? '…'}</strong></div>
        <div className="card stat"><span>Donaciones este año</span><strong>{counts?.donations ?? '…'}</strong></div>
        <div className="card stat"><span>Resultados por revisar</span><strong>{counts?.pending ?? '…'}</strong></div>
        <div className="card stat"><span>Correos enviados</span><strong>{counts?.sent ?? '…'}</strong></div>
      </div>

      <h2 className="section-title">Requiere tu atención</h2>
      <div className="card">
        {!counts && <p className="muted">Cargando…</p>}
        {counts && attention.length === 0 && <p className="muted">Todo al día. No hay nada pendiente.</p>}
        {attention.map((a) => (
          <div className="attention" key={a.text}>
            <span>{a.text}</span>
            <button className="secondary small" onClick={() => go(a.tab)}>{a.action}</button>
          </div>
        ))}
      </div>

      {profile.role === 'ADMIN' && (
        <div className="card admin-card">
          <div>
            <h3>Cuentas de acceso</h3>
            <p>Crea las cuentas para que tu equipo y los donantes puedan entrar al portal con su DNI.</p>
          </div>
          <button className="secondary" onClick={() => go('accounts', 'new')}>Crear una cuenta</button>
        </div>
      )}
    </>
  );
}
