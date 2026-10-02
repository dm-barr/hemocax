import nodemailer from 'nodemailer';
import { renderEmail } from './emailTemplate';

export type MailResult = { status: 'SENT' | 'FAILED' | 'DEMO_QUEUED'; externalId?: string; error?: string };

/** Solo se envía de verdad si AUTOMATION_DRY_RUN=false; cualquier otro valor simula el envío. */
export const isSimulated = () => process.env.AUTOMATION_DRY_RUN !== 'false';

function siteUrl(): string {
  if (process.env.NEXT_PUBLIC_SITE_URL) return process.env.NEXT_PUBLIC_SITE_URL.replace(/\/$/, '');
  if (process.env.VERCEL_PROJECT_PRODUCTION_URL) return `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`;
  return 'https://hemocax.vercel.app';
}

export async function sendEmail({ to, type, message, subject }: { to: string; type: string; message: string; subject?: string }): Promise<MailResult> {
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
    const mail = renderEmail({ type, message, siteUrl: siteUrl(), subject });
    const info = await transport.sendMail({
      from: { name: process.env.EMAIL_FROM_NAME || 'HEMOCAX', address },
      to,
      subject: mail.subject,
      html: mail.html,
      text: mail.text,
    });
    return { status: 'SENT', externalId: info.messageId };
  } catch (e) {
    return { status: 'FAILED', error: (e instanceof Error ? e.message : String(e)).slice(0, 500) };
  }
}
