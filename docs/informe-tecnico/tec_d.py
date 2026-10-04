# -*- coding: utf-8 -*-
"""Informe técnico — despliegue, pruebas, rendimiento, hallazgos, hoja de ruta y anexos."""
import docx_utils as U
import metricas as M

FIG = "fig/"

HALLAZGOS = [  # id, hallazgo, evidencia, severidad, impacto, propuesta, estado
    ("H-01", "El donante puede modificar **todas** las columnas de su propia ficha (teléfono, estado, grupo sanguíneo…), no solo las de consentimiento.",
     "Prueba con una sesión de donante el 04/10/2026: UPDATE de phone, first_name, status y blood_type afectó 1 fila cada vez. La política `donors_update_own_consent` autoriza la fila y el GRANT por columnas no restringe porque existe el permiso de tabla completo.",
     "Alta", "Integridad de los datos propios (no alcanza a otros donantes: RLS lo impide).",
     "Migración 0004: trigger BEFORE UPDATE `restrict_donor_self_update` que solo deja cambiar columnas de consentimiento a quien no es personal.", "Preparada y probada con rollback; **pendiente de aplicar**"),
    ("H-02", "La regla del máximo anual está escrita con 4 y 3 dentro del trigger, mientras *Parámetros* permite editar `*_annual_limit`.",
     "`enforce_annual_donation_limit` usa `case donor_gender when 'M' then 4 when 'F' then 3`.", "Media", "Pantalla y base podrían discrepar si el médico define otros valores.",
     "Migración que lea `system_config` dentro del trigger (con valores por defecto).", "Abierto"),
    ("H-03", "En modo simulación, un correo manual queda PENDING: el estado `DEMO_QUEUED` no está permitido por el CHECK de `communications.status`.",
     "`deliverCommunication` ignora el error del UPDATE.", "Baja", "Estado confuso solo en simulación.", "No actualizar en simulación o ampliar el CHECK.", "Abierto"),
    ("H-04", "El estado `CONSULTED` y la tabla `notifications` existen pero ningún código las usa.", "Búsqueda en el código.", "Baja", "Ninguno funcional.", "Implementar (marcar «visto» con una función SQL) o eliminar.", "Abierto"),
    ("H-05", "Render (plan gratuito) bloquea la salida SMTP.", "Error de red al enviar desde el reloj.", "Media (resuelta)", "Correos fallidos.", "Envío desde Vercel (ADR-05).", "Resuelto"),
    ("H-06", "El token de sesión se guarda en `localStorage` (comportamiento por defecto de supabase-js).", "`persistSession: true`.", "Media", "Un XSS podría leerlo.", "Sin sinks XSS conocidos; añadir CSP; evaluar cookies httpOnly con @supabase/ssr.", "Abierto"),
    ("H-07", "Sin política CSP ni cabeceras de seguridad adicionales, y sin límite de tasa propio en `/api`.", "`next.config.ts` solo desactiva `x-powered-by`.", "Media", "Superficie de ataque mayor; abuso de rutas.", "Cabeceras en `next.config.ts`; límite de tasa en rutas de envío.", "Abierto"),
    ("H-08", "Envíos secuenciales y límite de 60 s por ejecución; las campañas se envían desde el navegador (cerrar la pestaña las interrumpe).", "Bucles `for` en `/api/automations/run` y `CampaignsTab`.", "Media", "Volúmenes grandes no caben en una ejecución.", "Cola de envío o lotes en el servidor; las campañas ya son reanudables (excluyen a quienes recibieron).", "Abierto"),
    ("H-09", "El repositorio conserva código heredado (server.js, public/, n8n/, db/, docker-compose.yml).", "Listado del repositorio.", "Baja", "Confusión; riesgo de usarlo con datos reales.", "Mover a una rama de archivo.", "Abierto"),
    ("H-10", "`@supabase/ssr` está declarada como dependencia pero no se usa.", "Búsqueda de importaciones.", "Baja", "Peso y superficie de dependencias.", "Eliminar o adoptarla para cookies httpOnly.", "Abierto"),
    ("H-11", "No hay pruebas automatizadas.", "Sin framework de pruebas en package.json.", "Media", "Riesgo de regresiones.", "Pruebas unitarias (aptitud, CSV), de seguridad (RLS) y de rutas; CI (sec. 12.5).", "Abierto"),
    ("H-12", "Listas y reportes se calculan en el cliente con consultas de hasta 1 000 filas efectivas.", "`limit(5000)` y `limit(10000)` en ReportsTab; tope de PostgREST.", "Media a escala", "Datos incompletos con padrones grandes.", "Paginación y vistas/RPC con agregados.", "Abierto"),
    ("H-13", "Las contraseñas generadas para donantes tienen ≈ 23 bits de entropía.", "50 palabras³ × 90 combinaciones.", "Media", "Adivinación si no hay límite de intentos.", "Forzar cambio en el primer ingreso; confiar en los límites de Auth; opcionalmente aumentar palabras.", "Abierto"),
    ("H-14", "El secreto del reloj es estático y se compara con `!==`.", "`automations/run/route.ts`.", "Baja", "Comparación no constante en tiempo; sin rotación programada.", "`timingSafeEqual`; calendario de rotación.", "Abierto"),
    ("H-15", "`donors.updated_at` no se actualiza automáticamente.", "No hay trigger que lo mantenga.", "Baja", "Dato de auditoría incompleto.", "Trigger BEFORE UPDATE que fije `updated_at = now()`.", "Abierto"),
    ("H-16", "No existe una tabla de control de migraciones aplicadas.", "Procedimiento manual.", "Baja", "Dificulta saber el estado del esquema.", "Tabla `schema_migrations` o Supabase CLI.", "Abierto"),
]

