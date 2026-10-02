import { NextResponse } from 'next/server';
import { deliverCommunication } from '@/lib/communications';
import { bearerToken, createServiceRoleClient, createUserScopedClient } from '@/lib/supabase/server';

export const maxDuration = 60;

export async function POST(request: Request) {
  let token: string;
  try {
    token = bearerToken(request);
  } catch (e) {
    return NextResponse.json({ error: e instanceof Error ? e.message : 'No autorizado' }, { status: 401 });
  }

  const caller = createUserScopedClient(token);
  const { data: callerUser } = await caller.auth.getUser();
  if (!callerUser.user) return NextResponse.json({ error: 'Sesión inválida.' }, { status: 401 });

  const body = await request.json().catch(() => ({}));
  const donorId = Number(body.donor_id);
  const type = String(body.type || 'MANUAL');
  const message = String(body.message || '').trim();
  const resultId = body.result_id ? Number(body.result_id) : null;
  const campaignId = body.campaign_id ? Number(body.campaign_id) : null;
  if (!donorId || !message) return NextResponse.json({ error: 'Falta el donante o el mensaje.' }, { status: 400 });

  const { data: donor, error: donorError } = await caller
    .from('donors')
    .select('id,email,first_name,status,consent_email,opted_out')
    .eq('id', donorId)
    .single();
  if (donorError || !donor) return NextResponse.json({ error: 'Donante no encontrado.' }, { status: 404 });
  if (donor.status !== 'ACTIVE' || !donor.consent_email || donor.opted_out || !donor.email) {
    return NextResponse.json({ error: 'No se puede contactar: falta consentimiento vigente de correo o el donante no tiene correo registrado.' }, { status: 403 });
  }

  const { data: row, error: insertError } = await caller
    .from('communications')
    .insert({
      donor_id: donorId,
      result_id: resultId,
      campaign_id: campaignId,
      type,
      channel: 'EMAIL',
      email: donor.email,
      message,
      status: 'PENDING',
      created_by: callerUser.user.id,
    })
    .select('*')
    .single();
  if (insertError || !row) return NextResponse.json({ error: insertError?.message || 'No se pudo registrar la comunicación.' }, { status: 500 });

  const service = createServiceRoleClient();
  const result = await deliverCommunication(service, row);

  await service.from('audit_logs').insert({
    actor_id: callerUser.user.id,
    action: 'COMMUNICATION_CREATED',
    entity: 'communication',
    entity_id: row.id,
    detail: { type, donor_id: donorId, status: result.status },
  });

  return NextResponse.json({ ...row, status: result.status, error_message: result.error ?? null }, { status: 201 });
}
