# -*- coding: utf-8 -*-
"""Ensambla el informe de Gestión de Proyectos de HEMOCAX en un único documento Word.

Uso:  python informe.py      (genera fig/*.png y HEMOCAX_Informe_Gestion_de_Proyectos.docx)
"""
import importlib
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import graficos
import docx_utils as U

graficos.todo()

MODULOS = ["cap_a", "cap_b", "cap_c", "cap_d", "cap_e", "cap_f"]
SALIDA = "HEMOCAX_Informe_Gestion_de_Proyectos.docx"


def construir():
    doc = U.nuevo_documento()
    import cap_a
    cap_a.portada(doc)
    cap_a.control_versiones(doc)
    cap_a.resumen_ejecutivo(doc)
    cap_a.mapa_entregables(doc)
    cap_a.charter(doc)
    cap_a.interesados(doc)
    cap_a.plan_direccion(doc)
    for nombre in MODULOS[1:]:
        if os.path.exists(nombre + ".py"):
            mod = importlib.import_module(nombre)
            mod.construir(doc)
    U.pie_y_encabezado(doc, "HEMOCAX — Informe de Gestión de Proyectos")
    doc.save(SALIDA)
    print("Guardado:", os.path.abspath(SALIDA))


if __name__ == "__main__":
    construir()