VARIABLES = [  # nombre, servicio, obligatoria, secreta, descripción
    ("NEXT_PUBLIC_SUPABASE_URL", "Vercel · local", "Sí", "No", "URL del proyecto Supabase"),
    ("NEXT_PUBLIC_SUPABASE_ANON_KEY", "Vercel · local", "Sí", "No (pública)", "Clave pública sb_publishable_…"),
    ("SUPABASE_SERVICE_ROLE_KEY", "Vercel · local", "Sí", "**Sí**", "Clave de servicio sb_secret_… (omite RLS)"),
    ("DATABASE_URL", "Solo equipo", "Para migraciones", "**Sí**", "Conexión directa a PostgreSQL"),
    ("SMTP_HOST · SMTP_PORT · SMTP_USE_TLS", "Vercel", "Para enviar", "No", "smtp.gmail.com · 587 · true"),
    ("SMTP_USERNAME · SMTP_PASSWORD", "Vercel", "Para enviar", "**Sí** (contraseña)", "Cuenta y contraseña de aplicación"),
    ("EMAIL_FROM_ADDRESS · EMAIL_FROM_NAME", "Vercel", "Recomendada", "No", "Remitente"),
    ("AUTOMATION_DRY_RUN", "Vercel · Render", "Sí", "No", "Solo `false` envía de verdad; cualquier otro valor simula"),
    ("AUTOMATION_RUN_SECRET", "Vercel **y** Render (igual)", "Sí", "**Sí**", "Autentica al reloj ante la ruta"),
    ("AUTOMATIONS_ENABLED", "Render", "Sí", "No", "Interruptor del planificador"),
    ("AUTOMATION_TIMEZONE", "Render", "No", "No", "Por defecto America/Lima"),
    ("HEMOCAX_API_URL", "Render", "Sí", "No", "URL base del portal"),
    ("NEXT_PUBLIC_SITE_URL", "Vercel", "No", "No", "URL del botón de los correos (si falta, se deduce)"),
    ("AUTOMATION_WEBHOOK_SECRET · AUTOMATION_HOST · PORT", "Render", "No (camino heredado)", "**Sí** (webhook)", "Servidor HTTP del reloj"),
]


