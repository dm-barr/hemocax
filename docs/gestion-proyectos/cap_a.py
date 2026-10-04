# -*- coding: utf-8 -*-
"""Portada, resumen ejecutivo y Parte I: Charter, interesados y plan para la dirección del proyecto."""
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

import datos as D
import docx_utils as U
from fmt import f, fl, s, n, pct

FIG = "fig/"


def portada(doc):
    def centro(texto, tam, negrita=False, color=None, antes=0, despues=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(texto)
        r.font.size = Pt(tam)
        r.bold = negrita
        if color:
            r.font.color.rgb = color
        p.paragraph_format.space_before = Pt(antes)
        p.paragraph_format.space_after = Pt(despues)
        return p

    centro(D.UNIVERSIDAD.upper(), 16, True, U.AZUL, 10)
    centro(D.FACULTAD, 12)
    centro(D.ESCUELA, 12, despues=40)
    centro("INFORME DE GESTIÓN DEL PROYECTO", 13, True, RGBColor(0x7F, 0x8C, 0x8D), 20, 6)
    centro("HEMOCAX", 40, True, U.AZUL, 4, 6)
    centro("Plataforma digital para la fidelización y retención del donante voluntario de sangre", 15, True, None, 0, 4)
    centro("Hospital Regional Docente de Cajamarca — Servicio de Hemoterapia y Banco de Sangre", 12, False, None, 0, 40)
    centro("Documentación del proyecto según el PMBOK", 12, False, None, 0, 4)
    centro("Project Charter · Interesados · Requisitos y alcance · EDT · Cronograma · Costos y EVM · Calidad · Recursos humanos · Comunicaciones · Riesgos · Adquisiciones · Cierre", 10, False, RGBColor(0x55, 0x55, 0x55), 0, 40)
    centro("Presentado por", 11, True, None, 6, 6)
    for k in D.ORDEN_ROLES:
        e = D.EQUIPO[k]
        centro(f"{e['nombre']}  ({e['rol']})", 10.5, False, None, 0, 1)
    centro("Docente coordinadora", 11, True, None, 18, 4)
    centro(D.DOCENTE, 11.5)
    centro(f"Asignatura: {D.CURSO}  ·  Ciclo {D.CICLO}", 11, False, None, 14, 4)
    centro(f"Cajamarca, {D.FECHA_INFORME}", 11, False, None, 4, 0)
    U.salto_pagina(doc)


def control_versiones(doc):
    U.h1(doc, "Control de versiones")
    U.tabla(doc, ["Versión", "Hecha por", "Revisada por", "Aprobada por", "Fecha", "Motivo del cambio"], [
        ["1.0", "Diana M. Barrantes G. (PM)", "Ing. Ena Mirella Cacho Chávez", "Ing. Ena Mirella Cacho Chávez", "21/07/2026", "Versión inicial: Project Charter y registro de stakeholders."],
        ["2.0", "Diana M. Barrantes G. (PM)", "Equipo del proyecto", "Pendiente de la docente", f(D.CORTE), "Consolidación de la documentación de gestión con los datos de seguimiento al corte del 04/10/2026."],
    ], anchos=[1.4, 3.6, 3.2, 3.2, 2.0, 5.6], tam=8.5)
    U.parrafo(doc, "Los datos de seguimiento (avance, horas y costos reales) corresponden al corte del **04 de octubre de 2026**, fin de la semana 11. "
                   "La única actividad pendiente es la firma del acta de cierre (semana 12), con su fecha prevista.", tam=9.5)
    U.salto_pagina(doc)
    U.h1(doc, "Contenido")
    U.indice(doc)
    U.salto_pagina(doc)


def resumen_ejecutivo(doc):
    ult = D.indicadores(D.S_CORTE)
    U.h1(doc, "Resumen ejecutivo")
    U.parrafo(doc, "HEMOCAX es una plataforma web que permite al Banco de Sangre del Hospital Regional Docente de Cajamarca (HRDC) mantener una relación sostenida con el donante voluntario: "
                   "registra donantes y donaciones, calcula cuándo puede volver a donar, libera resultados no críticos de forma segura, envía correos institucionales con consentimiento y automatiza recordatorios, "
                   "agradecimientos y saludos. El donante entra con su DNI y ve en una sola pantalla si puede donar, su resultado y dónde acudir.", alineacion="justificado")
    U.parrafo(doc, "Este informe reúne la documentación de gestión del proyecto, elaborada según los procesos del PMBOK y organizada por áreas de conocimiento, y cierra con una lectura "
                   "desde los dominios de desempeño y principios del PMBOK 7.", alineacion="justificado")
    U.tabla(doc, ["Aspecto", "Resultado"], [
        ["Periodo del proyecto", f"{f(D.INICIO)} al {f(D.FIN_PLAN)} ({D.SEMANAS_PROY:.1f} semanas; corte de datos al {f(D.CORTE)})"],
        ["Esfuerzo", f"{D.HORAS_TOTALES} horas-persona planificadas (6 integrantes, ≈ {D.HORAS_TOTALES / 6 / D.SEMANAS_PROY:.0f} h por semana cada uno)"],
        ["Presupuesto base (BAC)", f"{s(D.BAC)}  = recursos humanos {s(D.COSTO_RRHH)} + gastos directos {s(D.GASTOS_TOTAL)}"],
        ["Reservas", f"Contingencia {s(D.RESERVA_CONTINGENCIA)} (suma del VME de los riesgos) · Gestión {s(D.RESERVA_GESTION)} (3 %)"],
        ["Presupuesto total", s(D.PRESUPUESTO_TOTAL)],
        ["Desempeño al corte (semana 11)", f"EV {s(ult['ev'])} · PV {s(ult['pv'])} · AC {s(ult['ac'])} → SPI {ult['spi']:.2f} · CPI {ult['cpi']:.2f}; costo final proyectado (EAC) {s(ult['eac1'])}"],
        ["Costo para el hospital", "S/ 0.00 por desarrollo. Costos recurrentes de operación: ver la sección 8.7."],
        ["Calidad", f"CoQ = {s(D.COQ_TOTAL)} ({pct(D.COQ_TOTAL / D.BAC)} del BAC); relación costo-beneficio {D.CB_RATIO:.2f}; {sum(n_ for _, n_ in D.DEFECTOS)} defectos registrados y analizados."],
        ["Riesgos", f"{len(D.RIESGOS)} riesgos identificados ({sum(1 for r in D.RIESGOS if r['tipo'] == 'Amenaza')} amenazas y {sum(1 for r in D.RIESGOS if r['tipo'] == 'Oportunidad')} oportunidades); "
                    f"{sum(1 for r in D.RIESGOS if r['pi'] >= 10 and r['tipo'] == 'Amenaza')} amenazas en nivel alto."],
        ["Interesados", f"{D.N_INTERESADOS} interesados identificados → {D.CANALES} canales potenciales de comunicación."],
    ], anchos=[4.2, 12.4], tam=9, primera_negrita=True)
    U.caja(doc, "El sobrecosto proyectado (≈ 5 %) es menor que la reserva de contingencia aprobada, por lo que el proyecto concluye dentro del presupuesto total. "
                "El retraso acumulado durante el desarrollo se recuperó antes del corte mediante horas adicionales de integración, que explican el CPI inferior a 1.",
           titulo="Lectura rápida")
    U.salto_pagina(doc)


def mapa_entregables(doc):
    U.h2(doc, "Mapa de los entregables del curso en este informe")
    U.tabla(doc, ["Entregable solicitado", "Dónde está"], [
        ["Project Charter", "Capítulo 1"],
        ["Registro de stakeholders", "Capítulo 2 (matriz de interés/influencia, cubo y plan de involucramiento)"],
        ["Documentación de requisitos", "Capítulo 4 (RF, RNF, calidad, reglas, trazabilidad)"],
        ["Definición del alcance", "Capítulo 5"],
        ["EDT", "Capítulo 6 (diagrama y diccionario)"],
        ["Cronograma", "Capítulo 7 (CPM, ruta crítica, Gantt, PERT)"],
        ["Estimación, presupuesto, curva S y EVM", "Capítulo 8"],
        ["CoQ, estándares ISO y herramientas de calidad", "Capítulo 9"],
        ["Organigrama, descripción de cargos y matriz RACI", "Capítulo 10"],
        ["Requisitos, plan y formatos de informe (comunicaciones)", "Capítulo 11 y capítulo 15 (informe de avance)"],
        ["Gestión de riesgos", "Capítulo 12"],
        ["Gestión de adquisiciones", "Capítulo 13 y anexo D (contratos modelo FFP y FPIF)"],
        ["Gestión de cambios, cierre y lecciones aprendidas", "Capítulos 14 y 16"],
        ["PMBOK 7: dominios, principios, beneficios y medición", "Capítulo 17"],
    ], anchos=[7.0, 9.6], tam=9, titulo="Correspondencia entre entregables y capítulos")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def charter(doc):
    ini, fin = D.INICIO, D.FIN_PLAN
    U.h1(doc, "PARTE I · INICIACIÓN E INTEGRACIÓN")
    U.h1(doc, "1. Project Charter (Acta de constitución del proyecto)")
    U.h2(doc, "1.1 Ficha del proyecto")
    U.tabla(doc, ["Campo", "Descripción"], [
        ["Denominación", D.TITULO],
        ["Cliente / entidad receptora", D.CLIENTE],
        ["Entidad ejecutora", f"{D.ESCUELA} — {D.UNIVERSIDAD} (proyección universitaria)"],
        ["Sponsor del proyecto", f"{D.DOCENTE} — Docente coordinadora, {D.CURSO}"],
        ["Director del proyecto (PM)", D.EQUIPO["PM"]["nombre"]],
        ["Contraparte funcional", "Dra. Marimar (encargada del Banco de Sangre), Jefatura del servicio y médico responsable"],
        ["Contraparte técnica", "Oficina de Estadística e Informática (OEI) del HRDC"],
        ["Fecha de inicio / cierre", f"{f(ini)} / {f(fin)} ({(fin - ini).days} días calendario, {D.SEMANAS_PROY:.1f} semanas)"],
        ["Modalidad", "Sin costo de desarrollo para el hospital (proyección universitaria)"],
        ["Ubicación", "Cajamarca, Perú"],
    ], anchos=[4.2, 12.4], tam=9, primera_negrita=True, titulo="Datos generales del proyecto")

    U.h2(doc, "1.2 Descripción del proyecto")
    U.parrafo(doc, "HEMOCAX es una plataforma web, con base de datos propia, que fortalece la captación, fidelización y retención del donante voluntario de sangre del HRDC. "
                   "Es una herramienta **complementaria**: no reemplaza ni modifica el sistema informático que el Banco de Sangre usa actualmente, no interviene en procesos asistenciales y no trabaja con datos de pacientes receptores.",
              alineacion="justificado")
    U.parrafo(doc, "El sistema tiene dos caras: un **panel del personal** (enfermería, médico responsable y administración) y un **portal del donante**, diseñado para ser muy simple en celular y en conexiones lentas, "
                   "porque una parte importante de los donantes proviene de zonas rurales.", alineacion="justificado")
    U.h2(doc, "1.3 Justificación y necesidad del negocio")
    U.parrafo(doc, "El levantamiento realizado con la Dra. Marimar, encargada del Banco de Sangre, y con la Jefatura del servicio identificó los siguientes problemas:")
    U.tabla(doc, ["Problema observado", "Qué hace HEMOCAX"], [
        ["El donante dona una sola vez y no vuelve; nadie le recuerda cuándo está apto otra vez.", "Recordatorio automático al cumplir el intervalo; el portal le muestra su próxima fecha."],
        ["No hay un canal institucional de contacto (se usa el celular personal del médico de turno).", "Correos institucionales enviados desde el sistema, con registro de cada envío."],
        ["Reserva insuficiente de grupos poco frecuentes (por ejemplo O negativo).", "Convocatoria dirigida por grupo sanguíneo y aptitud, con conteo por grupo."],
        ["El resultado tarda entre 48 horas y unos 5 días en llegar al donante.", "Entrega digital del resultado no crítico, con alerta cuando se acerca la meta de 48 horas."],
        ["No hay agradecimiento ni seguimiento posterior a la donación.", "Mensajes de fidelización: agradecimiento, cumpleaños y reconocimiento anual."],
    ], anchos=[8.3, 8.3], tam=9, titulo="Problemas identificados y respuesta del proyecto")
    U.caja(doc, "«Las emergencias no deberían estar esperando a las donaciones, sino que las donaciones deben esperar a las emergencias mediante un stock que las respalde.» — Principio operativo señalado por el servicio.", color="FEF9E7")
    U.tabla(doc, ["Indicador financiero", "Valor"], [
        ["Flujo de ingresos / egresos", "No aplica (proyecto social sin fines de lucro)"],
        ["VAN / TIR / relación beneficio-costo", "No aplica. El valor se mide en indicadores sociales y operativos (sección 17.4)."],
        ["Costo del desarrollo para el hospital", "S/ 0.00"],
    ], anchos=[6.0, 10.6], tam=9, titulo="Justificación cuantitativa")

    U.h2(doc, "1.4 Objetivos del proyecto")
    U.parrafo(doc, "**Objetivo general.** Implementar una plataforma digital que fortalezca la captación, fidelización y retención del donante voluntario de sangre del HRDC y agilice la comunicación del Banco de Sangre con sus donantes, sin modificar los sistemas de información en uso.")
    U.tabla(doc, ["Código", "Objetivo específico"], [
        ["OE-01", "Constituir un padrón digital propio de donantes con grupo sanguíneo, canal de contacto y consentimiento expreso."],
        ["OE-02", "Automatizar el recordatorio al donante cuando cumple el intervalo para volver a donar."],
        ["OE-03", "Implementar mensajes de fidelización: agradecimiento, cumpleaños y reconocimiento al donante frecuente."],
        ["OE-04", "Difundir de manera oportuna las campañas e información institucional del Banco de Sangre."],
        ["OE-05", "Habilitar la entrega digital de resultados no críticos en un plazo objetivo de 48 horas, previa liberación del médico."],
        ["OE-06", "Habilitar la convocatoria dirigida por grupo sanguíneo, con prioridad en los grupos de menor disponibilidad."],
        ["OE-07", "Garantizar el tratamiento seguro y confidencial de los datos conforme a la Ley N.° 29733."],
    ], anchos=[2.0, 14.6], tam=9, titulo="Objetivos específicos")
    U.tabla(doc, ["Restricción", "Objetivo", "Criterio de éxito"], [
        ["Alcance", "Construir 8 módulos funcionales: padrón, donaciones y aptitud, resultados, consentimiento y derechos del titular, comunicación por correo, automatizaciones, portal del donante y panel del personal.",
         "Los 17 requisitos funcionales del capítulo 4 implementados y verificados en el piloto interno."],
        ["Tiempo", f"Completar el proyecto entre el {f(D.INICIO)} y el {f(D.FIN_PLAN)}.", f"Acta de cierre firmada el {f(D.FIN_PLAN)}; hitos cumplidos según el cronograma."],
        ["Costo", f"Ejecutar el proyecto con el presupuesto base de {s(D.BAC)} y las reservas aprobadas; sin costo de desarrollo para el hospital.", f"Costo final proyectado menor que {s(D.PRESUPUESTO_TOTAL)}; costos de operación en planes gratuitos."],
        ["Calidad", "Cumplir las métricas de calidad ISO/IEC 25010 definidas en el plan de calidad.", "0 resultados críticos visibles para el donante; 100 % de las tablas con seguridad por filas; flujos críticos aprobados en el piloto interno."],
    ], anchos=[2.4, 8.0, 6.2], tam=8.5, titulo="Objetivos y criterios de éxito por restricción")

    U.h2(doc, "1.5 Productos y entregables del proyecto")
    U.tabla(doc, ["Fase", "Entregables"], [
        ["1. Inicio", "Project Charter · Registro de stakeholders · Acta de kick-off · Acta de levantamiento con el Banco de Sangre"],
        ["2. Planificación y diseño", "Documento de requisitos y definición del alcance · EDT · Cronograma · Presupuesto y línea base de costos · Planes de calidad, riesgos, RR.HH., comunicaciones y adquisiciones · Prototipos UX validados · Arquitectura y modelo de datos · Propuesta al HRDC"],
        ["3. Desarrollo", "Base de datos con seguridad · Padrón de donantes · Donaciones y reglas · Resultados · Consentimiento y derechos del titular · Correo y campañas · Automatizaciones · Portal del donante · Panel del personal · Sistema en producción"],
        ["4. Pruebas y capacitación", "Plan de pruebas · Informes de pruebas funcionales y de seguridad · Informe del piloto interno · Manuales y ayuda integrada · Video y guion de capacitación"],
        ["5. Cierre", "Informe final con lecciones aprendidas · Repositorio y documentación técnica · Acta de cierre y de aceptación"],
    ], anchos=[3.6, 13.0], tam=9, primera_negrita=True, titulo="Entregables por fase")

    U.h2(doc, "1.6 Requisitos de alto nivel")
    U.viñetas(doc, [
        "**Funcionales:** registro y búsqueda de donantes; cálculo de aptitud; registro de donaciones con máximo anual; resultados con liberación médica y marca de crítico; portal del donante; consentimiento versionado; correo y campañas; automatizaciones; reportes; cuentas por puesto; bitácora de auditoría; derechos del titular.",
        "**No funcionales:** uso fluido en celular de gama baja y conexión lenta; disponibilidad ≥ 99 % mensual; seguridad de datos de salud con permisos por rol; costo de operación cero en el piloto.",
        "**De calidad:** métricas ISO/IEC 25010 (sección 9.3) y pruebas por rol antes del despliegue.",
        "**Legales:** Ley N.° 29733 de Protección de Datos Personales (D.S. N.° 016-2024-JUS); los resultados críticos no se comunican por canal digital.",
    ])
    U.parrafo(doc, "El detalle completo se encuentra en el capítulo 4.", tam=9.5)

    U.h2(doc, "1.7 Cronograma de hitos")
    A = D.ACT
    hitos = [
        ("H1", "Project Charter aprobado", A["1.1"]["fin"]),
        ("H2", "Levantamiento inicial con el Banco de Sangre", A["1.4"]["fin"]),
        ("H3", "Requisitos y alcance aprobados", A["2.2"]["fin"]),
        ("H4", "EDT, cronograma y línea base de costos aprobados", A["2.5"]["fin"]),
        ("H5", "Arquitectura y modelo de datos aprobados", A["2.7"]["fin"]),
        ("H6", "Base de datos con seguridad aplicada", A["3.1"]["fin"]),
        ("H7", "Núcleo operativo: padrón, donaciones y resultados", A["3.5"]["fin"]),
        ("H8", "Comunicación, portal del donante y panel del personal completos", A["3.10"]["fin"]),
        ("H9", "Sistema desplegado en producción", A["3.11"]["fin"]),
        ("H10", "Pruebas y piloto interno concluidos", A["4.4"]["fin"]),
        ("H11", "Informe final y documentación entregados", A["5.2"]["fin"]),
        ("H12", "Acta de cierre y de aceptación firmada", A["5.3"]["fin"]),
    ]
    U.tabla(doc, ["Hito", "Evento significativo", "Fecha programada"], [[h, e, f(d)] for h, e, d in hitos],
            anchos=[1.6, 11.0, 4.0], alinear=["c", "l", "c"], tam=9, titulo="Hitos del proyecto (línea base)")

    U.h2(doc, "1.8 Presupuesto preliminar")
    U.tabla(doc, ["Concepto", "Monto (S/)"], [
        [f"Recursos humanos: {D.HORAS_TOTALES} horas-persona × S/ {D.TARIFA:.2f}", f"{D.COSTO_RRHH:,.2f}"],
        ["Gastos directos (desembolso real en efectivo)", f"{D.GASTOS_TOTAL:,.2f}"],
        ["**Presupuesto base — BAC**", f"**{D.BAC:,.2f}**"],
        ["Reserva de contingencia (suma del VME de los riesgos, sección 12.5)", f"{D.RESERVA_CONTINGENCIA:,.2f}"],
        ["Reserva de gestión (3 % del costo base)", f"{D.RESERVA_GESTION:,.2f}"],
        ["**Presupuesto total del proyecto**", f"**{D.PRESUPUESTO_TOTAL:,.2f}**"],
    ], anchos=[12.6, 4.0], alinear=["l", "r"], tam=9, titulo="Resumen del presupuesto (detalle en el capítulo 8)")
    U.parrafo(doc, "No hay inversión en infraestructura: Vercel, Supabase, Render, GitHub y Figma operan en planes gratuitos o educativos, y el correo usa una cuenta con contraseña de aplicación.", tam=9.5)

    U.h2(doc, "1.9 Interesados clave")
    U.parrafo(doc, "Se identificaron 15 interesados (capítulo 2). Los de mayor poder e interés son: la docente coordinadora (sponsor), el equipo del proyecto, la Dra. Marimar y la Jefatura del servicio, "
                   "la Dirección General y la OEI del HRDC, y los donantes, usuarios finales del portal.")

    U.h2(doc, "1.10 Amenazas y oportunidades de alto nivel")
    U.tabla(doc, ["Principales amenazas", "Principales oportunidades"], [
        ["Indisponibilidad de integrantes por carga académica concurrente.", "El HRDC o la DIRESA adoptan el sistema más allá de la etapa académica."],
        ["Cambios de requisitos tras validar los prototipos.", "Planes educativos gratuitos reducen el costo recurrente."],
        ["Baja disponibilidad de la Jefatura para validar valores clínicos y textos.", "El proyecto puede convertirse en tesis o publicación académica."],
        ["Límites de los planes gratuitos de infraestructura.", "Otros bancos de sangre u organizaciones pueden replicar la plataforma."],
        ["Exposición de datos de salud por permisos mal configurados.", ""],
    ], anchos=[8.3, 8.3], tam=9, titulo="Resumen de riesgos de alto nivel (registro completo en el capítulo 12)")

    U.h2(doc, "1.11 Supuestos y restricciones principales")
    U.viñetas(doc, [
        "El Banco de Sangre dispone de tiempo para sesiones de levantamiento y validación (≈ 6 visitas durante el proyecto).",
        "Los valores clínicos (intervalo de 90 días, máximos anuales de 4 y 3 donaciones) son **provisionales** hasta su validación por el médico responsable.",
        "El proyecto no tiene presupuesto externo ni puede contratar desarrollo; usa planes gratuitos de las herramientas.",
        "El plazo máximo corresponde al calendario académico del curso y no puede extenderse.",
        "El sistema no se integra con el sistema actual del hospital ni almacena información clínica.",
    ])

    U.h2(doc, "1.12 Designación y autoridad del Project Manager")
    U.parrafo(doc, f"Se designa a **{D.EQUIPO['PM']['nombre']}** como Project Manager. Tiene autoridad para: asignar tareas y recursos del equipo; aprobar cambios de bajo impacto "
                   "(menos de 1 día y S/ 0.00); representar al proyecto ante el sponsor y los interesados; decidir sobre decisiones técnicas y de diseño; y escalar al sponsor los riesgos críticos y los cambios de impacto alto "
                   "(más de 3 días o más de S/ 50.00).", alineacion="justificado")

    U.h2(doc, "1.13 Criterios de aprobación del proyecto")
    U.viñetas(doc, [
        "El sistema desplegado funciona con los 8 módulos y el piloto interno aprobó los flujos críticos de cada rol.",
        "Las pruebas de seguridad confirman que el donante no puede leer resultados críticos, plantillas ni bitácora.",
        "La documentación de gestión, los manuales y el repositorio están entregados.",
        "El acta de cierre es firmada por el PM y el sponsor.",
    ])
    U.firmas(doc, [(D.EQUIPO["PM"]["nombre"], "Project Manager"), (D.DOCENTE, "Sponsor — Docente coordinadora")])
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def interesados(doc):
    U.h1(doc, "2. Gestión de los interesados")
    U.h2(doc, "2.1 Registro de stakeholders")
    U.parrafo(doc, f"Se identificaron **{D.N_INTERESADOS} interesados**. La tabla presenta su identificación, evaluación (interés e influencia de 1 a 5) y clasificación.")
    U.seccion(doc, horizontal=True)
    filas = [[sid, f"**{nom}**\n{org}", rol, exp, str(i), str(infl), act, fase, est] for (sid, nom, org, rol, exp, i, infl, act, fase, est) in D.INTERESADOS]
    U.tabla(doc, ["ID", "Nombre y organización", "Rol en el proyecto", "Expectativas y requerimientos primordiales", "Int.", "Infl.", "Actitud", "Fase de mayor interés", "Estrategia"],
            filas, anchos=[1.0, 5.4, 3.8, 7.0, 1.0, 1.0, 1.7, 3.0, 2.8], alinear=["c", "l", "l", "l", "c", "c", "c", "l", "l"], tam=8,
            titulo="Registro de stakeholders del proyecto HEMOCAX")
    U.seccion(doc, horizontal=False)

    U.h2(doc, "2.2 Matriz de interés vs. influencia")
    U.figura(doc, FIG + "matriz_interes.png", 13.5, "Matriz de interés vs. influencia (los códigos S01–S15 corresponden al registro de stakeholders)")
    U.parrafo(doc, "**Interpretación.** El equipo, la docente, la Dra. Marimar y la Jefatura están en el cuadrante «gestionar de cerca»: se les comunica con mayor frecuencia y participan en decisiones. "
                   "La Dirección General, la OEI y la DIRESA tienen mucha influencia y menos interés cotidiano: se les «mantiene satisfechos» con informes puntuales. El personal de enfermería y los donantes tienen alto interés y poca "
                   "influencia: se les «mantiene informados» y se les consulta en las pruebas.", alineacion="justificado")

    U.h2(doc, "2.3 Cubo de stakeholders y modelo de prominencia")
    U.parrafo(doc, "El cubo de stakeholders agrega la actitud a la matriz poder–interés. El modelo de prominencia (*salience*) clasifica a los interesados según su **poder**, **urgencia** y **legitimidad**.")
    U.tabla(doc, ["ID", "Interesado", "Poder", "Urgencia", "Legitimidad", "Clase", "Actitud (cubo)"], [
        ["S01", "Docente coordinadora (sponsor)", "Alto", "Alta", "Alta", "Definitivo", "Patrocinador activo influyente"],
        ["S08", "Dra. Marimar (Banco de Sangre)", "Alto", "Alta", "Alta", "Definitivo", "Patrocinador activo influyente"],
        ["S09", "Jefatura y médico responsable", "Alto", "Media", "Alta", "Dominante", "Neutral influyente (validador)"],
        ["S12", "Dirección General del HRDC", "Alto", "Baja", "Alta", "Dominante", "Patrocinador pasivo influyente"],
        ["S11", "OEI del HRDC", "Medio", "Media", "Alta", "Dominante", "Neutral influyente"],
        ["S13", "Donantes voluntarios", "Bajo", "Alta", "Alta", "Dependiente", "Patrocinador activo"],
        ["S10", "Personal de enfermería y apoyo", "Bajo", "Alta", "Alta", "Dependiente", "Patrocinador activo"],
        ["S15", "DIRESA / MINSA", "Alto", "Baja", "Media", "Latente a dominante", "Neutral influyente"],
        ["S14", "Proveedores en la nube", "Medio", "Baja", "Baja", "Latente", "Neutral insignificante"],
    ], anchos=[1.1, 5.0, 1.7, 1.8, 2.0, 2.4, 4.0], alinear=["c", "l", "c", "c", "c", "c", "l"], tam=8.5, titulo="Prominencia y cubo de stakeholders (interesados principales)")

    U.h2(doc, "2.4 Plan de involucramiento")
    U.tabla(doc, ["Interesado", "Nivel actual", "Nivel deseado", "Estrategia concreta", "Responsable"], [
        ["Dra. Marimar y personal del Banco de Sangre", "Apoya", "Líder", "Sesiones de levantamiento y de validación de prototipos; versión de prueba para que tome decisiones sobre textos y reglas.", "PM y Analista"],
        ["Jefatura y médico responsable", "Neutral", "Apoya", "Validar de forma explícita los valores clínicos, el consentimiento y los textos automáticos; mostrar la protección de resultados críticos.", "PM"],
        ["Dirección General", "Neutral", "Apoya", "Propuesta formal con cero costo de desarrollo y definición del costo recurrente; informe de resultados al cierre.", "PM y Sponsor"],
        ["OEI del HRDC", "Neutral", "Apoya", "Entregar documentación técnica y de seguridad; no intervenir sus sistemas; reunión de transferencia.", "Líder Técnico"],
        ["Donantes", "No consciente del proyecto", "Apoya", "Portal de una pantalla, lenguaje claro, consentimiento libre y revocable; contraseñas fáciles de dictar.", "Analista y Frontend"],
        ["Docente coordinadora", "Apoya", "Líder", "Informe semanal, demos por hito y control de cambios.", "PM"],
        ["DIRESA / MINSA", "No consciente", "Neutral informado", "Presentar resultados cuando el hospital lo autorice; no se contacta antes.", "Sponsor"],
    ], anchos=[3.6, 2.2, 2.2, 6.6, 2.0], tam=8.5, titulo="Plan de involucramiento (nivel actual vs. deseado)")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def plan_direccion(doc):
    U.h1(doc, "3. Plan para la dirección del proyecto")
    U.h2(doc, "3.1 Propósito")
    U.parrafo(doc, "Este plan integra las líneas base y los planes subsidiarios, define cómo se ejecuta, se vigila y se controla el trabajo, y fija el enfoque de desarrollo del proyecto.", alineacion="justificado")
    U.h2(doc, "3.2 Enfoque de desarrollo y ciclo de vida (adaptación del PMBOK 7)")
    U.parrafo(doc, "Se adoptó un enfoque **híbrido**: planificación y gobierno predictivos (alcance, EDT, cronograma, presupuesto y riesgos acordados al inicio) y construcción **iterativa e incremental** "
                   "con ciclos semanales de diseñar, construir, probar y validar con el Banco de Sangre.", alineacion="justificado")
    U.figura(doc, FIG + "ciclo_vida.png", 16.0, "Ciclo de vida híbrido del proyecto HEMOCAX")
    U.tabla(doc, ["Factor de adaptación (*tailoring*)", "Situación del proyecto", "Decisión"], [
        ["Incertidumbre de requisitos", "Media: el Banco de Sangre aclara reglas y textos conforme ve prototipos.", "Entregas semanales y validación frecuente."],
        ["Riesgo regulatorio y de datos de salud", "Alto: Ley N.° 29733 y resultados críticos.", "Diseño de seguridad y consentimiento antes de construir (enfoque predictivo)."],
        ["Tamaño y distribución del equipo", "6 estudiantes con otros cursos, trabajo parcial.", "Roles claros, tablero de tareas y reunión semanal de 45 min."],
        ["Costo y plazo", "Presupuesto fijo y plazo académico cerrado.", "Línea base de costos y cronograma con control EVM."],
        ["Cliente disponible", "Disponibilidad limitada del personal de salud.", "Sesiones calendarizadas y valores clínicos parametrizables."],
    ], anchos=[4.2, 6.6, 5.8], tam=8.5, titulo="Factores de adaptación del ciclo de vida")
    U.h2(doc, "3.3 Líneas base y planes subsidiarios")
    U.tabla(doc, ["Componente", "Contenido", "Capítulo"], [
        ["Línea base del alcance", "Definición del alcance, EDT y diccionario de la EDT", "4, 5 y 6"],
        ["Línea base del cronograma", "Lista de actividades, ruta crítica, hitos y Gantt", "7"],
        ["Línea base de costos", "Estimación, presupuesto con reservas, curva S", "8"],
        ["Plan de gestión de la calidad", "Métricas ISO/IEC 25010, CoQ, herramientas de calidad", "9"],
        ["Plan de gestión de recursos humanos", "OBS, cargos, RACI, plan de personal", "10"],
        ["Plan de gestión de las comunicaciones", "Matriz, plan y formatos de informe", "11"],
        ["Plan de gestión de riesgos", "Registro, matriz P×I, VME y respuestas", "12"],
        ["Plan de gestión de adquisiciones", "Hacer o comprar, selección, SOW, contratos", "13"],
        ["Plan de gestión de cambios", "Proceso de control y registro de solicitudes", "14"],
        ["Plan de gestión de beneficios", "Beneficios, indicadores y medición", "17"],
    ], anchos=[5.2, 9.0, 2.4], alinear=["l", "l", "c"], tam=9, titulo="Componentes del plan para la dirección del proyecto")
    U.h2(doc, "3.4 Gobierno y toma de decisiones")
    U.tabla(doc, ["Decisión", "Quién decide", "Plazo"], [
        ["Cambio de impacto bajo (< 1 día y S/ 0.00)", "Project Manager", "24 h"],
        ["Cambio de impacto medio (1 a 3 días, menos de S/ 50.00)", "PM con el equipo", "24 h"],
        ["Cambio de impacto alto (> 3 días o > S/ 50.00)", "Sponsor", "48 h"],
        ["Uso de la reserva de contingencia", "PM, con informe al sponsor", "Inmediato"],
        ["Uso de la reserva de gestión", "Sponsor", "48 h"],
        ["Valores clínicos y textos que ve el donante", "Jefatura y médico responsable del HRDC", "Según calendario de validación"],
        ["Aprobación de mensajes automáticos", "Jefatura del Banco de Sangre", "Antes de producción"],
    ], anchos=[8.4, 5.2, 3.0], tam=9, titulo="Matriz de decisiones")
    U.h2(doc, "3.5 Seguimiento y control")
    U.viñetas(doc, [
        "**Semanal:** reunión de equipo (lunes 8:00 a. m., 45 min) y reporte al sponsor (viernes 5:00 p. m.).",
        "**Por hito:** demostración de avance y aprobación formal para continuar.",
        "**Indicadores:** EVM (PV, EV, AC, SPI, CPI), riesgos activos, defectos abiertos, solicitudes de cambio.",
        "**Umbrales:** si SPI o CPI < 0.90 se activa una acción correctiva; si el riesgo tiene exposición ≥ 15 se alerta al sponsor en menos de 2 horas.",
        "**Herramientas:** tablero de tareas en GitHub Projects, repositorio Git, carpeta compartida de actas y hojas de cálculo del EVM.",
    ])
    U.h2(doc, "3.6 Criterios de cierre")
    U.parrafo(doc, "El proyecto se cierra cuando se cumplen los criterios de aprobación del Project Charter (sección 1.13), se entregan los productos, se documentan las lecciones aprendidas y se firma el acta de cierre y de aceptación (capítulo 16).")
    U.salto_pagina(doc)
