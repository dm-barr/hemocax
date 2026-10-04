# -*- coding: utf-8 -*-
"""Informe técnico — modelo de datos, seguridad y lógica dentro de la base de datos."""
import docx_utils as U

FIG = "fig/"

TABLAS = [  # nombre, descripción, [(columna, tipo, restricciones / valor por defecto)]
    ("profiles", "Una fila por cuenta de acceso: DNI, nombre, rol y permiso de liberar resultados.", [
        ("user_id", "uuid", "PK · FK auth.users ON DELETE CASCADE"), ("dni", "text", "NOT NULL · UNIQUE · CHECK ^[0-9]{8}$"), ("full_name", "text", "NOT NULL"),
        ("role", "app_role", "NOT NULL (ADMIN, STAFF, DONOR)"), ("can_release_results", "boolean", "NOT NULL · default false · CHECK: solo ADMIN o STAFF"),
        ("active", "boolean", "NOT NULL · default true"), ("created_at", "timestamptz", "NOT NULL · default now()")]),
    ("donors", "Padrón de donantes: datos personales, contacto, grupo sanguíneo (opcional) y consentimiento de correo.", [
        ("id", "bigint", "PK · identity"), ("auth_user_id", "uuid", "UNIQUE · FK auth.users ON DELETE SET NULL (nulo si no tiene cuenta)"),
        ("dni", "text", "NOT NULL · UNIQUE · CHECK ^[0-9]{8}$"), ("first_name, last_name", "text", "NOT NULL"), ("gender", "text", "NOT NULL · CHECK M o F"),
        ("birth_date", "date", "NOT NULL"), ("phone", "text", "NOT NULL"), ("email", "text", "nulo permitido"),
        ("blood_type", "text", "CHECK O, A, B, AB · nulo si se desconoce"), ("rh_factor", "text", "CHECK + o − · nulo si blood_type es nulo"),
        ("status", "text", "NOT NULL · default ACTIVE · CHECK ACTIVE/INACTIVE"), ("preferred_channel", "text", "NOT NULL · default EMAIL · CHECK = EMAIL"),
        ("consent_email", "boolean", "NOT NULL · default false"), ("consent_at, consent_version", "timestamptz, text", "obligatorios si consent_email es true"),
        ("opted_out", "boolean", "NOT NULL · default false"), ("created_at, updated_at", "timestamptz", "default now() (updated_at no se refresca solo, H-15)"),
        ("CHECK donors_blood_pair_check", "—", "(blood_type is null) = (rh_factor is null)"),
        ("CHECK de consentimiento", "—", "consent_email=false OR (consent_at, consent_version y email no nulos)")]),
    ("donations", "Cada donación registrada.", [
        ("id", "bigint", "PK · identity"), ("donor_id", "bigint", "NOT NULL · FK donors (sin cascada: no se borran donantes con historial)"),
        ("donation_date", "date", "NOT NULL"), ("donation_type", "text", "NOT NULL · default WHOLE_BLOOD"), ("notes", "text", "p. ej. excepción de intervalo autorizada"),
        ("created_by", "uuid", "FK auth.users"), ("created_at", "timestamptz", "default now()")]),
    ("donation_results", "Resultado de cada donación; máquina de estados protegida.", [
        ("id", "bigint", "PK · identity"), ("donation_id", "bigint", "NOT NULL · UNIQUE · FK donations"), ("status", "result_status", "NOT NULL · default PENDING"),
        ("critical", "boolean", "NOT NULL · default false"), ("donor_message", "text", "mensaje para el donante"), ("available_at", "timestamptz", "fecha de liberación"),
        ("released_by", "uuid", "FK auth.users"), ("notified_at, consulted_at", "timestamptz", "—"), ("created_at", "timestamptz", "default now()"),
        ("CHECK 1", "—", "critical=false OR status IN (PENDING, CRITICAL_PENDING)"), ("CHECK 2", "—", "status liberado ⇒ critical=false AND available_at no nulo")]),
    ("campaigns", "Campañas por correo e información educativa.", [
        ("id", "bigint", "PK · identity"), ("name, message_template", "text", "NOT NULL"), ("description, location", "text", "—"), ("blood_groups", "text[]", "NOT NULL · default {}"),
        ("status", "text", "NOT NULL · default DRAFT · CHECK DRAFT/ACTIVE/INACTIVE/CLOSED"), ("kind", "text", "NOT NULL · default CAMPAIGN · CHECK CAMPAIGN/INFO"),
        ("starts_at, ends_at", "timestamptz", "—"), ("created_by", "uuid", "FK auth.users"), ("created_at", "timestamptz", "default now()")]),
    ("communications", "Cada correo: destinatario, tipo, estado y responsable.", [
        ("id", "bigint", "PK · identity"), ("donor_id", "bigint", "NOT NULL · FK donors"), ("campaign_id, result_id, related_donation_id", "bigint", "FK opcionales"),
        ("type", "text", "NOT NULL (MANUAL, CAMPAIGN, RESULT, BIRTHDAY, …)"), ("channel", "text", "NOT NULL · default EMAIL · CHECK = EMAIL"), ("email, message", "text", "NOT NULL"),
        ("status", "text", "NOT NULL · CHECK PENDING/QUEUED/SENT/DELIVERED/READ/FAILED"), ("external_id, error_message", "text", "messageId o motivo del fallo"),
        ("created_by, created_by_name", "uuid, text", "responsable (nombre o «Sistema (automático)»)"), ("sent_at, created_at", "timestamptz", "—"),
        ("created_year", "integer", "GENERATED ALWAYS AS (extract(year from created_at at time zone 'UTC')) STORED")]),
    ("campaign_recipients", "A quién se envió cada campaña.", [
        ("id", "bigint", "PK · identity"), ("campaign_id, donor_id", "bigint", "NOT NULL · FK · UNIQUE (campaign_id, donor_id)"), ("communication_id", "bigint", "FK communications"),
        ("status", "text", "NOT NULL · default PENDING"), ("created_at", "timestamptz", "default now()")]),
    ("notifications", "Avisos dentro del portal (reservada; sin uso en la interfaz, H-04).", [
        ("id", "bigint", "PK"), ("donor_id", "bigint", "NOT NULL · FK donors"), ("communication_id", "bigint", "FK"), ("title, message", "text", "NOT NULL"), ("read_at, created_at", "timestamptz", "—")]),
    ("system_config", "Parámetros editables del sistema.", [
        ("key", "text", "PK"), ("value", "jsonb", "NOT NULL"), ("description", "text", "—"), ("updated_at", "timestamptz", "default now()")]),
    ("audit_logs", "Bitácora de auditoría.", [
        ("id", "bigint", "PK · identity"), ("actor_id", "uuid", "FK auth.users"), ("actor_dni", "text", "—"), ("action, entity", "text", "NOT NULL"), ("entity_id", "bigint", "—"),
        ("detail", "jsonb", "NOT NULL · default {} (nombres de campos, no valores)"), ("created_at", "timestamptz", "default now()")]),
    ("consent_versions", "Texto del consentimiento por versión.", [
        ("version", "text", "PK (v1, v2, … o piloto-v1)"), ("body", "text", "NOT NULL"), ("active", "boolean", "NOT NULL · default false (una sola activa)"),
        ("created_by", "uuid", "FK auth.users"), ("created_at", "timestamptz", "default now()")]),
    ("consent_events", "Historial de cada aceptación o revocación.", [
        ("id", "bigint", "PK · identity"), ("donor_id", "bigint", "NOT NULL · FK donors ON DELETE CASCADE"), ("action", "text", "NOT NULL · CHECK GRANTED/REVOKED"),
        ("version", "text", "versión del texto"), ("recorded_by", "uuid", "sin FK (conserva el historial si se borra la cuenta)"),
        ("recorded_via", "text", "NOT NULL · CHECK DONOR/STAFF/SISTEMA"), ("created_at", "timestamptz", "default now()")]),
    ("message_templates", "Mensajes automáticos aprobables.", [
        ("type", "text", "PK · CHECK BIRTHDAY, RETURN_REMINDER, DONATION_THANKS, FREQUENT_DONOR"), ("subject, body", "text", "NOT NULL"),
        ("approved", "boolean", "NOT NULL · default false"), ("approved_by", "text", "—"), ("approved_at, updated_at", "timestamptz", "—")]),
]

