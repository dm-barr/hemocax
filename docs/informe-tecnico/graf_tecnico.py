# -*- coding: utf-8 -*-
"""Diagramas del informe técnico (Graphviz y Matplotlib)."""
import os
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

AQUI = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(AQUI, "fig")
os.makedirs(FIG, exist_ok=True)
AZUL, ROJO, VERDE, GRIS = "#1f4e79", "#c0392b", "#2e8b57", "#7f8c8d"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})

BASE = ('node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, margin="0.14,0.07"]; '
        'edge [color="#555555", fontname="Arial", fontsize=8.5]; ')


def _dot(nombre, cuerpo, dpi=170):
    src = os.path.join(FIG, nombre + ".dot")
    out = os.path.join(FIG, nombre + ".png")
    with open(src, "w", encoding="utf-8") as f:
        f.write(cuerpo)
    subprocess.run(["dot", "-Tpng", f"-Gdpi={dpi}", src, "-o", out], check=True)
    os.remove(src)
    return out


# ------------------------------------------------------------------------------------------------
def contexto():
    return _dot("contexto", 'digraph G { rankdir=LR; nodesep=0.45; ranksep=0.8; ' + BASE + '''
don [label="Donante\\n(navegador móvil o de escritorio)", fillcolor="#fdebd0"];
per [label="Personal del Banco de Sangre\\n(enfermería · médico · administrador)", fillcolor="#fdebd0"];
sis [label="HEMOCAX\\nportal web + base de datos + reloj", fillcolor="#1f4e79", fontcolor="white", fontsize=12];
gm [label="Gmail SMTP\\nsmtp.gmail.com:587 (STARTTLS)", fillcolor="#f5cba7"];
mon [label="Monitor externo (recomendado)\\n(UptimeRobot)", fillcolor="#eaeded"];
git [label="GitHub\\nrepositorio y CI/CD", fillcolor="#eaeded"];
don -> sis [label="HTTPS: consulta estado,\\nresultado y avisos"]; per -> sis [label="HTTPS: registra, libera,\\nconvoca y administra"];
sis -> gm [label="correos transaccionales"]; gm -> don [label="correo", style=dashed];
mon -> sis [label="GET /health", style=dashed]; git -> sis [label="despliegue", style=dashed];
}''')


def contenedores():
    return _dot("contenedores", 'digraph G { rankdir=LR; nodesep=0.35; ranksep=0.75; compound=true; ' + BASE + '''
nav [label="Navegador\\nReact 19 + supabase-js 2.117\\nsesión JWT persistida", fillcolor="#fdebd0"];
subgraph cluster_v { label="Vercel (funciones sin estado + CDN)"; style="rounded"; color="#2e86c1"; fontname="Arial"; fontsize=10;
  est [label="Activos estáticos\\nJS/CSS ≈ 276 KB gzip", fillcolor="#d6eaf8"];
  api [label="Route Handlers /api/*\\n(Node.js, TypeScript)\\n6 rutas", fillcolor="#d6eaf8"];
  mail [label="lib/email.ts\\nnodemailer 10", fillcolor="#d6eaf8"]; }
subgraph cluster_s { label="Supabase"; style="rounded"; color="#2e8b57"; fontname="Arial"; fontsize=10;
  auth [label="GoTrue (Auth)\\nemite JWT", fillcolor="#d5f5e3"];
  rest [label="PostgREST\\nAPI REST + RPC", fillcolor="#d5f5e3"];
  pg [label="PostgreSQL 17\\n13 tablas · 23 políticas RLS\\n14 funciones · 9 triggers", fillcolor="#abebc6"]; }
rel [label="Render (Docker)\\nworker.py (Python 3.12)\\nreloj + /health :8787", fillcolor="#f5cba7"];
gm [label="Gmail SMTP", fillcolor="#f5cba7"];
nav -> est [label="HTTPS GET"]; nav -> auth [label="login (password grant)"]; nav -> rest [label="REST con Bearer JWT\\n(camino A: RLS decide)"];
nav -> api [label="POST + Bearer JWT\\n(camino B)"]; rest -> pg; auth -> pg; api -> rest [label="service_role"]; api -> mail; mail -> gm [label="SMTP 587"];
rel -> api [label="POST /api/automations/run\\nx-hemocax-automation-secret"];
}''')


