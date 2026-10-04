# -*- coding: utf-8 -*-
"""Parte II (4) y III: adquisiciones, control de cambios, informe de avance y cierre."""
import datos as D
import docx_utils as U
from cap_d import CORTO
from fmt import f, s, n, pct

FIG = "fig/"

SCR = [  # id, fecha, solicitante, descripción, área, alcance, tiempo(d), costo(S/), prioridad, aprobado por, estado
    ("SCR-01", "07/09/2026", "PM / Banco de Sangre", "Cambiar el canal de mensajes de WhatsApp y SMS a correo electrónico, porque WhatsApp exige cuenta empresarial y plantillas aprobadas por un tercero.",
     "Comunicación (3.7, 3.8)", "Cambia el canal de RF-09 a RF-11", "0", "0.00", "Alta", "Sponsor", "Aprobado e implementado"),
    ("SCR-02", "17/09/2026", "Integraciones", "Enviar los correos desde el portal en lugar del servicio del reloj, que no permite salida SMTP en el plan gratuito (riesgo R05 materializado).",
     "Técnico (3.7, 3.8)", "Sin cambio", "+2", "128.00", "Alta", "PM con el equipo", "Aprobado e implementado"),
    ("SCR-03", "27/08/2026", "Analista Funcional", "Ingreso al sistema solo con DNI y contraseña (sin correo), porque muchos donantes no tienen correo.",
     "Seguridad y acceso (3.1, 3.9)", "Aclara RF-14", "0", "0.00", "Media", "PM", "Aprobado e implementado"),
    ("SCR-04", "10/09/2026", "Dra. Marimar / Analista", "Rediseñar el portal del donante en una sola pantalla, con letra grande, íconos y baja carga, para zonas rurales.",
     "Portal del donante (3.9)", "Precisa RNF-03", "+1", "32.00", "Alta", "PM con el equipo", "Aprobado e implementado"),
    ("SCR-05", "11/09/2026", "Jefatura del Banco de Sangre", "Plantillas de mensajes automáticos con aprobación previa y consentimiento versionado con historial.",
     "Consentimiento y automatizaciones (3.6, 3.8)", "Precisa RF-08 y RF-12", "+2", "64.00", "Alta", "Sponsor", "Aprobado e implementado"),
    ("SCR-06", "14/09/2026", "Jefatura / Ley N.° 29733", "Incluir los derechos del titular: descarga de datos y anonimización a pedido.",
     "Consentimiento y ARCO (3.6)", "Precisa RF-17", "+1", "48.00", "Alta", "PM con el equipo", "Aprobado e implementado"),
    ("SCR-07", "18/09/2026", "Enfermería", "Simplificar el panel del personal: buscador grande «Atender a un donante» y lenguaje de cada puesto.",
     "Panel del personal (3.10)", "Precisa RNF-03", "+1", "48.00", "Media", "PM con el equipo", "Aprobado e implementado"),
    ("SCR-08", "21/09/2026", "Banco de Sangre", "Programar campañas para una fecha futura.", "Campañas (3.7)", "Nuevo requisito", "+3", "192.00", "Baja", "Sponsor", "Diferido a la etapa siguiente"),
    ("SCR-09", "22/09/2026", "Dirección / OEI", "Agregar el envío de mensajes por SMS para donantes sin correo.", "Comunicación", "Nuevo canal", "+8", "Por definir", "Media", "Sponsor", "Diferido: requiere definir el costo recurrente"),
]


