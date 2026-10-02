'use client';

import { ReactNode } from 'react';
import { PageHeader, Profile, roleTitle } from './ui';

type Guide = { title: string; steps: string[]; note?: string };

const NURSE: Guide[] = [
  { title: 'Atender a un donante que llega', steps: [
    'En Inicio, escribe el DNI del donante en el buscador grande y pulsa su nombre.',
    'Se abre su ficha: mira si dice «Sí, está apto». Si dice «Todavía no», indica desde qué fecha podrá donar.',
    'Si es apto, pulsa «Registrar donación» y confirma la fecha (por defecto es hoy).',
    'Listo: el resultado queda pendiente para que lo revise el médico.',
  ] },
  { title: 'Registrar a un donante nuevo', steps: [
    'En Inicio, escribe su DNI. Si no existe, aparece el botón «Registrar donante nuevo».',
    'Completa nombres, apellidos, fecha de nacimiento, sexo, teléfono y, si lo sabe, su grupo sanguíneo (si no, deja «No sé»).',
    'Pídele su correo electrónico: sin correo no podemos avisarle de sus resultados.',
    'Si acepta recibir correos, marca la casilla al final. Solo márcala si él mismo te lo confirmó.',
  ] },
  { title: 'Registrar que el donante aceptó recibir correos', steps: [
    'Abre su ficha y pulsa «Registrar su autorización de correos».',
    'Léele el texto que aparece en pantalla.',
    'Si acepta, marca la casilla de confirmación y pulsa «Autorizar correos».',
    'Si más adelante pide dejar de recibirlos, abre la misma opción y pulsa «Quitar autorización».',
  ] },
  { title: 'Un donante todavía no puede donar, ¿qué hago?', steps: [
    'La ficha indica desde qué fecha cumple el intervalo entre donaciones, o si llegó al máximo del año.',
    'Si el médico responsable autoriza una excepción, al registrar la donación aparece una casilla «lo autorizó el médico»: márcala solo en ese caso.',
  ] },
];

const DOCTOR: Guide[] = [
  { title: 'Revisar y liberar un resultado', steps: [
    'Entra a Resultados: arriba están los pendientes, los más antiguos primero. La meta es liberarlos en 48 horas.',
    'Pulsa «Liberar resultado», revisa el mensaje para el donante y marca que lo revisaste y que no es crítico.',
    'Después pulsa «Avisar por correo» para que el donante sepa que ya puede verlo en su portal.',
  ], note: 'El donante verá en su portal el mensaje, las recomendaciones generales y la fecha en que podrá volver a donar.' },
  { title: 'Resultado reactivo o dudoso (crítico)', steps: [
    'En Resultados, pulsa «Marcar como crítico» y confirma.',
    'Un resultado crítico nunca se muestra en el portal ni se avisa por correo.',
    'Comunícate con el donante por teléfono o cita presencial, según el procedimiento vigente del Banco de Sangre.',
    'Si se marcó por error, «Quitar marca de crítico» lo devuelve a pendiente.',
  ] },
];

const ADMIN: Guide[] = [
  { title: 'Crear la cuenta de una persona', steps: [
    'Ve a Cuentas de acceso → «+ Crear cuenta».',
    'Elige el puesto: enfermería, médico responsable (puede liberar resultados), administrador o donante.',
    'Para un donante, elígelo de la lista. Para el personal, escribe su DNI y nombre.',
    'Copia los datos que aparecen al final y entrégaselos: la contraseña solo se muestra una vez. Debe cambiarla en «Mi cuenta».',
  ] },
  { title: 'Si alguien olvidó su contraseña', steps: ['En Cuentas de acceso, pulsa «Nueva contraseña» en su fila y entrégale la nueva.'] },
  { title: 'Aprobar los mensajes automáticos', steps: [
    'Ve a Parámetros → Mensajes automáticos.',
    'Lee cada texto (cumpleaños, recordatorio, agradecimiento, reconocimiento) y pulsa «Aprobar mensaje».',
    'Solo los mensajes aprobados se envían solos. Si editas uno, vuelve a quedar sin aprobar.',
  ] },
  { title: 'Cambiar las reglas de donación', steps: ['En Parámetros → Reglas de donación puedes ajustar el intervalo entre donaciones (por sexo) y el máximo anual. Confírmalo antes con el médico responsable.'] },
  { title: 'Atender los derechos del donante', steps: [
    'Abre su ficha → «Datos y privacidad».',
    '«Descargar archivo» entrega una copia de sus datos; «Dar de baja» deja de enviarle mensajes.',
    '«Eliminar datos personales» borra su identidad (no se puede deshacer).',
  ] },
  { title: 'Ver cifras para la Jefatura', steps: ['En Reportes están los indicadores del proyecto y la reserva por grupo sanguíneo. Los botones de abajo descargan los datos en Excel.'] },
];

const GLOSSARY: [string, string][] = [
  ['Apto / Puede donar', 'Ya pasó el tiempo mínimo desde su última donación y no llegó al máximo de donaciones del año.'],
  ['Intervalo', 'Días que deben pasar entre una donación y la siguiente.'],
  ['Máximo anual', 'Cuántas donaciones de sangre total se permiten en un año calendario.'],
  ['Consentimiento', 'La aceptación del donante para que el Banco de Sangre le escriba por correo. Puede retirarla cuando quiera.'],
  ['Resultado crítico', 'Resultado reactivo o dudoso: nunca se comunica por el portal ni por correo, solo por teléfono o consulta.'],
  ['Campaña', 'Un mensaje que se envía a varios donantes a la vez, por ejemplo cuando se necesita un grupo sanguíneo.'],
];

function Section({ title, children, open }: { title: string; children: ReactNode; open?: boolean }) {
  return <details className="help-section" open={open}><summary>{title}</summary>{children}</details>;
}

function GuideList({ guides }: { guides: Guide[] }) {
  return (
    <>
      {guides.map((g) => (
        <div className="guide" key={g.title}>
          <h4>{g.title}</h4>
          <ol>{g.steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
          {g.note && <p className="notice-box">{g.note}</p>}
        </div>
      ))}
    </>
  );
}

export default function HelpTab({ profile }: { profile: Profile }) {
  const isAdmin = profile.role === 'ADMIN';
  const isDoctor = profile.can_release_results || isAdmin;
  return (
    <>
      <PageHeader
        title="Ayuda"
        help={`Guía paso a paso para tu puesto (${roleTitle(profile)}). Toca un tema para abrirlo.`}
        action={<button className="secondary" onClick={() => window.print()}>Imprimir esta guía</button>}
      />
      <Section title="Atención de donantes (enfermería y personal de apoyo)" open={!isDoctor || !isAdmin}><GuideList guides={NURSE} /></Section>
      {isDoctor && <Section title="Resultados (médico responsable)" open><GuideList guides={DOCTOR} /></Section>}
      {isAdmin && <Section title="Administración"><GuideList guides={ADMIN} /></Section>}
      <Section title="Glosario: qué significa cada palabra">
        <dl className="glossary">{GLOSSARY.map(([t, d]) => <div key={t}><dt>{t}</dt><dd>{d}</dd></div>)}</dl>
      </Section>
    </>
  );
}
