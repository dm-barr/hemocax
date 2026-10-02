'use client';

import { useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { AUDIT_LABEL, Empty, Notify, PageHeader, friendlyError } from './ui';

type Log = { id: number; created_at: string; action: string; actor_dni: string | null; detail: Record<string, unknown> };

export default function AuditTab({ notify }: { notify: Notify }) {
  const [rows, setRows] = useState<Log[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getBrowserSupabaseClient().from('audit_logs').select('id,created_at,action,actor_dni,detail').order('created_at', { ascending: false }).limit(200)
      .then(({ data, error }) => {
        if (error) notify(friendlyError(error.message), 'error');
        else setRows((data || []) as Log[]);
        setLoading(false);
      });
  }, [notify]);

  return (
    <>
      <PageHeader title="Actividad" help="Registro de lo que pasó en el sistema: quién hizo qué y cuándo. Sirve para revisar cambios importantes. Solo los administradores lo ven." />
      {loading ? <p className="muted">Cargando…</p> : rows.length === 0 ? (
        <div className="card"><Empty title="Todavía no hay actividad registrada" /></div>
      ) : (
        <div className="card table-card">
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Fecha</th><th>Qué pasó</th><th>Quién</th><th>Detalle</th></tr></thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id}>
                    <td>{new Date(r.created_at).toLocaleString('es-PE', { dateStyle: 'medium', timeStyle: 'short' })}</td>
                    <td>{AUDIT_LABEL[r.action] ?? r.action}</td>
                    <td>{r.actor_dni || 'Sistema'}</td>
                    <td><small>{Object.entries(r.detail || {}).map(([k, v]) => `${k}: ${String(v)}`).join(' · ') || '—'}</small></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}