def adquisiciones(doc):
    U.h1(doc, "13. Gestión de las adquisiciones")
    U.parrafo(doc, "La gestión de las adquisiciones es el proceso de comprar o contratar productos, servicios o resultados que se necesitan fuera del equipo del proyecto. "
                   "En el PMBOK 7 se vincula con el principio de *valor* y el dominio de *trabajo del proyecto*, y se centra en la colaboración, la ética y la adaptabilidad.", alineacion="justificado")
    U.h2(doc, "13.1 Plan de gestión de adquisiciones")
    U.tabla(doc, ["Proceso", "Qué se hace en HEMOCAX", "Responsable"], [
        ["Planificar las adquisiciones", "Decidir qué se hace y qué se contrata; elegir tipo de contrato; preparar la declaración del trabajo (SOW) y los criterios de selección.", "PM"],
        ["Efectuar las adquisiciones", "Evaluar alternativas con criterios ponderados y aceptar los términos del proveedor elegido.", "Líder Técnico e Integraciones"],
        ["Controlar las adquisiciones", "Vigilar el cumplimiento del plan del proveedor, sus límites de uso y las incidencias.", "Integraciones"],
        ["Cerrar las adquisiciones", "Verificar entrega, cerrar cuentas y archivar documentos.", "PM"],
    ], anchos=[4.2, 9.4, 3.0], tam=9, primera_negrita=True, titulo="Procesos de gestión de adquisiciones")
    U.parrafo(doc, "**Políticas:** (1) no se firman contratos de pago sin autorización del sponsor; (2) toda compra en efectivo queda en el presupuesto de gastos directos; (3) se leen y respetan los términos de uso de cada proveedor; "
                   "(4) se prefieren planes gratuitos o educativos que no comprometan datos personales; (5) ningún dato personal real se envía a un proveedor sin una base legal documentada.", tam=9.5)

    U.h2(doc, "13.2 Análisis de hacer o comprar")
    U.tabla(doc, ["Elemento", "Decisión", "Razón"], [
        ["Código del portal, panel, reglas y automatizaciones", "**Hacer**", "Es el objeto del proyecto y requiere control total de la seguridad."],
        ["Alojamiento del portal (Vercel)", "Comprar / contratar servicio", "Despliegue automático y soporte nativo del framework; plan gratuito."],
        ["Base de datos y autenticación (Supabase)", "Comprar / contratar servicio", "Evita administrar servidores; trae seguridad por filas; plan gratuito."],
        ["Reloj de tareas programadas (Render)", "Comprar / contratar servicio", "Se necesita un proceso siempre activo que el alojamiento del portal no ofrece."],
        ["Envío de correo (cuenta con contraseña de aplicación)", "Comprar / contratar servicio", "Sin trámite ni costo para el piloto."],
        ["Diseño de prototipos (Figma Education)", "Comprar / contratar servicio", "Plan educativo gratuito."],
        ["Impresión y encuadernación de manuales", "Comprar", "Servicio local pequeño; costo menor."],
        ["Capacitación del personal", "**Hacer**", "El equipo conoce el sistema."],
        ["Mensajería SMS", "Comprar (etapa futura)", "Depende de la decisión de la Dirección sobre el costo recurrente."],
    ], anchos=[6.6, 3.6, 6.4], tam=8.5, titulo="Decisiones de hacer o comprar")

    U.h2(doc, "13.3 Registro de adquisiciones")
    U.seccion(doc, horizontal=True)
    U.tabla(doc, ["ID", "Bien o servicio", "Proveedor", "Tipo de acuerdo", "Costo", "Fecha", "Responsable", "Documento"], [
        ["A-01", "Alojamiento del portal", "Vercel (Hobby)", "Términos de servicio (precio fijo: gratuito)", "S/ 0.00", "17/08/2026", "Integraciones", "Cuenta y términos de uso"],
        ["A-02", "Base de datos y autenticación", "Supabase (Free)", "Términos de servicio (precio fijo: gratuito)", "S/ 0.00", "17/08/2026", "Líder Técnico", "Proyecto y términos"],
        ["A-03", "Reloj de recordatorios", "Render (Free)", "Términos de servicio (precio fijo: gratuito)", "S/ 0.00", "09/09/2026", "Integraciones", "Servicio y términos"],
        ["A-04", "Correo electrónico (SMTP)", "Google (cuenta con contraseña de aplicación)", "Términos de servicio", "S/ 0.00", "09/09/2026", "Integraciones", "Cuenta del proyecto"],
        ["A-05", "Repositorio y tablero", "GitHub", "Términos de servicio", "S/ 0.00", "21/07/2026", "Líder Técnico", "Organización/repositorio"],
        ["A-06", "Prototipos", "Figma (Education)", "Términos de servicio", "S/ 0.00", "21/07/2026", "Analista", "Cuenta educativa"],
        ["A-07", "Impresión de manuales (3 juegos) y documentos (2 ejemplares)", "Servicio de impresión local (por seleccionar)", "Precio fijo cerrado (FFP)", "S/ 110.00", "05/10/2026", "PM", "Cotización y contrato modelo (Anexo D.1)"],
        ["A-08", "Transporte y refrigerios de sesiones", "Compras menores", "Pago en efectivo", "S/ 100.00", "Todo el proyecto", "PM", "Comprobantes"],
        ["A-09", "Mensajería SMS (etapa futura)", "Por seleccionar", "Precio fijo más incentivos (FPIF) propuesto", "Por definir", "Posterior al cierre", "Dirección del HRDC", "Contrato modelo (Anexo D.2)"],
        ["A-10", "Subdominio institucional", "OEI del HRDC", "Compromiso institucional", "S/ 0.00", "Posterior al cierre", "OEI", "Solicitud al hospital"],
    ], anchos=[1.2, 4.6, 4.2, 4.4, 1.9, 2.6, 2.6, 4.4], alinear=["c", "l", "l", "l", "r", "c", "l", "l"], tam=8, titulo="Registro de adquisiciones")
    U.seccion(doc, horizontal=False)

    U.h2(doc, "13.4 Tipos de contrato y elección")
    U.tabla(doc, ["Tipo", "Descripción", "Riesgo principal lo asume", "Cuándo conviene"], [
        ["**FFP** — Precio fijo cerrado", "El precio es inamovible; los cambios van por orden de cambio.", "El proveedor", "Requisitos claros y estables (software con alcance definido)."],
        ["**FPIF** — Precio fijo más incentivos", "Precio objetivo, techo y reparto de ahorros o sobrecostos; bonos por desempeño medible.", "Compartido", "Cuando el rendimiento, la calidad o el plazo son críticos y se pueden medir."],
        ["**CPFF / CPIF** — Costo reembolsable", "El comprador paga los costos reales más una ganancia.", "El comprador", "Alcance incierto, investigación y desarrollo."],
        ["**T&M** — Tiempo y materiales", "Híbrido: se paga por el tiempo trabajado y los materiales, con tope.", "Compartido", "Trabajos cortos o con alcance no totalmente claro."],
    ], anchos=[3.6, 5.4, 3.0, 4.6], tam=8.5, titulo="Tipos de contrato")
    U.parrafo(doc, "**Aplicación (caso práctico de la clase).** Un desarrollo de software con requisitos claros, como el módulo de inventario del contrato modelo, se contrata mejor con **precio fijo cerrado (FFP)**. "
                   "Un proyecto de investigación y desarrollo, donde el alcance se descubre, debe usar **costo reembolsable**. En HEMOCAX: la impresión de manuales (alcance trivial) es FFP; el servicio de mensajería futuro, "
                   "cuyo rendimiento (entregas, tiempos) es medible y crítico, se propone como **FPIF**.", alineacion="justificado")

    U.h2(doc, "13.5 Declaración del trabajo (SOW)")
    U.h3(doc, "SOW 1 — Impresión y encuadernación de manuales (FFP)")
    U.tabla(doc, ["Elemento", "Descripción"], [
        ["Propósito", "Entregar copias físicas de la documentación al Banco de Sangre, a la OEI y a la docente."],
        ["Alcance del trabajo", "Impresión a color y encuadernación de 3 juegos del manual de usuario y manual técnico (≈ 60 páginas c/u) y 2 ejemplares anillados del informe de gestión."],
        ["Lugar de ejecución", "Cajamarca (entrega en la Escuela de Ingeniería de Sistemas)."],
        ["Periodo de ejecución", "3 días hábiles desde la entrega de los archivos finales (semana 12)."],
        ["Entregables", "3 juegos encuadernados + 2 ejemplares anillados."],
        ["Estándares de aceptación", "Sin páginas faltantes, fuera de orden o ilegibles; colores y tamaño conforme al archivo PDF."],
        ["Requisitos especiales", "Confidencialidad: no conservar copias digitales ni reproducir el contenido."],
        ["Forma de pago", "S/ 110.00 contra entrega y conformidad."],
    ], anchos=[4.2, 12.4], tam=8.5, primera_negrita=True, zebra=False)
    U.h3(doc, "SOW 2 — Servicio de mensajería para el Banco de Sangre (FPIF, etapa futura)")
    U.tabla(doc, ["Elemento", "Descripción"], [
        ["Propósito", "Contar con un canal institucional de mensajes (correo transaccional y SMS) para llegar a donantes sin correo o con conexión limitada."],
        ["Alcance del trabajo", "Envío de mensajes automáticos y de campaña desde el sistema, con reporte de entrega, durante 12 meses."],
        ["Entregables", "API de envío integrada, reportes mensuales de entrega, soporte técnico de nivel 1 y 2."],
        ["Estándares de aceptación", "Entrega ≥ 98 %; latencia al 95 % ≤ 60 s; disponibilidad del servicio ≥ 99.5 %."],
        ["Requisitos especiales", "Protección de datos personales conforme a la Ley N.° 29733; el contenido no incluye datos médicos."],
        ["Forma de pago", "Pagos mensuales base + incentivos por desempeño (ver el contrato modelo D.2)."],
    ], anchos=[4.2, 12.4], tam=8.5, primera_negrita=True, zebra=False)

    U.h2(doc, "13.6 Criterios de selección de proveedores")
    U.parrafo(doc, "Para cada decisión se definieron criterios con peso, se puntuó a cada alternativa de 1 (malo) a 5 (excelente) y se calculó el puntaje ponderado.")
    for decision, criterios, alternativas, elegida in D.SELECCION:
        filas = []
        pesos = [c[1] for c in criterios]
        for i, (cn, cp) in enumerate(criterios):
            filas.append([cn, f"{int(cp * 100)} %"] + [str(alternativas[a][i]) for a in alternativas])
        totales = {a: sum(p * v for p, v in zip(pesos, alternativas[a])) for a in alternativas}
        filas.append(["**Puntaje ponderado**", "100 %"] + [f"**{totales[a]:.2f}**" for a in alternativas])
        U.tabla(doc, ["Criterio", "Peso"] + [("✔ " if a == elegida else "") + a for a in alternativas], filas,
                anchos=[6.0, 1.4] + [3.0] * len(alternativas), alinear=["l", "c"] + ["c"] * len(alternativas), tam=8.5, titulo=f"Selección: {decision} — elegida: {elegida}")
        mejor = max(totales, key=totales.get)
        assert mejor == elegida, (decision, totales)
    U.caja(doc, "Los criterios priorizan la **seguridad por filas** y el **costo cero**, que son las restricciones centrales del proyecto. La decisión del alojamiento se confirmó con la experiencia: "
                "el plan gratuito del reloj no permite salida SMTP, por lo que el envío se hizo desde el portal.", color="FEF9E7")

    U.h2(doc, "13.7 Evaluación y control de proveedores")
    U.tabla(doc, ["Proveedor", "Cumplimiento", "Observación"], [
        ["Supabase", "Cumple", "Seguridad por filas, autenticación y base de datos estable en el plan gratuito; vigilar límite de 500 MB y pausa por inactividad."],
        ["Vercel", "Cumple", "Despliegue automático desde el repositorio; permite enviar correo desde el servidor."],
        ["Render", "Cumple parcialmente", "Sirve como reloj, pero **bloquea la salida SMTP** en el plan gratuito y se duerme tras 15 minutos: se mitiga con un monitor externo (recomendado, por configurar)."],
        ["Correo (cuenta con contraseña de aplicación)", "Cumple con límite", "Límite diario de envíos suficiente para el piloto; no apto para campañas masivas."],
        ["Figma y GitHub", "Cumple", "Sin incidencias."],
    ], anchos=[4.0, 3.0, 9.6], tam=8.5, titulo="Evaluación de desempeño de proveedores")
    U.salto_pagina(doc)