def despliegue():
    return _dot("despliegue", 'digraph G { rankdir=TB; nodesep=0.4; ranksep=0.55; ' + BASE + '''
dev [label="Desarrollo\\nnpm run dev · npm run build", fillcolor="#fdebd0"];
gh [label="GitHub (rama main)\\ndm-barr/hemocax", fillcolor="#eaeded"];
subgraph cluster_prod { label="Producción"; style="rounded,dashed"; color="#888888"; fontname="Arial";
 v [label="Vercel\\nhemocax.vercel.app\\nbuild: next build (Turbopack)", fillcolor="#d6eaf8"];
 r [label="Render (Free, Docker)\\nhemocax.onrender.com\\nDockerfile en /automations", fillcolor="#f5cba7"];
 s [label="Supabase\\nproyecto ajdqklbdqpduzzoqyouy\\nmigraciones SQL manuales", fillcolor="#d5f5e3"];
 u [label="UptimeRobot (recomendado)\\nGET /health cada 5 min", fillcolor="#eaeded"]; }
sv [label="Variables de entorno de Vercel\\nSUPABASE_*, SMTP_*, AUTOMATION_*", shape=note, fillcolor="#fcf3cf"];
sr [label="Variables de entorno de Render\\nHEMOCAX_API_URL, AUTOMATION_RUN_SECRET,\\nAUTOMATIONS_ENABLED", shape=note, fillcolor="#fcf3cf"];
dev -> gh [label="git push"]; gh -> v [label="webhook: build y deploy"]; gh -> r [label="webhook: docker build"];
dev -> s [label="psql / SQL Editor\\n(migraciones en orden)", style=dashed]; sv -> v [style=dotted]; sr -> r [style=dotted];
r -> v [label="HTTPS (reloj)"]; v -> s [label="HTTPS"]; u -> r [label="/health", style=dashed];
}''')


def confianza():
    return _dot("confianza", 'digraph G { rankdir=LR; nodesep=0.4; ranksep=0.7; ' + BASE + '''
subgraph cluster_a { label="Zona NO confiable — Internet / navegador"; style="rounded,filled"; color="#f5b7b1"; fillcolor="#fdedec"; fontname="Arial";
  nav [label="Navegador del usuario\\nclave pública (anon)\\nJWT del usuario", fillcolor="white"]; }
subgraph cluster_b { label="Zona semiconfiable — Funciones del servidor (Vercel)"; style="rounded,filled"; color="#f9e79f"; fillcolor="#fef9e7"; fontname="Arial";
  api [label="Rutas /api\\nvalidan JWT o secreto\\nusan service_role", fillcolor="white"]; }
subgraph cluster_c { label="Zona confiable — Base de datos (Supabase)"; style="rounded,filled"; color="#abebc6"; fillcolor="#eafaf1"; fontname="Arial";
  db [label="PostgreSQL\\nRLS · triggers · funciones\\nSECURITY DEFINER", fillcolor="white"]; }
rel [label="Reloj (Render)\\nsolo conoce el secreto compartido", fillcolor="#f5cba7"];
gm [label="Gmail SMTP\\ncredencial en Vercel", fillcolor="#f5cba7"];
nav -> db [label="1. Con JWT: RLS decide", color="#2e8b57", fontcolor="#2e8b57"];
nav -> api [label="2. Bearer JWT: la ruta decide", color="#b9770e", fontcolor="#b9770e"];
api -> db [label="3. service_role (sin RLS)", color="#c0392b", fontcolor="#c0392b"]; rel -> api [label="secreto"]; api -> gm;
}''')


def estados_resultado():
    return _dot("estados_resultado", 'digraph G { rankdir=LR; nodesep=0.5; ranksep=0.7; ' + BASE + '''
ini [shape=circle, label="", width=0.2, fillcolor="#333333"];
p [label="PENDING", fillcolor="#fdebd0"]; a [label="AVAILABLE\\nvisible al donante", fillcolor="#d5f5e3"]; n [label="NOTIFIED\\nvisible al donante", fillcolor="#d5f5e3"];
c [label="CRITICAL_PENDING\\noculto al donante", fillcolor="#f5b7b1"]; k [label="CONSULTED\\n(reservado, sin uso)", fillcolor="#eaeded", style="rounded,filled,dashed"];
ini -> p [label="trigger create_pending_result"]; p -> a [label="release_noncritical_result\\n(can_release_results)"]; p -> c [label="mark_result_critical\\n(is_staff)"];
c -> p [label="clear_result_critical\\n(can_release_results)"]; a -> n [label="correo SENT con result_id\\n(deliverCommunication)"]; n -> k [style=dashed, label="sin código"];
}''')