def despliegue(doc):
    U.h1(doc, "11. Despliegue y operación")
    U.h2(doc, "11.1 Entornos")
    U.tabla(doc, ["Entorno", "Descripción", "Datos"], [
        ["Local", "`npm run dev` con `.env`; puede apuntar a un proyecto Supabase de pruebas.", "De prueba"],
        ["Producción", "Vercel (portal) + Supabase (datos) + Render (reloj) + Gmail (salida).", "Reales (equipo) y de demostración (DNI 9900…)"],
        ["Preproducción", "No existe (limitación): las migraciones se prueban en transacciones que se deshacen o en un proyecto aparte.", "—"],
    ], anchos=[3.0, 10.0, 3.6], tam=8.5, primera_negrita=True, titulo="Entornos")
    U.h2(doc, "11.2 Canal de despliegue")
    U.figura(doc, FIG + "pipeline.png", 16.4, "Flujo de cambio a producción")
    U.viñetas(doc, [
        "Antes del `git push`: `npm run build` (compila y verifica tipos). Cada push a `main` dispara el despliegue automático en Vercel (≈ 1-2 minutos) y, si cambió `automations/`, en Render.",
        "Las migraciones **no** se despliegan solas: se aplican a Supabase en orden y después se despliega la versión de la aplicación que las necesita.",
        "Verificación posterior: `/health` del reloj, las rutas protegidas devuelven 401 sin credencial y una sesión de prueba por rol.",
    ])
    U.h2(doc, "11.3 Configuración de los servicios")
    U.tabla(doc, ["Servicio", "Parámetros"], [
        ["Vercel", "Proyecto importado desde GitHub; framework Next.js detectado; Node ≥ 20; variables de entorno (sec. 11.4); dominio `hemocax.vercel.app`."],
        ["Supabase", "Proyecto `ajdqklbdqpduzzoqyouy`; PostgreSQL 17.11; Auth con usuarios creados por `auth.admin.createUser` (correo confirmado); RLS activo en todas las tablas; claves nuevas `sb_publishable_` / `sb_secret_`."],
        ["Render", "Web Service con Docker; *Root Directory* `automations`; *Health Check Path* `/health`; plan Free; variables del reloj."],
        ["Gmail", "Verificación en dos pasos + contraseña de aplicación; puerto 587 (STARTTLS)."],
        ["UptimeRobot", "Recomendado: monitor HTTP a `https://hemocax.onrender.com/health` cada 5 minutos (configuración por confirmar)."],
    ], anchos=[3.0, 13.6], tam=8.5, primera_negrita=True, titulo="Configuración por servicio")
    U.h2(doc, "11.4 Variables de entorno")
    U.tabla(doc, ["Variable", "Dónde", "Obligatoria", "Secreta", "Descripción"], [list(v) for v in VARIABLES],
            anchos=[5.0, 2.8, 2.2, 2.0, 4.6], tam=7.8, titulo="Variables de entorno (plantilla en .env.example)")
    U.h2(doc, "11.5 Procedimiento de migración")
    U.numerada(doc, [
        "Revisar el archivo `supabase/migrations/AAAAMMDDNNNN_nombre.sql` y probarlo dentro de una transacción con `ROLLBACK` (ver `docs/informe-tecnico/probar_migracion_donante.js` como ejemplo).",
        "Aplicarlo en el SQL Editor de Supabase o con `psql \"$DATABASE_URL\" -f archivo.sql`.",
        "Comprobar el catálogo (ver consultas siguientes) y ejecutar las pruebas de rol.",
        "Desplegar la versión de la aplicación que dependa del cambio.",
    ])
    U.codigo(doc, """-- Verificación del esquema después de migrar
select count(*) from pg_tables   where schemaname='public' and rowsecurity;   -- 13 tablas con RLS
select count(*) from pg_policies where schemaname='public';                   -- 23 políticas
select tablename, policyname, cmd from pg_policies where schemaname='public' order by 1, 2;""", titulo="Consultas de verificación")
    U.h2(doc, "11.6 Observabilidad y monitoreo")
    U.tabla(doc, ["Fuente", "Qué muestra", "Cómo consultarla"], [
        ["/health del reloj", "{ok, enabled, dry_run}; confirma que el proceso está vivo y en qué modo", "GET https://hemocax.onrender.com/health"],
        ["Monitor externo (recomendado)", "Disponibilidad del reloj cada 5 minutos", "Panel de UptimeRobot (por configurar)"],
        ["Logs de funciones", "Errores 500 y trazas de las rutas /api", "Panel de Vercel → Logs"],
        ["Logs del reloj", "Ejecuciones, errores de llamada, estado del planificador", "Panel de Render → Logs"],
        ["Tabla communications", "Estado, error y responsable de cada correo", "Pestaña «Correos enviados» o SQL"],
        ["Tabla audit_logs", "Quién cambió qué", "Pestaña «Actividad» (solo ADMIN)"],
    ], anchos=[3.6, 7.0, 6.0], tam=8.5, titulo="Fuentes de observabilidad")
    U.codigo(doc, """-- Correos fallidos de los últimos 7 días
select created_at, type, email, error_message from communications
 where status='FAILED' and created_at > now() - interval '7 days' order by created_at desc;

-- Resultados pendientes con más de 48 horas
select id, created_at, extract(epoch from now()-created_at)/3600 as horas from donation_results
 where status='PENDING' and critical=false and created_at < now() - interval '48 hours';

-- Ejecuciones automáticas
select created_at, detail from audit_logs where action='AUTOMATION_RUN' order by created_at desc limit 10;""", titulo="Consultas de diagnóstico")
    U.h2(doc, "11.7 Respaldo y recuperación")
    U.parrafo(doc, "Los datos residen en Supabase. El plan gratuito **no garantiza respaldos diarios descargables** (verificar el plan vigente); se recomienda un volcado periódico con `pg_dump` usando `DATABASE_URL`, además de las descargas CSV de *Reportes*. "
                   "El código y las migraciones están en GitHub, por lo que el esquema puede reconstruirse aplicando las migraciones en orden. La recuperación de datos de una anonimización **no es posible** (es irreversible por diseño).", alineacion="justificado")
    U.h2(doc, "11.8 Guía de incidentes")
    U.tabla(doc, ["Síntoma", "Causa probable", "Diagnóstico y acción"], [
        ["Los correos quedan en FAILED", "Contraseña de aplicación inválida; límite diario; puerto bloqueado", "Ver `error_message`; renovar la contraseña de aplicación en Vercel; no enviar desde Render."],
        ["Los correos quedan en PENDING", "`AUTOMATION_DRY_RUN` no es `false` (simulación) o H-03", "Poner `false` en Vercel y volver a desplegar."],
        ["Los recordatorios no salen", "Plantillas sin aprobar; reloj dormido o deshabilitado", "Revisar «Parámetros»; `/health` debe mostrar `enabled:true`."],
        ["`401` desde el reloj", "AUTOMATION_RUN_SECRET distinto entre Vercel y Render", "Igualar el valor en ambos."],
        ["Lista vacía donde hay datos", "Falta política RLS o la sesión no tiene el rol esperado", "Probar la consulta con esa sesión; revisar `pg_policies`."],
        ["«Se alcanzó el máximo anual»", "Trigger del máximo (año de la fecha de la donación)", "Es correcto; revisar la fecha ingresada."],
        ["Un usuario no puede ingresar", "Cuenta desactivada o sin perfil", "Revisar `profiles.active` y el *ban* en Auth."],
    ], anchos=[4.0, 5.2, 7.4], tam=8, titulo="Incidentes frecuentes")
    U.h2(doc, "11.9 Rotación de secretos")
    U.tabla(doc, ["Secreto", "Procedimiento"], [
        ["Clave de servicio de Supabase", "Generar una nueva en el panel → actualizar `SUPABASE_SERVICE_ROLE_KEY` en Vercel → redesplegar → revocar la anterior."],
        ["Contraseña de la base (DATABASE_URL)", "Restablecer en el panel de Supabase → actualizar los `.env` locales del equipo."],
        ["Contraseña de aplicación de Gmail", "Revocar y crear otra en la cuenta de Google → actualizar `SMTP_PASSWORD` en Vercel → redesplegar."],
        ["AUTOMATION_RUN_SECRET", "Generar un valor largo aleatorio → actualizarlo en Vercel **y** Render el mismo día."],
        ["Contraseñas temporales de usuarios", "Se restablecen desde «Cuentas de acceso»; se muestran una sola vez."],
    ], anchos=[5.2, 11.4], tam=8.5, primera_negrita=True, titulo="Procedimientos de rotación")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
