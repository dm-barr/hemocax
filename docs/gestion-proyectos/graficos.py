# -*- coding: utf-8 -*-
"""Genera las figuras del informe (PNG) a partir del modelo de datos."""
import os
import subprocess
from datetime import timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

import datos as D

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
os.makedirs(FIG, exist_ok=True)
ROJO, AZUL, VERDE, GRIS, AMARILLO, NARANJA = "#c0392b", "#1f4e79", "#2e8b57", "#7f8c8d", "#f1c40f", "#e67e22"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def _guardar(fig, nombre):
    ruta = os.path.join(FIG, nombre)
    fig.savefig(ruta, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def _dot(nombre, codigo):
    src = os.path.join(FIG, nombre + ".dot")
    out = os.path.join(FIG, nombre + ".png")
    with open(src, "w", encoding="utf-8") as f:
        f.write(codigo)
    subprocess.run(["dot", "-Tpng", "-Gdpi=170", src, "-o", out], check=True)
    os.remove(src)
    return out


# ------------------------------------------------------------------------------------------------
def curva_s():
    sem = [f["semana"] for f in D.EVM]
    pv = [f["pv"] for f in D.EVM]
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.plot(sem, pv, color=AZUL, lw=2.4, marker="o", ms=4, label="PV  Valor planificado (línea base)")
    sr = [f["semana"] for f in D.EVM if f["ev"] is not None]
    ax.plot(sr, [f["ev"] for f in D.EVM if f["ev"] is not None], color=VERDE, lw=2.2, marker="s", ms=4, label="EV  Valor ganado")
    ax.plot(sr, [f["ac"] for f in D.EVM if f["ac"] is not None], color=ROJO, lw=2.2, marker="^", ms=4, label="AC  Costo real")
    ax.axhline(D.BAC, color=GRIS, ls="--", lw=1)
    ax.text(12.4, D.BAC - 330, f"BAC = S/ {D.BAC:,.2f}", color=GRIS, fontsize=8, ha="right")
    ax.axhline(D.BAC + D.RESERVA_CONTINGENCIA, color=NARANJA, ls=":", lw=1.2)
    ax.text(12.4, D.BAC + D.RESERVA_CONTINGENCIA + 80, f"BAC + contingencia = S/ {D.BAC + D.RESERVA_CONTINGENCIA:,.2f}", color=NARANJA, fontsize=8, ha="right")
    ax.axvline(D.S_CORTE, color="#999", ls=":", lw=1)
    ax.text(D.S_CORTE + 0.08, 450, "Corte\n04/10", fontsize=8, color="#666")
    ax.set_xticks(sem)
    ax.set_xticklabels([f"S{s}" for s in sem])
    ax.set_ylabel("Costo acumulado (S/)")
    ax.set_title("Curva S — Valor planificado, valor ganado y costo real", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=.25)
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.62), frameon=False, fontsize=8.5)
    ax.set_ylim(0, D.BAC + D.RESERVA_CONTINGENCIA + 700)
    return _guardar(fig, "curva_s.png")


def indices_evm():
    sem = [f["semana"] for f in D.EVM if f["ev"] is not None]
    spi = [f["ev"] / f["pv"] for f in D.EVM if f["ev"] is not None]
    cpi = [f["ev"] / f["ac"] for f in D.EVM if f["ev"] is not None]
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    ax.plot(sem, spi, color=AZUL, marker="o", lw=2, label="SPI (cronograma)")
    ax.plot(sem, cpi, color=ROJO, marker="s", lw=2, label="CPI (costo)")
    ax.axhline(1.0, color=GRIS, ls="--", lw=1)
    ax.axhspan(0.9, 1.1, color="#2e8b57", alpha=.07)
    ax.set_ylim(0.85, 1.12)
    ax.set_xticks(sem)
    ax.set_xticklabels([f"S{s}" for s in sem])
    ax.set_title("Evolución de los índices de desempeño (SPI y CPI)", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False, loc="lower right", fontsize=8.5)
    return _guardar(fig, "indices_evm.png")