def cambios(doc):
    U.h1(doc, "14. Gestión de cambios")
    U.h2(doc, "14.1 Proceso de control de cambios")
    U.tabla(doc, ["Paso", "Nombre", "Descripción", "Herramienta / salida", "Plazo"], [
        ["1", "Solicitud", "Cualquier integrante o interesado detecta una necesidad de cambio.", "Solicitud de cambio (descripción, justificación, área afectada)", "24 h"],
        ["2", "Evaluación de impacto", "El PM analiza el efecto en alcance, tiempo, costo, calidad y riesgos.", "Análisis documentado", "24 h"],
        ["3", "Clasificación", "Bajo (< 1 día y S/ 0.00): decide el PM. Medio (1-3 días y < S/ 50.00): PM con el equipo. Alto (> 3 días o > S/ 50.00): sponsor.", "Nivel de impacto y aprobador", "2 h"],
        ["4", "Decisión", "Aprobación o rechazo con justificación escrita.", "Acta de decisión", "PM 24 h; sponsor 48 h"],
        ["5", "Implementación", "Actualizar EDT, cronograma, línea base y notificar al equipo.", "Documentos con nueva versión", "Inmediato"],
        ["6", "Seguimiento", "Verificar que el cambio se aplicó y cerrar la solicitud.", "Reunión semanal y registro", "Siguiente reunión"],
    ], anchos=[1.1, 2.8, 6.4, 4.4, 1.9], alinear=["c", "l", "l", "l", "c"], tam=8.5, titulo="Proceso formal de control de cambios")
    U.h2(doc, "14.2 Registro de solicitudes de cambio (SCR)")
    U.seccion(doc, horizontal=True)
    filas = [[a, b, c_, d, e, g, h, i, j, k, l] for (a, b, c_, d, e, g, h, i, j, k, l) in SCR]
    U.tabla(doc, ["ID", "Fecha", "Solicitante", "Descripción del cambio", "Área afectada", "Impacto en alcance", "Tiempo (d)", "Costo (S/)", "Prioridad", "Aprobado por", "Estado"], filas,
            anchos=[1.3, 1.9, 2.8, 7.4, 3.2, 2.6, 1.3, 1.6, 1.4, 2.0, 3.0], alinear=["c", "c", "l", "l", "l", "l", "c", "r", "c", "l", "l"], tam=7.5, titulo="Registro de solicitudes de cambio")
    U.seccion(doc, horizontal=False)
    aprob = [x for x in SCR if x[10].startswith("Aprobado")]
    U.parrafo(doc, f"Se tramitaron **{len(SCR)} solicitudes**: {len(aprob)} aprobadas e implementadas (impacto estimado conjunto de +{sum(int(x[6].replace('+', '')) for x in aprob)} días y {s(sum(float(x[7]) for x in aprob))}, "
                   "absorbido por las reservas) y 2 diferidas a una etapa posterior. Todas pasaron por el proceso de clasificación y quedaron respaldadas en acta.", alineacion="justificado")
    U.h2(doc, "14.3 Control de configuración")
    U.viñetas(doc, [
        "El código y las migraciones SQL se versionan en Git; cada cambio importante es un *commit* descriptivo.",
        "Las migraciones de la base de datos se numeran y no se editan una vez aplicadas.",
        "Los documentos de gestión llevan control de versiones (tabla al inicio de este informe).",
        "Las claves y contraseñas no se guardan en el repositorio (archivo .env ignorado).",
    ])
    U.salto_pagina(doc)