PRUEBAS = [
    ("PF-01", "Alta y búsqueda de donante", "Crear un donante, buscarlo por DNI y por apellido sin acentos; abrir la ficha.", "Aparece con su estado de aptitud.", "Aprobada"),
    ("PF-02", "Importación CSV", "Archivo con filas válidas y con errores (DNI de 7 dígitos, sexo vacío, «No sé»).", "Solo se cargan las válidas; cada error indica fila y motivo.", "Aprobada"),
    ("PF-03", "Cálculo de aptitud", "Donantes hombre y mujer con distintas fechas y conteos del año.", "APTO, ESPERA con fecha, MAXIMO e INACTIVO correctos.", "Aprobada"),
    ("PF-04", "Donación y máximo anual", "Registrar donaciones hasta superar el máximo; intentar una antes del intervalo.", "La base rechaza la que supera el máximo; el intervalo exige confirmación.", "Aprobada"),
    ("PF-05", "Resultados", "Liberar, marcar crítico y quitar la marca con el rol correspondiente.", "Transiciones válidas; auditoría registrada.", "Aprobada"),
    ("PF-06", "Portal del donante", "Entrar como donante en escritorio y celular (320-375 px).", "Una pantalla; estado y resultado correctos.", "Aprobada"),
    ("PF-07", "Consentimiento", "Otorgar, revocar y consultar el historial.", "Eventos GRANTED/REVOKED con versión y origen.", "Aprobada"),
    ("PF-08", "Correo individual", "Enviar a un donante con consentimiento (envío real) y a uno sin él.", "Llega con diseño institucional; el segundo se rechaza (403).", "Aprobada"),
    ("PF-09", "Campaña", "Vista previa y envío a O negativo.", "Solo destinatarios elegibles; sin repetir.", "Aprobada"),
    ("PF-10", "Automatizaciones", "Llamar a la ruta con y sin plantilla aprobada, en simulación.", "Sin aprobación: skipped; simulación: lista sin registrar.", "Aprobada con observación (plantillas por aprobar)"),
    ("PF-11", "Parámetros", "Cambiar intervalo y recomendaciones.", "Se reflejan en pantalla y bitácora.", "Aprobada"),
    ("PF-12", "Reportes", "Revisar indicadores y descargar CSV.", "Cifras coherentes con los datos.", "Aprobada"),
    ("PS-01", "Aislamiento del donante", "Sesión de donante consulta tablas del personal, plantillas y bitácora.", "Cero filas o permiso denegado.", "Aprobada"),
    ("PS-02", "Resultado crítico", "Sesión de donante lee un resultado marcado crítico.", "No lo recibe.", "Aprobada"),
    ("PS-03", "Cuentas", "Sesión STAFF llama a /api/admin/users; ADMIN desactiva al último ADMIN.", "403 y 400 respectivamente.", "Aprobada"),
    ("PS-04", "Bitácora", "Sesión STAFF y DONOR consultan audit_logs.", "Sin acceso.", "Aprobada"),
    ("PS-05", "ARCO", "Descargar datos y anonimizar con confirmación.", "Archivo con los datos; ficha anonimizada y cuenta eliminada.", "Aprobada"),
    ("PS-06", "Rutas sin credencial", "POST sin token a las 6 rutas.", "401 en todas (04/10/2026).", "Aprobada"),
    ("PS-07", "Edición de la ficha por el donante", "UPDATE de phone, status y blood_type con sesión de donante.", "Debería rechazarse.", "**No aprobada (H-01); corrección preparada**"),
]


