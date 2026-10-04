# -*- coding: utf-8 -*-
from datetime import date

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "setiembre", "octubre", "noviembre", "diciembre"]


def f(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def fcorta(d: date) -> str:
    return d.strftime("%d/%m")


def fl(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def s(x: float) -> str:
    return f"S/ {x:,.2f}" if x >= 0 else f"−S/ {abs(x):,.2f}"


def n(x: float, dec: int = 1) -> str:
    return f"{x:,.{dec}f}"


def pct(x: float, dec: int = 1) -> str:
    return f"{100 * x:.{dec}f} %"
