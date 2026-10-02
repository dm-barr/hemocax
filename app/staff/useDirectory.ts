'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Params, loadParams } from '@/lib/params';
import { Eligibility, computeEligibility } from '@/lib/eligibility';
import { Donor, Notify, friendlyError } from './ui';

export type DonationRow = { id: number; donor_id: number; donation_date: string };

const DEFAULT_PARAMS: Params = { limits: { M: 4, F: 3 }, intervals: { M: 90, F: 90 }, recommendations: '', contactInfo: '' };

/** Carga el padrón de donantes con sus donaciones y calcula quién puede donar hoy. */
export function useDirectory(notify: Notify) {
  const [donors, setDonors] = useState<Donor[]>([]);
  const [donations, setDonations] = useState<DonationRow[]>([]);
  const [params, setParams] = useState<Params>(DEFAULT_PARAMS);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    const supabase = getBrowserSupabaseClient();
    const [d, ds, p] = await Promise.all([
      supabase.from('donors')
        .select('id,dni,first_name,last_name,gender,birth_date,phone,email,blood_type,rh_factor,status,consent_email,opted_out,auth_user_id')
        .order('last_name'),
      supabase.from('donations').select('id,donor_id,donation_date').eq('donation_type', 'WHOLE_BLOOD'),
      loadParams(supabase),
    ]);
    if (d.error) notify(friendlyError(d.error.message), 'error');
    else setDonors((d.data || []) as Donor[]);
    if (ds.data) setDonations(ds.data as DonationRow[]);
    setParams(p);
    setLoading(false);
  }, [notify]);

  useEffect(() => { reload(); }, [reload]);

  const eligibility = useMemo(() => {
    const byDonor = new Map<number, string[]>();
    for (const x of donations) byDonor.set(x.donor_id, [...(byDonor.get(x.donor_id) || []), x.donation_date]);
    const map = new Map<number, Eligibility>();
    for (const d of donors) map.set(d.id, computeEligibility({ gender: d.gender, active: d.status === 'ACTIVE', donationDates: byDonor.get(d.id) || [], params }));
    return map;
  }, [donors, donations, params]);

  return { donors, donations, params, eligibility, loading, reload };
}

export const normalizeText = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