def aptitud():
    return _dot("aptitud", 'digraph G { rankdir=TB; nodesep=0.3; ranksep=0.4; ' + BASE + '''
s [label="computeEligibility(gender, active, donationDates, params, today)", fillcolor="#d6eaf8"];
a [label="¿active?", shape=diamond, fillcolor="#fcf3cf"]; b [label="¿donaciones del año ≥ límite[sexo]?", shape=diamond, fillcolor="#fcf3cf"];
c [label="¿hay última donación y\\núltima + intervalo[sexo] > hoy?", shape=diamond, fillcolor="#fcf3cf"];
i [label="INACTIVO", fillcolor="#eaeded"]; m [label="MAXIMO\\neligibleFrom = 1 de enero siguiente", fillcolor="#fdebd0"]; e [label="ESPERA\\neligibleFrom = última + intervalo", fillcolor="#fdebd0"]; ok [label="APTO", fillcolor="#d5f5e3"];
s -> a; a -> i [label="no"]; a -> b [label="sí"]; b -> m [label="sí"]; b -> c [label="no"]; c -> e [label="sí"]; c -> ok [label="no"];
}''')


def pipeline():
    return _dot("pipeline", 'digraph G { rankdir=LR; nodesep=0.3; ranksep=0.5; ' + BASE + '''
a [label="Commit local", fillcolor="#fdebd0"]; b [label="npm run build\\ncompila + tipos estrictos", fillcolor="#d6eaf8"]; c [label="git push origin main", fillcolor="#fdebd0"];
d [label="GitHub", fillcolor="#eaeded"]; e [label="Vercel: build y deploy\\nautomático (≈ 1-2 min)", fillcolor="#d6eaf8"]; f [label="Render: docker build\\nsi cambia /automations", fillcolor="#f5cba7"];
g [label="Verificación:\\n/health, rutas 401,\\nprueba de rol", fillcolor="#d5f5e3"]; h [label="Migraciones SQL\\n(manual, en orden)", fillcolor="#fcf3cf"];
a -> b -> c -> d; d -> e; d -> f; e -> g; f -> g; h -> g [style=dashed];
}''')


def arbol_frontend():
    return _dot("arbol_frontend", 'digraph G { rankdir=LR; nodesep=0.2; ranksep=0.5; ' + BASE + '''
root [label="app/layout.tsx\\nfuentes + portal.css", fillcolor="#1f4e79", fontcolor="white"]; page [label="app/page.tsx\\nlogin + reparto por rol", fillcolor="#d6eaf8"];
dp [label="DonorPortal.tsx\\n(dynamic, ssr:false)", fillcolor="#fdebd0"]; sp [label="staff/StaffPanel.tsx\\n(dynamic, ssr:false)", fillcolor="#fdebd0"];
u [label="staff/ui.tsx\\nModal · Badge · Field · friendlyError", fillcolor="#eaeded"]; api [label="staff/api.ts\\ncallApi()", fillcolor="#eaeded"]; uh [label="staff/useDirectory.ts\\ndonantes + donaciones + aptitud", fillcolor="#eaeded"];
t [label="Pestañas (11)\\nHome · Donors · Results · Campaigns · Emails\\nReports · Accounts · Params · Audit · Help · MyAccount", fillcolor="#f9e79f"];
l1 [label="lib/eligibility.ts", fillcolor="#d5f5e3"]; l2 [label="lib/params.ts", fillcolor="#d5f5e3"]; l3 [label="lib/csv.ts", fillcolor="#d5f5e3"]; l4 [label="lib/supabase/client.ts", fillcolor="#d5f5e3"];
root -> page; page -> dp; page -> sp; sp -> t; t -> u; t -> api; t -> uh; uh -> l1; uh -> l2; dp -> l1; dp -> l2; t -> l3; t -> l4; dp -> l4;
}''')


