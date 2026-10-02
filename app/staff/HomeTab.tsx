'use client';

import { useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { limaToday } from '@/lib/eligibility';
import DonorFicha from './DonorFicha';
import { normalizeText, useDirectory } from './useDirectory';
import { Badge, Go, Notify, PageHeader, Profile, fullName, isAuthorized, roleTitle } from './ui';

type PendingRow = { id: number; created_at: string; donations: { donors: { first_name: string; last_name: string } } };

const hoursSince = (iso: string) => Math.floor((Date.now() - new Date(iso).getTime()) / 3_600_000);

export default function HomeTab({ profile, go, notify }: { profile: Profile; go: Go; notify: Notify }) {
  const { donors, donations, params, eligibility, loading, reload } = useDirectory(notify);
  const [query, setQuery] = useState('');
  const [fichaId, setFichaId] = useState<number | null>(null);
  const [pending, setPending] = useState<PendingRow[] | null>(null);
  const [unapproved, setUnapproved] = useState(0);
  const isAdmin = profile.role === 'ADMIN';
  const isDoctor = profile.can_release_results;

  useEffect(() => {
    (async () => {
      const supabase = getBrowserSupabaseClient();
      const [p, t] = await Promise.all([
        supabase.from('donation_results')
          .select('id,created_at,donations!inner(donors!inner(first_name,last_name))')
          .eq('status', 'PENDING').eq('critical', false).order('created_at', { ascending: true }).limit(50),
        supabase.from('message_templates').select('type', { count: 'exact', head: true }).eq('approved', false),
      ]);
      setPending((p.data || []) as unknown as PendingRow[]);
      setUnapproved(t.count ?? 0);
    })();
  }, []);

  const firstName = profile.full_name.split(' ')[0];
  const q = normalizeText(query.trim());
  const matches = q.length < 2 ? [] : donors.filter((d) => d.dni.startsWith(q) || normalizeText(fullName(d)).includes(q) || d.dni.includes(q));
  const shown = matches.slice(0, 6);
  const looksLikeDni = /^\d{8}$/.test(query.trim());

  const today = limaToday();
  const todays = donations.filter((d) => d.donation_date === today).map((d) => donors.find((x) => x.id === d.donor_id)).filter((d): d is NonNullable<typeof d> => !!d);
  const overdue = (pending ?? []).filter((r) => hoursSince(r.created_at) >= 36).length;
  const unauthorized = donors.filter((d) => d.status === 'ACTIVE' && !isAuthorized(d)).length;
  const ficha = fichaId !== null ? donors.find((d) => d.id === fichaId) : undefined;

  return (
    <>
      <PageHeader title={`Hola, ${firstName}`} help={`${roleTitle(profile)}. Empieza buscando al donante que tienes enfrente.`} />

      <div className="card attend">
        <h2>Atender a un donante</h2>
        <p className="muted">Escribe su DNI o su nombre. Verás si puede donar hoy y podrás registrar su donación.</p>
        <input
          className="search big"
          autoFocus
          inputMode="search"
          placeholder="DNI o nombre del donante"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Buscar donante por DNI o nombre"
        />
        {loading && q.length >= 2 && <p className="muted">Buscando…</p>}
        {!loading && q.length >= 2 && shown.length > 0 && (
          <ul className="results-list">
            {shown.map((d) => {
              const e = eligibility.get(d.id)!;
              return (
                <li key={d.id}>
                  <button className="result-row" onClick={() => setFichaId(d.id)}>
                    <span><b>{fullName(d)}</b><small>DNI {d.dni}{d.blood_type ? ` · ${d.blood_type}${d.rh_factor}` : ''}</small></span>
                    {e.state === 'APTO' ? <Badge tone="ok">Puede donar</Badge> : e.state === 'INACTIVO' ? <Badge>Inactivo</Badge> : <Badge tone="warn">{e.state === 'MAXIMO' ? 'Máximo anual' : 'Aún no puede'}</Badge>}
                  </button>
                </li>
              );
            })}
            {matches.length > shown.length && <li className="more">Hay {matches.length - shown.length} más: escribe un poco más para afinar.</li>}
          </ul>
        )}
        {!loading && q.length >= 2 && shown.length === 0 && (
          <div className="notice-box warn not-found">
            <span>{looksLikeDni ? `No hay ningún donante con el DNI ${query.trim()}.` : 'No encontramos a nadie con ese nombre.'}</span>
            <button className="primary small" onClick={() => go('donors', looksLikeDni ? `new:${query.trim()}` : 'new')}>Registrar donante nuevo</button>
          </div>
        )}
      </div>

      <div className="columns home-columns">
        <section className="card">
          <h3>Resultados por revisar</h3>
          <p className="muted">{isDoctor ? 'Ábrelos para liberarlos o marcarlos como críticos.' : 'Los revisa y libera el médico responsable.'}</p>
          {pending === null ? <p className="muted">Cargando…</p> : pending.length === 0 ? <p className="ok-line">No hay resultados pendientes.</p> : (
            <ul className="mini-list">
              {pending.slice(0, 5).map((r) => {
                const h = hoursSince(r.created_at);
                return (
                  <li key={r.id}>
                    <span>{r.donations.donors.first_name} {r.donations.donors.last_name}</span>
                    <Badge tone={h >= 48 ? 'danger' : h >= 36 ? 'warn' : 'muted'}>{h >= 48 ? `${h} h · pasó la meta` : `hace ${h} h`}</Badge>
                  </li>
                );
              })}
              {pending.length > 5 && <li className="more">y {pending.length - 5} más…</li>}
            </ul>
          )}
          <button className="secondary small" onClick={() => go('results')}>Ir a Resultados{pending && pending.length ? ` (${pending.length})` : ''}</button>
        </section>

        <section className="card">
          <h3>Donaciones de hoy</h3>
          <p className="muted">Las que se registraron en el día.</p>
          {loading ? <p className="muted">Cargando…</p> : todays.length === 0 ? <p className="muted">Todavía no se registró ninguna hoy.</p> : (
            <ul className="mini-list">
              {todays.slice(0, 8).map((d, i) => (
                <li key={`${d.id}-${i}`}><button className="link-btn" onClick={() => setFichaId(d.id)}>{fullName(d)}</button>{d.blood_type && <span className="blood-type">{d.blood_type}{d.rh_factor}</span>}</li>
              ))}
            </ul>
          )}
          <button className="secondary small" onClick={() => go('donors')}>Ver todos los donantes</button>
        </section>
      </div>

      {(overdue > 0 || unauthorized > 0 || (isAdmin && unapproved > 0)) && (
        <section className="card">
          <h3>Requiere atención</h3>
          {overdue > 0 && (
            <div className="attention"><span>{overdue} resultado(s) llevan más de 36 horas esperando: la meta es liberarlos en 48.</span><button className="secondary small" onClick={() => go('results')}>Revisar ahora</button></div>
          )}
          {isAdmin && unapproved > 0 && (
            <div className="attention"><span>{unapproved} mensaje(s) automático(s) sin aprobar: no se enviarán recordatorios hasta que se aprueben.</span><button className="secondary small" onClick={() => go('params')}>Aprobar mensajes</button></div>
          )}
          {unauthorized > 0 && (
            <div className="attention"><span>{unauthorized} donante(s) todavía no autorizan recibir correos.</span><button className="secondary small" onClick={() => go('donors')}>Ver donantes</button></div>
          )}
        </section>
      )}

      <div className="home-links">
        <button className="link-card" onClick={() => go('help')}><b>¿Necesitas ayuda?</b><span>Guía paso a paso para tu puesto</span></button>
        {isAdmin && <button className="link-card" onClick={() => go('accounts', 'new')}><b>Crear una cuenta</b><span>Para el personal o un donante</span></button>}
        <button className="link-card" onClick={() => go('donors', 'new')}><b>Registrar donante nuevo</b><span>Una persona que viene por primera vez</span></button>
      </div>

      {ficha && <DonorFicha donor={ficha} donations={donations} params={params} eligibility={eligibility.get(ficha.id)!} isAdmin={isAdmin} notify={notify} onClose={() => setFichaId(null)} onChanged={reload} />}
    </>
  );
}
