# -*- coding: utf-8 -*-
"""Recuento de líneas e inventario de archivos del repositorio (se calcula al generar el informe)."""
import os

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _lineas(ruta):
    with open(ruta, encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)


def _archivos(carpeta, exts):
    out = []
    base = os.path.join(RAIZ, carpeta)
    for dp, _dn, fn in os.walk(base):
        for n in sorted(fn):
            if n.endswith(exts):
                out.append(os.path.join(dp, n))
    return sorted(out)


def metricas():
    app = [p for p in _archivos("app", (".ts", ".tsx"))]
    lib = [p for p in _archivos("lib", (".ts", ".tsx"))]
    css = _archivos("app", (".css",))
    sql = [p for p in _archivos("supabase/migrations", (".sql",)) if "20261004000400" not in p]
    py = [os.path.join(RAIZ, "automations", "worker.py")]
    return dict(
        loc_app=sum(map(_lineas, app)), loc_lib=sum(map(_lineas, lib)), n_ts=len(app) + len(lib),
        loc_ts=sum(map(_lineas, app)) + sum(map(_lineas, lib)),
        loc_css=sum(map(_lineas, css)), n_css=len(css), loc_sql=sum(map(_lineas, sql)), n_sql=len(sql),
        loc_py=sum(map(_lineas, py)),
    )


PROPOSITO = {
    "app/layout.tsx": "Raíz: fuentes, metadatos y hoja de estilos global",
    "app/page.tsx": "Inicio de sesión por DNI y reparto según el rol",
    "app/DonorPortal.tsx": "Portal del donante (estado, resultado, campañas, avisos, datos)",
    "app/donorIcons.tsx": "Íconos SVG en línea del portal",
    "app/portal.css": "Estilos globales y del panel del personal",
    "app/donor.css": "Estilos del portal del donante (1 y 2 columnas)",
    "app/staff/StaffPanel.tsx": "Menú, pestañas y avisos del personal",
    "app/staff/HomeTab.tsx": "Inicio: buscador, pendientes y alertas",
    "app/staff/DonorsTab.tsx": "Lista de donantes con filtros",
    "app/staff/DonorFicha.tsx": "Ficha del donante y acciones",
    "app/staff/DonorModals.tsx": "Formularios: donante, donación, consentimiento, datos y privacidad",
    "app/staff/ImportDonors.tsx": "Importación masiva desde CSV",
    "app/staff/useDirectory.ts": "Hook: donantes + donaciones + aptitud",
    "app/staff/ResultsTab.tsx": "Resultados: liberar, crítico, avisar",
    "app/staff/CampaignsTab.tsx": "Campañas e información",
    "app/staff/EmailsTab.tsx": "Historial y envío manual de correos",
    "app/staff/ReportsTab.tsx": "Indicadores y descargas CSV",
    "app/staff/AccountsTab.tsx": "Cuentas por puesto",
    "app/staff/ParamsTab.tsx": "Parámetros, consentimiento y plantillas",
    "app/staff/AuditTab.tsx": "Bitácora de actividad",
    "app/staff/HelpTab.tsx": "Ayuda por puesto",
    "app/staff/MyAccountTab.tsx": "Cambio de contraseña propia",
    "app/staff/ui.tsx": "Componentes y etiquetas comunes (Modal, Badge, friendlyError…)",
    "app/staff/api.ts": "callApi(): POST con Bearer",
    "app/api/admin/users/route.ts": "Crear cuenta (Auth + perfil + vínculo)",
    "app/api/admin/users/manage/route.ts": "Restablecer contraseña, activar/desactivar, permiso",
    "app/api/admin/donors/anonymize/route.ts": "Anonimizar donante y borrar su cuenta",
    "app/api/communications/send/route.ts": "Enviar un correo y registrar su estado",
    "app/api/communications/webhook/route.ts": "(Heredada) callback del reloj",
    "app/api/automations/run/route.ts": "Ejecutar una automatización diaria",
    "lib/eligibility.ts": "Cálculo de aptitud (función pura)",
    "lib/params.ts": "Lectura de system_config → Params",
    "lib/csv.ts": "Parser y validador de CSV de donantes",
    "lib/email.ts": "Transporte SMTP (nodemailer)",
    "lib/emailTemplate.ts": "Plantilla HTML y texto del correo",
    "lib/communications.ts": "deliverCommunication(): envía y guarda el estado",
    "lib/adminGuard.ts": "requireAdmin() para rutas de administración",
    "lib/supabase/client.ts": "Cliente de Supabase del navegador",
    "lib/supabase/server.ts": "Clientes de servidor (service_role y por usuario)",
    "automations/worker.py": "Reloj diario y /health (Python)",
    "automations/Dockerfile": "Imagen del reloj",
    "supabase/migrations/20260927000100_initial_schema.sql": "Tablas base, RLS, trigger del máximo anual, liberar resultado",
    "supabase/migrations/20261002000200_pilot_features.sql": "Críticos, consentimiento, auditoría, plantillas, ARCO",
    "supabase/migrations/20261003000300_contact_info.sql": "Datos de contacto visibles al donante",
}


def inventario():
    filas = []
    for carpeta, exts in (("app", (".ts", ".tsx", ".css")), ("lib", (".ts", ".tsx")), ("automations", (".py",)), ("supabase/migrations", (".sql",))):
        for p in _archivos(carpeta, exts):
            rel = os.path.relpath(p, RAIZ).replace("\\", "/")
            if "20261004000400" in rel:
                continue
            filas.append((rel, _lineas(p), PROPOSITO.get(rel, "")))
    dock = os.path.join(RAIZ, "automations", "Dockerfile")
    filas.append(("automations/Dockerfile", _lineas(dock), PROPOSITO["automations/Dockerfile"]))
    return filas