def er():
    def tabla(n, filas, color="#d6eaf8"):
        t = f'{n} [shape=plain, label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="white"><TR><TD BGCOLOR="{color}"><B>{n}</B></TD></TR>'
        for f in filas:
            t += f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="9">{f}</FONT></TD></TR>'
        return t + "</TABLE>>];\n"
    cuerpo = 'digraph G { rankdir=LR; nodesep=0.35; ranksep=0.9; splines=true; node [fontname="Arial"]; edge [color="#555555", fontname="Arial", fontsize=8, arrowsize=0.7];\n'
    cuerpo += tabla("profiles", ["<B>user_id</B> uuid PK", "dni text UK", "full_name", "role app_role", "can_release_results", "active"], "#d5f5e3")
    cuerpo += tabla("donors", ["<B>id</B> bigint PK", "auth_user_id uuid UK", "dni text UK", "first_name · last_name", "gender · birth_date · phone", "email · blood_type · rh_factor", "status · consent_email", "consent_at · consent_version", "opted_out"], "#fdebd0")
    cuerpo += tabla("donations", ["<B>id</B> bigint PK", "donor_id FK", "donation_date date", "donation_type · notes", "created_by uuid"])
    cuerpo += tabla("donation_results", ["<B>id</B> bigint PK", "donation_id FK UK", "status result_status", "critical bool", "donor_message", "available_at · released_by", "notified_at"], "#f5b7b1")
    cuerpo += tabla("communications", ["<B>id</B> bigint PK", "donor_id FK", "campaign_id FK", "result_id FK", "related_donation_id FK", "type · channel · email", "message · status", "created_year (generada)"], "#f9e79f")
    cuerpo += tabla("campaigns", ["<B>id</B> bigint PK", "name · kind · status", "message_template", "blood_groups text[]"], "#f9e79f")
    cuerpo += tabla("campaign_recipients", ["<B>id</B> bigint PK", "campaign_id FK", "donor_id FK", "communication_id FK", "UNIQUE(campaign_id, donor_id)"], "#f9e79f")
    cuerpo += tabla("consent_events", ["<B>id</B> bigint PK", "donor_id FK (cascade)", "action GRANTED/REVOKED", "version · recorded_via"], "#e8daef")
    cuerpo += tabla("consent_versions", ["<B>version</B> text PK", "body text", "active bool"], "#e8daef")
    cuerpo += tabla("message_templates", ["<B>type</B> text PK", "subject · body", "approved · approved_by", "approved_at"], "#e8daef")
    cuerpo += tabla("system_config", ["<B>key</B> text PK", "value jsonb", "updated_at"], "#eaeded")
    cuerpo += tabla("audit_logs", ["<B>id</B> bigint PK", "actor_id · actor_dni", "action · entity · entity_id", "detail jsonb"], "#eaeded")
    cuerpo += tabla("notifications", ["<B>id</B> bigint PK", "donor_id FK", "communication_id FK", "title · message · read_at"], "#eaeded")
    cuerpo += tabla("auth_users", ["<B>auth.users</B> (Supabase)", "id uuid", "email dni-DNI@login.hemocax.org"], "#fcf3cf")
    for a, b, lab in [("donations", "donors", "N:1"), ("donation_results", "donations", "1:1"), ("communications", "donors", "N:1"), ("communications", "campaigns", "N:1"),
                      ("communications", "donation_results", "N:1"), ("communications", "donations", "N:1"), ("campaign_recipients", "campaigns", "N:1"),
                      ("campaign_recipients", "donors", "N:1"), ("campaign_recipients", "communications", "N:1"), ("consent_events", "donors", "N:1"),
                      ("notifications", "donors", "N:1"), ("donors", "auth_users", "0..1"), ("profiles", "auth_users", "1:1")]:
        cuerpo += f'{a} -> {b} [label="{lab}"];\n'
    cuerpo += "}"
    return _dot("er", cuerpo, 150)


