import nodemailer from 'nodemailer';

const SUBJECTS: Record<string, string> = {
  BIRTHDAY: '¡Feliz cumpleaños de parte de HEMOCAX!',
  RETURN_REMINDER: 'Ya puedes volver a donar sangre',
  DONATION_THANKS: 'Gracias por tu donación de sangre',
  FREQUENT_DONOR: 'Reconocimiento a tu compromiso como donante',
  CAMPAIGN: 'Campaña del Banco de Sangre HRDC',
  MANUAL: 'Mensaje del Banco de Sangre HRDC',
  RESULT: 'Tienes un resultado disponible en tu portal HEMOCAX',
};

export type MailResult = { status: 'SENT' | 'FAILED' | 'DEMO_QUEUED'; externalId?: string; error?: string };

/** Solo se envía de verdad si AUTOMATION_DRY_RUN=false; cualquier otro valor simula el envío. */
export const isSimulated = () => process.env.AUTOMATION_DRY_RUN !== 'false';

export async function sendEmail({ to, type, message }: { to: string; type: string; message: string }): Promise<MailResult> {
  if (isSimulated()) return { status: 'DEMO_QUEUED' };

  const host = process.env.SMTP_HOST;
  const user = process.env.SMTP_USERNAME;
  const pass = process.env.SMTP_PASSWORD;
  const address = process.env.EMAIL_FROM_ADDRESS || user;
  if (!host || !user || !pass || !address) {
    return { status: 'FAILED', error: 'Falta configurar el servidor de correo (SMTP) en las variables de entorno.' };
  }

  const port = Number(process.env.SMTP_PORT || 587);
  const transport = nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    requireTLS: port !== 465 && process.env.SMTP_USE_TLS !== 'false',
    auth: { user, pass },
    connectionTimeout: 15_000,
    greetingTimeout: 15_000,
    socketTimeout: 20_000,
  });

  try {
    const info = await transport.sendMail({
      from: { name: process.env.EMAIL_FROM_NAME || 'HEMOCAX', address },
      to,
      subject: SUBJECTS[type] ?? SUBJECTS.MANUAL,
      text: message,
    });
    return { status: 'SENT', externalId: info.messageId };
  } catch (e) {
    return { status: 'FAILED', error: (e instanceof Error ? e.message : String(e)).slice(0, 500) };
  }
}