POLITICAS = [  # tabla, política, operación, expresión (resumen)
    ("profiles", "profiles_read_self_or_admin", "SELECT", "user_id = auth.uid() OR current_role() = 'ADMIN'"),
    ("donors", "donors_read_self_or_staff", "SELECT", "auth_user_id = auth.uid() OR is_staff()"),
    ("donors", "donors_insert_staff", "INSERT", "WITH CHECK is_staff()"),
    ("donors", "donors_update_staff", "UPDATE", "USING / WITH CHECK is_staff()"),
    ("donors", "donors_update_own_consent", "UPDATE", "USING / WITH CHECK auth_user_id = auth.uid()  ⚠ ver H-01"),
    ("donations", "donations_read_owner_or_staff", "SELECT", "is_staff() OR donor_id = current_donor_id()"),
    ("donations", "donations_insert_staff", "INSERT", "WITH CHECK is_staff()"),
    ("donations", "donations_update_staff", "UPDATE", "USING / WITH CHECK is_staff()"),
    ("donation_results", "results_read_released_owner_or_staff", "SELECT", "is_staff() OR (critical = false AND status IN (AVAILABLE, NOTIFIED, CONSULTED) AND la donación es del donante)"),
    ("campaigns", "campaigns_read_active_or_staff", "SELECT", "is_staff() OR status = 'ACTIVE'"),
    ("campaigns", "campaigns_write_staff", "ALL", "is_staff()"),
    ("communications", "communications_staff_only", "ALL", "is_staff()"),
    ("campaign_recipients", "campaign_recipients_staff_only", "ALL", "is_staff()"),
    ("notifications", "notifications_read_own_or_staff", "SELECT", "is_staff() OR donor_id = current_donor_id()"),
    ("notifications", "notifications_update_own", "UPDATE", "donor_id = current_donor_id()"),
    ("system_config", "config_read_staff", "SELECT", "is_staff()"),
    ("system_config", "config_write_admin", "ALL", "current_role() = 'ADMIN'"),
    ("system_config", "config_read_public_keys", "SELECT", "key IN (límites, intervalos, recomendaciones, contact_info)"),
    ("audit_logs", "audit_read_admin", "SELECT", "current_role() = 'ADMIN'"),
    ("consent_versions", "consent_versions_read", "SELECT", "true (cualquier usuario autenticado)"),
    ("consent_events", "consent_events_read", "SELECT", "is_staff() OR donor_id = current_donor_id()"),
    ("message_templates", "message_templates_read_staff", "SELECT", "is_staff()"),
    ("message_templates", "message_templates_write_admin", "ALL", "current_role() = 'ADMIN'"),
]