# ------------------------------------------------------------------------------------------------
def secuencia(nombre, titulo, partes, msgs, ancho=11.5):
    """msgs: ('m', i, j, texto) llamada; ('r', i, j, texto) respuesta (punteada); ('n', i, j, texto) nota; ('s', i, texto) auto-llamada."""
    n = len(partes)
    dx = ancho / n
    xs = [dx * (i + 0.5) for i in range(n)]
    pasos = []
    y = 0
    for m in msgs:
        lineas = m[-1].count("\n") + 1
        y -= 0.55 + 0.26 * (lineas - 1)
        pasos.append((m, y))
    alto = -y + 1.4
    fig, ax = plt.subplots(figsize=(ancho, max(3.4, alto * 0.62)))
    ax.set_xlim(0, ancho)
    ax.set_ylim(y - 0.9, 1.2)
    ax.axis("off")
    for x, p in zip(xs, partes):
        ax.add_patch(FancyBboxPatch((x - dx * 0.42, 0.25), dx * 0.84, 0.75, boxstyle="round,pad=0.02", fc="#d6eaf8", ec=AZUL, lw=1.2))
        ax.text(x, 0.62, p, ha="center", va="center", fontsize=8, fontweight="bold", color=AZUL)
        ax.plot([x, x], [0.25, y - 0.6], color="#aab7b8", lw=0.9, ls=(0, (4, 3)))
    for m, yy in pasos:
        tipo = m[0]
        if tipo in ("m", "r"):
            _, i, j, txt = m
            x1, x2 = xs[i], xs[j]
            ax.annotate("", xy=(x2, yy), xytext=(x1, yy), arrowprops=dict(arrowstyle="-|>", lw=1.1, color=(ROJO if tipo == "r" else "#2c3e50"), ls=("--" if tipo == "r" else "-"), shrinkA=0, shrinkB=0))
            ax.text((x1 + x2) / 2, yy + 0.07, txt, ha="center", va="bottom", fontsize=7.2, color="#2c3e50" if tipo == "m" else "#922b21")
        elif tipo == "s":
            _, i, txt = m
            x1 = xs[i]
            ax.plot([x1, x1 + 0.38, x1 + 0.38, x1], [yy + 0.16, yy + 0.16, yy - 0.16, yy - 0.16], color="#2c3e50", lw=1)
            ax.annotate("", xy=(x1, yy - 0.16), xytext=(x1 + 0.2, yy - 0.16), arrowprops=dict(arrowstyle="-|>", lw=1, color="#2c3e50"))
            ax.text(x1 + 0.46, yy, txt, ha="left", va="center", fontsize=7.2, color="#2c3e50")
        else:
            _, i, j, txt = m
            x1, x2 = xs[i] - dx * 0.4, xs[j] + dx * 0.4
            ax.add_patch(FancyBboxPatch((x1, yy - 0.2), x2 - x1, 0.4, boxstyle="round,pad=0.02", fc="#fcf3cf", ec="#b7950b", lw=0.8))
            ax.text((x1 + x2) / 2, yy, txt, ha="center", va="center", fontsize=7, color="#7d6608")
    ax.set_title(titulo, fontsize=10, fontweight="bold", color="#17202a")
    ruta = os.path.join(FIG, nombre + ".png")
    fig.savefig(ruta, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def secuencias():
    out = []
    out.append(secuencia("seq_login", "Inicio de sesión por DNI",
        ["Usuario", "page.tsx\n(navegador)", "Supabase Auth", "PostgREST", "PostgreSQL"],
        [("m", 0, 1, "DNI + contraseña"),
         ("s", 1, "valida 8 dígitos; arma dni-DNI@login.hemocax.org"),
         ("m", 1, 2, "POST /auth/v1/token?grant_type=password"),
         ("r", 2, 1, "access_token (JWT) + refresh_token"),
         ("m", 1, 3, "GET /rest/v1/profiles?user_id=eq.{uid}\nAuthorization: Bearer JWT"),
         ("m", 3, 4, "SET LOCAL role authenticated; claims del JWT\nSELECT … (RLS: user_id = auth.uid() o ADMIN)"),
         ("r", 4, 1, "rol, nombre, can_release_results"),
         ("r", 1, 0, "StaffPanel (STAFF/ADMIN) o DonorPortal (DONOR)")]))
    out.append(secuencia("seq_donacion", "Registro de una donación (reglas aplicadas por la base de datos)",
        ["Enfermería\n(DonationModal)", "PostgREST", "RLS", "Trigger\nenforce_annual…", "Trigger\ncreate_pending…"],
        [("s", 0, "computeEligibility: advierte ESPERA / MAXIMO"),
         ("m", 0, 1, "POST /rest/v1/donations  {donor_id, donation_date, …}"),
         ("m", 1, 2, "WITH CHECK is_staff()"),
         ("m", 2, 3, "BEFORE INSERT: SELECT donors … FOR UPDATE\ncuenta donaciones WHOLE_BLOOD del año"),
         ("n", 3, 3, "si count ≥ 4 (M) o 3 (F) → EXCEPTION"),
         ("m", 3, 4, "AFTER INSERT: INSERT donation_results (PENDING)\n+ audit_row_change DONATION_CREATED"),
         ("r", 1, 0, "201 Created  |  400 con el mensaje del máximo anual")]))
    out.append(secuencia("seq_resultado", "Liberación de un resultado y aviso por correo",
        ["Médico\n(ResultsTab)", "PostgREST\n(RPC)", "PostgreSQL", "/api/communications\n/send", "Gmail SMTP"],
        [("m", 0, 1, "rpc release_noncritical_result(id, mensaje)"),
         ("m", 1, 2, "can_release_results()? UPDATE … WHERE status='PENDING' AND critical=false"),
         ("r", 2, 0, "AVAILABLE (+ auditoría RESULT_RELEASED)"),
         ("m", 0, 3, "POST {donor_id, result_id, type:RESULT, message}\nAuthorization: Bearer JWT"),
         ("m", 3, 2, "getUser(); SELECT donors (cliente del usuario, RLS)\nvalida consentimiento y correo; INSERT communications"),
         ("m", 3, 4, "nodemailer.sendMail (HTML + texto)"),
         ("r", 4, 3, "messageId"),
         ("m", 3, 2, "service_role: communications → SENT; result → NOTIFIED; audit"),
         ("r", 3, 0, "201 { status: SENT }")]))
    out.append(secuencia("seq_automatizacion", "Automatización diaria (ejemplo: recordatorio de retorno a las 08:15)",
        ["Reloj\n(worker.py)", "/api/automations\n/run", "PostgreSQL\n(service_role)", "Gmail SMTP"],
        [("s", 0, "cada minuto: ¿hora Lima = 08:15 y no ejecutada hoy?"),
         ("m", 0, 1, "POST {type, dry_run}\nx-hemocax-automation-secret"),
         ("s", 1, "compara el secreto → 401 si no coincide"),
         ("m", 1, 2, "SELECT message_templates WHERE type"),
         ("n", 1, 1, "plantilla no aprobada → { eligible:0, skipped }"),
         ("m", 1, 2, "SELECT donors (ACTIVE, consent, sin baja, con correo)\n+ donations de esos donantes"),
         ("s", 1, "candidatos = APTO y con ≥ 1 donación"),
         ("m", 1, 2, "INSERT communications (PENDING) por candidato"),
         ("n", 2, 2, "índice único → 23505 si ya se envió: se omite"),
         ("m", 1, 3, "sendMail → SENT / FAILED"),
         ("r", 1, 0, "202 { count } (o lista si es simulación)")]))
    out.append(secuencia("seq_campana", "Envío de una campaña dirigida",
        ["Personal\n(CampaignsTab)", "PostgREST", "/api/communications\n/send", "Gmail SMTP"],
        [("m", 0, 1, "SELECT donors + donations + campaign_recipients"),
         ("s", 0, "calcula destinatarios: activos, con consentimiento,\naptos, grupo elegido y que no estén ya en la campaña"),
         ("n", 0, 0, "vista previa y confirmación del usuario"),
         ("m", 0, 2, "por cada donante: POST {type:CAMPAIGN, campaign_id}"),
         ("m", 2, 3, "valida consentimiento → sendMail"),
         ("r", 2, 0, "201 { id, status }"),
         ("m", 0, 1, "INSERT campaign_recipients (UNIQUE campaign_id, donor_id)"),
         ("s", 0, "barra de progreso: enviados / fallidos")]))
    return out


def bundle():
    datos = [("Compartido 1 (framework)", 237.5, 61.3), ("Compartido 2 (react-dom)", 223.8, 69.9), ("Compartido 3 (supabase-js)", 174.2, 46.2),
             ("Compartido 4", 110.0, 38.7), ("Panel del personal", 91.6, 24.5), ("CSS global", 29.5, 6.1), ("Portal del donante", 19.6, 7.1)]
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    nombres = [d[0] for d in datos][::-1]
    ax.barh(nombres, [d[1] for d in datos][::-1], color="#aed6f1", label="sin comprimir")
    ax.barh(nombres, [d[2] for d in datos][::-1], color=AZUL, label="gzip")
    for i, d in enumerate(datos[::-1]):
        ax.text(d[1] + 4, i, f"{d[1]:.0f} KB ({d[2]:.0f} KB gz)", va="center", fontsize=7.5)
    ax.set_xlim(0, 330)
    ax.set_xlabel("KB")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("Composición del bundle del cliente (build de producción, 16 archivos, 952 KB / 276 KB gzip)", fontsize=9.5, fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ruta = os.path.join(FIG, "bundle.png")
    fig.savefig(ruta, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def todo():
    return [contexto(), contenedores(), despliegue(), confianza(), estados_resultado(), aptitud(), pipeline(), arbol_frontend(), er(), *secuencias(), bundle()]


if __name__ == "__main__":
    for r in todo():
        print(r)
