# -*- coding: utf-8 -*-
"""Informe técnico — portada, introducción, requisitos, arquitectura y pila tecnológica."""
import os
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

import docx_utils as U
import metricas as M

FIG = "fig/"


def portada(doc):
    def centro(texto, tam, negrita=False, color=None, antes=0, despues=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(texto)
        r.font.size = Pt(tam)
        r.bold = negrita
        if color:
            r.font.color.rgb = color
        p.paragraph_format.space_before = Pt(antes)
        p.paragraph_format.space_after = Pt(despues)

    centro("UNIVERSIDAD NACIONAL DE CAJAMARCA", 16, True, U.AZUL, 10)
    centro("Facultad de Ingeniería", 12)
    centro("Escuela Académico Profesional de Ingeniería de Sistemas", 12, despues=50)
    centro("INFORME TÉCNICO", 14, True, RGBColor(0x7F, 0x8C, 0x8D), 20, 6)
    centro("HEMOCAX", 44, True, U.AZUL, 4, 8)
    centro("Arquitectura, diseño e implementación de la plataforma digital para la fidelización y retención del donante voluntario de sangre", 14, True, None, 0, 8)
    centro("Hospital Regional Docente de Cajamarca — Servicio de Hemoterapia y Banco de Sangre", 11.5, False, None, 0, 40)
    centro("Next.js · React · TypeScript · Supabase (PostgreSQL con seguridad por filas) · Python · SMTP", 10.5, False, RGBColor(0x55, 0x55, 0x55), 0, 40)
    centro("Equipo de desarrollo", 11, True, None, 6, 6)
    for linea in ("Diana Michelle Barrantes Gallardo — Project Manager", "Jesús Arturo Valdiviezo Zavaleta — Líder Técnico y base de datos",
                  "Scarlet Sahori Terrones Cerna — Frontend", "Darick André Pérez Briceño — Integraciones y automatizaciones",
                  "Dider Anthony Díaz Becerra — QA y seguridad de datos", "Adriana Anthonela Limay Rodríguez — Análisis funcional y UX"):
        centro(linea, 10.5, False, None, 0, 1)
    centro("Versión 1.0 · Cajamarca, octubre de 2026", 11, False, None, 30, 2)
    centro("Repositorio: github.com/dm-barr/hemocax  ·  Producción: hemocax.vercel.app", 10, False, RGBColor(0x55, 0x55, 0x55), 0, 0)
    U.salto_pagina(doc)


def control(doc):
    U.h1(doc, "Control del documento")
    U.tabla(doc, ["Versión", "Fecha", "Autor", "Descripción"], [
        ["1.0", "04/10/2026", "Equipo HEMOCAX", "Primera versión del informe técnico. Describe el sistema desplegado en producción y el estado del repositorio a esa fecha."],
    ], anchos=[1.6, 2.4, 3.6, 9.0], tam=9)
    U.caja(doc, "Este informe es **netamente técnico**. La gestión del proyecto (alcance, cronograma, costos, riesgos, calidad, recursos) está en el *Informe de Gestión de Proyectos*; "
                "el funcionamiento para los usuarios, en el README y en la ayuda integrada del sistema.", color="EAF2FB")
    U.h1(doc, "Contenido")
    U.indice(doc)
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def introduccion(doc):
    m = M.metricas()
    U.h1(doc, "1. Introducción")
    U.h2(doc, "1.1 Propósito y audiencia")
    U.parrafo(doc, "Este documento describe cómo está construido HEMOCAX: su arquitectura, modelo de datos, mecanismos de seguridad, algoritmos, interfaces, despliegue, pruebas y limitaciones. "
                   "Está dirigido a quienes deban **operar, auditar o mantener** el sistema (Oficina de Estadística e Informática del HRDC, evaluadores técnicos y futuros desarrolladores) "
                   "y asume conocimientos de desarrollo web, bases de datos relacionales y HTTP.", alineacion="justificado")
    U.h2(doc, "1.2 Alcance")
    U.viñetas(doc, [
        "**Incluye:** el portal web (panel del personal y portal del donante), las rutas del servidor, el esquema de PostgreSQL con sus políticas de seguridad, el reloj de recordatorios en Python y el procedimiento de despliegue.",
        "**No incluye:** la gestión del proyecto (otro informe), manuales de usuario ni el sistema informático actual del hospital, con el que HEMOCAX no se integra.",
    ])
    U.h2(doc, "1.3 Resumen del sistema")
    U.parrafo(doc, "HEMOCAX es una aplicación web que permite al Banco de Sangre del Hospital Regional Docente de Cajamarca mantener una relación sostenida con el donante voluntario. "
                   "El personal registra donantes y donaciones, libera resultados no críticos y convoca por correo; el donante entra con su DNI y ve, en una sola pantalla, si puede volver a donar, su resultado y dónde acudir. "
                   "Un reloj diario envía recordatorios, agradecimientos y saludos. Los resultados críticos jamás se comunican por el canal digital.", alineacion="justificado")
    U.tabla(doc, ["Módulo", "Ubicación principal en el código", "Datos que maneja"], [
        ["Acceso y sesión", "app/page.tsx · lib/supabase/client.ts", "auth.users, profiles"],
        ["Padrón y ficha del donante", "app/staff/DonorsTab, DonorFicha, DonorModals, ImportDonors · lib/csv.ts", "donors"],
        ["Donaciones y aptitud", "app/staff/DonorModals (DonationModal) · lib/eligibility.ts · trigger SQL", "donations, system_config"],
        ["Resultados", "app/staff/ResultsTab · funciones SQL de liberación", "donation_results"],
        ["Consentimiento y derechos del titular", "DonorModals (ConsentModal, DataModal) · funciones SQL · /api/admin/donors/anonymize", "consent_versions, consent_events"],
        ["Correo y campañas", "app/staff/EmailsTab, CampaignsTab · /api/communications/send · lib/email.ts, emailTemplate.ts", "communications, campaigns, campaign_recipients"],
        ["Automatizaciones", "/api/automations/run · automations/worker.py", "message_templates, communications"],
        ["Portal del donante", "app/DonorPortal.tsx · donor.css", "lectura de donors, donations, donation_results, campaigns"],
        ["Administración", "app/staff/AccountsTab, ParamsTab, AuditTab, ReportsTab · /api/admin/users*", "profiles, system_config, audit_logs"],
    ], anchos=[3.8, 8.0, 4.8], tam=8.5, titulo="Módulos del sistema y su ubicación en el código")
    U.h2(doc, "1.4 El sistema en cifras")
    U.tabla(doc, ["Magnitud", "Valor", "Fuente"], [
        ["Código TypeScript/TSX", f"{m['loc_ts']:,} líneas en {m['n_ts']} archivos ({m['loc_app']:,} en app/ y {m['loc_lib']:,} en lib/)", "Recuento del repositorio"],
        ["Hojas de estilo (CSS)", f"{m['loc_css']} líneas en {m['n_css']} archivos", "Recuento del repositorio"],
        ["SQL (migraciones)", f"{m['loc_sql']} líneas en {m['n_sql']} archivos", "supabase/migrations/"],
        ["Python (reloj)", f"{m['loc_py']} líneas (biblioteca estándar, sin dependencias)", "automations/worker.py"],
        ["Tablas / políticas RLS / funciones / triggers / índices", "13 / 23 / 14 / 9 / 30", "Consulta al catálogo de la base en producción"],
        ["Rutas del servidor", "6 (todas rechazan con 401 una petición sin credencial)", "Verificación en producción, sección 12.2"],
        ["Pantallas del personal", "11 pestañas por rol; portal del donante de una pantalla", "app/staff/, app/DonorPortal.tsx"],
        ["Tipos de correo", "7 (BIRTHDAY, RETURN_REMINDER, DONATION_THANKS, FREQUENT_DONOR, CAMPAIGN, MANUAL, RESULT)", "lib/emailTemplate.ts"],
        ["Compilación de producción", "22 s de compilación + 16 s de verificación de tipos; 9 páginas estáticas", "next build (Turbopack)"],
        ["Tamaño del cliente", "952 KB en 16 archivos; 276 KB comprimidos (gzip)", "Medición del directorio .next/static"],
        ["Dependencias de ejecución", "5 (next, react, react-dom, @supabase/supabase-js, nodemailer) + @supabase/ssr declarada sin uso", "package.json"],
    ], anchos=[5.4, 7.6, 3.6], tam=8.5, titulo="Magnitudes del sistema (medidas al 04/10/2026)")
    U.h2(doc, "1.5 Convenciones")
    U.viñetas(doc, [
        "Los nombres de archivos, tablas, funciones y variables se escriben en `monoespaciado` o en bloques de código.",
        "**Camino A** = el navegador accede a Supabase con el JWT del usuario y decide la base de datos (RLS). **Camino B** = el navegador llama a una ruta `/api` del servidor, que valida y opera con la clave de servicio (sección 3.4).",
        "Las fechas de negocio se calculan en hora de Lima (UTC−5, sin horario de verano). Los instantes se guardan como `timestamptz`.",
        "Las referencias «sec. N» remiten a secciones de este documento.",
    ])
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def requisitos(doc):
    U.h1(doc, "2. Requisitos que guían el diseño")
    U.h2(doc, "2.1 Requisitos funcionales agrupados")
    U.tabla(doc, ["Grupo", "Requisitos", "Implicación técnica"], [
        ["Padrón y donaciones", "Alta, búsqueda, importación CSV, ficha, aptitud y registro de donaciones con máximo anual por sexo.", "Esquema relacional con restricciones; trigger de máximo anual; módulo compartido de aptitud."],
        ["Resultados", "Pendiente → liberado → avisado; marca de crítico; solo el médico libera; el donante nunca ve un crítico.", "Máquina de estados en la base; políticas RLS; funciones con permiso explícito."],
        ["Privacidad", "Consentimiento versionado con historial, revocación, descarga y anonimización, bitácora.", "Tablas de eventos; triggers de auditoría; función de anonimización; ruta con service_role para la cuenta de Auth."],
        ["Comunicación", "Correo individual y campañas dirigidas con vista previa; plantillas aprobables; sin duplicados.", "SMTP desde el servidor; índices únicos; estado de cada envío; plantilla HTML escapada."],
        ["Automatización", "Cumpleaños, recordatorio, agradecimiento y reconocimiento diarios en hora de Lima.", "Planificador externo + ruta protegida por secreto + modo seguro por defecto."],
        ["Administración", "Cuentas por puesto, parámetros, reportes y bitácora.", "Rutas con service_role solo para Auth; resto con RLS."],
    ], anchos=[3.0, 7.2, 6.4], tam=8.5, titulo="Requisitos funcionales y su implicación técnica")
    U.h2(doc, "2.2 Atributos de calidad (escenarios)")
    U.tabla(doc, ["Atributo", "Escenario", "Medida de respuesta", "Táctica adoptada"], [
        ["Confidencialidad", "Un donante autenticado intenta leer un resultado crítico o los datos de otro donante.", "Cero filas devueltas; sin error que revele existencia.", "RLS en 13 de 13 tablas; helpers SECURITY DEFINER (sec. 6.4)."],
        ["Integridad", "Dos enfermeras registran a la vez la última donación permitida de un donante.", "Solo una se guarda; la otra recibe el mensaje del máximo anual.", "Trigger BEFORE INSERT con SELECT … FOR UPDATE sobre el donante (sec. 7.2)."],
        ["Idempotencia", "El reloj corre dos veces o falla a medias.", "Ningún donante recibe el mismo correo automático dos veces.", "Índices únicos parciales + omisión del error 23505 (sec. 7.5)."],
        ["Usabilidad rural", "Un donante abre el portal en un celular de gama baja con 4G intermitente.", "Primera pantalla útil en ≤ 3 s; una sola columna.", "Carga diferida por rol, fuentes propias, sin librería de UI, SVG en línea (sec. 9.8)."],
        ["Disponibilidad", "El reloj gratuito se duerme o el servicio de correo falla.", "El portal y los envíos manuales siguen funcionando.", "Reloj desacoplado del envío; monitor externo recomendado de /health (sec. 11.6)."],
        ["Seguridad operativa", "Un despliegue mal configurado podría enviar correos reales.", "No sale ningún correo sin configuración explícita.", "AUTOMATION_DRY_RUN: solo el valor false envía (sec. 8.3)."],
        ["Auditabilidad", "Un administrador necesita saber quién cambió un dato sensible.", "Quién, qué campo y cuándo, sin guardar valores.", "audit_row_change en 5 tablas (sec. 7.3)."],
        ["Costo", "El piloto no tiene presupuesto de infraestructura.", "S/ 0 mensuales.", "Backend como servicio (BaaS), funciones sin estado, planes gratuitos."],
        ["Mantenibilidad", "Un nuevo desarrollador debe añadir una regla o pantalla.", "Cambios localizados; compilación detecta errores de tipos.", "TypeScript estricto, módulos pequeños, migraciones numeradas (sec. 9 y 11.5)."],
    ], anchos=[2.6, 5.4, 4.2, 4.4], tam=8, titulo="Escenarios de atributos de calidad")
    U.h2(doc, "2.3 Restricciones técnicas")
    U.tabla(doc, ["Restricción", "Origen", "Efecto en el diseño"], [
        ["Sin presupuesto de infraestructura", "Proyecto universitario", "Planes gratuitos de Vercel, Supabase, Render y Gmail; límites de cada uno (sec. 13)."],
        ["El plan gratuito del reloj bloquea el puerto SMTP", "Política de Render (hallazgo H-05)", "El envío sale de Vercel; el reloj solo decide cuándo (ADR-05)."],
        ["No integrar con el sistema actual del hospital", "Alcance acordado", "Base de datos propia e independiente."],
        ["Datos de salud sensibles (Ley N.° 29733)", "Normativa", "Seguridad por filas, consentimiento, minimización, ARCO."],
        ["Supabase devuelve como máximo 1 000 filas por consulta", "Configuración del servicio", "Listas y reportes pensados para escala de piloto (sec. 13)."],
        ["Gmail limita los envíos diarios", "Servicio gratuito", "No apto para campañas masivas; ruta de migración a un servicio transaccional."],
        ["Sin pruebas automatizadas", "Alcance del proyecto", "Verificación manual y por compilación; propuesta de pruebas en sec. 12.5."],
    ], anchos=[5.4, 3.6, 7.6], tam=8.5, titulo="Restricciones")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
ADR = [
    ("ADR-01", "Supabase (PostgreSQL + RLS + Auth) como backend principal",
     "Se necesitaba una base relacional con permisos por rol y por fila, autenticación y cero costo.",
     "Usar Supabase: Auth, PostgREST (API REST/RPC generada) y PostgreSQL con seguridad a nivel de filas.",
     "(+) La autorización vive en un solo lugar y se cumple aunque el cliente se manipule. (+) Menos código de servidor. (−) Dependencia del proveedor; límites del plan gratuito.",
     "Firebase (NoSQL, sin SQL ni triggers); servidor Node propio con PostgreSQL (más código y operación)."),
    ("ADR-02", "Next.js con una sola ruta y carga diferida por rol",
     "Dos audiencias (personal y donantes) con necesidades de peso y conexión muy distintas.",
     "Una página que decide el rol y carga con next/dynamic (ssr:false) solo el panel del personal o el portal del donante.",
     "(+) El portal del donante pesa unos 7 KB gzip propios. (−) Sin URL por pestaña; no hay SEO (no se requiere).",
     "Rutas separadas por rol; SPA con enrutador de cliente."),
    ("ADR-03", "Ingreso por DNI mediante un correo sintético",
     "Muchos donantes no tienen correo electrónico.",
     "El DNI se convierte en dni-<DNI>@login.hemocax.org, identificador interno de Supabase Auth; nunca se envían mensajes a esa dirección.",
     "(+) Ingreso simple para el donante. (−) Sin recuperación autónoma de contraseña: la restablece un administrador.",
     "Login por correo real; OTP por SMS (costo recurrente)."),
    ("ADR-04", "Reglas críticas dentro de la base de datos",
     "Las reglas de máximo anual, liberación de resultados y protección de críticos no pueden depender del navegador.",
     "Triggers, funciones SECURITY DEFINER, CHECK y políticas RLS.",
     "(+) Cumplimiento garantizado y atómico. (−) La regla del máximo anual está duplicada como parámetro en pantalla (hallazgo H-02).",
     "Validación solo en el cliente o en rutas del servidor."),
    ("ADR-05", "Enviar el correo desde el portal; el reloj solo planifica",
     "El plan gratuito de Render bloquea el puerto SMTP (error de red al conectar).",
     "worker.py llama a /api/automations/run; el envío con nodemailer ocurre en la función de Vercel.",
     "(+) Los envíos manuales no dependen del reloj. (−) Dos servicios que coordinar y compartir un secreto.",
     "Enviar desde Render con un puerto alternativo o API HTTP de correo."),
    ("ADR-06", "Plantillas aprobables y modo de envío seguro por defecto",
     "El hospital debe validar los textos y un error de configuración no debe enviar correos reales.",
     "message_templates.approved; AUTOMATION_DRY_RUN debe ser exactamente false para enviar; en simulación no se registra nada.",
     "(+) Seguridad operativa. (−) Una automatización no sale hasta que la Jefatura apruebe.",
     "Textos fijos en el código."),
    ("ADR-07", "Anti-duplicados con índices únicos parciales",
     "El reloj puede ejecutarse más de una vez por día.",
     "Índices únicos por (donante, año, tipo) o (donación, tipo) sobre communications; se ignora el error 23505.",
     "(+) Idempotencia garantizada por el motor. (−) Una fila simulada ocuparía el índice: por eso la simulación no inserta.",
     "Consultar antes de insertar (condición de carrera)."),
    ("ADR-08", "Auditoría por triggers con nombres de campos",
     "Se necesita trazabilidad sin copiar datos sensibles a la bitácora.",
     "audit_row_change registra acción, entidad y los nombres de los campos modificados, no sus valores.",
     "(+) Minimización de datos. (−) No permite reconstruir el valor anterior.",
     "Auditoría con valores antes/después (más riesgo de privacidad)."),
    ("ADR-09", "Aptitud calculada en un solo módulo",
     "Lista, ficha, portal y automatizaciones deben decir lo mismo.",
     "lib/eligibility.ts (función pura) importada por el navegador y por la ruta de automatización.",
     "(+) Una sola fuente de verdad y fácil de probar. (−) Parte de la regla (máximo anual) también vive en SQL.",
     "Cálculo en SQL con una vista."),
    ("ADR-10", "Cálculo de listas y reportes en el cliente",
     "Escala de piloto (cientos de donantes) y cero costo de servidor.",
     "Se descargan las filas permitidas por RLS y se calcula en memoria.",
     "(+) Simplicidad. (−) Límite de 1 000 filas por consulta y mayor consumo en el navegador a gran escala.",
     "Vistas o funciones SQL con paginación (propuesta, sec. 13)."),
    ("ADR-11", "Migraciones SQL manuales y numeradas",
     "Pocas migraciones y un único entorno.",
     "Archivos AAAAMMDDNNNN_nombre.sql aplicados en orden; no se editan una vez aplicados.",
     "(+) Sin herramienta adicional. (−) Sin control automático de qué migración está aplicada.",
     "Supabase CLI o Prisma Migrate."),
    ("ADR-12", "CSS plano sin librería de componentes",
     "Control del peso y del diseño para celulares de gama baja.",
     "Dos hojas de estilo propias (portal.css, donor.css) y componentes pequeños.",
     "(+) 276 KB totales de cliente. (−) Más trabajo de maquetación manual.",
     "Tailwind o una librería de UI."),
]


def arquitectura(doc):
    U.h1(doc, "3. Arquitectura")
    U.h2(doc, "3.1 Principios arquitectónicos")
    U.tabla(doc, ["N.°", "Principio", "Consecuencia"], [
        ["P1", "**La base de datos decide.** Los permisos y las reglas críticas viven en PostgreSQL.", "El navegador puede hablar directo con la API de datos; manipularlo no sirve."],
        ["P2", "**Servidor mínimo y sin estado.** Solo lo que ningún usuario común puede hacer pasa por una ruta con clave de servicio.", "Seis rutas; sin servidor siempre activo propio."],
        ["P3", "**Cada rol descarga lo suyo.** El código del personal no se envía al donante.", "Portal del donante ligero para redes lentas."],
        ["P4", "**Seguro por defecto.** Sin configuración explícita no se envía nada.", "AUTOMATION_DRY_RUN; plantillas sin aprobar; secretos obligatorios."],
        ["P5", "**Una fuente de verdad por regla.**", "lib/eligibility.ts, system_config, funciones SQL."],
        ["P6", "**Fallar de forma explícita.** Los errores técnicos se traducen a lenguaje claro y se registran.", "friendlyError; estados FAILED con motivo."],
    ], anchos=[1.0, 8.4, 7.2], alinear=["c", "l", "l"], tam=8.5, titulo="Principios")
    U.h2(doc, "3.2 Contexto del sistema")
    U.figura(doc, FIG + "contexto.png", 16.0, "Diagrama de contexto")
    U.h2(doc, "3.3 Contenedores")
    U.figura(doc, FIG + "contenedores.png", 16.4, "Contenedores, protocolos y credenciales")
    U.tabla(doc, ["Contenedor", "Tecnología", "Responsabilidad", "Credencial que usa"], [
        ["Navegador", "React 19, supabase-js 2.117", "Interfaz; llamadas a Supabase y a /api", "Clave pública (anon) + JWT del usuario"],
        ["Activos estáticos", "Next.js (Turbopack) en la CDN de Vercel", "JS/CSS comprimidos", "—"],
        ["Rutas /api", "Next.js Route Handlers (Node.js)", "Crear cuentas, restablecer contraseñas, anonimizar, enviar correo, correr automatizaciones", "JWT del usuario (rutas de personal) o secreto compartido (reloj); service_role hacia la base"],
        ["Supabase Auth", "GoTrue", "Identidad, contraseñas, JWT", "—"],
        ["PostgREST", "API REST y RPC sobre PostgreSQL", "Traduce HTTP en SQL con el rol y las claims del JWT", "—"],
        ["PostgreSQL", "17.11 (Supabase)", "Datos, RLS, triggers, funciones", "Roles anon, authenticated, service_role"],
        ["Reloj", "Python 3.12 en Docker (Render)", "Planificador diario + /health", "Secreto AUTOMATION_RUN_SECRET"],
        ["Correo", "Gmail SMTP, puerto 587 STARTTLS", "Entrega de mensajes", "Contraseña de aplicación (en Vercel)"],
    ], anchos=[2.8, 4.2, 5.4, 4.2], tam=8, titulo="Inventario de contenedores")
    U.h2(doc, "3.4 Los dos caminos de acceso a datos")
    U.tabla(doc, ["", "Camino A: navegador → Supabase", "Camino B: navegador → /api → Supabase"], [
        ["Credencial", "Clave pública + JWT del usuario", "JWT del usuario hacia la ruta; la ruta usa service_role"],
        ["Quién autoriza", "**PostgreSQL** (RLS, CHECK, triggers, funciones)", "**La ruta**, tras validar JWT y rol (o secreto)"],
        ["Cuándo se usa", "Lecturas, altas y ediciones de donantes y donaciones, liberar resultados (RPC), campañas, parámetros, consentimiento", "Crear usuarios de Auth, restablecer contraseñas, activar/desactivar cuentas, anonimizar, enviar correo, automatizaciones"],
        ["Por qué", "Menos código; la regla se cumple siempre", "Ningún usuario puede crear usuarios de Auth ni usar SMTP; la clave de servicio no puede salir del servidor"],
        ["Riesgo principal", "Una política RLS mal escrita (hallazgo H-01)", "Una ruta que olvide validar el rol"],
    ], anchos=[2.6, 6.8, 7.2], tam=8.5, primera_negrita=True, titulo="Comparación de los caminos")
    U.h2(doc, "3.5 Vista de despliegue")
    U.figura(doc, FIG + "despliegue.png", 14.5, "Topología de despliegue")
    U.tabla(doc, ["Servicio", "Plan", "Qué ejecuta", "Disparador de despliegue"], [
        ["Vercel", "Hobby", "Aplicación Next.js (estáticos + funciones /api)", "git push a main (build automático)"],
        ["Supabase", "Free", "Base de datos, Auth y PostgREST", "Migraciones SQL manuales"],
        ["Render", "Free (Docker)", "automations/worker.py", "git push que cambie /automations"],
        ["Gmail", "Cuenta gratuita", "Salida SMTP", "—"],
        ["UptimeRobot (recomendado)", "Gratuito", "Consulta /health del reloj cada 5 minutos para evitar que se duerma; configuración por confirmar", "—"],
    ], anchos=[2.6, 2.6, 7.2, 4.2], tam=8.5, titulo="Servicios de la topología")
    U.h2(doc, "3.6 Decisiones arquitectónicas (ADR)")
    for cod, titulo, contexto, decision, consecuencias, alternativas in ADR:
        U.tabla(doc, ["Campo", f"{cod} · {titulo}"], [
            ["Contexto", contexto], ["Decisión", decision], ["Consecuencias", consecuencias], ["Alternativas", alternativas],
        ], anchos=[2.6, 14.0], tam=8.5, primera_negrita=True, zebra=False)
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def pila(doc):
    U.h1(doc, "4. Pila tecnológica")
    U.h2(doc, "4.1 Componentes y versiones")
    U.tabla(doc, ["Componente", "Versión instalada", "Rol"], [
        ["Node.js", "≥ 20 (campo engines)", "Entorno de compilación y de las funciones /api"],
        ["Next.js", "16.3.8 (App Router, Turbopack)", "Framework web, compilación, Route Handlers"],
        ["React / React DOM", "19.3.0", "Interfaz de usuario"],
        ["TypeScript", "5.9.3 (strict)", "Tipado estático"],
        ["@supabase/supabase-js", "2.117.2", "Cliente de Auth y PostgREST (navegador y servidor)"],
        ["@supabase/ssr", "0.12.7", "Declarada pero **sin uso** en el código (hallazgo H-10)"],
        ["nodemailer", "10.0.13", "Envío SMTP desde las funciones de Vercel"],
        ["PostgreSQL", "17.11 (Supabase, aarch64)", "Base de datos"],
        ["Python", "3.12 (imagen slim) · solo biblioteca estándar", "Reloj de recordatorios (worker.py)"],
        ["Docker", "Dockerfile de 7 líneas", "Empaqueta el reloj para Render"],
    ], anchos=[4.4, 5.6, 6.6], tam=8.5, titulo="Pila tecnológica")
    U.h2(doc, "4.2 Configuración de compilación")
    U.codigo(doc, """// tsconfig.json (extracto)
"strict": true, "noEmit": true, "target": "ES2017", "moduleResolution": "bundler",
"isolatedModules": true, "jsx": "react-jsx", "paths": { "@/*": ["./*"] }

// next.config.ts
const nextConfig: NextConfig = { poweredByHeader: false };""", titulo="Configuración relevante")
    U.viñetas(doc, [
        "`strict: true` obliga a manejar nulos y tipos implícitos; la compilación de producción falla si hay un error de tipos (verificado en cada despliegue).",
        "El alias `@/*` evita rutas relativas largas (`@/lib/eligibility`).",
        "Se desactiva la cabecera `x-powered-by` para no revelar el framework.",
        "Las tipografías (DM Sans y Manrope) se descargan en la compilación con `next/font` y se sirven desde el mismo dominio: sin peticiones externas.",
    ])
    U.h2(doc, "4.3 Comandos del proyecto")
    U.tabla(doc, ["Comando", "Efecto"], [
        ["npm run dev", "Servidor de desarrollo con recarga (http://localhost:3000)"],
        ["npm run build", "Compilación de producción y verificación de tipos (puerta de calidad previa al push)"],
        ["npm start", "Sirve la compilación"],
        ["python automations/worker.py [--once TIPO]", "Reloj completo o una sola ejecución de una automatización"],
        ["node demo/seed-demo.js · limpiar-demo.js", "Crea y borra los datos de demostración (DNI 9900…)"],
    ], anchos=[6.6, 10.0], tam=8.5, titulo="Comandos")
    U.h2(doc, "4.4 Código heredado")
    U.parrafo(doc, "El repositorio conserva, solo como referencia histórica, un prototipo anterior (`server.js`, `public/`, `data/`), exportaciones de n8n (`n8n/`), `db/schema.sql` y un `docker-compose.yml`. "
                   "No forman parte del sistema en producción. Se recomienda moverlos a una rama de archivo (hallazgo H-09).", alineacion="justificado")
    U.salto_pagina(doc)


def construir(doc):
    introduccion(doc)
    requisitos(doc)
    arquitectura(doc)
    pila(doc)