def avance(doc):
    p = D.indicadores(D.S_CORTE)
    U.h1(doc, "15. Informe de avance del proyecto (semana 11)")
    U.parrafo(doc, f"**Proyecto:** HEMOCAX · **PM:** {D.EQUIPO['PM']['nombre']} · **Sponsor:** {D.DOCENTE} · **Semana de reporte:** 11 ({f(D.rango_semana(11)[0])} al {f(D.rango_semana(11)[1])}) · **Fecha de emisión:** {f(D.CORTE)}")
    U.h2(doc, "15.1 Estado del cronograma")
    pend = [a for a in D._A if a["fin"] >= D.CORTE and a["dur"] > 0]
    U.viñetas(doc, [
        "**Fase actual:** 4 y 5. Pruebas, piloto interno y capacitación casi concluidos; cierre en curso.",
        "**Completado esta semana:** despliegue en producción (3.11), piloto interno (4.4), correcciones (4.5), manuales y ayuda (4.6), video y guion de capacitación (4.7), informe final (5.1, este documento) y entrega del repositorio (5.2).",
        f"**Pendiente:** {', '.join(a['id'] + ' ' + a['nombre'].split('(')[0].strip() for a in pend)} (firma el {f(D.FIN_PLAN)}).",
        f"**Desvío del cronograma:** SPI = {p['spi']:.2f} · SV = {s(p['sv'])}. **Estado: 🟢 en tiempo** (el atraso de semanas 6 a 9 se recuperó).",
    ])
    U.h2(doc, "15.2 Estado del presupuesto (valor ganado)")
    U.tabla(doc, ["Indicador", "Valor", "Interpretación"], [
        ["BAC", s(D.BAC), "Presupuesto base aprobado."],
        ["PV acumulado (S11)", s(p["pv"]), "Trabajo planificado hasta el corte."],
        ["EV acumulado (S11)", s(p["ev"]), f"{pct(p['pct'])} del trabajo terminado."],
        ["AC acumulado (S11)", s(p["ac"]), "Costo real incurrido (ya supera el BAC)."],
        ["SV = EV − PV", s(p["sv"]), "Sin atraso: el plazo se recuperó."],
        ["CV = EV − AC", s(p["cv"]), "Sobrecosto de horas extra en integraciones y pruebas."],
        ["CPI = EV / AC", f"{p['cpi']:.3f}", "Ineficiente en costo: por cada sol gastado se entrega S/ 0.95 de valor."],
        ["SPI = EV / PV", f"{p['spi']:.3f}", "Cronograma al día."],
        ["EAC = BAC / CPI", s(p["eac1"]), "Costo total proyectado al cierre."],
        ["VAC = BAC − EAC", s(p["vac"]), f"Sobrecosto esperado; cubierto con {pct(-p['vac'] / D.RESERVA_CONTINGENCIA)} de la contingencia."],
    ], anchos=[4.0, 3.2, 9.4], alinear=["l", "r", "l"], tam=8.5, titulo="Estado del presupuesto al corte")
    U.h2(doc, "15.3 Riesgos activos")
    activos = sorted([r for r in D.RIESGOS if r["tipo"] == "Amenaza" and r["pi"] >= 10], key=lambda r: -r["pi"])[:5]
    U.tabla(doc, ["ID", "Descripción", "P×I", "Nivel", "Estado", "Acción tomada"],
            [[r["id"], CORTO[r["id"]], str(r["pi"]), "Alto", r.get("estado", "Vigente"), r["acc"]] for r in activos],
            anchos=[1.1, 6.0, 1.0, 1.4, 3.0, 4.1], alinear=["c", "l", "c", "c", "l", "l"], tam=8, titulo="Principales riesgos activos")
    U.parrafo(doc, "**Nuevos riesgos identificados esta semana:** ninguno.", tam=9.5)
    U.h2(doc, "15.4 Próximos hitos")
    U.tabla(doc, ["Hito", "Fecha", "Responsable", "Estado"], [
        ["Informe final y lecciones aprendidas", f(D.ACT["5.1"]["fin"]), D.EQUIPO["PM"]["corto"], "Completado"],
        ["Entrega de repositorio y documentación", f(D.ACT["5.2"]["fin"]), D.EQUIPO["LT"]["corto"], "Completado"],
        ["Acta de cierre y de aceptación", f(D.ACT["5.3"]["fin"]), D.EQUIPO["PM"]["corto"], "En tiempo"],
    ], anchos=[7.6, 2.6, 4.0, 2.4], alinear=["l", "c", "l", "c"], tam=9, titulo="Hitos pendientes")
    U.h2(doc, "15.5 Solicitudes de decisión al sponsor")
    U.numerada(doc, [
        f"**Autorizar el uso de la reserva de contingencia** por {s(-p['vac'])} (sobrecosto proyectado). Si no se decide antes del cierre, el acta no podrá reflejar el costo final.",
        "**Definir con la Dirección del HRDC** quién asume el costo recurrente de operación y si se aprueba la etapa de mensajería SMS (SCR-09).",
    ])
    U.salto_pagina(doc)