def pruebas(doc):
    U.h1(doc, "12. Pruebas y verificación")
    U.h2(doc, "12.1 Estrategia")
    U.parrafo(doc, "El proyecto no cuenta con pruebas automatizadas (H-11). La calidad se aseguró con cuatro mecanismos: (1) **compilación con TypeScript estricto** como puerta antes de cada despliegue; "
                   "(2) **pruebas manuales por rol** con datos temporales que luego se eliminaron; (3) **pruebas de seguridad con sesiones reales** de cada rol contra la base de datos; "
                   "y (4) **verificaciones en producción** tras cada cambio. Este documento añade una propuesta concreta de automatización (sec. 12.5).", alineacion="justificado")
    U.h2(doc, "12.2 Verificaciones ejecutadas para este informe (04/10/2026)")
    U.tabla(doc, ["Verificación", "Resultado observado"], [
        ["`next build` (Next.js 16.3.8, Turbopack)", "Compilado en 21.7 s; verificación de tipos en 15.8 s; 9 páginas estáticas; rutas dinámicas: 6 `/api`; sin errores."],
        ["Rutas sin credencial (6 de 6)", "`POST /api/automations/run`, `/api/admin/users`, `/api/admin/users/manage`, `/api/admin/donors/anonymize`, `/api/communications/send`, `/api/communications/webhook` → **401**."],
        ["/health del reloj", "`{\"ok\": true, \"enabled\": true, \"dry_run\": false}`."],
        ["Catálogo de la base", "13 tablas con RLS; 23 políticas; 14 funciones; 9 triggers; 30 índices; PostgreSQL 17.11."],
        ["`npm audit --omit=dev`", "0 vulnerabilidades en las dependencias de ejecución."],
        ["Edición de la ficha por un donante (H-01)", "Antes de la migración 0004: un UPDATE de `phone` afectó 1 fila. Con la migración, dentro de una transacción deshecha: `phone`, `status` y `blood_type` fueron **rechazados**; activar o revocar el consentimiento, la edición por enfermería y la del servidor siguieron funcionando."],
        ["Escrituras del donante en otras tablas", "`UPDATE donation_results` → *permission denied*; `UPDATE profiles` y `UPDATE system_config` → 0 filas."],
    ], anchos=[5.4, 11.2], tam=8.5, primera_negrita=True, titulo="Evidencias")
    U.h2(doc, "12.3 Casos de prueba")
    U.tabla(doc, ["ID", "Objetivo", "Procedimiento", "Resultado esperado", "Estado"], [list(p) for p in PRUEBAS],
            anchos=[1.2, 3.0, 5.4, 4.4, 2.6], alinear=["c", "l", "l", "l", "l"], tam=7.5, titulo="Pruebas funcionales (PF) y de seguridad (PS)")
    U.h2(doc, "12.4 Script de verificación de permisos")
    U.codigo(doc, """const c = createClient(URL, ANON_KEY);
await c.auth.signInWithPassword({ email: 'dni-<DNI>@login.hemocax.org', password: '…' });   // sesión de DONANTE
console.log((await c.from('audit_logs').select('id')).data);             // []      sin acceso
console.log((await c.from('message_templates').select('type')).data);    // []
console.log((await c.from('donation_results').select('id,critical')).data); // solo los suyos, liberados y no críticos
const r = await c.from('donors').update({ phone: '900000001' }).eq('id', miId).select('id');
// H-01: devuelve 1 fila (debería rechazarse)""", titulo="Prueba de aislamiento con la API (Node 20+)")
    U.parrafo(doc, "Para probar migraciones sin dejar cambios se usa una transacción con `set local role authenticated` y `set_config('request.jwt.claims', …)` que simula la sesión de un usuario y termina en `ROLLBACK` (`docs/informe-tecnico/probar_migracion_donante.js`).", tam=9.5)
    U.h2(doc, "12.5 Pruebas automatizadas propuestas")
    U.tabla(doc, ["Nivel", "Qué probar", "Herramienta sugerida", "Prioridad"], [
        ["Unitarias", "`computeEligibility`, `parseCsv`/`mapDonorRows`, `renderEmail` (escape de HTML), `limaToday`", "Vitest", "Alta"],
        ["Base de datos", "RLS por rol, triggers (máximo anual con dos sesiones), funciones de resultados, anonimización", "pgTAP o scripts Node con sesiones reales", "Alta"],
        ["Rutas /api", "401/403/400, reversión al crear cuenta, 403 sin consentimiento, simulación", "Vitest + `fetch` contra `next start`", "Media"],
        ["Extremo a extremo", "Ingreso, registrar donación, liberar y ver el resultado como donante", "Playwright", "Media"],
        ["Accesibilidad", "Reglas WCAG en las dos pantallas principales", "axe-core", "Baja"],
    ], anchos=[2.6, 7.2, 4.6, 2.2], tam=8.5, titulo="Plan de automatización")
    U.codigo(doc, """// tests/eligibility.test.ts  (Vitest)
import { computeEligibility } from '@/lib/eligibility';
const params = { limits: { M: 4, F: 3 }, intervals: { M: 90, F: 90 } };

test('mujer con 3 donaciones este año → MAXIMO', () => {
  const r = computeEligibility({ gender: 'F', active: true, today: '2026-10-04', params,
    donationDates: ['2026-01-12', '2026-04-10', '2026-07-14'] });
  expect(r.state).toBe('MAXIMO');
  expect(r.eligibleFrom).toBe('2027-01-01');
});
test('última donación hace 40 días → ESPERA', () => {
  const r = computeEligibility({ gender: 'M', active: true, today: '2026-10-04', params, donationDates: ['2026-08-25'] });
  expect(r.state).toBe('ESPERA'); expect(r.eligibleFrom).toBe('2026-11-23');
});""", titulo="Ejemplo de prueba unitaria")
    U.codigo(doc, """# .github/workflows/ci.yml (propuesta)
name: ci
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npx vitest run
      - run: npm run build""", titulo="Integración continua (propuesta)")
    U.h2(doc, "12.6 Cobertura y brechas")
    U.tabla(doc, ["Área", "Cobertura actual", "Brecha"], [
        ["Tipos y compilación", "Total (strict)", "—"],
        ["Reglas de negocio (aptitud, máximo anual)", "Manual", "Sin regresión automática"],
        ["Seguridad (RLS)", "Manual con sesiones reales", "No automatizada; H-01 se detectó recién en esta revisión"],
        ["Rutas /api", "Manual + 401 verificado", "Sin pruebas de casos felices ni de error automatizadas"],
        ["Interfaz", "Manual en escritorio y celular", "Sin pruebas e2e ni de accesibilidad"],
        ["Automatizaciones", "Manual (simulación y plantilla sin aprobar)", "Sin prueba con reloj simulado ni de carga"],
    ], anchos=[5.0, 5.4, 6.2], tam=8.5, titulo="Cobertura")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def rendimiento(doc):
    U.h1(doc, "13. Rendimiento y escalabilidad")
    U.h2(doc, "13.1 Mediciones disponibles")
    U.tabla(doc, ["Medida", "Valor"], [
        ["Cliente (JS + CSS)", "952 KB sin comprimir · 276 KB con gzip · 16 archivos"],
        ["Fragmento del portal del donante", "19.6 KB (7.1 KB gzip) + 6.7 KB de CSS (2.0 KB gzip)"],
        ["Fragmento del panel del personal", "91.6 KB (24.5 KB gzip)"],
        ["Compilación", "21.7 s + 15.8 s de tipos; 9 páginas estáticas en 3.0 s"],
    ], anchos=[6.0, 10.6], tam=8.5, primera_negrita=True, titulo="Mediciones (build de producción)")
    U.parrafo(doc, "No se midieron tiempos de respuesta de la API bajo carga: el piloto es de escala pequeña y no se ejecutó una prueba de carga (brecha). La meta de diseño es un portal visible en ≤ 3 s en 4G.", tam=9.5)
    U.h2(doc, "13.2 Límites y cuellos de botella")
    U.tabla(doc, ["Límite", "Efecto", "Mitigación"], [
        ["1 000 filas por consulta (PostgREST)", "Listas y reportes incompletos con padrones grandes (H-12)", "Paginación; vistas/RPC con agregados en SQL"],
        ["Cálculo de aptitud en el navegador para todos los donantes", "Mayor uso de memoria y CPU en celulares con miles de donantes", "Calcular en el servidor o paginar"],
        ["Envío secuencial con límite de 60 s", "Pocas centenas de correos por ejecución (H-08)", "Cola de envío o lotes"],
        ["Gmail (≈ 500 envíos/día)", "Campañas masivas no caben", "Servicio de correo transaccional"],
        ["Supabase Free (500 MB; pausa por inactividad)", "Límite de datos y arranque en frío", "Plan de pago o limpieza; actividad periódica"],
        ["Render Free (se duerme a los 15 min)", "El reloj puede no ejecutar una tarea", "Monitor externo o plan de pago"],
        ["Serialización por donante en el trigger", "Sin efecto práctico (solo bloquea al mismo donante)", "—"],
    ], anchos=[5.4, 6.0, 5.2], tam=8.5, titulo="Límites")
    U.h2(doc, "13.3 Evolución recomendada")
    U.numerada(doc, [
        "Vista o función SQL que devuelva la aptitud y los agregados de reportes por grupo; el cliente solo muestra.",
        "Paginación del lado del servidor en *Donantes*, *Correos enviados* y *Actividad* (`range()` de PostgREST).",
        "Cola de envíos (tabla `PENDING` + proceso que la consuma por lotes) para desacoplar el envío del tiempo de la petición.",
        "Servicio de correo transaccional y subdominio institucional con SPF/DKIM para mejorar la entrega.",
        "Estrategia de caché y compresión ya cubiertas por la CDN de Vercel; evaluar *Edge* solo si la latencia lo exige.",
    ])
    U.salto_pagina(doc)


