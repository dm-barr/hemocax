import { SupabaseClient } from '@supabase/supabase-js';
import { MailResult, sendEmail } from './email';

type Comm = { id: number; email: string; type: string; message: string; result_id: number | null; subject?: string };

/** Envía el correo de una comunicación ya registrada y guarda el resultado del envío. Usar con el cliente de servicio. */
export async function deliverCommunication(service: SupabaseClient, comm: Comm): Promise<MailResult> {
  const result = await sendEmail({ to: comm.email, type: comm.type, message: comm.message, subject: comm.subject });

  await service.from('communications').update({
    status: result.status,
    external_id: result.externalId ?? null,
    error_message: result.error ?? null,
    sent_at: result.status === 'SENT' ? new Date().toISOString() : null,
  }).eq('id', comm.id);

  if (result.status === 'SENT' && comm.result_id) {
    await service.from('donation_results')
      .update({ status: 'NOTIFIED', notified_at: new Date().toISOString() })
      .eq('id', comm.result_id)
      .eq('status', 'AVAILABLE');
  }
  return result;
}
