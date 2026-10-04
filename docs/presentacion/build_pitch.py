# -*- coding: utf-8 -*-
"""Genera la presentación interactiva de HEMOCAX (HTML autocontenido).

Uso:  python build_pitch.py
Salida:
  HEMOCAX_Pitch.html     archivo completo: se abre con doble clic, sin internet (las tipografías usan alternativas del sistema)
  pitch_artifact.html    mismo contenido sin <html>/<head>, para publicarlo como Artifact

Las cifras salen de ../gestion-proyectos/datos.py y cap_d.py (mismos datos que el informe de gestión).
"""
import json
import os
import sys
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "gestion-proyectos"))
sys.stdout.reconfigure(encoding="utf-8")

import datos as D          # noqa: E402
import cap_d               # noqa: E402

POR_QUE = {  # id: (por qué el poder, por qué el interés)
    "S01": ("Aprueba el charter, el presupuesto y el cierre, y califica el proyecto.", "Su curso evalúa la documentación y el producto."),
    "S02": ("Dirige el proyecto y decide dentro de su autoridad.", "Responde por el resultado completo."),
    "S03": ("Decide la arquitectura y acepta o rechaza el código.", "Su diseño sostiene la seguridad de los datos."),
    "S04": ("Construye el portal y el panel; sin su trabajo no hay entrega.", "Quiere requisitos y diseño aprobados antes de construir."),
    "S05": ("Su integración de correo y reloj es la pieza que más depende de terceros.", "Necesita servicios externos estables."),
    "S06": ("Puede detener un despliegue si no se cumple la calidad.", "Su trabajo es proteger los datos y los permisos."),
    "S07": ("Fija y prioriza requisitos con el Banco de Sangre.", "Necesita usuarios reales para validar prototipos."),
    "S08": ("Valida si el sistema sirve a su servicio.", "Es la usuaria principal y vive el problema cada día."),
    "S09": ("Aprueba valores clínicos y textos, y puede frenar el uso.", "Le preocupa la confidencialidad y los resultados críticos."),
    "S10": ("Usa el panel pero no decide el alcance.", "Su trabajo diario cambia con el sistema."),
    "S11": ("Controla la infraestructura y cualquier integración futura.", "No le afecta el día a día mientras no se toque su sistema."),
    "S12": ("Autoriza el proyecto y el costo recurrente.", "Le interesan el costo y el riesgo, no el detalle."),
    "S13": ("Su adopción define el éxito, pero uno a uno no deciden.", "Quieren saber cuándo pueden donar y ver su resultado."),
    "S14": ("Pueden cambiar límites o bloquear servicios (ya bloquearon el puerto de correo del reloj).", "Solo les importa que se respeten sus términos."),
    "S15": ("Regula la salud digital y los datos personales.", "Todavía no tiene vínculo directo con el proyecto."),
}
CORTO = dict(cap_d.CORTO)


def iso(d):
    return d.isoformat()


