'use client';

import { useEffect, useMemo, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Params, loadParams } from '@/lib/params';
import { computeEligibility, limaToday } from '@/lib/eligibility';
import { EMAIL_STATUS_LABEL, EMAIL_TYPE_LABEL, Notify, PageHeader, downloadCsv, friendlyError } from './ui';

type DonorRow = {
  id: number; dni: string; first_name: string; last_name: string; gender: 'M' | 'F'; birth_date: string; phone: string; email: string | null;
  blood_type: string | null; rh_factor: string | null; status: string; consent_email: boolean; opted_out: boolean; created_at: string;
};
type DonationRow = { id: number; donor_id: number; donation_date: string };
type ResultRow = { id: number; status: string; critical: boolean; created_at: string; available_at: string | null; donation_id: number };
type MailRow = { id: number; type: string; status: string; created_at: string; created_by_name: string | null; donor_id: number };

const GROUPS = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'];
const pct = (a: number, b: number) => (b ? `${Math.round((a / b) * 100)} %` : '—');

export default function ReportsTab({ notify }: { notify: Notify }) {
  const [donors, setDonors] = useState<DonorRow[]>([]);
  const [donations, setDonations] = useState<DonationRow[]>([]);
  const [results, setResults] = useState<ResultRow[]>([]);
  const [mails, setMails] = useState<MailRow[]>([]);
  const [params, setParams] = useState<Params | null>(null);

  useEffect(() => {
    (async () => {
      const supabase = getBrowserSupabaseClient();
      const [d, ds, r, m, p] = await Promise.all([
        supabase.from('donors').select('id,dni,first_name,last_name,gender,birth_date,phone,email,blood_type,rh_factor,status,consent_email,opted_out,created_at').limit(5000),
        supabase.from('donations').select('id,donor_id,donation_date').eq('donation_type', 'WHOLE_BLOOD').limit(10000),
        supabase.from('donation_results').select('id,status,critical,created_at,available_at,donation_id').limit(10000),
        supabase.from('communications').select('id,type,status,created_at,created_by_name,donor_id').order('created_at', { ascending: false }).limit(5000),
        loadParams(supabase),
      ]);
      const firstError = d.error || ds.error || r.error || m.error;
      if (firstError) notify(friendlyError(firstError.message), 'error');
      setDonors((d.data || []) as DonorRow[]);
      setDonations((ds.data || []) as DonationRow[]);
      setResults((r.data || []) as ResultRow[]);
      setMails((m.data || []) as MailRow[]);
      setParams(p);
    })();
  }, [notify]);

  const stats = useMemo(() => {
    if (!params) return null;
    const today = limaToday();
    const active = donors.filter((d) => d.status === 'ACTIVE');
    const authorized = active.filter((d) => d.consent_email && !d.opted_out);

    const counts = new Map<number, string[]>();
    for (const x of donations) counts.set(x.donor_id, [...(counts.get(x.donor_id) || []), x.donation_date]);
    const donated = donors.filter((d) => (counts.get(d.id)?.length ?? 0) >= 1);
    const recurrent = donors.filter((d) => (counts.get(d.id)?.length ?? 0) >= 2);

    const oneg = donors.filter((d) => d.blood_type === 'O' && d.rh_factor === '-');
    const onegActive = oneg.filter((d) => d.status === 'ACTIVE');
    const onegConsent = onegActive.filter((d) => d.consent_email && !d.opted_out);

    const released = results.filter((r) => r.available_at && !r.critical);
    const hours = released.map((r) => (new Date(r.available_at!).getTime() - new Date(r.created_at).getTime()) / 3_600_000);
    const avgHours = hours.length ? hours.reduce((a, b) => a + b, 0) / hours.length : null;
    const within48 = hours.filter((h) => h <= 48).length;
    const pending = results.filter((r) => r.status === 'PENDING' && !r.critical);
    const pendingAges = pending.map((r) => (Date.now() - new Date(r.created_at).getTime()) / 3_600_000);

    const since = Date.now() - 30 * 86_400_000;
    const recentMails = mails.filter((m) => new Date(m.created_at).getTime() >= since);
    const byType = new Map<string, { total: number; sent: number; failed: number }>();
    for (const m of recentMails) {
      const cur = byType.get(m.type) ?? { total: 0, sent: 0, failed: 0 };
      cur.total += 1;
      if (['SENT', 'DELIVERED', 'READ'].includes(m.status)) cur.sent += 1;
      if (m.status === 'FAILED') cur.failed += 1;
      byType.set(m.type, cur);
    }

    const aptoNow = (d: DonorRow) => computeEligibility({ gender: d.gender, active: d.status === 'ACTIVE', donationDates: counts.get(d.id) || [], params, today }).state === 'APTO';
    const reserve = [...GROUPS, ''].map((g) => {
      const list = donors.filter((d) => (d.blood_type ? `${d.blood_type}${d.rh_factor}` : '') === g);
      return {
        group: g || 'Sin dato', total: list.length, active: list.filter((d) => d.status === 'ACTIVE').length,
        authorized: list.filter((d) => d.status === 'ACTIVE' && d.consent_email && !d.opted_out).length, apto: list.filter(aptoNow).length,
      };
    });

    return {
      active: active.length, authorized: authorized.length, donated: donated.length, recurrent: recurrent.length,
      oneg: oneg.length, onegActive: onegActive.length, onegConsent: onegConsent.length,
      released: released.length, avgHours, within48, pending: pending.length,
      oldestPending: pendingAges.length ? Math.max(...pendingAges) : null, overdue: pendingAges.filter((h) => h >= 48).length,
      recentMails: recentMails.length, byType: [...byType.entries()], reserve,
    };
  }, [donors, donations, results, mails, params]);

  function exportDonors() {
    downloadCsv(`donantes-${limaToday()}.csv`, donors.map((d) => ({
      dni: d.dni, nombres: d.first_name, apellidos: d.last_name, sexo: d.gender, fecha_nacimiento: d.birth_date, telefono: d.phone, correo: d.email ?? '',
      grupo_sanguineo: d.blood_type ? `${d.blood_type}${d.rh_factor}` : '', estado: d.status, correo_autorizado: d.consent_email && !d.opted_out ? 'Sí' : 'No', registrado: d.created_at.slice(0, 10),
    })));
  }
  function exportMails() {
    const names = new Map(donors.map((d) => [d.id, `${d.first_name} ${d.last_name}`]));
    downloadCsv(`correos-${limaToday()}.csv`, mails.map((m) => ({
      fecha: m.created_at, donante: names.get(m.donor_id) ?? '', tipo: EMAIL_TYPE_LABEL[m.type] ?? m.type, canal: 'Correo',
      enviado_por: m.created_by_name ?? '', estado: EMAIL_STATUS_LABEL[m.status]?.text ?? m.status,
    })));
  }
  function exportResults() {
    downloadCsv(`resultados-${limaToday()}.csv`, results.map((r) => ({
      registrado: r.created_at, liberado: r.available_at ?? '', estado: r.critical ? 'Crítico' : r.status,
      horas_hasta_liberar: r.available_at ? Math.round((new Date(r.available_at).getTime() - new Date(r.created_at).getTime()) / 3_600_000) : '',
    })));
  }

  if (!stats) return <p className="muted">Calculando reportes…</p>;

  return (
    <>
      <PageHeader title="Reportes" help="Cifras para la Jefatura del Banco de Sangre: los indicadores del proyecto, la reserva por grupo sanguíneo y la actividad de comunicación. Puedes descargar los datos en Excel (CSV)." />

      <h2 className="section-title">Indicadores del proyecto</h2>
      <div className="stats">
        <div className="card stat"><span>Donantes recurrentes</span><strong>{pct(stats.recurrent, stats.donated)}</strong><small>{stats.recurrent} de {stats.donated} que han donado volvieron a donar</small></div>
        <div className="card stat"><span>Tiempo medio de entrega de resultados</span><strong>{stats.avgHours === null ? '—' : `${Math.round(stats.avgHours)} h`}</strong><small>Meta: 48 h · {stats.released ? `${pct(stats.within48, stats.released)} dentro de la meta` : 'aún sin resultados liberados'}</small></div>
        <div className="card stat"><span>Donantes O negativo</span><strong>{stats.onegConsent}</strong><small>con consentimiento · {stats.onegActive} vigentes · {stats.oneg} registrados</small></div>
        <div className="card stat"><span>Mensajes en 30 días</span><strong>{stats.recentMails}</strong><small>con bitácora de auditoría completa</small></div>
      </div>

      <h2 className="section-title">Donantes y resultados</h2>
      <div className="stats">
        <div className="card stat"><span>Donantes activos</span><strong>{stats.active}</strong></div>
        <div className="card stat"><span>Con correo autorizado</span><strong>{pct(stats.authorized, stats.active)}</strong><small>{stats.authorized} de {stats.active} activos</small></div>
        <div className="card stat"><span>Resultados pendientes</span><strong>{stats.pending}</strong><small>{stats.overdue} pasaron las 48 h{stats.oldestPending !== null ? ` · el más antiguo: ${Math.round(stats.oldestPending)} h` : ''}</small></div>
      </div>

      <h2 className="section-title">Reserva por grupo sanguíneo</h2>
      <div className="card table-card"><div className="table-wrap"><table className="table">
        <thead><tr><th>Grupo</th><th>Registrados</th><th>Activos</th><th>Con correo autorizado</th><th>Aptos hoy</th></tr></thead>
        <tbody>{stats.reserve.map((r) => <tr key={r.group}><td><b>{r.group}</b></td><td>{r.total}</td><td>{r.active}</td><td>{r.authorized}</td><td>{r.apto}</td></tr>)}</tbody>
      </table></div></div>

      <h2 className="section-title">Mensajes de los últimos 30 días</h2>
      <div className="card table-card"><div className="table-wrap"><table className="table">
        <thead><tr><th>Tipo</th><th>Total</th><th>Enviados</th><th>Fallidos</th></tr></thead>
        <tbody>
          {stats.byType.length === 0 && <tr><td colSpan={4} className="empty">Todavía no hay mensajes en este período.</td></tr>}
          {stats.byType.map(([type, v]) => <tr key={type}><td>{EMAIL_TYPE_LABEL[type] ?? type}</td><td>{v.total}</td><td>{v.sent}</td><td>{v.failed}</td></tr>)}
        </tbody>
      </table></div></div>

      <h2 className="section-title">Descargar en Excel (CSV)</h2>
      <div className="card export-row">
        <button className="secondary" onClick={exportDonors}>Padrón de donantes</button>
        <button className="secondary" onClick={exportMails}>Bitácora de correos</button>
        <button className="secondary" onClick={exportResults}>Resultados y tiempos</button>
      </div>
    </>
  );
}
