# -*- coding: utf-8 -*-
"""Informe técnico — servicios del servidor, cliente web y algoritmos."""
import docx_utils as U

FIG = "fig/"


def servidor(doc):
    U.h1(doc, "8. Servicios del servidor")
    U.h2(doc, "8.1 Patrón común de las rutas")
    U.parrafo(doc, "Las rutas viven en `app/api/**/route.ts` (Route Handlers de Next.js, ejecutadas como funciones sin estado). Comparten tres piezas de `lib/supabase/server.ts` y `lib/adminGuard.ts`:", alineacion="justificado")
    U.tabla(doc, ["Pieza", "Qué hace"], [
        ["bearerToken(request)", "Extrae el JWT de `Authorization: Bearer …`; lanza error si falta (→ 401)."],
        ["createUserScopedClient(token)", "Cliente de supabase-js con la clave pública y el JWT del usuario: **las políticas RLS siguen aplicando**. Se usa para validar al llamante y para operar «como él»."],
        ["createServiceRoleClient()", "Cliente con la clave de servicio: omite RLS. Solo se crea dentro de la ruta y nunca sale al navegador."],
        ["requireAdmin(request)", "Valida el JWT (`auth.getUser()`), consulta `rpc('current_role')` y exige ADMIN (→ 401 o 403). Devuelve el cliente del usuario, el de servicio y el usuario."],
    ], anchos=[4.6, 12.0], tam=8.5, primera_negrita=True, titulo="Utilidades del servidor")
    U.codigo(doc, """export async function POST(request: Request) {
  const guard = await requireAdmin(request);            // 401 sin sesión · 403 si no es ADMIN
  if ('error' in guard) return guard.error;
  const { caller, service } = guard;
  ...
  const { error } = await caller.rpc('anonymize_donor', { p_donor_id: donorId });  // RLS/funciones deciden
  if (donor.auth_user_id) await service.auth.admin.deleteUser(donor.auth_user_id); // solo service_role puede
}""", titulo="Patrón de una ruta de administración (anonymize)")
    U.h2(doc, "8.2 Contratos de las rutas")
    U.tabla(doc, ["Ruta", "Autenticación", "Cuerpo (JSON)", "Respuestas"], [
        ["POST /api/admin/users", "Bearer · ADMIN", "dni (8 dígitos), full_name, role (ADMIN/STAFF/DONOR), password (≥ 12), can_release_results?, donor_id (si DONOR)", "201 {user_id, …} · 400 validación · 401 · 403 · 409 DNI ya registrado o donante ya vinculado"],
        ["POST /api/admin/users/manage", "Bearer · ADMIN", "user_id, action: reset_password | set_active (active) | set_release (value)", "200 {password} o {ok:true} · 400 (p. ej. desactivarse a sí mismo o al último ADMIN) · 404"],
        ["POST /api/admin/donors/anonymize", "Bearer · ADMIN", "donor_id", "200 {ok:true} · 400 · 404 · 500"],
        ["POST /api/communications/send", "Bearer · personal (RLS en communications)", "donor_id, message, type (MANUAL por defecto), result_id?, campaign_id?", "201 {…, status} · 400 · 401 · 403 sin consentimiento o sin correo · 404"],
        ["POST /api/automations/run", "Cabecera x-hemocax-automation-secret", "type ∈ BIRTHDAY | RETURN_REMINDER | FREQUENT_DONOR | DONATION_THANKS; dry_run?", "202 {count} · 200 {eligible, donors} (simulación) o {skipped} · 400 · 401"],
        ["POST /api/communications/webhook", "Cabecera x-hemocax-webhook-secret", "communication_id, status, external_id?, error_message?", "200 · 400 · 401 · 404 (camino heredado)"],
    ], anchos=[3.8, 3.2, 5.6, 4.0], tam=7.8, titulo="Referencia de rutas")
    U.h3(doc, "Creación de cuenta con reversión (POST /api/admin/users)")
    U.numerada(doc, [
        "Valida sesión y rol de administrador y los campos del cuerpo.",
        "`auth.admin.createUser({ email, password, email_confirm: true, user_metadata })`; un 422 o «already registered» devuelve 409.",
        "Inserta la fila en `profiles`; si falla, **elimina el usuario de Auth** (reversión) y devuelve 409.",
        "Si el rol es DONOR, vincula `donors.auth_user_id` solo si estaba nulo (`.is('auth_user_id', null)`); si falla, elimina perfil y usuario (reversión).",
        "Registra `USER_CREATED` en la bitácora y responde 201.",
    ])
    U.h2(doc, "8.3 Envío de correo")
    U.tabla(doc, ["Aspecto", "Implementación"], [
        ["Modo seguro", "`isSimulated = process.env.AUTOMATION_DRY_RUN !== 'false'`. Solo el valor exacto `false` envía; cualquier otro (o ausencia) devuelve DEMO_QUEUED sin conectarse."],
        ["Transporte", "nodemailer con `host`, `port` (587 por defecto), `secure = (port === 465)`, `requireTLS = port !== 465 && SMTP_USE_TLS !== 'false'`; autenticación con usuario y contraseña de aplicación."],
        ["Tiempos de espera", "connectionTimeout 15 s · greetingTimeout 15 s · socketTimeout 20 s (la función admite hasta 60 s: `maxDuration`)."],
        ["Contenido", "`renderEmail` genera asunto, HTML (tablas y estilos en línea para compatibilidad con clientes de correo) y una alternativa de texto plano; botón al portal en los tipos RETURN_REMINDER y RESULT."],
        ["Seguridad del HTML", "`escapeHtml` sobre todo texto dinámico; `linkify` convierte solo URLs `http(s)` ya escapadas; pie con la forma de darse de baja."],
        ["Resultado", "`MailResult { status: SENT | FAILED | DEMO_QUEUED, externalId?, error? }` (mensaje de error truncado a 500 caracteres)."],
        ["Persistencia del estado", "`deliverCommunication` actualiza `communications` (status, external_id, error_message, sent_at) y, si hay `result_id` y el envío fue SENT, pasa el resultado de AVAILABLE a NOTIFIED."],
    ], anchos=[3.4, 13.2], tam=8.5, primera_negrita=True, titulo="Módulo de correo (lib/email.ts, lib/emailTemplate.ts, lib/communications.ts)")
    U.figura(doc, FIG + "seq_resultado.png", 16.0, "Secuencia: liberar un resultado y avisar por correo")
    U.h2(doc, "8.4 Automatizaciones (POST /api/automations/run)")
    U.codigo(doc, """1. verificar secreto            → 401 si no coincide con AUTOMATION_RUN_SECRET
2. plantilla = message_templates[type]
   si no existe o approved = false → responder { eligible:0, skipped }      // compuerta de aprobación
3. params   = loadParams(service)              // límites e intervalos desde system_config
4. donantes = ACTIVE ∧ consent_email ∧ ¬opted_out ∧ email no nulo
5. donaciones = WHOLE_BLOOD de esos donantes   // una sola consulta; se agrupa en memoria
6. candidatos según type:
     BIRTHDAY        → mes y día de birth_date = hoy (Lima)
     RETURN_REMINDER → ≥ 1 donación ∧ computeEligibility = APTO      (referencia: última donación)
     FREQUENT_DONOR  → computeEligibility = MAXIMO
     DONATION_THANKS → donación con 0 ≤ antigüedad ≤ 7 días          (referencia: esa donación)
7. si dry_run ∨ simulado → responder { eligible, donors } sin escribir nada
8. por cada candidato (secuencial):
     INSERT communications (PENDING, created_by_name='Sistema (automático)')
        – si falla (23505 unique_violation) → omitir: ya se envió este tipo para ese periodo
     deliverCommunication → SMTP → SENT/FAILED
9. INSERT audit_logs AUTOMATION_RUN; responder 202 { count }""", titulo="Algoritmo de la ejecución")
    U.figura(doc, FIG + "seq_automatizacion.png", 16.0, "Secuencia de una ejecución diaria")
    U.tabla(doc, ["Propiedad", "Valor / análisis"], [
        ["Costo de cálculo", "O(D + N): D donantes elegibles y N donaciones; una consulta por tabla y agrupación en un Map."],
        ["Idempotencia", "Garantizada por los índices únicos (sec. 7.5); una segunda ejecución produce count = 0 para los ya enviados."],
        ["Límite de tiempo", "`maxDuration = 60` s; el envío secuencial limita la cantidad por ejecución (≈ cientos con Gmail). Una ejecución cortada se reintenta al día siguiente (H-08)."],
        ["Zona horaria", "`limaToday()` = fecha UTC − 5 h; se evita depender de la zona del servidor."],
        ["Trazabilidad", "Cada mensaje queda con su tipo, estado, error y responsable «Sistema (automático)»."],
    ], anchos=[3.6, 13.0], tam=8.5, primera_negrita=True, titulo="Propiedades")
    U.h2(doc, "8.5 Reloj de recordatorios (automations/worker.py)")
    U.parrafo(doc, "Proceso de Python 3.12 (solo biblioteca estándar) empaquetado en Docker. Cumple dos funciones: **planificador** y **servidor HTTP mínimo** (`ThreadingHTTPServer`, puerto `PORT` o 8787).", alineacion="justificado")
    U.tabla(doc, ["Elemento", "Detalle"], [
        ["Calendario", "SCHEDULE = BIRTHDAY 08:00 · RETURN_REMINDER 08:15 · DONATION_THANKS 08:30 · FREQUENT_DONOR 08:45 (hora America/Lima)."],
        ["Bucle", "Cada minuto (alineado al segundo 0) compara `HH:MM` local con el calendario; un conjunto `completed` evita repetir la tarea del día; se limpia al cambiar de día."],
        ["Zona horaria", "`zoneinfo` con respaldo a UTC−5 fijo si la base de zonas no está disponible (Perú no usa horario de verano)."],
        ["Llamada", "POST a `{HEMOCAX_API_URL}/api/automations/run` con `x-hemocax-automation-secret`; `dry_run` según `AUTOMATION_DRY_RUN`."],
        ["Fallos", "Si la llamada falla, se registra la excepción y **no** se marca como completada: se reintenta en el siguiente minuto hasta tener éxito."],
        ["Interruptor", "`AUTOMATIONS_ENABLED` debe ser true; si no, el planificador no ejecuta nada."],
        ["HTTP", "GET /health → {ok, enabled, dry_run}. POST /email (camino heredado, exige AUTOMATION_WEBHOOK_SECRET)."],
        ["Modo manual", "`python worker.py --once BIRTHDAY` ejecuta una vez y muestra el resultado."],
        ["Contenedor", "FROM python:3.12-slim · instala tzdata · COPY worker.py · EXPOSE 8787 · CMD python worker.py."],
    ], anchos=[3.2, 13.4], tam=8.5, primera_negrita=True, titulo="Funcionamiento del reloj")
    U.parrafo(doc, "**Limitación del plan gratuito:** Render duerme el servicio tras 15 minutos sin tráfico; el monitor externo consulta `/health` cada 5 minutos para evitarlo (sec. 11.6).", tam=9.5)
    U.h2(doc, "8.6 Manejo de errores")
    U.tabla(doc, ["Situación", "Tratamiento"], [
        ["Petición sin credencial", "401 con mensaje claro (verificado en las 6 rutas)."],
        ["Rol insuficiente", "403."],
        ["Cuerpo inválido", "400 con el campo que falla, en español."],
        ["Conflicto (duplicado)", "409 (DNI ya registrado, donante ya vinculado)."],
        ["Fallo parcial al crear cuenta", "Reversión de pasos anteriores."],
        ["Fallo de SMTP", "No se lanza error: la comunicación queda FAILED con `error_message`; la respuesta incluye el estado."],
        ["Excepción inesperada", "Respuesta 500 con el mensaje de la capa que falló; el registro queda en los logs de Vercel."],
    ], anchos=[5.0, 11.6], tam=8.5, titulo="Estrategia de errores")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def cliente(doc):
    U.h1(doc, "9. Cliente web")
    U.h2(doc, "9.1 Estructura")
    U.figura(doc, FIG + "arbol_frontend.png", 16.4, "Árbol de módulos del cliente")
    U.h2(doc, "9.2 Arranque, sesión y reparto por rol")
    U.codigo(doc, """// app/page.tsx (extracto)
const StaffPanel  = dynamic(() => import('./staff/StaffPanel'), { ssr: false, loading: () => <p>Cargando…</p> });
const DonorPortal = dynamic(() => import('./DonorPortal'),     { ssr: false, loading: () => <p>Cargando…</p> });

await supabase.auth.signInWithPassword({ email: `dni-${dni}@login.hemocax.org`, password });
const { data: p } = await supabase.from('profiles').select('dni,full_name,role,can_release_results').eq('user_id', auth.user.id).single();
return p.role !== 'DONOR' ? <StaffPanel profile={p} …/> : <DonorPortal profile={p} …/>;""", titulo="Reparto según el rol")
    U.parrafo(doc, "`getBrowserSupabaseClient()` crea **un único cliente por pestaña** (patrón *singleton*) con `persistSession` y `autoRefreshToken`. "
                   "Como ambas pantallas se importan de forma diferida, el navegador del donante nunca descarga el código del panel del personal (sec. 9.11).", alineacion="justificado")
    U.figura(doc, FIG + "seq_login.png", 15.5, "Secuencia de inicio de sesión")
    U.h2(doc, "9.3 Acceso a datos")
    U.viñetas(doc, [
        "**Lecturas con relaciones incrustadas** de PostgREST: `donation_results … donations!inner(donation_date, donors!inner(first_name,last_name))` evita varias consultas.",
        "**Las consultas del donante no filtran por su identidad:** `from('donation_results').select(…)` devuelve solo lo suyo porque lo decide RLS. Es intencional: el filtro de la interfaz no es una medida de seguridad.",
        "**Escrituras** directas (insert/update) con las políticas RLS como autoridad; los errores se traducen con `friendlyError`.",
        "**Operaciones privilegiadas** únicamente a través de `callApi(path, body)`, que lee el `access_token` de la sesión y hace `POST` con `Authorization: Bearer`.",
        "**Límites explícitos:** `limit(50)` en pendientes del inicio, `limit(200)` en resultados y bitácora, hasta 5 000 y 10 000 filas en reportes (el tope real de Supabase es 1 000, H-12).",
    ])
    U.h2(doc, "9.4 Estado y hooks")
    U.tabla(doc, ["Elemento", "Función"], [
        ["useDirectory(notify)", "Carga donantes (ordenados por apellido), donaciones de sangre total y parámetros en paralelo (`Promise.all`); calcula con `useMemo` un `Map<donorId, Eligibility>`; expone `reload()`."],
        ["StaffPanel", "Estado `nav = { tab, intent }`; la función `go(tab, intent)` permite saltar entre pestañas con una intención (p. ej. `new:12345678` abre el alta con el DNI ya escrito)."],
        ["Toasts", "`notify(mensaje, 'ok'|'error')` agrega un aviso con temporizador (5 s / 8 s)."],
        ["Modal", "Pila de modales (uno dentro de otro, p. ej. ficha → registrar donación)."],
    ], anchos=[4.2, 12.4], tam=8.5, primera_negrita=True, titulo="Estado compartido")
    U.h2(doc, "9.5 Pantallas del personal y su lógica")
    U.tabla(doc, ["Pestaña", "Datos que lee/escribe", "Lógica destacada"], [
        ["Inicio (HomeTab)", "donation_results PENDING, message_templates, useDirectory", "Buscador por DNI o nombre sin acentos; alertas a 36 h y 48 h; plantillas sin aprobar."],
        ["Donantes / Ficha", "donors, donations, donation_results, communications, consent_events", "Filtros por grupo, aptos hoy y con correo autorizado; edición; consentimiento; descarga de datos; anonimización (confirmar escribiendo el DNI)."],
        ["Donación (DonationModal)", "INSERT donations", "Calcula el conteo del año y el intervalo; bloquea si se alcanzó el máximo; exige marcar la autorización médica si es antes del intervalo y la deja en `notes`."],
        ["Resultados", "donation_results; RPC liberar / crítico / quitar marca; /api/communications/send", "Muestra horas de espera con colores; avisar solo si hay consentimiento y correo."],
        ["Campañas", "campaigns, campaign_recipients, /api/communications/send", "Vista previa de destinatarios; envío en bucle con barra de progreso; evita repetidos."],
        ["Correos enviados", "communications, donors, /api/communications/send", "Historial con estado, responsable y error; formulario de envío manual."],
        ["Reportes", "donors, donations, donation_results, communications", "Indicadores y reserva por grupo calculados en el cliente; descarga CSV con BOM."],
        ["Cuentas", "profiles, donors, /api/admin/users*", "Generadores de contraseña; restablecer, activar/desactivar, permiso de liberar."],
        ["Parámetros", "system_config, message_templates, consent_versions; RPC publish_consent_version", "Edición de reglas, recomendaciones, contacto y plantillas; aprobación."],
        ["Actividad", "audit_logs (200 más recientes)", "Traduce acciones y nombres de campos a lenguaje claro."],
    ], anchos=[3.4, 5.6, 7.6], tam=8, titulo="Pantallas del personal")
    U.h2(doc, "9.6 Estilos")
    U.parrafo(doc, "Dos hojas de CSS plano (`portal.css` ≈ 233 líneas y `donor.css` ≈ 121) con variables CSS para el color y las tipografías (`--font`, `--font-head`). El portal del donante usa un diseño de una columna en celular y dos en escritorio mediante `grid` y consultas de medios; "
                   "los íconos son SVG en línea (`donorIcons.tsx`), sin librerías de íconos ni imágenes externas.", alineacion="justificado")
    U.salto_pagina(doc)

    U.h2(doc, "9.7 Importación desde CSV")
    U.tabla(doc, ["Paso", "Descripción"], [
        ["Lectura", "`File.text()`; se descarta el BOM inicial."],
        ["Delimitador", "Se detecta contando `;` y `,` en la primera línea (Excel en español usa `;`)."],
        ["Parser", "Máquina de estados de un carácter: dentro/fuera de comillas, `\"\"` como comilla literal, `\\n`/`\\r\\n` como fin de fila; las filas vacías se ignoran."],
        ["Encabezados", "Se normalizan (sin acentos, minúsculas, no alfanuméricos → `_`) y se asocian por alias (`nombres`/`nombre`, `sexo`/`genero`, `correo`/`email`, `grupo_sanguineo`/`sangre`…)."],
        ["Validación por fila", "DNI de 8 dígitos y no repetido en el archivo; nombre y apellido; sexo (M/F/hombre/mujer…); fecha `AAAA-MM-DD` o `DD/MM/AAAA` real, ≥ 1900 y no futura; teléfono ≥ 7 dígitos; correo con formato; grupo `O|A|B|AB` + `+|-` o vacío / «No sé»."],
        ["Resultado", "`{ valid:[{line,row}], errors:[{line,message}] }`; la línea es la del archivo (índice + 2)."],
        ["Inserción", "Una a una (`insert`) para informar el motivo exacto de cada fila rechazada (p. ej. DNI duplicado en la base). No otorga consentimiento."],
    ], anchos=[3.0, 13.6], tam=8.5, primera_negrita=True, titulo="Importador (lib/csv.ts + ImportDonors.tsx)")
    U.h2(doc, "9.8 Portal del donante")
    U.viñetas(doc, [
        "**Una sola carga:** `donors`, luego en paralelo `donations`, `donation_results`, `campaigns` activas, `consent_versions` activa y `loadParams`.",
        "**Mensaje principal calculado en el cliente** con `computeEligibility` (APTO, ESPERA con fecha, MÁXIMO, INACTIVO) y su ícono y color.",
        "**Resultado:** muestra solo estados liberados (AVAILABLE, NOTIFIED, CONSULTED); las recomendaciones salen de `system_config`.",
        "**Consentimiento:** el donante activa o retira los avisos con un `UPDATE` de su propia fila (consent_email, consent_at, consent_version, opted_out); el trigger registra el evento.",
        "**Descarga de datos:** arma un JSON con la ficha (sin auth_user_id), donaciones, resultados y eventos de consentimiento.",
        "**Pensado para redes lentas:** sin imágenes, SVG en línea, fuentes propias, componente de ~7 KB gzip y un solo estilo adicional de ~2 KB gzip.",
    ])
    U.h2(doc, "9.9 Traducción de errores")
    U.tabla(doc, ["Mensaje técnico (contiene)", "Mensaje mostrado"], [
        ["duplicate key", "Ya existe un registro con esos datos (por ejemplo, el mismo DNI)."],
        ["row-level security / permission denied", "Tu cuenta no tiene permiso para hacer esto."],
        ["donors_check", "Para autorizar correos, el donante necesita tener un correo registrado."],
        ["failed to fetch", "No hay conexión con el servidor. Revisa tu internet e inténtalo de nuevo."],
    ], anchos=[6.0, 10.6], tam=8.5, titulo="friendlyError()")
    U.h2(doc, "9.10 Accesibilidad y usabilidad")
    U.viñetas(doc, [
        "Etiquetas en formularios (`label`), `aria-live` en avisos, `aria-current` en el menú y `aria-label` en el buscador.",
        "Objetivos táctiles grandes y letra de 16 a 18 px en el portal del donante; contraste alto; íconos con texto.",
        "Mensajes de error en lenguaje claro; confirmaciones explícitas para acciones destructivas (escribir el DNI).",
        "Pendiente: auditoría formal de accesibilidad (WCAG) y pruebas con lectores de pantalla.",
    ])
    U.h2(doc, "9.11 Rendimiento del cliente")
    U.figura(doc, FIG + "bundle.png", 15.0, "Peso del cliente por fragmento (medido en el build de producción)")
    U.parrafo(doc, "El total del cliente es **952 KB sin comprimir y 276 KB con gzip** en 16 archivos. El fragmento propio del portal del donante pesa **19.6 KB (7.1 KB gzip)** y el del personal **91.6 KB (24.5 KB gzip)**; "
                   "el resto es código compartido (framework, react-dom, supabase-js). Con la carga diferida por rol, el donante no descarga el panel del personal. Al inicio solo se carga la pantalla de ingreso.", alineacion="justificado")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def algoritmos(doc):
    U.h1(doc, "10. Algoritmos clave")
    U.h2(doc, "10.1 Cálculo de aptitud")
    U.figura(doc, FIG + "aptitud.png", 11.5, "Diagrama de decisión de computeEligibility")
    U.codigo(doc, """export function computeEligibility({ gender, active, donationDates, params, today = limaToday() }) {
  const year = today.slice(0, 4);
  const limit = params.limits[gender], intervalDays = params.intervals[gender];
  const lastDate = donationDates.reduce((max, d) => (!max || d > max ? d : max), null);
  const thisYear = donationDates.filter((d) => d.slice(0, 4) === year).length;
  if (!active)            return { state: 'INACTIVO', eligibleFrom: null, ... };
  if (thisYear >= limit)  return { state: 'MAXIMO',   eligibleFrom: `${Number(year) + 1}-01-01`, ... };
  if (lastDate) { const from = addDays(lastDate, intervalDays);
                  if (from > today) return { state: 'ESPERA', eligibleFrom: from, ... }; }
  return { state: 'APTO', eligibleFrom: null, ... };
}""", titulo="lib/eligibility.ts (extracto)")
    U.tabla(doc, ["Caso", "Entrada", "Salida"], [
        ["Donante inactivo", "active = false", "INACTIVO"],
        ["Alcanzó el máximo", "mujer con 3 donaciones este año", "MAXIMO · elegible desde el 1 de enero siguiente"],
        ["Dentro del intervalo", "última donación hace 40 días, intervalo 90", "ESPERA · elegible desde la última + 90 días"],
        ["Cumplió el intervalo", "última donación hace 120 días, 1 donación este año", "APTO"],
        ["Nunca donó", "sin fechas", "APTO"],
    ], anchos=[4.2, 6.4, 6.0], tam=8.5, titulo="Casos de prueba de la regla")
    U.parrafo(doc, "**Propiedades:** función pura (sin efectos laterales ni acceso a red), tiempo O(n) en el número de donaciones del donante; las fechas se manejan como cadenas `AAAA-MM-DD` (orden lexicográfico = orden cronológico) y la fecha de hoy es la de Lima. "
                   "Es el candidato ideal para pruebas unitarias (sec. 12.5).", alineacion="justificado")
    U.h2(doc, "10.2 Generación de contraseñas")
    U.tabla(doc, ["Tipo", "Formato", "Fuente de aleatoriedad", "Entropía aproximada"], [
        ["Personal", "14 caracteres de un alfabeto de 55 símbolos sin caracteres ambiguos (sin 0, 1, I, L, O, l, o)", "`crypto.getRandomValues`", "14 × log₂ 55 ≈ **81 bits**"],
        ["Donante", "tres palabras de una lista de 50 + dos dígitos (ej. `sol-rio-casa47`)", "`crypto.getRandomValues`", "log₂(50³ × 90) ≈ **23 bits** (H-13)"],
    ], anchos=[2.4, 6.6, 4.0, 3.6], tam=8.5, titulo="Contraseñas generadas por el sistema")
    U.parrafo(doc, "Las contraseñas de donantes son **temporales** y están pensadas para dictarse por teléfono; la protección frente a adivinación depende de los límites de intentos de Supabase Auth. "
                   "Se recomienda forzar el cambio en el primer ingreso (propuesta, sec. 14).", tam=9.5)
    U.h2(doc, "10.3 Indicadores de Reportes")
    U.tabla(doc, ["Indicador", "Fórmula"], [
        ["Donantes recurrentes", "|donantes con ≥ 2 donaciones| / |donantes con ≥ 1 donación|"],
        ["Tiempo medio de entrega", "promedio de (available_at − created_at) de resultados liberados no críticos, en horas; meta 48 h"],
        ["Liberados dentro de 48 h", "|resultados con horas ≤ 48| / |liberados|"],
        ["Pendientes con atraso", "|resultados PENDING no críticos con (ahora − created_at) ≥ 48 h|"],
        ["O negativo con consentimiento", "|donantes O− ACTIVE ∧ consent_email ∧ ¬opted_out|"],
        ["Reserva por grupo", "por grupo: registrados, activos, con correo autorizado y aptos hoy (computeEligibility = APTO)"],
        ["Mensajes de 30 días", "agrupados por tipo: total, enviados (SENT/DELIVERED/READ) y fallidos"],
    ], anchos=[4.6, 12.0], tam=8.5, primera_negrita=True, titulo="Fórmulas de ReportsTab")
    U.h2(doc, "10.4 Resumen de complejidades")
    U.tabla(doc, ["Operación", "Complejidad / costo", "Observación"], [
        ["Aptitud de un donante", "O(n) con n = sus donaciones", "Función pura"],
        ["Aptitud de todos los donantes (lista)", "O(D + N)", "Agrupación en Map; useMemo"],
        ["Búsqueda en Inicio", "O(D) por pulsación", "Filtro en memoria con 6 resultados visibles"],
        ["Candidatos de automatización", "O(D + N)", "Una consulta por tabla"],
        ["Importación de CSV", "O(F) para validar + F inserciones", "F filas; inserciones secuenciales"],
        ["Registro de donación", "1 búsqueda indexada + 1 conteo indexado", "Bloqueo de fila del donante"],
    ], anchos=[6.4, 5.0, 5.2], tam=8.5, titulo="Complejidad")
    U.salto_pagina(doc)


def construir(doc):
    servidor(doc)
    cliente(doc)
    algoritmos(doc)