def datos(doc):
    U.h1(doc, "5. Modelo de datos")
    U.h2(doc, "5.1 Visión general")
    U.parrafo(doc, "La base es relacional (PostgreSQL 17.11) y está normalizada alrededor de **donors → donations → donation_results**. Todas las claves primarias de negocio son `bigint` generadas (*identity*); "
                   "las cuentas de acceso usan `uuid` de `auth.users`. El esquema `public` tiene **13 tablas, todas con RLS activo, 30 índices, 14 funciones y 9 triggers**.", alineacion="justificado")
    U.figura(doc, FIG + "er.png", 16.4, "Diagrama entidad-relación (columnas principales; el diccionario completo está en la sección 5.3)")
    U.h2(doc, "5.2 Tipos enumerados y datos iniciales")
    U.tabla(doc, ["Elemento", "Valores / contenido"], [
        ["app_role (enum)", "ADMIN · STAFF · DONOR"],
        ["result_status (enum)", "PENDING · AVAILABLE · NOTIFIED · CONSULTED · CRITICAL_PENDING"],
        ["system_config (semilla)", "male_annual_limit=4 · female_annual_limit=3 · donation_interval_days=90 · recognition_at_annual_limit=true · male_interval_days · female_interval_days · result_recommendations · contact_info"],
        ["consent_versions (semilla)", "piloto-v1 (activa) con el texto de consentimiento del piloto"],
        ["message_templates (semilla)", "4 plantillas (BIRTHDAY, RETURN_REMINDER, DONATION_THANKS, FREQUENT_DONOR) **sin aprobar**"],
    ], anchos=[4.4, 12.2], tam=8.5, primera_negrita=True, titulo="Enumerados y semillas")
    U.h2(doc, "5.3 Diccionario de datos")
    for nombre, desc, cols in TABLAS:
        U.tabla(doc, ["Columna", "Tipo", "Restricciones / valor por defecto"], [list(c) for c in cols],
                anchos=[4.4, 2.6, 9.6], tam=8, titulo=f"{nombre} — {desc}")
    U.h2(doc, "5.4 Índices")
    U.tabla(doc, ["Índice", "Tabla (columnas)", "Propósito"], [
        ["donors_dni_key / donors_auth_user_id_key", "donors (dni) · (auth_user_id)", "Unicidad y búsqueda por DNI y por cuenta"],
        ["donors_blood_group_idx", "donors (blood_type, rh_factor)", "Filtros por grupo sanguíneo"],
        ["donors_contactable_idx", "donors (status, consent_email, opted_out)", "Selección de destinatarios"],
        ["donations_donor_date_idx", "donations (donor_id, donation_date DESC)", "Historial y último intervalo"],
        ["donation_results_donation_id_key", "donation_results (donation_id)", "Un resultado por donación"],
        ["communications_donor_created_idx", "communications (donor_id, created_at DESC)", "Historial por donante"],
        ["communications_type_created_idx", "communications (type, created_at DESC)", "Reportes por tipo"],
        ["birthday_once_per_year_idx", "communications (donor_id, created_year, type) WHERE type='BIRTHDAY'", "Un cumpleaños por donante y año"],
        ["frequent_once_per_year_idx", "ídem WHERE type='FREQUENT_DONOR'", "Un reconocimiento por donante y año"],
        ["donation_thanks_once_idx", "communications (related_donation_id, type) WHERE type='DONATION_THANKS'", "Un agradecimiento por donación"],
        ["return_reminder_once_per_donation_idx", "ídem WHERE type='RETURN_REMINDER'", "Un recordatorio por donación"],
        ["campaign_recipients_campaign_id_donor_id_key", "campaign_recipients (campaign_id, donor_id)", "Nadie recibe dos veces la misma campaña"],
        ["consent_events_donor_idx", "consent_events (donor_id, created_at DESC)", "Historial de consentimiento"],
        ["audit_created_idx", "audit_logs (created_at DESC)", "Lectura de la bitácora"],
    ], anchos=[5.6, 6.6, 4.4], tam=8, titulo="Índices relevantes (30 en total, incluidos los de clave primaria)")
    U.h2(doc, "5.5 Migraciones")
    U.tabla(doc, ["N.°", "Archivo", "Contenido", "Estado"], [
        ["1", "20260927000100_initial_schema.sql", "Tablas base, funciones auxiliares, RLS, trigger del máximo anual, resultado pendiente automático, release_noncritical_result", "Aplicada"],
        ["2", "20261002000200_pilot_features.sql", "Críticos, parámetros, consentimiento versionado e historial, auditoría, plantillas, anonimización", "Aplicada"],
        ["3", "20261003000300_contact_info.sql", "Clave contact_info y política de lectura pública de parámetros", "Aplicada"],
        ["4", "20261004000400_restrict_donor_self_update.sql", "Restringe lo que el donante puede cambiar en su ficha (corrige H-01)", "**Preparada y probada; pendiente de aplicar**"],
    ], anchos=[1.0, 5.8, 7.2, 2.6], alinear=["c", "l", "l", "l"], tam=8, titulo="Migraciones")
    U.parrafo(doc, "Convención: `AAAAMMDDNNNN_nombre.sql`; se aplican en orden con el SQL Editor de Supabase o con `psql \"$DATABASE_URL\" -f archivo.sql`; nunca se editan una vez aplicadas. "
                   "No existe una tabla de control de versiones del esquema (limitación aceptada, ADR-11).", tam=9.5)
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def seguridad(doc):
    U.h1(doc, "6. Seguridad")
    U.h2(doc, "6.1 Modelo de amenazas")
    U.figura(doc, FIG + "confianza.png", 16.0, "Zonas y límites de confianza (1: RLS decide · 2: la ruta decide · 3: sin RLS)")
    U.tabla(doc, ["STRIDE", "Amenaza concreta", "Control", "Riesgo residual"], [
        ["Suplantación", "Alguien inicia sesión como otro usuario.", "Contraseñas gestionadas por Supabase Auth (hash); sin auto-registro; límites de intentos de Auth.", "Contraseñas fáciles de dictar de los donantes (H-13)."],
        ["Manipulación", "Un usuario altera datos que no le corresponden desde el navegador.", "RLS por fila; CHECK; triggers; REVOKE UPDATE en resultados.", "H-01: el donante puede alterar los datos de su propia ficha."],
        ["Repudio", "Un usuario niega haber liberado un resultado o cambiado un parámetro.", "released_by; bitácora por triggers (quién, qué campo, cuándo).", "La bitácora no guarda valores."],
        ["Divulgación", "Un donante lee un resultado crítico o datos ajenos; filtración de claves.", "Política de resultados; helpers SECURITY DEFINER; claves de servicio solo en el servidor; mensajes sin datos médicos.", "Token de sesión en localStorage (H-06)."],
        ["Denegación de servicio", "Abuso de rutas de envío o de la API de datos.", "Funciones sin estado y escalables; límites de plataforma.", "Sin límite de tasa propio en /api (H-07)."],
        ["Elevación de privilegios", "Un STAFF intenta liberar resultados o crear cuentas.", "can_release_results() dentro de la función; requireAdmin() en rutas; el perfil no se puede modificar por los usuarios.", "Bajo."],
    ], anchos=[2.6, 4.8, 5.8, 3.4], tam=8, titulo="Amenazas y controles (STRIDE)")

    U.h2(doc, "6.2 Autenticación y sesión")
    U.viñetas(doc, [
        "**Identidad:** Supabase Auth con contraseña. El DNI se transforma en `dni-<DNI>@login.hemocax.org` (correo confirmado, nunca usado para enviar).",
        "**Cuentas:** solo las crea un administrador (`POST /api/admin/users`); no hay registro público. Una cuenta inactiva recibe un *ban* de 876 000 horas y `profiles.active=false`; `current_role()` ignora perfiles inactivos.",
        "**Sesión:** JWT de acceso y de renovación gestionados por supabase-js con `persistSession: true` y `autoRefreshToken: true`. Cada llamada a Supabase o a `/api` lleva `Authorization: Bearer <JWT>`.",
        "**Contraseñas:** mínimo 12 caracteres para el personal (aleatorias de 14 en la creación) y 8 para el donante al cambiarla; el administrador puede restablecerlas.",
        "**Autorización por rol:** `profiles.role` (ADMIN, STAFF, DONOR) + `can_release_results`. La interfaz decide qué mostrar, pero el control real es de la base.",
    ])
    U.h2(doc, "6.3 Seguridad a nivel de filas (RLS)")
    U.parrafo(doc, "Con RLS activo, PostgREST ejecuta cada consulta con el rol `authenticated` y las *claims* del JWT; las políticas añaden condiciones a cada consulta. "
                   "Las 23 políticas vigentes (consulta a `pg_policies` en producción) son:", alineacion="justificado")
    U.tabla(doc, ["Tabla", "Política", "Operación", "Condición"], [list(p) for p in POLITICAS],
            anchos=[2.8, 4.8, 1.6, 7.4], alinear=["l", "l", "c", "l"], tam=7.5, titulo="Políticas RLS vigentes")
    U.tabla(doc, ["Rol", "Capacidad efectiva"], [
        ["DONOR", "Lee su ficha, sus donaciones, sus resultados **liberados y no críticos**, las campañas activas, el consentimiento vigente y sus eventos; puede actualizar su ficha (H-01)."],
        ["STAFF", "Lee y administra donantes, donaciones, campañas, comunicaciones y plantillas (solo lectura); registra donaciones; marca críticos; libera solo con `can_release_results`."],
        ["ADMIN", "Todo lo de STAFF más cuentas, parámetros, plantillas, bitácora y anonimización."],
        ["service_role", "Omite RLS; solo se usa en el servidor (rutas /api y reloj a través de ellas)."],
    ], anchos=[3.0, 13.6], tam=8.5, primera_negrita=True, titulo="Capacidad efectiva por rol")
    U.h2(doc, "6.4 Funciones SECURITY DEFINER")
    U.parrafo(doc, "Las funciones auxiliares se ejecutan con los privilegios de su dueño para consultar `profiles` sin que RLS genere recursión; por ello se declaran con `set search_path=public` (evita secuestro de rutas de búsqueda) "
                   "y, en los *helpers*, `set row_security=off`.", alineacion="justificado")
    U.tabla(doc, ["Función", "Tipo", "Seguridad", "Quién puede llamarla"], [
        ["current_role(), current_donor_id(), is_staff(), can_release_results()", "Helpers estables", "SECURITY DEFINER · row_security=off", "Usadas por las políticas"],
        ["release_noncritical_result(id, mensaje)", "RPC", "SECURITY DEFINER", "can_release_results() verificado dentro"],
        ["mark_result_critical(id)", "RPC", "SECURITY DEFINER · REVOKE de public/anon", "is_staff()"],
        ["clear_result_critical(id)", "RPC", "SECURITY DEFINER · REVOKE de public/anon", "can_release_results()"],
        ["publish_consent_version(texto)", "RPC", "SECURITY DEFINER · REVOKE de public/anon", "ADMIN"],
        ["anonymize_donor(id)", "RPC", "SECURITY DEFINER · REVOKE de public/anon", "ADMIN"],
        ["enforce_annual_donation_limit, create_pending_result, log_consent_change, audit_row_change, reset_template_approval", "Trigger", "SECURITY DEFINER", "Disparadas por la base"],
    ], anchos=[6.4, 2.2, 4.6, 3.4], tam=8, titulo="Funciones y su control de acceso")
    U.h2(doc, "6.5 Protección de los resultados críticos")
    U.tabla(doc, ["Capa", "Mecanismo", "Efecto"], [
        ["1. Interfaz", "ResultsTab no ofrece liberar un resultado marcado crítico; el portal solo muestra estados liberados.", "Evita el error humano."],
        ["2. Función", "release_noncritical_result actualiza solo si status='PENDING' AND critical=false; CHECK de la tabla impide liberados con critical=true.", "Aunque se llame a la API directamente, falla."],
        ["3. Política RLS", "results_read_released_owner_or_staff exige critical=false y estado liberado para el donante.", "Aunque el donante pida el resultado por la API, recibe cero filas."],
        ["+ Correo", "Los mensajes de aviso nunca incluyen resultados: invitan a entrar al portal.", "El canal digital no transporta datos médicos."],
    ], anchos=[2.6, 9.0, 5.0], tam=8.5, titulo="Defensa en profundidad (probada con una sesión de donante, PS-02)")
    U.h2(doc, "6.6 Secretos y configuración sensible")
    U.tabla(doc, ["Secreto", "Dónde vive", "Quién lo usa", "Exposición", "Rotación"], [
        ["SUPABASE_SERVICE_ROLE_KEY", "Variables de Vercel (y .env local)", "Rutas /api", "Solo servidor; omite RLS", "Panel de Supabase"],
        ["NEXT_PUBLIC_SUPABASE_ANON_KEY", "Cliente (pública)", "Navegador", "Pública por diseño; sin privilegios sin RLS", "Panel de Supabase"],
        ["SMTP_PASSWORD (contraseña de aplicación)", "Variables de Vercel", "lib/email.ts", "Solo servidor", "Cuenta de Google"],
        ["AUTOMATION_RUN_SECRET", "Vercel y Render (mismo valor)", "Reloj → /api/automations/run", "Cabecera HTTP; comparación simple (H-14)", "Manual en ambos servicios"],
        ["DATABASE_URL", "Solo equipo (.env local)", "Migraciones", "No se despliega", "Panel de Supabase"],
    ], anchos=[4.2, 3.6, 3.2, 3.4, 2.2], tam=8, titulo="Inventario de secretos")
    U.parrafo(doc, "El archivo `.env` está en `.gitignore`. Se verificó que el historial de git no contiene claves. Las claves que se compartieron por mensajería durante el desarrollo deben **rotarse** antes de la operación real.", tam=9.5)
    U.h2(doc, "6.7 Validación de entradas y salidas")
    U.tabla(doc, ["Capa", "Controles"], [
        ["Cliente", "Validación de DNI (8 dígitos), formatos y obligatorios; traducción de errores (friendlyError)."],
        ["Rutas /api", "Validan sesión y rol, cuerpo JSON (tipos y rangos), DNI, rol permitido, longitud de contraseña, identificadores numéricos; devuelven códigos 400/401/403/404/409."],
        ["Base de datos", "CHECK, UNIQUE, NOT NULL, FK, tipos y triggers: última barrera frente a cualquier cliente."],
        ["Salida (correo)", "El texto del usuario se escapa con escapeHtml antes de insertarse en el HTML; los enlaces se detectan y generan con atributos controlados. No hay dangerouslySetInnerHTML en la interfaz."],
        ["Importación CSV", "Parser propio con comillas; cada fila se valida; los inserts van parametrizados por PostgREST (sin SQL concatenado)."],
    ], anchos=[3.2, 13.4], tam=8.5, primera_negrita=True, titulo="Validación por capa")
    U.h2(doc, "6.8 Privacidad y derechos del titular")
    U.viñetas(doc, [
        "**Consentimiento versionado** (`consent_versions`) con historial inmutable de aceptaciones y revocaciones (`consent_events`), incluido quién lo registró (DONOR, STAFF o SISTEMA).",
        "**Acceso:** el donante descarga un JSON con sus datos, donaciones, resultados y consentimientos desde su portal; el personal lo hace desde la ficha.",
        "**Cancelación:** `anonymize_donor` reemplaza nombre, DNI (por `9` + id con ceros), teléfono y correo, deja el donante inactivo y sin consentimiento, enmascara sus comunicaciones y elimina su cuenta de Auth desde la ruta del servidor.",
        "**Minimización:** la bitácora guarda nombres de campos, no valores; los correos no incluyen datos médicos.",
    ])
    U.h2(doc, "6.9 Correspondencia con OWASP Top 10 (2021)")
    U.tabla(doc, ["Categoría", "Estado", "Evidencia / hallazgo"], [
        ["A01 Control de acceso roto", "Controlado, con una excepción", "RLS en 13 de 13 tablas; pruebas por rol (PS-01 a PS-06). **H-01:** el donante puede editar su ficha."],
        ["A02 Fallos criptográficos", "Controlado", "HTTPS en Vercel y Supabase; contraseñas con hash en Auth; STARTTLS en SMTP."],
        ["A03 Inyección", "Controlado", "PostgREST parametriza; correo escapado; sin SQL dinámico en el cliente."],
        ["A04 Diseño inseguro", "Controlado", "Defensa en profundidad para críticos; modo seguro por defecto (ADR-04, ADR-06)."],
        ["A05 Configuración de seguridad incorrecta", "Mejorable", "No hay CSP ni cabeceras adicionales (H-07); x-powered-by desactivado."],
        ["A06 Componentes vulnerables", "Controlado", "npm audit --omit=dev: 0 vulnerabilidades (04/10/2026); versiones fijadas por package-lock."],
        ["A07 Fallos de identificación y autenticación", "Mejorable", "Contraseñas fáciles de donantes (H-13); sin recuperación autónoma."],
        ["A08 Fallos de integridad de software", "Parcial", "Despliegue desde la rama main; sin firma de commits ni revisión obligatoria."],
        ["A09 Fallos de registro y monitoreo", "Parcial", "Bitácora y estados de correo; monitor externo de disponibilidad; sin alertas automáticas de errores."],
        ["A10 SSRF", "No aplica", "El servidor no recibe URLs de usuarios."],
    ], anchos=[4.6, 3.0, 9.0], tam=8, titulo="OWASP Top 10")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def logica_bd(doc):
    U.h1(doc, "7. Lógica dentro de la base de datos")
    U.h2(doc, "7.1 Funciones auxiliares de identidad")
    U.codigo(doc, """create or replace function public.current_role()
returns public.app_role language sql stable security definer set search_path=public set row_security=off
as $$ select role from public.profiles where user_id=auth.uid() and active=true $$;

create or replace function public.is_staff()
returns boolean language sql stable security definer set search_path=public set row_security=off
as $$ select coalesce(public.current_role() in ('ADMIN','STAFF'),false) $$;""", titulo="current_role() e is_staff() (extracto)")
    U.h2(doc, "7.2 Máximo anual de donaciones (concurrencia)")
    U.codigo(doc, """create or replace function public.enforce_annual_donation_limit() returns trigger ... as $$
declare donor_gender text; annual_limit integer; existing_count integer; year_start date;
begin
  if new.donation_type <> 'WHOLE_BLOOD' then return new; end if;
  select gender into donor_gender from public.donors where id=new.donor_id for update;   -- bloquea al donante
  annual_limit := case donor_gender when 'M' then 4 when 'F' then 3 else 0 end;           -- ⚠ valores fijos (H-02)
  year_start := make_date(extract(year from new.donation_date)::integer,1,1);
  select count(*) into existing_count from public.donations
    where donor_id=new.donor_id and donation_type='WHOLE_BLOOD'
      and donation_date >= year_start and donation_date < (year_start + interval '1 year')::date;
  if existing_count >= annual_limit then raise exception 'Se alcanzó el máximo anual …'; end if;
  return new;
end $$;""", titulo="Trigger BEFORE INSERT sobre donations")
    U.parrafo(doc, "**Análisis de concurrencia.** `SELECT … FOR UPDATE` toma un bloqueo de fila sobre el donante: dos inserciones simultáneas del mismo donante se serializan; la segunda ve el conteo ya actualizado y puede ser rechazada. "
                   "Sin ese bloqueo, ambas leerían el mismo conteo (condición de carrera). Las donaciones de otros donantes no se bloquean entre sí. Complejidad: una búsqueda por el índice `donations_donor_date_idx`.", alineacion="justificado")
    U.h2(doc, "7.3 Bitácora de auditoría por triggers")
    U.codigo(doc, """-- audit_row_change(accion_base, entidad): AFTER INSERT/UPDATE/DELETE
v_fields := array(select n.key from jsonb_each(to_jsonb(new)) n join jsonb_each(to_jsonb(old)) o on o.key=n.key
                  where n.value is distinct from o.value and n.key not in ('updated_at'));
insert into public.audit_logs(actor_id,actor_dni,action,entity,entity_id,detail)
  values(auth.uid(), (select dni from public.profiles where user_id=auth.uid()), v_action, tg_argv[1],
         nullif(rowj->>'id','')::bigint, jsonb_strip_nulls(jsonb_build_object('campos',v_fields,'clave',...)));""", titulo="Extracto de la función")
    U.tabla(doc, ["Trigger", "Tabla", "Acciones registradas"], [
        ["donors_audit", "donors", "DONOR_CREATED / _UPDATED / _DELETED"], ["donations_audit", "donations", "DONATION_CREATED / _UPDATED / _DELETED"],
        ["campaigns_audit", "campaigns", "CAMPAIGN_*"], ["system_config_audit", "system_config", "CONFIG_*"], ["message_templates_audit", "message_templates", "TEMPLATE_UPDATED"],
    ], anchos=[5.0, 4.0, 7.6], tam=8.5, titulo="Triggers de auditoría")
    U.parrafo(doc, "Las operaciones de negocio sensibles (liberar, marcar crítico, publicar consentimiento, anonimizar) insertan además su propia fila de bitácora dentro de la función. "
                   "Las rutas del servidor registran la creación de cuentas, los cambios de contraseña y permisos, los envíos y las ejecuciones automáticas.", tam=9.5)
    U.h2(doc, "7.4 Máquina de estados del resultado")
    U.figura(doc, FIG + "estados_resultado.png", 16.0, "Estados de donation_results y quién puede cambiarlos")
    U.codigo(doc, """create or replace function public.release_noncritical_result(p_result_id bigint, p_donor_message text) returns public.donation_results ... as $$
begin
  if not public.can_release_results() then raise exception 'No autorizado para liberar resultados'; end if;
  update public.donation_results set status='AVAILABLE', critical=false, donor_message=p_donor_message,
         available_at=now(), released_by=auth.uid()
   where id=p_result_id and status='PENDING' and critical=false returning * into result_row;
  if result_row.id is null then raise exception 'Resultado inexistente, crítico o ya liberado'; end if;
  insert into public.audit_logs(...) values(auth.uid(),'RESULT_RELEASED','donation_result',p_result_id,jsonb_build_object('critical',false));
  return result_row;
end $$;""", titulo="release_noncritical_result (extracto)")
    U.parrafo(doc, "`UPDATE` directo sobre `donation_results` está revocado para `anon` y `authenticated` (`REVOKE UPDATE`); solo estas funciones y el servidor (que marca NOTIFIED) lo modifican. El estado `CONSULTED` existe en el enum pero ningún código lo asigna (H-04).", tam=9.5)
    U.h2(doc, "7.5 Idempotencia de los correos automáticos")
    U.codigo(doc, """create unique index birthday_once_per_year_idx on public.communications(donor_id, created_year, type) where type='BIRTHDAY';
create unique index donation_thanks_once_idx on public.communications(related_donation_id, type)
  where type='DONATION_THANKS' and related_donation_id is not null;
-- Un segundo INSERT idéntico falla con SQLSTATE 23505 (unique_violation); la ruta lo interpreta como "ya enviado" y continúa.""")
    U.parrafo(doc, "`created_year` es una columna generada y almacenada, de modo que el índice funciona sin lógica en la aplicación. **Consecuencia de diseño:** en modo simulación no se inserta ninguna fila, porque una fila simulada ocuparía el índice del año y bloquearía el envío real.", tam=9.5)
    U.h2(doc, "7.6 Consentimiento y anonimización")
    U.tabla(doc, ["Función / trigger", "Comportamiento"], [
        ["log_consent_change (trigger AFTER INSERT/UPDATE en donors)", "Inserta un consent_event GRANTED o REVOKED cuando cambian consent_email u opted_out; recorded_via = SISTEMA (sin sesión), DONOR (la propia cuenta) o STAFF."],
        ["publish_consent_version(texto)", "Solo ADMIN; texto ≥ 40 caracteres; crea vN, desactiva la anterior, audita."],
        ["reset_template_approval (trigger BEFORE UPDATE)", "Si cambian asunto o cuerpo, approved=false y se limpian approved_by/approved_at."],
        ["anonymize_donor(id)", "Solo ADMIN; sustituye datos personales, deshabilita el contacto, enmascara comunicaciones, elimina notificaciones y audita. La ruta elimina además la cuenta de Auth."],
    ], anchos=[6.4, 10.2], tam=8.5, titulo="Funciones de privacidad")
    U.salto_pagina(doc)


def construir(doc):
    datos(doc)
    seguridad(doc)
    logica_bd(doc)
