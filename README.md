# HEMOCAX

Portal piloto para donantes del Banco de Sangre HRDC. La aplicación Next.js está preparada para desplegarse en Vercel y leer datos desde Supabase. El antiguo prototipo JSON sigue disponible únicamente para demostración local (`npm run legacy:demo`); no usarlo para datos personales.

## Desarrollo y despliegue

Requiere Node.js 20.9 o posterior. Instala dependencias con `pnpm install` o `npm install` y ejecuta `npm run dev`. Para Vercel, importar este repositorio y configurar las variables de entorno indicadas en `.env.example`.

En Supabase, ejecuta `supabase/migrations/20260927000100_initial_schema.sql` en un proyecto nuevo. Configura en Vercel `NEXT_PUBLIC_SUPABASE_URL` y `NEXT_PUBLIC_SUPABASE_ANON_KEY`. `SUPABASE_SERVICE_ROLE_KEY` es solo para operaciones de servidor; no exponerla en el navegador. `NEXT_PUBLIC_SUPABASE_URL` y la clave anon no sustituyen las políticas RLS.

### Inicio por DNI

El portal convierte el DNI de ocho dígitos al identificador de acceso `dni-<DNI>@login.hemocax.org` para autenticarlo con Supabase Auth y contraseña. Las cuentas y perfiles deben ser provisionados en Supabase Auth/`profiles`; para donantes, `donors.auth_user_id` debe apuntar al mismo usuario. No habilitar auto-registro público: el personal debe verificar identidad y asignar permisos desde un proceso administrativo seguro. No reutilizar credenciales demo.

El esquema limita sangre total a 4 donaciones/año para sexo M y 3 para sexo F, con protección en base de datos ante registros simultáneos. El intervalo entre donaciones de 90 días sigue siendo solo un valor provisional de configuración: la elegibilidad individual debe confirmarla el personal clínico. Resultados críticos no se muestran en el portal; solo personal con autorización puede liberar los no críticos.

## Automatizaciones Python y correo

El servicio en `automations/worker.py` reemplaza n8n: cumpleaños 08:00, recordatorio de retorno 08:15, agradecimientos 08:30 y reconocimiento anual 08:45, en `America/Lima`. Usa solo la biblioteca estándar de Python (`smtplib`/`email`, sin dependencias nuevas). Para correrlo localmente, inicia la app, configura los secretos en `.env` y ejecuta `python automations/worker.py`; su estado se ve en `http://localhost:8787/health`. `python automations/worker.py --once BIRTHDAY` permite consultar candidatos manualmente. También puedes correrlo en Docker con `docker compose up -d --build automations`. El callback local usa `AUTOMATION_WEBHOOK_URL=http://localhost:8787/email` y los mismos secretos compartidos en `.env`.

Por seguridad `AUTOMATIONS_ENABLED=false` y `AUTOMATION_DRY_RUN=true` por defecto. En simulación consulta los candidatos sin registrar comunicaciones ni mandar correos. Para activarlo solo se requiere un buzón SMTP (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM_ADDRESS`): puede ser Gmail/Outlook con una contraseña de aplicación, o el SMTP de un dominio propio. No se necesita plantilla aprobada por ningún tercero. Guardar credenciales localmente en `.env` (ignorado por git) y en el gestor seguro del proveedor al desplegar; nunca en el repositorio. Habilitar envíos reales solo después de validar consentimiento y el flujo con el equipo.

Las exportaciones previas de n8n se conservan como referencia histórica en `n8n/`; ya no forman parte del despliegue.

## Backoffice de personal

El personal con perfil STAFF o ADMIN accede, con el mismo inicio por DNI, a un panel con pestañas: donantes (alta y búsqueda), donaciones (registro, el límite anual se aplica por un trigger en la base de datos), resultados (liberar resultados no críticos), campañas y comunicaciones (envío manual/masivo por correo), y para ADMIN además bitácora de auditoría y cuentas. Casi todo el panel llama directamente a Supabase desde el navegador y se apoya en las mismas políticas de RLS del esquema (`is_staff()`, `current_role()`); solo el aprovisionamiento de cuentas nuevas (`/api/admin/users`) y el puente con el worker de Python (`/api/communications/send`, `/api/communications/webhook`, `/api/automations/run`) corren en el servidor con la clave de servicio, porque son operaciones que la Auth API o el worker necesitan fuera de una sesión de usuario. Cualquier cuenta autenticada puede cambiar su propia contraseña desde "Mi cuenta".

## Estado y cuidado de datos

La vista del donante y la migración Supabase son el inicio de la migración del prototipo; las funciones administrativas, aprovisionamiento seguro de usuarios y conexión de producción deben completarse antes de operar con datos reales. La versión de demostración usa `data/demo.json` y datos ficticios. No se afirma que la aplicación esté desplegada, conectada a una cuenta Supabase/Vercel, ni aprobada para producción. Requiere revisión clínica, privacidad/consentimiento, seguridad y pruebas de aceptación del HRDC antes del piloto real.