def hallazgos(doc):
    U.h1(doc, "14. Hallazgos, limitaciones y deuda técnica")
    U.parrafo(doc, "Resultado de la revisión técnica del 04/10/2026. La severidad considera el impacto en datos de salud y la probabilidad en el contexto del piloto.", alineacion="justificado")
    U.seccion(doc, horizontal=True)
    U.tabla(doc, ["ID", "Hallazgo", "Evidencia", "Severidad", "Impacto", "Propuesta", "Estado"], [list(h) for h in HALLAZGOS],
            anchos=[1.1, 6.0, 5.6, 1.9, 3.8, 5.2, 2.6], alinear=["c", "l", "l", "c", "l", "l", "l"], tam=7.3, titulo="Registro de hallazgos")
    U.seccion(doc, horizontal=False)
    U.caja(doc, "**H-01** es el único hallazgo de severidad alta y tiene corrección lista: la migración `20261004000400_restrict_donor_self_update.sql`, probada en una transacción que se deshizo. "
                "Hasta aplicarla, la documentación que afirme que el donante «solo puede cambiar sus columnas de consentimiento» es incorrecta.", titulo="Prioridad inmediata", color="FDEDEC")
    U.h2(doc, "14.1 Limitaciones funcionales")
    U.viñetas(doc, [
        "Solo correo electrónico: un donante sin correo o sin internet no recibe avisos (SMS como trabajo futuro).",
        "Las campañas no se pueden programar a una fecha futura.",
        "Sin recuperación de contraseña autónoma: la restablece un administrador.",
        "Los valores clínicos (intervalo de 90 días, máximos 4 y 3) son provisionales hasta su validación por el médico responsable.",
        "El sistema no se integra con el sistema actual del hospital.",
    ])


