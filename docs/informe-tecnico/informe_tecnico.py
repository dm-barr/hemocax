# -*- coding: utf-8 -*-
"""Genera el informe técnico de HEMOCAX en Word.

Uso:  python informe_tecnico.py      (genera fig/*.png y HEMOCAX_Informe_Tecnico.docx)
Requiere: python-docx, matplotlib y Graphviz (comando `dot`).
Las utilidades de Word se reutilizan de ../gestion-proyectos/docx_utils.py.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)
sys.path.insert(0, AQUI)
sys.path.append(os.path.join(AQUI, "..", "gestion-proyectos"))
sys.stdout.reconfigure(encoding="utf-8")

import docx_utils as U      # noqa: E402
import graf_tecnico          # noqa: E402
import tec_a, tec_b, tec_c, tec_d  # noqa: E402

SALIDA = "HEMOCAX_Informe_Tecnico.docx"


def construir():
    graf_tecnico.todo()
    doc = U.nuevo_documento()
    tec_a.portada(doc)
    tec_a.control(doc)
    tec_a.construir(doc)
    tec_b.construir(doc)
    tec_c.construir(doc)
    tec_d.construir(doc)
    U.pie_y_encabezado(doc, "HEMOCAX — Informe técnico", encabezado="Universidad Nacional de Cajamarca · EPIS · HEMOCAX · Informe técnico v1.0")
    doc.save(SALIDA)
    print("Guardado:", os.path.join(AQUI, SALIDA))


if __name__ == "__main__":
    construir()
