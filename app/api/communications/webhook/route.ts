import { NextResponse } from 'next/server';
import { createServiceRoleClient } from '@/lib/supabase/server';

/** Callback que invoca automations/worker.py después de intentar enviar un correo. */
export async function POST(request: Request) {
  const secret = process.env.AUTOMATION_WEBHOOK_SECRET;
  if (!secret || request.headers.get('x-hemocax-webhook-secret') !== secret) {
    return NextResponse.json({ error: 'Webhook no autorizado.' }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const communicationId = Number(body?.communication_id);
  if (!communicationId) return NextResponse.json({ error: 'Falta communication_id.' }, { status: 400 });
  const status = String(body?.status || 'SENT');
  const externalId = body?.external_id ?? null;
  const errorMessage = body?.error_message ?? null;

  const service = createServiceRoleClient();
  const { data: comm, error: fetchError } = await service
    .from('communications')
    .select('id,result_id,sent_at')
    .eq('id', communicationId)
    .single();
  if (fetchError || !comm) return NextResponse.json({ error: 'Comunicación no encontrada.' }, { status: 404 });

  const sentAt = ['SENT', 'DELIVERED', 'READ'].includes(status) ? comm.sent_at || new Date().toISOString() : comm.sent_at;
  await service.from('communications').update({ status, external_id: externalId, error_message: errorMessage, sent_at: sentAt }).eq('id', communicationId);

  if (comm.result_id && ['SENT', 'DELIVERED'].includes(status)) {
    const { data: result } = await service.from('donation_results').select('id,status').eq('id', comm.result_id).single();
    if (result && result.status === 'AVAILABLE') {
      await service.from('donation_results').update({ status: 'NOTIFIED', notified_at: new Date().toISOString() }).eq('id', comm.result_id);
    }
  }

  await service.from('campaign_recipients').update({ status }).eq('communication_id', communicationId);
  await service.from('audit_logs').insert({ action: 'EMAIL_STATUS_UPDATED', entity: 'communication', entity_id: communicationId, actor_dni: 'PYTHON', detail: { status } });

  return NextResponse.json({ received: true, communication_id: communicationId, status });
}