def hoja_ruta(doc):
    U.h1(doc, "15. Hoja de ruta técnica")
    U.tabla(doc, ["Plazo", "Acción", "Hallazgos", "Esfuerzo"], [
        ["Inmediato (días)", "Aplicar la migración 0004; actualizar la matriz de permisos del README; rotar las claves compartidas por mensajería.", "H-01", "≈ 1 h"],
        ["Inmediato", "Aprobar plantillas, validar valores clínicos y definir el costo recurrente (decisiones del hospital).", "—", "Gestión"],
        ["Corto (1-2 semanas)", "Migración: máximo anual leído de `system_config`; trigger de `updated_at`; estado de simulación; cabeceras de seguridad; `timingSafeEqual`.", "H-02, H-03, H-07, H-14, H-15", "≈ 1 día"],
        ["Corto", "Pruebas unitarias de aptitud y CSV, pruebas de RLS con sesiones reales y CI.", "H-11", "≈ 2-3 días"],
        ["Medio (1-2 meses)", "Cola de envíos; paginación y agregados en SQL; forzar cambio de contraseña inicial; evaluar cookies httpOnly.", "H-06, H-08, H-12, H-13", "≈ 1-2 semanas"],
        ["Medio", "Canal SMS para donantes sin correo; campañas programadas; recuperación de contraseña.", "—", "≈ 2-3 semanas"],
        ["Limpieza", "Mover el código heredado a una rama de archivo; retirar `@supabase/ssr` si no se adopta; decidir `CONSULTED` y `notifications`.", "H-04, H-09, H-10, H-16", "≈ 0.5 día"],
    ], anchos=[2.8, 8.6, 3.2, 2.0], tam=8.5, titulo="Plan de mejoras priorizado")