def gantt():
    acts = [a for a in D._A]
    fig, ax = plt.subplots(figsize=(10.5, 9.2))
    colores = {"1": "#7fb3d5", "2": "#76d7c4", "3": "#f7dc6f", "4": "#f0b27a", "5": "#bb8fce"}
    for i, a in enumerate(acts):
        y = len(acts) - i
        ini, fin = a["ini"], a["fin"] + timedelta(days=1)
        col = ROJO if a.get("critica") else colores[a["fase"]]
        ax.barh(y, (fin - ini).days, left=mdates.date2num(ini), height=.58, color=col, edgecolor="white")
        if a["dur"] > 0:
            r_ini = a["ini"]
            for _ in range(a["seg"][0]):
                r_ini = D.sig_laborable(r_ini)
            ax.plot([mdates.date2num(r_ini), mdates.date2num(a["fin_real"] + timedelta(days=1))], [y - .36, y - .36], color="#222", lw=1.3)
    ax.set_yticks([len(acts) - i for i in range(len(acts))])
    ax.set_yticklabels([f"{a['id']}  {a['nombre'][:60]}" for a in acts], fontsize=7.4)
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=7.5)
    ax.axvline(mdates.date2num(D.CORTE), color="#555", ls="--", lw=1)
    ax.text(mdates.date2num(D.CORTE) + .4, len(acts) + 0.6, "Corte 04/10", fontsize=8, color="#555")
    ax.grid(axis="x", alpha=.25)
    ax.set_title("Cronograma del proyecto (Gantt). Rojo = ruta crítica; línea negra = ejecución real", fontsize=11, fontweight="bold")
    ax.set_xlim(mdates.date2num(D.SEMANA1), mdates.date2num(D.SEMANA1 + timedelta(days=7 * D.N_SEMANAS)))
    return _guardar(fig, "gantt.png")


