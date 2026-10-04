# -*- coding: utf-8 -*-
"""Gráficos adicionales: diagrama de Ishikawa."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

AZUL, ROJO = "#1f4e79", "#c0392b"
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")


def ishikawa():
    causas = {
        "Método": ["Sin prueba de concepto temprana de\nenvío real de correo", "No se definió quién decide y quién\nenvía (reloj vs. portal)", "Criterios de aceptación de las\nplantillas poco claros"],
        "Mano de obra": ["Primera vez del equipo con SMTP\ny tareas programadas", "Interpretaciones distintas de\n«consentimiento vigente»", "Dependencia de una sola persona\npara integraciones"],
        "Materiales\n(tecnología)": ["Plan gratuito del reloj bloquea\nel puerto SMTP", "Límite diario de envíos del\ncorreo gratuito", "Zona horaria UTC vs. Lima en\nlas fechas"],
        "Medición": ["Sin pruebas automáticas de la\nregla anti-duplicados", "Sin meta de entrega definida\nal inicio", "El modo simulación deja estados\nconfusos"],
        "Medio ambiente": ["Variables de entorno distintas\nentre local y producción", "El reloj gratuito se duerme\ntras 15 minutos", "Cambios de los términos de\nlos proveedores"],
        "Máquina\n(infraestructura)": ["Reloj y envío en servicios\nseparados", "Planes gratuitos sin\ngarantía de servicio", "Sin monitoreo de errores de\nenvío al inicio"],
    }
    fig, ax = plt.subplots(figsize=(11.8, 6.2))
    ax.set_xlim(-1.6, 12.4)
    ax.set_ylim(-3.9, 3.9)
    ax.axis("off")
    ax.annotate("", xy=(10.2, 0), xytext=(-1.2, 0), arrowprops=dict(arrowstyle="-|>", lw=2.4, color=AZUL))
    ax.add_patch(Rectangle((10.25, -.85), 2.1, 1.7, facecolor="#fadbd8", edgecolor=ROJO, lw=1.6))
    ax.text(11.3, 0, "Alta tasa de\ndefectos en\nComunicaciones y\nautomatizaciones\n(13 defectos, 27 %)", ha="center", va="center", fontsize=7.6, fontweight="bold", color=ROJO)
    posiciones = [(2.6, 1), (5.9, 1), (9.2, 1), (2.6, -1), (5.9, -1), (9.2, -1)]
    for (cat, lista), (x, lado) in zip(causas.items(), posiciones):
        ax.plot([x - 1.1, x + .3], [3.1 * lado, 0], color=AZUL, lw=1.6)
        ax.text(x - 1.1, 3.4 * lado, cat, ha="center", va="center", fontsize=8.6, fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=AZUL, edgecolor="none"))
        for k, txt in enumerate(lista):
            yy = lado * (2.5 - k * .88)
            xx = x - 1.1 + (3.1 - abs(yy)) / 3.1 * 1.4
            ax.plot([xx - .1, xx], [yy, yy], color="#7f8c8d", lw=1)
            ax.text(xx - .14, yy, txt, ha="right", va="center", fontsize=6.3)
    ax.set_title("Diagrama de Ishikawa — causas raíz de los defectos en Comunicaciones y automatizaciones", fontsize=10.5, fontweight="bold")
    ruta = os.path.join(FIG, "ishikawa.png")
    fig.savefig(ruta, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def histograma_recursos():
    import datos as D
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    base = [0.0] * D.N_SEMANAS
    cols = {"PM": "#1f4e79", "LT": "#2e86c1", "AF": "#58d68d", "FE": "#f4d03f", "INT": "#e67e22", "QA": "#a569bd"}
    xs = list(range(1, D.N_SEMANAS + 1))
    for r in D.ORDEN_ROLES:
        vals = D.HORAS_SEM[r]
        ax.bar(xs, vals, bottom=base, color=cols[r], label=D.EQUIPO[r]["corto"].split()[0] + " (" + r + ")", width=.7)
        base = [b + v for b, v in zip(base, vals)]
    ax.axhline(90, color="#7f8c8d", ls="--", lw=1)
    ax.text(0.55, 92, "capacidad nominal del equipo (6 × 15 h)", fontsize=7.5, color="#7f8c8d")
    ax.set_xticks(xs)
    ax.set_xticklabels(["S%d" % x for x in xs])
    ax.set_ylabel("Horas-persona por semana")
    ax.set_title("Histograma de recursos (horas planificadas por semana y persona)", fontsize=10.5, fontweight="bold")
    ax.legend(ncol=3, fontsize=7.5, frameon=False, loc="upper left")
    ax.set_ylim(0, max(base) * 1.35)
    ruta = os.path.join(FIG, "histograma_recursos.png")
    fig.savefig(ruta, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


if __name__ == "__main__":
    print(ishikawa())