# ------------------------------------------------------------------------------------------------
def anexos(doc):
    U.h1(doc, "ANEXOS")
    U.h2(doc, "Anexo A. Inventario de archivos")
    inv = M.inventario()
    filas = [[ruta, str(n), prop] for ruta, n, prop in inv]
    filas.append(["**Total**", f"**{sum(n for _, n, _ in inv):,}**", ""])
    U.tabla(doc, ["Archivo", "Líneas", "Propósito"], filas, anchos=[7.0, 1.4, 8.2], alinear=["l", "c", "l"], tam=7.5, titulo="Archivos de código fuente (recuento automático al generar el informe)")
    U.h2(doc, "Anexo B. Glosario")
    U.tabla(doc, ["Término", "Significado"], [
        ["RLS", "Row Level Security: la base de datos añade condiciones a cada consulta según el usuario."],
        ["JWT", "Token firmado que identifica al usuario y su rol en cada petición."],
        ["PostgREST", "Servicio que expone las tablas y funciones de PostgreSQL como API REST."],
        ["service_role", "Rol de Supabase que omite RLS; solo para el servidor."],
        ["SECURITY DEFINER", "Función que se ejecuta con los privilegios de quien la definió."],
        ["Route Handler", "Función de servidor de Next.js asociada a una ruta HTTP."],
        ["Trigger", "Procedimiento que la base ejecuta automáticamente ante un INSERT/UPDATE/DELETE."],
        ["DRY_RUN", "Modo de simulación: calcula pero no envía ni registra."],
        ["ARCO", "Acceso, rectificación, cancelación y oposición del titular de datos."],
        ["ADR", "Registro de una decisión arquitectónica."],
    ], anchos=[3.4, 13.2], tam=8.5, primera_negrita=True)
    U.h2(doc, "Anexo C. Referencias")
    for ref in [
        "Next.js Documentation (v16): App Router, Route Handlers y Turbopack. Vercel.",
        "Supabase Documentation: Auth, PostgREST y Row Level Security. Supabase Inc.",
        "PostgreSQL 17 Documentation: Row Security Policies, Triggers y Explicit Locking (SELECT … FOR UPDATE). PostgreSQL Global Development Group.",
        "Nodemailer Documentation: SMTP transport. Andris Reinman.",
        "OWASP Top 10 – 2021. OWASP Foundation.",
        "ISO/IEC 25010:2011. Systems and software engineering — SQuaRE — System and software quality models.",
        "Ley N.° 29733, Ley de Protección de Datos Personales (Perú), y su reglamento, D.S. N.° 016-2024-JUS.",
        "Bass, L., Clements, P. y Kazman, R. (2021). *Software Architecture in Practice* (4.ª ed.). Addison-Wesley.",
    ]:
        U.parrafo(doc, ref, tam=9.5, despues=3)


def construir(doc):
    despliegue(doc)
    pruebas(doc)
    rendimiento(doc)
    hallazgos(doc)
    hoja_ruta(doc)
    anexos(doc)
