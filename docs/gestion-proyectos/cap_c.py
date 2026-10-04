# -*- coding: utf-8 -*-
"""Parte II (2): costos (estimación, presupuesto, curva S, EVM) y calidad (ISO 25010, CoQ, herramientas)."""
import datos as D
import docx_utils as U
from fmt import f, s, n, pct

FIG = "fig/"


def _por_fase():
    out = {}
    for k in D.FASES:
        h = sum(a["h"] for a in D._A if a["fase"] == k)
        out[k] = h
    return out


def costos(doc):
    U.h1(doc, "8. Gestión de los costos del proyecto")
    U.h2(doc, "8.1 Plan de gestión de costos")
    U.tabla(doc, ["Elemento", "Definición"], [
        ["Unidad de medida", "Horas-persona (HH) para el trabajo del equipo; soles (S/) para gastos en efectivo."],
        ["Tarifa imputada", f"S/ {D.TARIFA:.2f} por hora-persona (tarifa referencial del curso; el trabajo es voluntario y académico)."],
        ["Nivel de precisión", "Estimación bottom-up por paquete de trabajo, con margen de ±5 a 10 %."],
        ["Control", "Valor ganado (EVM) semanal; umbral de acción correctiva: SPI o CPI menores a 0.90."],
        ["Reservas", "Contingencia calculada con el VME de los riesgos (no con un porcentaje arbitrario); reserva de gestión del 3 %."],
        ["Línea base", f"BAC = {s(D.BAC)} (costo base sin reservas), medido con la curva S de la sección 8.4."],
        ["Gestión del cambio", "Todo cambio que afecte el costo en más de S/ 50.00 requiere aprobación del sponsor."],
    ], anchos=[3.6, 13.0], tam=9, primera_negrita=True, titulo="Plan de gestión de costos")

    U.h2(doc, "8.2 Estimación de costos")
    U.tabla(doc, ["Técnica", "Descripción", "Uso en HEMOCAX"], [
        ["Análoga (top-down)", "Usa datos históricos de proyectos similares. Precisión ±25-75 %.", "No se usó como base: no existen datos históricos comparables del equipo."],
        ["Paramétrica", "Relaciones estadísticas (costo por unidad). Precisión ±10-25 %.", f"Verificación cruzada: {D.HORAS_TOTALES} h / 17 requisitos funcionales ≈ {D.HORAS_TOTALES / 17:.0f} h por requisito (S/ {D.COSTO_RRHH / 17:,.0f})."],
        ["**Bottom-up**", "Estima cada paquete de trabajo y suma hacia arriba. Precisión ±5-10 %.", "**Técnica principal.** Horas por rol en cada una de las actividades de la EDT (tabla siguiente)."],
        ["Tres puntos (PERT)", "E = (O + 4M + P) / 6. Gestiona la incertidumbre.", "Aplicada a las cinco actividades más inciertas (sección 7.4)."],
    ], anchos=[3.2, 6.2, 7.2], tam=8.5, titulo="Técnicas de estimación consideradas")

    U.h3(doc, "Estimación bottom-up por paquete de trabajo")
    filas = []
    for a in D._A:
        filas.append([a["id"], a["nombre"], str(a["h"]), f"{a['h'] * D.TARIFA:,.2f}",
                      ", ".join(f"{r} {a['horas'][r]}" for r in D.ORDEN_ROLES if r in a["horas"])])
    filas.append(["", "**TOTAL RECURSOS HUMANOS**", f"**{D.HORAS_TOTALES}**", f"**{D.COSTO_RRHH:,.2f}**", ""])
    U.seccion(doc, horizontal=True)
    U.tabla(doc, ["EDT", "Paquete de trabajo", "HH", "Costo (S/)", "Horas por rol (PM project manager, LT líder técnico, AF analista, FE frontend, INT integraciones, QA calidad)"], filas,
            anchos=[1.2, 10.0, 1.4, 2.4, 10.4], alinear=["c", "l", "c", "r", "l"], tam=8, titulo="Estimación bottom-up de recursos humanos")
    U.seccion(doc, horizontal=False)

    U.h2(doc, "8.3 Presupuesto del proyecto")
    U.h3(doc, "Costo de recursos humanos por integrante")
    filas = []
    for r in D.ORDEN_ROLES:
        e = D.EQUIPO[r]
        h = D.HORAS_ROL[r]
        filas.append([e["nombre"], e["rol"], str(h), f"{h * D.TARIFA:,.2f}", pct(h / D.HORAS_TOTALES), f"{h / D.SEMANAS_PROY:.1f}"])
    filas.append(["**Total**", "", f"**{D.HORAS_TOTALES}**", f"**{D.COSTO_RRHH:,.2f}**", "100 %", f"**{D.HORAS_TOTALES / D.SEMANAS_PROY / 6:.1f}** (promedio)"])
    U.tabla(doc, ["Integrante", "Rol", "Horas", "Costo (S/)", "% del costo RR.HH.", "Horas por semana"], filas,
            anchos=[5.0, 4.8, 1.3, 2.0, 1.9, 1.9], alinear=["l", "l", "c", "r", "c", "c"], tam=8.5, titulo="Recursos humanos")
    U.h3(doc, "Distribución del costo por fase")
    ph = _por_fase()
    U.parrafo(doc, "Los gastos directos se asignan a la fase en la que se desembolsan (tabla de gastos directos).", tam=9.5)
    filas = []
    directos_fase = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
    asignacion = {0: "2", 1: "4", 2: "5", 3: "5", 4: "4"}
    for i, g in enumerate(D.GASTOS):
        directos_fase[asignacion[i]] += g[2]
    for k, nom in D.FASES.items():
        hh = ph[k]
        d = directos_fase[k]
        filas.append([f"{k}.0 {nom}", str(hh), f"{hh * D.TARIFA:,.2f}", f"{d:,.2f}", f"{hh * D.TARIFA + d:,.2f}", pct((hh * D.TARIFA + d) / D.BAC)])
    filas.append(["**Total**", f"**{D.HORAS_TOTALES}**", f"**{D.COSTO_RRHH:,.2f}**", f"**{D.GASTOS_TOTAL:,.2f}**", f"**{D.BAC:,.2f}**", "100 %"])
    U.tabla(doc, ["Fase", "Horas", "RR.HH. (S/)", "Gastos directos (S/)", "Costo total (S/)", "% del BAC"], filas,
            anchos=[5.6, 1.5, 2.5, 2.7, 2.6, 1.7], alinear=["l", "c", "r", "r", "r", "c"], tam=8.5, titulo="Distribución del presupuesto por fase")
    U.h3(doc, "Gastos directos (desembolso real en efectivo)")
    filas = [[str(i + 1), g[0], g[1], f"{g[2]:,.2f}", g[5]] for i, g in enumerate(D.GASTOS)]
    filas.append(["", "**Subtotal gastos directos**", "", f"**{D.GASTOS_TOTAL:,.2f}**", ""])
    U.tabla(doc, ["N.°", "Concepto", "Cantidad", "Total (S/)", "Justificación"], filas,
            anchos=[1.0, 7.4, 2.2, 2.0, 4.0], alinear=["c", "l", "c", "r", "l"], tam=8.5, titulo="Gastos directos")
    U.parrafo(doc, "**Infraestructura tecnológica: S/ 0.00.** Vercel (Hobby), Supabase (Free), Render (Free), GitHub, Figma (Education) y la cuenta de correo con contraseña de aplicación no tienen costo en el piloto.", tam=9.5)

    U.h3(doc, "Reservas y presupuesto total")
    U.tabla(doc, ["Concepto", "Monto (S/)", "Fundamento"], [
        ["Costo de recursos humanos", f"{D.COSTO_RRHH:,.2f}", f"{D.HORAS_TOTALES} h × S/ {D.TARIFA:.2f}"],
        ["Gastos directos", f"{D.GASTOS_TOTAL:,.2f}", "Tabla de gastos directos"],
        ["**Costo base (BAC)**", f"**{D.BAC:,.2f}**", "Línea base de costos sin reservas"],
        ["Reserva de contingencia", f"{D.RESERVA_CONTINGENCIA:,.2f}", f"Σ VME de las amenazas con impacto monetario (sección 12.5) = {pct(D.RESERVA_CONTINGENCIA / D.BAC)} del BAC"],
        ["Reserva de gestión", f"{D.RESERVA_GESTION:,.2f}", "3 % del costo base, para riesgos desconocidos; solo la usa el sponsor"],
        ["**Presupuesto total**", f"**{D.PRESUPUESTO_TOTAL:,.2f}**", f"S/ {D.PRESUPUESTO_TOTAL / D.HORAS_TOTALES:.2f} por hora efectiva; S/ {D.PRESUPUESTO_TOTAL / 6:,.2f} por integrante"],
    ], anchos=[5.0, 3.0, 8.6], alinear=["l", "r", "l"], tam=9, titulo="Presupuesto total del proyecto")
    U.caja(doc, "La reserva de contingencia no se calculó como un porcentaje arbitrario: es la suma del valor monetario esperado (VME) de los riesgos identificados. "
                "Omitir la reserva de contingencia es el error más frecuente en proyectos de TI.", color="FEF9E7")

    U.h2(doc, "8.4 Línea base de costos y curva S")
    U.parrafo(doc, "El valor planificado (PV) se obtuvo distribuyendo las horas de cada actividad entre sus días laborables y sumando los desembolsos en efectivo en la semana en que ocurren. "
                   "La curva tiene forma de **S** porque al inicio hay pocas personas trabajando (gasto lento), en el desarrollo trabaja todo el equipo (gasto acelerado) y al cierre vuelve a bajar.", alineacion="justificado")
    U.figura(doc, FIG + "curva_s.png", 15.5, "Curva S: PV (línea base), EV y AC acumulados por semana")
    filas = []
    prev = 0.0
    for fila in D.EVM:
        sem = fila["semana"]
        ini, fin = D.rango_semana(sem)
        filas.append([f"S{sem}", f"{f(ini)[:5]} – {f(fin)[:5]}", f"{fila['pv'] - prev:,.2f}", f"{fila['pv']:,.2f}", pct(fila["pv"] / D.BAC)])
        prev = fila["pv"]
    U.tabla(doc, ["Semana", "Periodo", "PV de la semana (S/)", "PV acumulado (S/)", "% de la línea base"], filas,
            anchos=[1.8, 3.8, 3.8, 3.8, 3.4], alinear=["c", "c", "r", "r", "c"], tam=8.5, titulo="Línea base de costos (valor planificado)")

    U.h2(doc, "8.5 Control de costos: valor ganado (EVM)")
    U.parrafo(doc, f"El seguimiento se realizó semanalmente con corte al **{f(D.CORTE)}** (semana {D.S_CORTE}). **EV** es el valor de lo realmente terminado (horas presupuestadas × avance real); "
                   "**AC** es el costo realmente incurrido (horas reales × tarifa más el efectivo gastado).", alineacion="justificado")
    filas = []
    for fila in D.EVM:
        if fila["ev"] is None:
            filas.append([f"S{fila['semana']}", f"{fila['pv']:,.2f}", "—", "—", "—", "—", "—", "—"])
            continue
        pv, ev, ac = fila["pv"], fila["ev"], fila["ac"]
        filas.append([f"S{fila['semana']}", f"{pv:,.2f}", f"{ev:,.2f}", f"{ac:,.2f}", f"{ev - pv:,.2f}", f"{ev - ac:,.2f}", f"{ev / pv:.3f}", f"{ev / ac:.3f}"])
    U.tabla(doc, ["Sem.", "PV (S/)", "EV (S/)", "AC (S/)", "SV = EV − PV", "CV = EV − AC", "SPI = EV/PV", "CPI = EV/AC"], filas,
            anchos=[1.3, 2.2, 2.2, 2.2, 2.4, 2.4, 2.0, 2.0], alinear=["c", "r", "r", "r", "r", "r", "c", "c"], tam=8.5,
            titulo="Valor ganado acumulado por semana (la semana 12 aún no tiene datos reales)")
    U.figura(doc, FIG + "indices_evm.png", 14.0, "Evolución de SPI y CPI")

    U.h3(doc, "Indicadores en tres puntos de control")
    pts = [D.indicadores(6), D.indicadores(9), D.indicadores(D.S_CORTE)]
    def fila(nombre, clave, fmt="s"):
        out = [nombre]
        for p in pts:
            v = p[clave]
            out.append(f"{v:,.2f}" if fmt == "s" else (f"{v:.3f}" if fmt == "i" else f"{100 * v:.1f} %"))
        return out
    U.tabla(doc, ["Indicador", "Semana 6", "Semana 9", f"Semana {D.S_CORTE} (corte)"], [
        fila("BAC (S/)", "pv") if False else ["BAC (S/)", f"{D.BAC:,.2f}", f"{D.BAC:,.2f}", f"{D.BAC:,.2f}"],
        fila("PV — valor planificado (S/)", "pv"), fila("EV — valor ganado (S/)", "ev"), fila("AC — costo real (S/)", "ac"),
        fila("SV = EV − PV (S/)", "sv"), fila("CV = EV − AC (S/)", "cv"), fila("SPI = EV / PV", "spi", "i"), fila("CPI = EV / AC", "cpi", "i"),
        fila("% completado = EV / BAC", "pct", "p"),
        fila("EAC = BAC / CPI (S/)", "eac1"), fila("EAC = AC + (BAC − EV) (S/)", "eac2"), fila("EAC = AC + (BAC − EV)/(CPI×SPI) (S/)", "eac3"),
        fila("ETC = EAC − AC (S/)", "etc"), fila("VAC = BAC − EAC (S/)", "vac"),
        ["TCPI = (BAC − EV)/(BAC − AC)"] + [(f"{p['tcpi']:.3f}" if p['ac'] < D.BAC else "no aplica (AC > BAC)") for p in pts],
    ], anchos=[7.0, 3.2, 3.2, 3.2], alinear=["l", "r", "r", "r"], tam=8.5, titulo="Indicadores de valor ganado")

    p6, p9, p11 = pts
    U.h3(doc, "Interpretación")
    U.viñetas(doc, [
        f"**Semana 6 (inicio del desarrollo):** SPI {p6['spi']:.2f} y CPI {p6['cpi']:.2f}. Hay un ligero atraso de {abs(p6['sv']):,.0f} soles de trabajo por las entrevistas más largas de lo previsto; el costo está casi en línea. Se aceptó, sin acción adicional.",
        f"**Semana 9 (pleno desarrollo):** SPI {p9['spi']:.2f} y CPI {p9['cpi']:.2f}. El proyecto va más lento y es menos eficiente en costos (CV = {p9['cv']:,.0f}). El TCPI de {p9['tcpi']:.2f} indica que había que mejorar el rendimiento en un {100 * (p9['tcpi'] - 1):.0f} % para terminar con el BAC, lo que no era realista. "
        "**Acción correctiva:** el PM autorizó horas adicionales en integraciones y dejó para el final las actividades con holgura.",
        f"**Semana {D.S_CORTE} (corte):** SPI {p11['spi']:.2f}: el plazo se recuperó y las actividades planificadas están terminadas. CPI {p11['cpi']:.2f}: recuperar el plazo costó horas extra, y el costo acumulado ({s(p11['ac'])}) ya supera el BAC.",
        f"**Pronóstico:** con el desempeño de costo observado, el costo final es de **{s(p11['eac1'])}** (VAC = {s(p11['vac'])}, un sobrecosto de {pct(-p11['vac'] / D.BAC)}).",
    ])
    U.h2(doc, "8.6 Uso de las reservas")
    usado = -p11["vac"]
    U.tabla(doc, ["Concepto", "Monto (S/)"], [
        ["Costo base (BAC)", f"{D.BAC:,.2f}"],
        ["Costo final proyectado (EAC = BAC / CPI)", f"{p11['eac1']:,.2f}"],
        ["Sobrecosto a cubrir (−VAC)", f"{usado:,.2f}"],
        ["Reserva de contingencia disponible", f"{D.RESERVA_CONTINGENCIA:,.2f}"],
        ["**Contingencia utilizada**", f"**{usado:,.2f}  ({pct(usado / D.RESERVA_CONTINGENCIA)} de la reserva)**"],
        ["Contingencia que queda", f"{D.RESERVA_CONTINGENCIA - usado:,.2f}"],
        ["Reserva de gestión (sin uso)", f"{D.RESERVA_GESTION:,.2f}"],
    ], anchos=[10.6, 6.0], alinear=["l", "r"], tam=9, titulo="Cobertura del sobrecosto con la reserva de contingencia")
    U.parrafo(doc, "El sobrecosto se origina principalmente en tres paquetes con costo por encima de lo estimado: el correo y las campañas (3.7), el esquema de base de datos con seguridad (3.1) y la importación de archivos (3.3). "
                   "Esto coincide con los riesgos R05 (bloqueo de correo en el alojamiento) y R02 (cambios de requisitos), cuya reserva ya estaba prevista.", alineacion="justificado")

    U.h2(doc, "8.7 Costos recurrentes después de la transferencia")
    U.parrafo(doc, "El desarrollo no genera costo para el hospital. La operación sí puede generarlo si el uso supera los límites gratuitos. Los valores son **referenciales** (precios de lista de cada proveedor, por verificar al contratar).")
    U.tabla(doc, ["Servicio", "Plan actual", "Costo actual", "Plan siguiente (referencial)", "Cuándo se necesita"], [
        ["Portal web (Vercel)", "Hobby", "S/ 0", "Pro ≈ US$ 20 / mes", "Uso comercial o mayor tráfico"],
        ["Base de datos y autenticación (Supabase)", "Free (500 MB)", "S/ 0", "Pro ≈ US$ 25 / mes", "Más de 500 MB o respaldos diarios"],
        ["Reloj de recordatorios (Render)", "Free", "S/ 0", "Starter ≈ US$ 7 / mes", "Evitar que el servicio se duerma"],
        ["Correo (cuenta con contraseña de aplicación)", "Gratuito (≈ 500 envíos/día)", "S/ 0", "Servicio de correo transaccional (por consumo)", "Campañas masivas"],
        ["Mensajería SMS (etapa futura)", "No incluido", "—", "Por consumo (por definir con la Dirección)", "Donantes sin correo ni internet"],
        ["Subdominio institucional", "hemocax.vercel.app", "S/ 0", "Subdominio del HRDC", "Imagen institucional"],
    ], anchos=[4.6, 2.6, 1.8, 4.2, 3.4], tam=8.5, titulo="Costos recurrentes de operación (referenciales)")
    U.parrafo(doc, "Se solicita a la Dirección del HRDC definir quién asumirá estos costos al concluir la transferencia. Con infraestructura propia del hospital y un subdominio institucional, el costo se reduce de forma considerable.", tam=9.5)
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
PRUEBAS = [
    ("PF-01", "Alta de donante y búsqueda por DNI/nombre; la ficha muestra aptitud", "RF-01, RF-03", "Enfermería", "Aprobada"),
    ("PF-02", "Importación CSV con filas válidas e inválidas (DNI corto, sexo vacío, «No sé»)", "RF-02", "Enfermería", "Aprobada"),
    ("PF-03", "Cálculo de aptitud: apto, en espera, máximo anual e inactivo (hombre y mujer)", "RF-04", "Enfermería", "Aprobada"),
    ("PF-04", "Registro de donación; la base rechaza la que supera el máximo anual; excepción de intervalo", "RF-05", "Enfermería", "Aprobada"),
    ("PF-05", "Liberación de un resultado, marca de crítico y retirada de la marca", "RF-06", "Médico", "Aprobada"),
    ("PF-06", "Portal del donante en computadora y en celular (320 y 375 px)", "RF-07", "Donante", "Aprobada"),
    ("PF-07", "Consentimiento: otorgar, revocar, historial y versión del texto", "RF-08", "Enfermería y donante", "Aprobada"),
    ("PF-08", "Correo individual real a un donante con consentimiento (diseño institucional)", "RF-09", "Enfermería", "Aprobada"),
    ("PF-09", "Campaña dirigida con vista previa; sin envío doble", "RF-10", "Médico", "Aprobada"),
    ("PF-10", "Automatizaciones: sin plantilla aprobada no se envía; simulación sin registro", "RF-11, RF-12", "Administrador", "Aprobada con observación: falta aprobar las plantillas"),
    ("PF-11", "Parámetros: cambiar intervalo y recomendaciones", "RF-13", "Administrador", "Aprobada"),
    ("PF-12", "Reportes y descargas CSV", "RF-15", "Médico", "Aprobada"),
    ("PS-01", "El donante no lee tablas del personal, plantillas ni bitácora", "RNF-04", "Donante", "Aprobada"),
    ("PS-02", "El donante no lee un resultado crítico aunque lo solicite directamente", "RF-06, RF-07", "Donante", "Aprobada"),
    ("PS-03", "Solo el administrador gestiona cuentas; no se desactiva al último administrador", "RF-14", "Administrador", "Aprobada"),
    ("PS-04", "Solo el administrador consulta la bitácora", "RF-16", "Administrador", "Aprobada"),
    ("PS-05", "Descarga de datos del donante y anonimización con confirmación", "RF-17", "Administrador", "Aprobada"),
    ("PS-06", "Las rutas del servidor rechazan peticiones sin sesión o sin secreto", "RNF-04", "—", "Aprobada"),
]


