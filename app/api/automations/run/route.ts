import { NextResponse } from 'next/server';
import { createServiceRoleClient } from '@/lib/supabase/server';

type Donor = { id: number; first_name: string; email: string; gender: 'M' | 'F'; birth_date: string };
type Donation = { id: number; donor_id: number; donation_date: string };

const MESSAGES: Record<string, (firstName: string) => string> = {
  BIRTHDAY: (n) => `Feliz cumpleaños, ${n}. Desde HEMOCAX y el Banco de Sangre te deseamos un excelente día. Gracias por formar parte de nuestra comunidad de donantes.`,
  RETURN_REMINDER: (n) => `Hola ${n}. Según el intervalo registrado desde tu última donación, puedes volver a considerar participar como donante. La evaluación final corresponde al personal de salud.`,
  FREQUENT_DONOR: (n) => `Hola ${n}. Gracias por tu compromiso y tus donaciones de este año. Tu solidaridad es muy valiosa para la comunidad.`,
  DONATION_THANKS: (n) => `Hola ${n}. Gracias por tu donación voluntaria. Cuídate y sigue las recomendaciones que te brindó el personal de salud.`,
};

async function dispatchToWorker(payload: object) {
  const url = process.env.AUTOMATION_WEBHOOK_URL;
  if (!url) return { dispatched: false as const };
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-hemocax-webhook-secret': process.env.AUTOMATION_WEBHOOK_SECRET || '' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`El servicio de correo respondió HTTP ${response.status}`);
    return { dispatched: true as const };
  } catch (e) {
    return { dispatched: true as const, error: e instanceof Error ? e.message : 'Error desconocido' };
  }
}

export async function POST(request: Request) {
  const secret = process.env.AUTOMATION_RUN_SECRET;
  if (!secret || request.headers.get('x-hemocax-automation-secret') !== secret) {
    return NextResponse.json({ error: 'Automatización no autorizada.' }, { status: 401 });
  }

  const body = await request.json().catch(() => ({}));
  const type = String(body?.type || '');
  if (!['BIRTHDAY', 'RETURN_REMINDER', 'FREQUENT_DONOR', 'DONATION_THANKS'].includes(type)) {
    return NextResponse.json({ error: 'Tipo de automatización no válido.' }, { status: 400 });
  }

  const service = createServiceRoleClient();
  const now = new Date();
  const year = now.getFullYear();
  const todayMonthDay = now.toISOString().slice(5, 10);

  const { data: config } = await service.from('system_config').select('key,value').in('key', ['donation_interval_days', 'male_annual_limit', 'female_annual_limit']);
  const configMap = Object.fromEntries((config || []).map((row) => [row.key, Number(row.value)]));
  const intervalDays = configMap.donation_interval_days ?? 90;
  const annualLimit = (gender: 'M' | 'F') => (gender === 'M' ? configMap.male_annual_limit ?? 4 : configMap.female_annual_limit ?? 3);

  const { data: donorsData } = await service
    .from('donors')
    .select('id,first_name,email,gender,birth_date')
    .eq('status', 'ACTIVE')
    .eq('consent_email', true)
    .eq('opted_out', false)
    .not('email', 'is', null);
  const donors = (donorsData || []) as Donor[];
  const donorIds = donors.map((d) => d.id);

  const { data: donationsData } = donorIds.length
    ? await service.from('donations').select('id,donor_id,donation_date').eq('donation_type', 'WHOLE_BLOOD').in('donor_id', donorIds)
    : { data: [] as Donation[] };
  const donations = (donationsData || []) as Donation[];
  const donationsByDonor = new Map<number, Donation[]>();
  for (const d of donations) {
    const list = donationsByDonor.get(d.donor_id) || [];
    list.push(d);
    donationsByDonor.set(d.donor_id, list);
  }

  type Candidate = { donor: Donor; relatedDonationId: number | null };
  let candidates: Candidate[] = [];

  if (type === 'BIRTHDAY') {
    candidates = donors.filter((d) => d.birth_date.slice(5) === todayMonthDay).map((donor) => ({ donor, relatedDonationId: null }));
  } else if (type === 'RETURN_REMINDER') {
    candidates = donors
      .map((donor): Candidate | null => {
        const list = (donationsByDonor.get(donor.id) || []).slice().sort((a, b) => b.donation_date.localeCompare(a.donation_date));
        const last = list[0] || null;
        const daysSinceLast = last ? (now.getTime() - new Date(`${last.donation_date}T00:00:00`).getTime()) / 86_400_000 : Infinity;
        const countThisYear = list.filter((x) => x.donation_date.slice(0, 4) === String(year)).length;
        const eligible = daysSinceLast >= intervalDays && countThisYear < annualLimit(donor.gender);
        return eligible ? { donor, relatedDonationId: last?.id ?? null } : null;
      })
      .filter((x): x is Candidate => x !== null);
  } else if (type === 'FREQUENT_DONOR') {
    candidates = donors
      .filter((donor) => (donationsByDonor.get(donor.id) || []).filter((x) => x.donation_date.slice(0, 4) === String(year)).length >= annualLimit(donor.gender))
      .map((donor) => ({ donor, relatedDonationId: null }));
  } else if (type === 'DONATION_THANKS') {
    for (const donation of donations) {
      const ageDays = (now.getTime() - new Date(`${donation.donation_date}T00:00:00`).getTime()) / 86_400_000;
      if (ageDays < 0 || ageDays > 7) continue;
      const donor = donors.find((d) => d.id === donation.donor_id);
      if (donor) candidates.push({ donor, relatedDonationId: donation.id });
    }
  }

  if (body?.dry_run === true) {
    return NextResponse.json({ type, eligible: candidates.length, donors: candidates.map((c) => c.donor) });
  }

  const created: unknown[] = [];
  for (const { donor, relatedDonationId } of candidates) {
    const message = MESSAGES[type](donor.first_name);
    const { data: row, error: insertError } = await service
      .from('communications')
      .insert({
        donor_id: donor.id,
        related_donation_id: relatedDonationId,
        type,
        channel: 'EMAIL',
        email: donor.email,
        message,
        status: 'PENDING',
      })
      .select('*')
      .single();
    if (insertError) {
      if (insertError.code === '23505') continue; // ya se envió este tipo para este donante/periodo
      continue;
    }
    const { dispatched, error: dispatchError } = await dispatchToWorker({
      communication_id: row.id,
      donor_id: donor.id,
      email: donor.email,
      recipient_name: donor.first_name,
      message,
      type,
    });
    if (!dispatched) {
      await service.from('communications').update({ status: 'DEMO_QUEUED' }).eq('id', row.id);
    } else if (dispatchError) {
      await service.from('communications').update({ status: 'FAILED', error_message: dispatchError }).eq('id', row.id);
    }
    created.push(row);
  }

  await service.from('audit_logs').insert({ action: 'AUTOMATION_RUN', entity: 'automation', actor_dni: 'PYTHON', detail: { type, count: created.length } });

  return NextResponse.json({ type, count: created.length, communications: created }, { status: 202 });
}