def construir_datos():
    ev = []
    for f in D.EVM:
        ev.append(dict(s=f["semana"], pv=f["pv"], ev=f["ev"], ac=f["ac"]))
    pts = {str(s): {k: (round(v, 4) if isinstance(v, float) else v) for k, v in D.indicadores(s).items()} for s in (6, 9, D.S_CORTE)}
    riesgos = []
    for r in D.RIESGOS:
        riesgos.append(dict(id=r["id"], tipo=r["tipo"], corto=CORTO.get(r["id"], r["desc"][:60]), desc=r["desc"], p=r["p"], i=r["i"], pi=r["pi"], est=r["est"],
                            dueno=D.EQUIPO[r["dueno"]]["corto"].split()[0], acc=r["acc"], trig=r["trig"], cont=r["cont"], vme=r["vme"], estado=r.get("estado", "Vigente")))
    fases = []
    for k, nom in D.FASES.items():
        acts = [dict(id=a["id"], n=a["nombre"], ini=iso(a["ini"]), fin=iso(a["fin"]), crit=bool(a.get("critica")), h=a["h"], continua=a["dur"] == 0)
                for a in D._A if a["fase"] == k]
        fases.append(dict(k=k, nombre=nom, ini=iso(min(a["ini"] for a in D._A if a["fase"] == k and a["dur"] > 0)),
                          fin=iso(max(a["fin"] for a in D._A if a["fase"] == k and a["dur"] > 0)), acts=acts, h=sum(a["h"] for a in D._A if a["fase"] == k)))
    inter = []
    for (sid, nom, org, rol, exp, i, infl, act, fase, est) in D.INTERESADOS:
        inter.append(dict(id=sid, nombre=nom, org=org, rol=rol, exp=exp, interes=i, poder=infl, actitud=act, estrategia=est, pq_poder=POR_QUE[sid][0], pq_interes=POR_QUE[sid][1]))
    A = D.ACT
    hitos = [("H1", "Project Charter aprobado", A["1.1"]["fin"]), ("H3", "Requisitos y alcance aprobados", A["2.2"]["fin"]), ("H5", "Arquitectura y datos aprobados", A["2.7"]["fin"]),
             ("H7", "Núcleo operativo listo", A["3.5"]["fin"]), ("H9", "Sistema en producción", A["3.11"]["fin"]), ("H12", "Acta de cierre", A["5.3"]["fin"])]
    raci = [dict(n=n, **fila) for n, fila in cap_d.RACI]
    equipo = [dict(k=k, nombre=D.EQUIPO[k]["nombre"], corto=D.EQUIPO[k]["corto"], rol=D.EQUIPO[k]["rol"], h=D.HORAS_ROL[k]) for k in D.ORDEN_ROLES]
    return dict(
        bac=D.BAC, rrhh=D.COSTO_RRHH, gastos=D.GASTOS_TOTAL, cont=D.RESERVA_CONTINGENCIA, gest=D.RESERVA_GESTION, total=D.PRESUPUESTO_TOTAL,
        horas=D.HORAS_TOTALES, semanas=round(D.SEMANAS_PROY, 1), inicio=iso(D.INICIO), fin=iso(D.FIN_PLAN), corte=iso(D.CORTE), s_corte=D.S_CORTE,
        canales=D.CANALES, n_int=D.N_INTERESADOS, evm=ev, ind=pts, riesgos=riesgos, fases=fases, interesados=inter, hitos=[dict(h=h, n=n, f=iso(f)) for h, n, f in hitos],
        raci=raci, cols=cap_d.COLS, equipo=equipo,
        coq=dict(tot=D.COQ_TOTAL, cat={k: D.COQ_COSTO[k] for k in D.COQ_CAT}, pct_bac=D.COQ_TOTAL / D.BAC, cb=D.CB_RATIO),
        defectos=[dict(n=n, v=v) for n, v in D.DEFECTOS],
        n_act=len(D._A), ruta=[a["id"] for a in D._A if a.get("critica")],
    )


def main():
    datos = construir_datos()
    with open("pitch_template.html", encoding="utf-8") as f:
        plantilla = f.read()
    cuerpo = plantilla.replace("__DATA__", json.dumps(datos, ensure_ascii=False))
    with open("pitch_artifact.html", "w", encoding="utf-8") as f:
        f.write(cuerpo)
    envoltura = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                 '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n'
                 + cuerpo + "\n</body></html>\n")
    with open("HEMOCAX_Pitch.html", "w", encoding="utf-8") as f:
        f.write(envoltura)
    # copia servida por Vercel en /pitch (ver rewrites en next.config.ts)
    destino = os.path.join(AQUI, "..", "..", "public", "pitch.html")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(envoltura)
    print("HEMOCAX_Pitch.html", round(len(envoltura) / 1024), "KB  ->  public/pitch.html")


if __name__ == "__main__":
    main()