def calidad(doc):
    U.h1(doc, "9. Gestión de la calidad del proyecto")
    U.h2(doc, "9.1 Plan de gestión de la calidad")
    U.tabla(doc, ["Proceso", "Qué se hace en HEMOCAX", "Responsable"], [
        ["Planificar la calidad", "Se definen estándares (ISO/IEC 25010, Ley N.° 29733), métricas cuantificables y criterios de aceptación por requisito.", "QA con el PM"],
        ["Gestionar la calidad (aseguramiento)", "Revisión de código entre pares, prototipos validados con el Banco de Sangre, compilación sin errores de tipos antes de cada despliegue, ayuda integrada.", "Líder Técnico"],
        ["Controlar la calidad", "Pruebas funcionales y de seguridad por rol, registro de defectos por módulo, análisis de Pareto e Ishikawa, piloto interno.", "QA"],
    ], anchos=[4.2, 9.4, 3.0], tam=9, primera_negrita=True, titulo="Procesos de la gestión de la calidad")
    U.tabla(doc, ["Estándar o referencia", "Aplicación"], [
        ["ISO/IEC 25010:2011 (SQuaRE)", "Modelo de calidad del producto: las métricas de la sección 9.3 se definen con sus características."],
        ["Ley N.° 29733 y D.S. N.° 016-2024-JUS", "Requisitos de seguridad, consentimiento y minimización de datos."],
        ["OWASP (lista de verificación)", "Criterios de seguridad de la aplicación web usados como lista de control (no es una auditoría completa)."],
        ["Referencia a ISO 9001", "Enfoque de mejora continua en el ciclo de revisión semanal."],
    ], anchos=[5.6, 11.0], tam=9, titulo="Estándares y normas consideradas")

    U.h2(doc, "9.2 Costo de la calidad (CoQ)")
    U.parrafo(doc, "El CoQ agrupa lo que el proyecto invierte para lograr calidad (**prevención** y **evaluación**, costos de conformidad) y lo que pierde por no lograrla (**fallas internas** y **externas**, costos de no conformidad). "
                   "Según Crosby, «lo que cuesta dinero son las cosas sin calidad».", alineacion="justificado")
    filas = []
    for cat in D.COQ_CAT:
        for k, act, hh in D.COQ:
            if k == cat:
                filas.append([k, act, str(hh), f"{hh * D.TARIFA:,.2f}"])
    U.tabla(doc, ["Categoría", "Actividad", "HH", "Costo (S/)"], filas, anchos=[3.0, 10.2, 1.4, 2.0], alinear=["l", "l", "c", "r"], tam=8.5,
            titulo=f"Costos de calidad detallados (tarifa S/ {D.TARIFA:.2f} por hora)")
    filas = []
    for cat in D.COQ_CAT:
        filas.append([cat, str(D.COQ_HH[cat]), f"{D.COQ_COSTO[cat]:,.2f}", pct(D.COQ_COSTO[cat] / D.COQ_TOTAL), "Conformidad" if cat in ("Prevención", "Evaluación") else "No conformidad"])
    filas.append(["**TOTAL CoQ**", f"**{sum(D.COQ_HH.values())}**", f"**{D.COQ_TOTAL:,.2f}**", "100 %", f"CC {s(D.COQ_CC)} | CNC {s(D.COQ_CNC)}"])
    U.tabla(doc, ["Categoría", "HH", "Costo (S/)", "% del CoQ", "Tipo"], filas, anchos=[4.0, 1.6, 3.0, 2.4, 5.6], alinear=["l", "c", "r", "c", "l"], tam=9, titulo="Resumen del CoQ")
    U.figura(doc, FIG + "coq.png", 12.5, "Distribución del costo de la calidad")
    U.parrafo(doc, f"El CoQ es el **{pct(D.COQ_TOTAL / D.BAC)}** del BAC, dentro del rango típico de 15 a 30 % para proyectos de TI. El {pct(D.COQ_CC / D.COQ_TOTAL)} es costo de conformidad, es decir, inversión proactiva en calidad.", alineacion="justificado")
    U.h3(doc, "Análisis costo-beneficio de la calidad")
    U.parrafo(doc, "Relación C-B = beneficio / inversión en calidad. Si es mayor que 1, la inversión es rentable. Los supuestos están marcados.")
    U.tabla(doc, ["Concepto", "Cálculo", "Valor (S/)"], [
        ["Sin plan de calidad: fallas esperadas", f"({D.CB_DEFECTOS_SIN_PLAN} defectos × {D.CB_HORAS_POR_DEFECTO} h + {D.CB_RETRABAJO_REQUISITOS} h de rediseño por requisitos mal entendidos) × S/ {D.TARIFA:.2f}  (supuesto)", f"{D.CB_FALLAS_SIN:,.2f}"],
        ["Con plan de calidad: fallas que llegaron al usuario", f"{D.CB_DEFECTOS_CON_PLAN} defectos × {D.CB_HORAS_POR_DEFECTO} h × S/ {D.TARIFA:.2f}", f"{D.CB_FALLAS_CON:,.2f}"],
        ["**Beneficio** (costos de falla evitados)", "Fallas sin plan − fallas con plan", f"**{D.CB_BENEFICIO:,.2f}**"],
        ["**Inversión** en calidad", f"Prevención {D.COQ_COSTO['Prevención']:,.2f} + Evaluación {D.COQ_COSTO['Evaluación']:,.2f}", f"**{D.CB_INVERSION:,.2f}**"],
        ["**Relación C-B**", f"{D.CB_BENEFICIO:,.2f} / {D.CB_INVERSION:,.2f}", f"**{D.CB_RATIO:.2f}**"],
    ], anchos=[5.2, 8.6, 2.8], alinear=["l", "l", "r"], tam=8.5, titulo="Análisis costo-beneficio")
    U.caja(doc, f"Por cada sol invertido en calidad se evitaron S/ {D.CB_RATIO:.2f} en costos de falla (rentabilidad de {100 * (D.CB_RATIO - 1):.0f} %). **Decisión: la inversión en el plan de calidad se justifica.**", color="EAF7EE")

    U.h2(doc, "9.3 Métricas de calidad ISO/IEC 25010")
    U.parrafo(doc, "Cada característica se mide con una métrica cuantificable (no «que sea rápido», sino «≤ 3 segundos»). El estado corresponde al corte del informe.")
    U.seccion(doc, horizontal=True)
    U.tabla(doc, ["N.°", "Característica ISO 25010", "Métrica específica", "Meta", "Método de medición", "Frecuencia", "Estado al corte"], [
        ["1", "Adecuación funcional (completitud)", "% de requisitos funcionales implementados y verificados", "100 % de los RF «Alta» y ≥ 95 % del total", "Registro de pruebas funcionales (PF) contra la lista de RF", "Cada ciclo semanal", "**17 de 17 RF** implementados y verificados"],
        ["2", "Eficiencia de desempeño (comportamiento temporal)", "Tiempo de carga del portal del donante en red 4G", "≤ 3 s", "Medición con las herramientas del navegador", "Antes de cada despliegue", "En seguimiento durante la operación"],
        ["3", "Usabilidad (operabilidad y aprendizaje)", "Tarea clave: la enfermera registra una donación; el donante ve «¿puedo donar?»", "Enfermería ≤ 2 min; donante ≤ 10 s; valoración ≥ 4.0/5", "Observación en el piloto y encuesta", "Piloto", "Pendiente del piloto con el Banco de Sangre"],
        ["4", "Fiabilidad (disponibilidad y tolerancia a fallos)", "Disponibilidad mensual; % de correos enviados con éxito", "≥ 99 % y ≥ 95 %", "Monitor externo /health; estados SENT / FAILED en la bitácora de correos", "Semanal", "En seguimiento durante la operación"],
        ["5", "Seguridad (confidencialidad)", "% de tablas con seguridad por filas; resultados críticos legibles por el donante", "100 % y 0", "Revisión de migraciones y prueba con sesión de donante", "Antes del despliegue", "**13 de 13 tablas** con RLS; **0** críticos legibles (PS-01, PS-02)"],
        ["6", "Mantenibilidad (capacidad de ser modificado)", "Compilación sin errores de tipos; documentación técnica completa", "0 errores; README + migraciones versionadas", "Compilación (npm run build) y revisión de documentos", "Cada despliegue", "Cumplida"],
        ["7", "Compatibilidad / Portabilidad", "Funciona en Chrome, Edge, Firefox y Chrome para Android", "Sin errores críticos", "Pruebas manuales en cada navegador y en celular", "Piloto", "Cumplida en navegadores de escritorio y celular (PF-06)"],
    ], anchos=[1.0, 4.0, 5.2, 3.6, 5.2, 2.4, 4.8], alinear=["c", "l", "l", "l", "l", "l", "l"], tam=8, titulo="Métricas de calidad ISO/IEC 25010")
    U.seccion(doc, horizontal=False)

    U.h2(doc, "9.4 Herramientas básicas de calidad")
    U.h3(doc, "Diagrama de Pareto — defectos por módulo")
    tot = sum(v for _, v in D.DEFECTOS)
    ac = 0
    filas = []
    for nom, v in D.DEFECTOS:
        ac += v
        filas.append([nom, str(v), pct(v / tot), pct(ac / tot), "Sí" if (ac - v) / tot < 0.8 else "—"])
    filas.append(["**Total**", f"**{tot}**", "100 %", "", ""])
    U.tabla(doc, ["Módulo", "Defectos", "% individual", "% acumulado", "Zona 80 %"], filas, anchos=[7.4, 2.0, 2.4, 2.6, 2.2], alinear=["l", "c", "c", "c", "c"], tam=9,
            titulo=f"Defectos registrados durante las pruebas (n = {tot})")
    U.figura(doc, FIG + "pareto.png", 14.0, "Diagrama de Pareto de defectos por módulo")
    n80 = sum(1 for i in range(len(D.DEFECTOS)) if sum(v for _, v in D.DEFECTOS[:i]) / tot < 0.8)
    U.parrafo(doc, f"Los primeros {n80} módulos concentran el {pct(sum(v for _, v in D.DEFECTOS[:n80]) / tot)} de los defectos. **Prioridad correctiva:** Comunicaciones y automatizaciones (13), Importación y registro de donantes (10), Portal del donante (9) y Panel del personal (7).", alineacion="justificado")
    U.h3(doc, "Diagrama de Ishikawa — causa principal")
    U.figura(doc, FIG + "ishikawa.png", 16.4, "Ishikawa del módulo con más defectos")
    U.h3(doc, "Plan de acción correctiva")
    U.tabla(doc, ["Causa raíz", "Acción", "Responsable", "Estado"], [
        ["Plan gratuito del reloj bloquea el puerto SMTP", "El portal envía los correos; el reloj solo decide cuándo.", "Integraciones", "Hecha"],
        ["Sin prueba temprana de envío real", "Prueba de concepto de envío en la primera semana de cualquier proyecto de correo.", "Integraciones", "Lección aprendida"],
        ["Sin pruebas automáticas de duplicados", "Índices únicos en la base de datos que impiden duplicados aunque el reloj corra dos veces.", "Líder Técnico", "Hecha"],
        ["Modo simulación confuso", "Modo seguro por defecto (solo `false` envía) y documentar los estados.", "Integraciones", "Hecha; mejora pendiente en el estado de la simulación"],
        ["Variables de entorno distintas", "Plantilla .env.example y lista de verificación de despliegue.", "Líder Técnico", "Hecha"],
        ["Límite de envíos del correo gratuito", "Registrar el consumo y plan de ampliación para la Dirección.", "PM", "En seguimiento"],
    ], anchos=[4.8, 6.6, 2.6, 2.6], tam=8.5, titulo="Acciones derivadas del Ishikawa")
    U.h3(doc, "Hoja de verificación — liberación a producción")
    U.tabla(doc, ["N.°", "Ítem de verificación", "Cumple"], [
        ["1", "La compilación termina sin errores de tipos.", "☑"],
        ["2", "Todas las tablas nuevas tienen seguridad por filas y políticas por rol.", "☑"],
        ["3", "Las variables de entorno están cargadas y las claves privadas solo en el servidor.", "☑"],
        ["4", "La prueba con cuenta de donante no accede a críticos, plantillas ni bitácora.", "☑"],
        ["5", "El modo de envío está en simulación hasta aprobar las plantillas.", "☑"],
        ["6", "El monitor externo consulta /health y el reloj responde.", "☑"],
        ["7", "Los datos de prueba fueron eliminados.", "☑"],
        ["8", "El cambio quedó registrado en el control de versiones.", "☑"],
    ], anchos=[1.2, 13.0, 2.4], alinear=["c", "l", "c"], tam=9, titulo="Lista de verificación de despliegue")
    U.parrafo(doc, "El diagrama de flujo del proceso de resultados está en el capítulo 5 (Figura de flujo de resultados). No se usaron histograma, diagrama de dispersión ni gráfica de control porque no hubo series de datos suficientes en un proyecto de once semanas.", tam=9.5)

    U.h2(doc, "9.5 Registro de pruebas")
    U.tabla(doc, ["Código", "Prueba", "Requisitos", "Rol de prueba", "Resultado"], [list(x) for x in PRUEBAS],
            anchos=[1.4, 8.0, 2.2, 2.4, 2.8], alinear=["c", "l", "c", "l", "l"], tam=8, titulo="Pruebas funcionales (PF) y de seguridad (PS)")
    U.parrafo(doc, "Las pruebas se ejecutaron manualmente con datos temporales que luego se eliminaron. No hay aún pruebas automatizadas; se declara como limitación y como trabajo futuro.", tam=9.5)
    U.salto_pagina(doc)


def construir(doc):
    costos(doc)
    calidad(doc)
