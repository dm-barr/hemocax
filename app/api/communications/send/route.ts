import { NextResponse } from 'next/server';
import { bearerToken, createServiceRoleClient, createUserScopedClient } from '@/lib/supabase/server';

async function dispatchToWorker(payload: {
  communication_id: number; donor_id: number; email: string; recipient_name: string; message: string; type: string;
}) {
  const url = process.env.AUTOMATION_WEBHOOK_URL;
  const secret = process.env.AUTOMATION_WEBHOOK_SECRET || '';
  if (!url) return { dispatched: false as const };
  try {
    const response = await fetch(`${url.replace(/\/$/, '')}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-hemocax-webhook-secret': secret },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`El servicio de correo respondió HTTP ${response.status}`);
    return { dispatched: true as const };
  } catch (e) {
    return { dispatched: true as const, error: e instanceof Error ? e.message : 'Error desconocido' };
  }
}

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

  const { dispatched, error: dispatchError } = await dispatchToWorker({
    communication_id: row.id,
    donor_id: donor.id,
    email: donor.email,
    recipient_name: donor.first_name,
    message,
    type,
  });
  if (!dispatched) {
    await caller.from('communications').update({ status: 'DEMO_QUEUED' }).eq('id', row.id);
    row.status = 'DEMO_QUEUED';
  } else if (dispatchError) {
    await caller.from('communications').update({ status: 'FAILED', error_message: dispatchError }).eq('id', row.id);
    row.status = 'FAILED';
    row.error_message = dispatchError;
  }

  const service = createServiceRoleClient();
  await service.from('audit_logs').insert({
    actor_id: callerUser.user.id,
    action: 'COMMUNICATION_CREATED',
    entity: 'communication',
    entity_id: row.id,
    detail: { type, donor_id: donorId },
  });

  return NextResponse.json(row, { status: 201 });
}