def mapa_calor():
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    for p in range(1, 6):
        for i in range(1, 6):
            v = p * i
            col = "#e74c3c" if v >= 10 else ("#f4d03f" if v >= 5 else "#58d68d")
            ax.add_patch(Rectangle((i - .5, p - .5), 1, 1, facecolor=col, edgecolor="white", lw=2, alpha=.85))
            ax.text(i + .38, p - .4, str(v), fontsize=7, ha="right", va="bottom", color="#444")
    celdas = {}
    for r in D.RIESGOS:
        celdas.setdefault((r["p"], r["i"]), []).append(r)
    for (p, i), lst in celdas.items():
        for k, r in enumerate(lst):
            col = "#154360" if r["tipo"] == "Amenaza" else "#7d3c98"
            dx = -.28 + (k % 2) * .5
            dy = .22 - (k // 2) * .27
            ax.text(i + dx, p + dy, r["id"], fontsize=9, fontweight="bold", color=col, ha="center", va="center")
    ax.set_xlim(.5, 5.5)
    ax.set_ylim(.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_xticklabels(["1\nMuy bajo", "2\nBajo", "3\nMedio", "4\nAlto", "5\nMuy alto"])
    ax.set_yticks(range(1, 6))
    ax.set_yticklabels(["1 Muy improbable", "2 Poco probable", "3 Posible", "4 Probable", "5 Casi seguro"])
    ax.set_xlabel("Impacto")
    ax.set_ylabel("Probabilidad")
    ax.set_title("Matriz de probabilidad × impacto (azul = amenaza, morado = oportunidad)", fontsize=10.5, fontweight="bold")
    for s in ax.spines.values():
        s.set_visible(False)
    return _guardar(fig, "mapa_calor.png")


def pareto():
    datos = sorted(D.DEFECTOS, key=lambda x: -x[1])
    nombres = [n for n, _ in datos]
    vals = [v for _, v in datos]
    tot = sum(vals)
    acum, a = [], 0
    for v in vals:
        a += v
        acum.append(100 * a / tot)
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    ax.bar(range(len(vals)), vals, color=[ROJO if c - 100 * v / tot < 80 else "#95a5a6" for v, c in zip(vals, acum)], width=.62)
    for i, v in enumerate(vals):
        ax.text(i, v + .25, str(v), ha="center", fontsize=8.5)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels([n.replace(" y ", " y\n").replace(" de ", " de\n", 1) for n in nombres], fontsize=7.6)
    ax.set_ylabel("N.° de defectos")
    ax2 = ax.twinx()
    ax2.plot(range(len(vals)), acum, color=AZUL, marker="o", lw=2)
    ax2.axhline(80, color=GRIS, ls="--", lw=1)
    ax2.text(len(vals) - 1, 82, "80 %", ha="right", fontsize=8, color=GRIS)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("% acumulado")
    ax2.spines["right"].set_visible(True)
    ax.set_title(f"Diagrama de Pareto — defectos por módulo (n = {tot})", fontsize=11, fontweight="bold")
    return _guardar(fig, "pareto.png")


def coq():
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    cats = D.COQ_CAT
    vals = [D.COQ_COSTO[c] for c in cats]
    cols = [VERDE, "#58d68d", NARANJA, ROJO]
    ax.barh(cats[::-1], vals[::-1], color=cols[::-1], height=.55)
    for i, v in enumerate(vals[::-1]):
        ax.text(v + 15, i, f"S/ {v:,.2f}  ({100 * v / D.COQ_TOTAL:.1f} %)", va="center", fontsize=8.5)
    ax.set_xlim(0, max(vals) * 1.55)
    ax.set_title(f"Costo de la calidad (CoQ) = S/ {D.COQ_TOTAL:,.2f}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Costo (S/)")
    return _guardar(fig, "coq.png")


def matriz_interes():
    fig, ax = plt.subplots(figsize=(8.4, 6.2))
    ax.add_patch(Rectangle((0.5, 3), 2.5, 2.5, color="#fadbd8", alpha=.5))
    ax.add_patch(Rectangle((3, 3), 2.5, 2.5, color="#d5f5e3", alpha=.6))
    ax.add_patch(Rectangle((0.5, .5), 2.5, 2.5, color="#eaeded", alpha=.6))
    ax.add_patch(Rectangle((3, .5), 2.5, 2.5, color="#fcf3cf", alpha=.6))
    ax.text(1.75, 5.68, "Mantener satisfecha", ha="center", fontsize=9, color="#7b241c", fontweight="bold")
    ax.text(4.25, 5.68, "Gestionar de cerca", ha="center", fontsize=9, color="#1e8449", fontweight="bold")
    ax.text(1.75, .62, "Monitorear", ha="center", fontsize=9, color="#555", fontweight="bold")
    ax.text(4.25, .62, "Mantener informado", ha="center", fontsize=9, color="#9a7d0a", fontweight="bold")
    usados = {}
    marc = {"Apoya": ("o", VERDE), "Neutral": ("s", GRIS), "Se resiste": ("^", ROJO)}
    for (sid, nom, org, rol, exp, inte, infl, act, fase, est) in D.INTERESADOS:
        k = (inte, infl)
        n = usados.get(k, 0)
        usados[k] = n + 1
        x = inte + (-.28 + .28 * (n % 3))
        y = infl + (.22 - .27 * (n // 3))
        m, c = marc[act]
        ax.scatter(x, y, marker=m, color=c, s=70, zorder=3)
        ax.text(x, y + .09, sid, fontsize=7.6, ha="center", va="bottom", fontweight="bold")
    ax.set_xlim(.5, 5.5)
    ax.set_ylim(.5, 5.85)
    ax.set_xlabel("Interés en el proyecto  →")
    ax.set_ylabel("Influencia sobre el proyecto  →")
    ax.set_title("Matriz de interés vs. influencia de los interesados", fontsize=11, fontweight="bold")
    ax.plot([], [], "o", color=VERDE, label="Apoya")
    ax.plot([], [], "s", color=GRIS, label="Neutral")
    ax.legend(loc="lower left", frameon=True, fontsize=8, title="Actitud", bbox_to_anchor=(0.0, 0.08))
    return _guardar(fig, "matriz_interes.png")


# ------------------------------------------------------------------------------------------------
def edt():
    rama = {
        "1": ("1. INICIO", ["1.1 Project Charter", "1.2 Registro de stakeholders", "1.3 Kick-off", "1.4 Reunión con Jefatura", "1.5 Dirección y seguimiento"]),
        "2": ("2. PLANIFICACIÓN Y DISEÑO", ["2.1 Entrevistas y talleres", "2.2 Requisitos y alcance", "2.3 Prototipos UX", "2.4 Validación de prototipos", "2.5 EDT, cronograma y costos",
                                           "2.6 Planes subsidiarios", "2.7 Arquitectura y datos", "2.8 Propuesta al HRDC"]),
        "3": ("3. DESARROLLO", ["3.1 Base de datos y seguridad", "3.2 Padrón y ficha", "3.3 Importación CSV", "3.4 Donaciones y reglas", "3.5 Resultados", "3.6 Consentimiento y ARCO",
                               "3.7 Correo y campañas", "3.8 Automatizaciones", "3.9 Portal del donante", "3.10 Panel del personal", "3.11 Despliegue"]),
        "4": ("4. PRUEBAS Y CAPACITACIÓN", ["4.1 Plan de pruebas", "4.2 Pruebas funcionales", "4.3 Pruebas de seguridad", "4.4 Piloto interno", "4.5 Correcciones", "4.6 Manuales y ayuda", "4.7 Video de capacitación"]),
        "5": ("5. CIERRE", ["5.1 Informe final y lecciones", "5.2 Entrega de repositorio", "5.3 Acta de cierre"]),
    }
    col = {"1": "#aed6f1", "2": "#a3e4d7", "3": "#f9e79f", "4": "#f5cba7", "5": "#d7bde2"}
    lineas = ['digraph G {rankdir=TB; nodesep=0.25; ranksep=0.45; node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11, margin="0.14,0.08"]; edge [color="#888888"];',
              'root [label="HEMOCAX — Plataforma digital de fidelización del donante de sangre", fillcolor="#1f4e79", fontcolor="white", fontsize=14];']
    for k, (tit, hijos) in rama.items():
        lineas.append(f'f{k} [label="{tit}", fillcolor="{col[k]}", fontsize=12];')
        lineas.append(f"root -> f{k};")
        cuerpo = "\\l".join(h for h in hijos) + "\\l"
        lineas.append(f'n{k} [label="{cuerpo}", shape=box, style="filled", fillcolor="white", color="#999999", fontsize=10.5];')
        lineas.append(f"f{k} -> n{k};")
    lineas.append("}")
    return _dot("edt", "\n".join(lineas))


def obs():
    c = D.EQUIPO
    codigo = f'''digraph G {{ rankdir=TB; nodesep=0.35; ranksep=0.5;
node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11, margin="0.14,0.08"]; edge [color="#666666"];
spo [label="NIVEL 1 · Patrocinio\\nIng. Ena Mirella Cacho Chávez\\n(Sponsor académico)", fillcolor="#1f4e79", fontcolor="white"];
cli [label="Cliente / usuario clave\\nHRDC — Banco de Sangre\\nDra. Marimar · Jefatura · OEI\\n(participa 20 % en validación)", fillcolor="#fdebd0"];
pm [label="NIVEL 2 · Dirección del proyecto\\n{c['PM']['nombre']}\\nProject Manager", fillcolor="#2e86c1", fontcolor="white"];
lt [label="NIVEL 3 · Desarrollo y datos\\n{c['LT']['nombre']}\\nLíder Técnico", fillcolor="#aed6f1"];
af [label="NIVEL 3 · Análisis y UX\\n{c['AF']['nombre']}\\nAnalista Funcional", fillcolor="#aed6f1"];
qa [label="NIVEL 3 · Calidad y seguridad\\n{c['QA']['nombre']}\\nQA y Seguridad de datos", fillcolor="#aed6f1"];
fe [label="NIVEL 4\\n{c['FE']['nombre']}\\nDesarrolladora Frontend", fillcolor="#d6eaf8"];
it [label="NIVEL 4\\n{c['INT']['nombre']}\\nIntegraciones y automatizaciones", fillcolor="#d6eaf8"];
prov [label="Soporte externo\\nProveedores en la nube\\n(Supabase, Vercel, Render, Google)", fillcolor="#eaeded", style="rounded,filled,dashed"];
spo -> pm; cli -> pm [style=dashed, label=" valida"]; pm -> lt; pm -> af; pm -> qa; lt -> fe; lt -> it; it -> prov [style=dashed];
{{rank=same; spo; cli}} {{rank=same; lt; af; qa}} {{rank=same; fe; it; prov}}
}}'''
    return _dot("obs", codigo)


def arquitectura():
    codigo = '''digraph G { rankdir=LR; nodesep=0.35; ranksep=0.7;
node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11, margin="0.14,0.08"]; edge [color="#555555", fontname="Arial", fontsize=9];
don [label="Donante\\n(celular o PC)", fillcolor="#fdebd0"]; per [label="Personal del Banco de Sangre\\n(enfermería, médico, administrador)", fillcolor="#fdebd0"];
subgraph cluster_v { label="Vercel — portal Next.js"; style="rounded"; color="#2e86c1"; fontname="Arial";
  ui [label="Pantallas\\n(portal del donante y panel del personal)", fillcolor="#d6eaf8"]; api [label="Rutas del servidor\\n(cuentas, correo, automatizaciones)", fillcolor="#d6eaf8"]; }
subgraph cluster_s { label="Supabase"; style="rounded"; color="#2e8b57"; fontname="Arial";
  auth [label="Autenticación\\n(ingreso por DNI)", fillcolor="#d5f5e3"]; db [label="PostgreSQL\\n(RLS, triggers, funciones)", fillcolor="#d5f5e3"]; }
rel [label="Render\\nreloj de recordatorios", fillcolor="#f5cba7"]; gm [label="Gmail SMTP\\n(envío de correo)", fillcolor="#f5cba7"];
don -> ui; per -> ui; ui -> auth [label="sesión"]; ui -> db [label="permisos por fila (RLS)"]; ui -> api [label="acciones privilegiadas"];
api -> db; api -> gm; rel -> api [label="08:00 – 08:45 (Lima)"]; gm -> don [label="correo"]; }'''
    return _dot("arquitectura", codigo)


def ciclo_vida():
    codigo = '''digraph G { rankdir=LR; nodesep=0.3; ranksep=0.45;
node [shape=box, style="rounded,filled", fontname="Arial", fontsize=11, margin="0.14,0.08"]; edge [color="#555555"];
a [label="Inicio\\nCharter, stakeholders", fillcolor="#aed6f1"]; b [label="Planificación predictiva\\nalcance, EDT, cronograma,\\npresupuesto, riesgos", fillcolor="#a3e4d7"];
subgraph cluster_i { label="Desarrollo iterativo e incremental (ciclos semanales)"; style="rounded,dashed"; color="#b9770e"; fontname="Arial";
 c [label="Diseñar", fillcolor="#f9e79f"]; d [label="Construir", fillcolor="#f9e79f"]; e [label="Probar", fillcolor="#f9e79f"]; f [label="Validar con\\nel Banco de Sangre", fillcolor="#f9e79f"]; c -> d -> e -> f; f -> c [constraint=false, label=" ajustar"]; }
g [label="Despliegue,\\npiloto interno", fillcolor="#f5cba7"]; h [label="Cierre y\\ntransferencia", fillcolor="#d7bde2"];
a -> b -> c; f -> g -> h; }'''
    return _dot("ciclo_vida", codigo)


def flujo_resultados():
    codigo = '''digraph G { rankdir=TB; nodesep=0.3; ranksep=0.35;
node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, margin="0.12,0.06"]; edge [color="#555555", fontname="Arial", fontsize=9];
a [label="Se registra la donación", fillcolor="#d6eaf8"]; b [label="Resultado PENDIENTE", fillcolor="#fdebd0"];
c [label="¿Resultado normal?", shape=diamond, fillcolor="#fcf3cf"]; d [label="Médico libera con mensaje", fillcolor="#d5f5e3"];
e [label="Marca de CRÍTICO\\n(no se muestra ni se envía nada)", fillcolor="#f5b7b1"]; f [label="Aviso por correo\\n(sin datos médicos)", fillcolor="#d5f5e3"];
g [label="El donante lo ve en su portal", fillcolor="#d5f5e3"]; h [label="El médico contacta al donante\\npor teléfono o en consulta", fillcolor="#f5b7b1"];
a -> b -> c; c -> d [label="sí"]; c -> e [label="reactivo / dudoso"]; d -> f -> g; e -> h; }'''
    return _dot("flujo_resultados", codigo)


from graf_extra import ishikawa, histograma_recursos  # noqa: E402


def todo():
    return [curva_s(), indices_evm(), gantt(), mapa_calor(), pareto(), coq(), matriz_interes(), edt(), obs(),
            arquitectura(), ciclo_vida(), flujo_resultados(), ishikawa(), histograma_recursos()]


if __name__ == "__main__":
    for r in todo():
        print(r)
