type Config = { subject: string; eyebrow: string; heading: string; preheader: string; cta?: string };

const CONFIG: Record<string, Config> = {
  BIRTHDAY: { subject: '¡Feliz cumpleaños de parte de HEMOCAX!', eyebrow: 'Cumpleaños', heading: '¡Feliz cumpleaños!', preheader: 'Te deseamos un excelente día.' },
  RETURN_REMINDER: { subject: 'Ya puedes volver a donar sangre', eyebrow: 'Recordatorio', heading: 'Ya puedes volver a donar', preheader: 'Tu próxima donación puede salvar vidas.', cta: 'Entrar a mi portal' },
  DONATION_THANKS: { subject: 'Gracias por tu donación de sangre', eyebrow: 'Gracias', heading: 'Gracias por donar sangre', preheader: 'Tu donación voluntaria ayuda a muchas personas.' },
  FREQUENT_DONOR: { subject: 'Reconocimiento a tu compromiso como donante', eyebrow: 'Reconocimiento', heading: 'Gracias por tu compromiso', preheader: 'Tu constancia como donante es muy valiosa.' },
  CAMPAIGN: { subject: 'Campaña del Banco de Sangre HRDC', eyebrow: 'Campaña', heading: 'El Banco de Sangre te necesita', preheader: 'Tu ayuda puede salvar vidas.' },
  MANUAL: { subject: 'Mensaje del Banco de Sangre HRDC', eyebrow: 'Mensaje', heading: 'Mensaje del Banco de Sangre', preheader: 'Tienes un mensaje del Banco de Sangre HRDC.' },
  RESULT: { subject: 'Tienes un resultado disponible en tu portal HEMOCAX', eyebrow: 'Resultado disponible', heading: 'Tu resultado está listo', preheader: 'Entra a tu portal con tu DNI para verlo.', cta: 'Ver mi resultado' },
};

const RED = '#d94e68';
const INK = '#1e293b';
const MUTED = '#7d8999';
const FONT = "'DM Sans',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif";

const escapeHtml = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function linkify(escaped: string): string {
  return escaped.replace(/https?:\/\/[^\s<]+/g, (match) => {
    const url = match.replace(/[.,;:!?)]+$/, '');
    const rest = match.slice(url.length);
    return `<a href="${url}" style="color:${RED};text-decoration:underline;">${url}</a>${rest}`;
  });
}

export function renderEmail({ type, message, siteUrl, subject }: { type: string; message: string; siteUrl: string; subject?: string }) {
  const c = CONFIG[type] ?? CONFIG.MANUAL;
  const paragraphs = message.split(/\n+/).map((p) => p.trim()).filter(Boolean);

  const body = paragraphs
    .map((p) => `<p style="margin:0 0 16px;font-size:16px;line-height:1.65;color:${INK};">${linkify(escapeHtml(p))}</p>`)
    .join('');

  const button = c.cta
    ? `<table role="presentation" cellpadding="0" cellspacing="0" style="margin:8px 0 6px;"><tr><td style="background:${RED};border-radius:10px;">
         <a href="${siteUrl}" style="display:inline-block;padding:14px 28px;font-family:${FONT};font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;">${escapeHtml(c.cta)}</a>
       </td></tr></table>`
    : '';

  const footerText = `Recibes este correo porque autorizaste recibir mensajes del Banco de Sangre del HRDC. Si ya no quieres recibirlos, entra a tu portal (${siteUrl}) y desactiva «Mensajes por correo», o pídelo al personal del Banco de Sangre.`;

  const html = `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>${escapeHtml(c.subject)}</title></head>
<body style="margin:0;padding:0;background:#f6f8fb;font-family:${FONT};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#f6f8fb;">${escapeHtml(c.preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f8fb;"><tr><td align="center" style="padding:28px 12px;">
  <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="width:100%;max-width:560px;">
    <tr><td style="padding:0 4px 18px;">
      <table role="presentation" cellpadding="0" cellspacing="0"><tr>
        <td width="34" height="34" align="center" style="background:${RED};border-radius:9px;color:#ffffff;font-family:${FONT};font-size:17px;font-weight:800;">H</td>
        <td style="padding-left:10px;font-family:${FONT};font-size:19px;font-weight:800;letter-spacing:-0.5px;color:${INK};">HEMO<span style="color:${RED};">CAX</span></td>
      </tr></table>
    </td></tr>
    <tr><td style="background:#ffffff;border:1px solid #e9edf2;border-top:4px solid ${RED};border-radius:14px;padding:32px 32px 26px;font-family:${FONT};">
      <p style="margin:0 0 10px;font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:${RED};">${escapeHtml(c.eyebrow)}</p>
      <h1 style="margin:0 0 20px;font-size:26px;line-height:1.25;font-weight:800;letter-spacing:-0.6px;color:${INK};">${escapeHtml(c.heading)}</h1>
      ${body}
      ${button}
    </td></tr>
    <tr><td style="padding:22px 8px 0;font-family:${FONT};text-align:center;">
      <p style="margin:0 0 6px;font-size:13px;font-weight:700;color:${INK};">Banco de Sangre · HRDC</p>
      <p style="margin:0;font-size:12px;line-height:1.6;color:${MUTED};">${escapeHtml(footerText)}</p>
    </td></tr>
  </table>
</td></tr></table>
</body></html>`;

  const text = [c.heading, '', ...paragraphs, ...(c.cta ? ['', `${c.cta}: ${siteUrl}`] : []), '', '—', 'Banco de Sangre · HRDC', footerText].join('\n');

  return { subject: subject || c.subject, html, text };
}
