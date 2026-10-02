'use client';

import { ReactNode, useEffect } from 'react';
import { limaToday } from '@/lib/eligibility';

export type Role = 'ADMIN' | 'STAFF' | 'DONOR';
export type Profile = { dni: string; full_name: string; role: Role; can_release_results: boolean };
export type TabKey = 'home' | 'donors' | 'results' | 'campaigns' | 'emails' | 'reports' | 'accounts' | 'params' | 'audit' | 'account';
export type Notify = (message: string, kind?: 'ok' | 'error') => void;
export type Go = (tab: TabKey, intent?: string) => void;

export type Donor = {
  id: number; dni: string; first_name: string; last_name: string; gender: 'M' | 'F'; birth_date: string;
  phone: string; email: string | null; blood_type: string | null; rh_factor: string | null; status: string;
  consent_email: boolean; opted_out: boolean; auth_user_id: string | null;
};

export const fullName = (d: { first_name: string; last_name: string }) => `${d.first_name} ${d.last_name}`;
export const isAuthorized = (d: Pick<Donor, 'consent_email' | 'opted_out'>) => d.consent_email && !d.opted_out;
export const todayISO = limaToday;

type Tone = 'ok' | 'warn' | 'danger' | 'muted' | 'info';

export const ROLE_LABEL: Record<Role, string> = { ADMIN: 'Administrador', STAFF: 'Personal del Banco de Sangre', DONOR: 'Donante' };

export const RESULT_LABEL: Record<string, { text: string; tone: Tone }> = {
  PENDING: { text: 'Pendiente de revisión', tone: 'warn' },
  AVAILABLE: { text: 'Liberado', tone: 'ok' },
  NOTIFIED: { text: 'Liberado y avisado', tone: 'ok' },
  CONSULTED: { text: 'Visto por el donante', tone: 'ok' },
  CRITICAL_PENDING: { text: 'Crítico', tone: 'danger' },
};

export const EMAIL_STATUS_LABEL: Record<string, { text: string; tone: Tone }> = {
  PENDING: { text: 'En cola', tone: 'info' },
  QUEUED: { text: 'En cola', tone: 'info' },
  SENT: { text: 'Enviado', tone: 'ok' },
  DELIVERED: { text: 'Entregado', tone: 'ok' },
  READ: { text: 'Leído', tone: 'ok' },
  FAILED: { text: 'No se pudo enviar', tone: 'danger' },
  DEMO_QUEUED: { text: 'Simulado (no salió)', tone: 'muted' },
};

export const EMAIL_TYPE_LABEL: Record<string, string> = {
  BIRTHDAY: 'Cumpleaños',
  RETURN_REMINDER: 'Recordatorio para volver a donar',
  DONATION_THANKS: 'Agradecimiento por donar',
  FREQUENT_DONOR: 'Reconocimiento anual',
  CAMPAIGN: 'Campaña',
  MANUAL: 'Mensaje manual',
  RESULT: 'Aviso de resultado',
};

export const AUDIT_LABEL: Record<string, string> = {
  USER_CREATED: 'Se creó una cuenta de acceso',
  USER_PASSWORD_RESET: 'Se restableció una contraseña',
  USER_ACTIVATED: 'Se activó una cuenta',
  USER_DEACTIVATED: 'Se desactivó una cuenta',
  USER_PERMISSION_CHANGED: 'Cambió el permiso de liberar resultados',
  DONOR_CREATED: 'Se registró un donante',
  DONOR_UPDATED: 'Se editaron datos de un donante',
  DONOR_DELETED: 'Se eliminó un donante',
  DONOR_ANONYMIZED: 'Se anonimizaron los datos de un donante',
  DONATION_CREATED: 'Se registró una donación',
  DONATION_UPDATED: 'Se editó una donación',
  DONATION_DELETED: 'Se eliminó una donación',
  RESULT_RELEASED: 'Se liberó un resultado',
  RESULT_MARKED_CRITICAL: 'Se marcó un resultado como crítico',
  RESULT_CRITICAL_CLEARED: 'Se quitó la marca de crítico',
  CAMPAIGN_CREATED: 'Se creó una campaña',
  CAMPAIGN_UPDATED: 'Se editó una campaña',
  CAMPAIGN_DELETED: 'Se eliminó una campaña',
  COMMUNICATION_CREATED: 'Se envió un correo',
  EMAIL_STATUS_UPDATED: 'Cambió el estado de un correo',
  AUTOMATION_RUN: 'Se ejecutó una automatización',
  CONFIG_CREATED: 'Se creó un parámetro',
  CONFIG_UPDATED: 'Se cambió un parámetro',
  TEMPLATE_UPDATED: 'Se editó o aprobó un mensaje automático',
  CONSENT_TEXT_PUBLISHED: 'Se publicó un nuevo texto de consentimiento',
};

export function friendlyError(message: string): string {
  const m = message.toLowerCase();
  if (m.includes('duplicate key')) return 'Ya existe un registro con esos datos (por ejemplo, el mismo DNI).';
  if (m.includes('row-level security') || m.includes('permission denied')) return 'Tu cuenta no tiene permiso para hacer esto.';
  if (m.includes('donors_check')) return 'Para autorizar correos, el donante necesita tener un correo registrado.';
  if (m.includes('failed to fetch')) return 'No hay conexión con el servidor. Revisa tu internet e inténtalo de nuevo.';
  return message;
}

export function PageHeader({ title, help, action }: { title: string; help: string; action?: ReactNode }) {
  return (
    <div className="page-head">
      <div><h1>{title}</h1><p>{help}</p></div>
      {action}
    </div>
  );
}

export function Badge({ tone = 'muted', children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

export function Empty({ title, hint, action }: { title: string; hint?: string; action?: ReactNode }) {
  return (
    <div className="empty-state">
      <b>{title}</b>
      {hint && <p>{hint}</p>}
      {action}
    </div>
  );
}

export function Field({ label, hint, children, className }: { label: string; hint?: string; children: ReactNode; className?: string }) {
  return (
    <label className={`field ${className ?? ''}`}>
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title}>
        <div className="modal-head">
          <h2>{title}</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Cerrar">×</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function downloadFile(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/** CSV con BOM para que Excel respete las tildes. */
export function downloadCsv(filename: string, rows: Record<string, unknown>[]) {
  if (!rows.length) return;
  const cols = Object.keys(rows[0]);
  const esc = (v: unknown) => {
    const t = v === null || v === undefined ? '' : String(v);
    return /[",\n]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t;
  };
  const csv = [cols.join(','), ...rows.map((r) => cols.map((c) => esc(r[c])).join(','))].join('\r\n');
  downloadFile(filename, '﻿' + csv, 'text/csv;charset=utf-8');
}