def cierre(doc):
    U.h1(doc, "PARTE III · MONITOREO Y CIERRE")
    U.h1(doc, "16. Cierre del proyecto")
    U.h2(doc, "16.1 Resultados frente a los objetivos")
    U.tabla(doc, ["Objetivo", "Indicador / evidencia", "Resultado"], [
        ["OE-01 Padrón digital", "Registro con consentimiento, importación y baja; 6 donantes del equipo cargados y consentimiento verificado.", "**Cumplido**"],
        ["OE-02 Recordatorio de retorno", "Automatización a las 08:15 con aptitud calculada y sin duplicados.", "**Cumplido en funcionalidad;** falta aprobar la plantilla para producción."],
        ["OE-03 Fidelización", "Agradecimiento, cumpleaños y reconocimiento anual implementados.", "**Cumplido en funcionalidad;** falta aprobar las plantillas."],
        ["OE-04 Campañas e información", "Campañas con vista previa e información publicada en el portal.", "**Cumplido**"],
        ["OE-05 Resultados en 48 h", "Flujo pendiente → liberado → avisado con alertas a 36 y 48 h.", "**Cumplido en funcionalidad;** el tiempo real se medirá con el uso del Banco de Sangre."],
        ["OE-06 Convocatoria dirigida", "Filtro por grupo y aptitud con conteo de O negativo.", "**Cumplido**"],
        ["OE-07 Datos seguros", "RLS en 13 de 13 tablas; críticos protegidos; bitácora; derechos del titular.", "**Cumplido;** falta la revisión legal formal del hospital."],
    ], anchos=[4.2, 7.8, 4.6], tam=8.5, titulo="Cumplimiento de los objetivos específicos")
    U.h2(doc, "16.2 Lecciones aprendidas")
    U.parrafo(doc, "Las lecciones se registraron a lo largo del proyecto (no solo al final), conforme al principio de aprendizaje continuo del PMBOK 7.")
    U.tabla(doc, ["N.°", "Área", "Situación", "Lección y recomendación"], [
        ["1", "Alcance", "El documento de propuesta ofrecía WhatsApp y SMS; el canal real fue el correo (SCR-01).", "Validar con el cliente las restricciones de canal y su costo antes de comprometerlo en el alcance."],
        ["2", "Adquisiciones / Técnico", "El plan gratuito del reloj no permitía enviar correos (R05).", "Hacer una prueba de concepto de las integraciones externas en la primera semana, no al final."],
        ["3", "Calidad", "La seguridad en la base de datos (RLS) evitó fallas de permisos, pero exigió pruebas con cada rol.", "Diseñar la seguridad primero y probar con una sesión de cada rol antes de cada despliegue."],
        ["4", "Usuarios", "Parte de los donantes proviene de zonas rurales (SCR-04).", "Prototipar con usuarios reales y diseñar para celulares de gama baja desde el inicio."],
        ["5", "Interesados", "Los valores clínicos y los textos necesitaron validación del médico.", "Parametrizar los valores y programar las validaciones con anticipación; documentarlos como supuestos."],
        ["6", "Costos", "El pico de carga de la semana 9 provocó horas extra y CPI < 1.", "Nivelar los recursos: adelantar el frontend a las semanas con baja carga."],
        ["7", "Calidad", "La regla del máximo anual está escrita dentro de la base de datos y también como parámetro de pantalla.", "Mantener una sola fuente de verdad para cada regla del negocio."],
        ["8", "Comunicaciones", "Las decisiones tomadas por mensajería rápida no quedaban registradas.", "Toda decisión se confirma por correo o acta (criterio de uso de herramientas)."],
        ["9", "Equipo", "Las dependencias de una sola persona para integraciones generaron riesgo.", "Documentar procedimientos y rotar responsabilidades."],
        ["10", "Gestión", "Los documentos de gestión deben actualizarse cuando cambia el alcance.", "Mantener sincronizados charter, EDT, presupuesto y riesgos con cada solicitud de cambio aprobada."],
    ], anchos=[0.9, 2.6, 6.2, 6.9], alinear=["c", "l", "l", "l"], tam=8, titulo="Registro de lecciones aprendidas")
    U.h2(doc, "16.3 Cierre de adquisiciones")
    U.tabla(doc, ["Ítem", "Estado"], [
        ["Cuentas de los servicios en la nube (A-01 a A-06)", "Vigentes; se transfieren al hospital o se dan de baja según su decisión."],
        ["Impresión de manuales (A-07)", "Pago contra entrega y conformidad (semana 12)."],
        ["Compras menores (A-08)", "Comprobantes archivados."],
        ["Mensajería SMS y subdominio (A-09, A-10)", "Pendientes de la decisión de la Dirección."],
    ], anchos=[7.6, 9.0], tam=9, titulo="Cierre de las adquisiciones")
    U.h2(doc, "16.4 Transferencia al hospital")
    U.tabla(doc, ["Se entrega", "Detalle"], [
        ["Código fuente", "Repositorio Git con migraciones SQL, README técnico y documentación."],
        ["Documentación", "Manual de usuario, manual técnico, ayuda integrada por puesto, video de capacitación e informe de gestión."],
        ["Credenciales y accesos", "Cuentas de administrador creadas desde la pantalla de cuentas; las claves del servidor se entregan por un canal seguro y se recomienda **rotarlas** al asumir el hospital la titularidad."],
        ["Capacitación", "Guion y video de demostración para enfermería, médico responsable y administrador."],
    ], anchos=[4.2, 12.4], tam=9, primera_negrita=True, titulo="Contenido de la transferencia")
    U.parrafo(doc, "**Pendientes para el hospital antes de producción:** aprobar las cuatro plantillas de mensajes; validar con el médico responsable los valores clínicos; completar «Dónde y cuándo donar»; "
                   "definir el costo recurrente; y realizar la revisión legal del consentimiento.", alineacion="justificado")
    U.h2(doc, "16.5 Lista de verificación del cierre administrativo")
    U.tabla(doc, ["Acción", "Responsable", "Estado"], [
        ["Verificar que todos los entregables estén aceptados", "PM", "En curso (acta de aceptación)"],
        ["Documentar las lecciones aprendidas", "PM y equipo", "Hecho (sección 16.2)"],
        ["Archivar los documentos del proyecto", "PM", "En curso"],
        ["Cerrar las adquisiciones", "PM", "En curso"],
        ["Liberar al equipo (plan de liberación)", "PM", f"Programado para el {f(D.FIN_PLAN)}"],
        ["Entregar el informe final a la docente", "PM", "Entregado con este informe"],
        ["Firmar el acta de cierre", "PM y sponsor", f"Programado para el {f(D.ACT['5.3']['fin'])}"],
    ], anchos=[8.6, 3.4, 4.6], tam=9, titulo="Cierre administrativo")

    U.h2(doc, "16.6 Acta de aceptación del producto")
    U.tabla(doc, ["Criterio de aceptación (capítulo 5)", "Cumple"], [
        ["Sistema desplegado con los 8 módulos operativos, accesible desde computadora y celular.", "☑"],
        ["Métricas ISO/IEC 25010 definidas; seguridad por filas en 13 de 13 tablas; 0 resultados críticos visibles.", "☑"],
        ["Documentación de gestión completa y actas firmadas (cierre pendiente de firma).", "☐ pendiente"],
        ["Piloto interno aprobado con cuentas de cada rol; manuales y ayuda entregados.", "☑"],
    ], anchos=[13.2, 3.4], alinear=["l", "c"], tam=9, titulo="Verificación de los criterios de aceptación")
    U.h2(doc, "16.7 Acta de cierre del proyecto")
    U.parrafo(doc, f"En Cajamarca, a los {D.FIN_PLAN.day} días del mes de octubre de 2026, el Project Manager y el sponsor dan por concluido el proyecto **HEMOCAX**, ejecutado entre el {f(D.INICIO)} y el {f(D.FIN_PLAN)}, "
                   f"con un costo final proyectado de {s(D.indicadores(D.S_CORTE)['eac1'])} frente a un presupuesto total aprobado de {s(D.PRESUPUESTO_TOTAL)}. "
                   "Los productos fueron entregados y se documentaron las lecciones aprendidas. El hospital queda como titular del sistema y de los datos.", alineacion="justificado")
    U.firmas(doc, [(D.EQUIPO["PM"]["nombre"], "Project Manager"), (D.DOCENTE, "Sponsor — Docente coordinadora"), ("Representante del Banco de Sangre HRDC", "Cliente (conformidad)")])
    U.salto_pagina(doc)


def construir(doc):
    adquisiciones(doc)
    cambios(doc)
    avance(doc)
    cierre(doc)
