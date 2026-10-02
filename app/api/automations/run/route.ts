import { NextResponse } from 'next/server';
import { deliverCommunication } from '@/lib/communications';
import { isSimulated } from '@/lib/email';
import { computeEligibility, daysBetween, limaToday } from '@/lib/eligibility';
import { loadParams } from '@/lib/params';
import { createServiceRoleClient } from '@/lib/supabase/server';

export const maxDuration = 60;

type Donor = { id: number; first_name: string; email: string; gender: 'M' | 'F'; birth_date: string };
type Donation = { id: number; donor_id: number; donation_date: string };
type Candidate = { donor: Donor; relatedDonationId: number | null };

const TYPES = ['BIRTHDAY', 'RETURN_REMINDER', 'FREQUENT_DONOR', 'DONATION_THANKS'];

export async function POST(request: Request) {
  const secret = process.env.AUTOMATION_RUN_SECRET;
  if (!secret || request.headers.get('x-hemocax-automation-secret') !== secret) {
    return NextResponse.json({ error: 'Automatización no autorizada.' }, { status: 401 });
  }

  const body = await request.json().catch(() => ({}));
  const type = String(body?.type || '');
  if (!TYPES.includes(type)) return NextResponse.json({ error: 'Tipo de automatización no válido.' }, { status: 400 });

  const service = createServiceRoleClient();

  // Solo salen mensajes automáticos con texto aprobado por la Jefatura.
  const { data: template } = await service.from('message_templates').select('subject,body,approved').eq('type', type).single();
  if (!template || !template.approved) {
    return NextResponse.json({ type, eligible: 0, skipped: 'La plantilla de este mensaje no está aprobada.' });
  }

  const today = limaToday();
  const params = await loadParams(service);

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
  const byDonor = new Map<number, Donation[]>();
  for (const d of donations) byDonor.set(d.donor_id, [...(byDonor.get(d.donor_id) || []), d]);

  const eligibility = (donor: Donor) => {
    const list = byDonor.get(donor.id) || [];
    return {
      list,
      result: computeEligibility({ gender: donor.gender, active: true, donationDates: list.map((x) => x.donation_date), params, today }),
    };
  };

  let candidates: Candidate[] = [];
  if (type === 'BIRTHDAY') {
    candidates = donors.filter((d) => d.birth_date.slice(5) === today.slice(5)).map((donor) => ({ donor, relatedDonationId: null }));
  } else if (type === 'RETURN_REMINDER') {
    for (const donor of donors) {
      const { list, result } = eligibility(donor);
      if (!list.length || result.state !== 'APTO') continue; // sin donaciones previas no hay a qué "volver"
      const last = list.reduce((a, b) => (b.donation_date > a.donation_date ? b : a));
      candidates.push({ donor, relatedDonationId: last.id });
    }
  } else if (type === 'FREQUENT_DONOR') {
    candidates = donors.filter((d) => eligibility(d).result.state === 'MAXIMO').map((donor) => ({ donor, relatedDonationId: null }));
  } else if (type === 'DONATION_THANKS') {
    for (const donation of donations) {
      const age = daysBetween(donation.donation_date, today);
      const donor = donors.find((d) => d.id === donation.donor_id);
      if (donor && age >= 0 && age <= 7) candidates.push({ donor, relatedDonationId: donation.id });
    }
  }

  // Si el envío está simulado no se registra nada: una fila simulada bloquearía el envío real de ese año.
  if (body?.dry_run === true || isSimulated()) {
    return NextResponse.json({ type, eligible: candidates.length, donors: candidates.map((c) => c.donor) });
  }

  const created: unknown[] = [];
  for (const { donor, relatedDonationId } of candidates) {
    const message = template.body.replaceAll('{{nombre}}', donor.first_name);
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
        created_by_name: 'Sistema (automático)',
      })
      .select('*')
      .single();
    if (insertError || !row) continue; // 23505: ya se envió este tipo para este donante/periodo
    const result = await deliverCommunication(service, { ...row, subject: template.subject });
    created.push({ ...row, status: result.status });
  }

  await service.from('audit_logs').insert({ action: 'AUTOMATION_RUN', entity: 'automation', actor_dni: 'SISTEMA', detail: { type, count: created.length } });

  return NextResponse.json({ type, count: created.length, communications: created }, { status: 202 });
}
