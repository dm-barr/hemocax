import type { Params } from './params';

/** Fecha de hoy en Lima (UTC-5), como AAAA-MM-DD. */
export const limaToday = () => new Date(Date.now() - 5 * 3600 * 1000).toISOString().slice(0, 10);

export function addDays(iso: string, days: number): string {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

export const daysBetween = (fromIso: string, toIso: string) =>
  Math.round((new Date(`${toIso}T00:00:00Z`).getTime() - new Date(`${fromIso}T00:00:00Z`).getTime()) / 86_400_000);

export type EligibilityState = 'APTO' | 'ESPERA' | 'MAXIMO' | 'INACTIVO';
export type Eligibility = {
  state: EligibilityState;
  /** Primer día en que puede volver a donar (null si ya es apto o está inactivo). */
  eligibleFrom: string | null;
  thisYear: number;
  limit: number;
  intervalDays: number;
  lastDate: string | null;
};

export function computeEligibility(opts: {
  gender: 'M' | 'F';
  active: boolean;
  donationDates: string[];
  params: Pick<Params, 'limits' | 'intervals'>;
  today?: string;
}): Eligibility {
  const today = opts.today ?? limaToday();
  const year = today.slice(0, 4);
  const limit = opts.params.limits[opts.gender];
  const intervalDays = opts.params.intervals[opts.gender];
  const lastDate = opts.donationDates.reduce<string | null>((max, d) => (!max || d > max ? d : max), null);
  const thisYear = opts.donationDates.filter((d) => d.slice(0, 4) === year).length;
  const base = { thisYear, limit, intervalDays, lastDate };

  if (!opts.active) return { ...base, state: 'INACTIVO', eligibleFrom: null };
  if (thisYear >= limit) return { ...base, state: 'MAXIMO', eligibleFrom: `${Number(year) + 1}-01-01` };
  if (lastDate) {
    const from = addDays(lastDate, intervalDays);
    if (from > today) return { ...base, state: 'ESPERA', eligibleFrom: from };
  }
  return { ...base, state: 'APTO', eligibleFrom: null };
}

export const formatDate = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('es-PE', { day: 'numeric', month: 'short', year: 'numeric' });
