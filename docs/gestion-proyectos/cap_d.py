# -*- coding: utf-8 -*-
"""Parte II (3): recursos humanos, comunicaciones y riesgos."""
import datos as D
import docx_utils as U
from fmt import f, s, n, pct

FIG = "fig/"

CORTO = {
    "R01": "Indisponibilidad de integrantes por carga académica", "R02": "Cambios de requisitos tras validar prototipos",
    "R03": "Poca disponibilidad de la Jefatura para validar", "R04": "Límites de los planes gratuitos de infraestructura",
    "R05": "Bloqueo de correo (SMTP) en el alojamiento", "R06": "Exposición de datos de salud por permisos mal configurados",
    "R07": "Resultado crítico visible para el donante", "R08": "Baja adopción del donante rural",
    "R09": "Valores clínicos provisionales erróneos",
}

# ------------------------------------------------------------------------------------------------
# RACI: columnas PM, LT, AF, FE, INT, QA, SPO (sponsor), CLI (cliente HRDC)
COLS = ["PM", "LT", "AF", "FE", "INT", "QA", "SPO", "CLI"]
RACI = [
    ("1. Project Charter",                           dict(PM="R", LT="I", AF="C", FE="I", INT="I", QA="I", SPO="A", CLI="C")),
    ("2. Registro y estrategia de stakeholders",     dict(PM="A", LT="I", AF="R", FE="I", INT="I", QA="I", SPO="C", CLI="C")),
    ("3. Documentación de requisitos y alcance",     dict(PM="C", LT="C", AF="R", FE="I", INT="I", QA="C", SPO="A", CLI="C")),
    ("4. EDT y cronograma",                          dict(PM="R", LT="C", AF="C", FE="I", INT="I", QA="I", SPO="A", CLI="I")),
    ("5. Presupuesto, curva S y EVM",                dict(PM="R", LT="C", AF="I", FE="I", INT="I", QA="I", SPO="A", CLI="I")),
    ("6. Plan de calidad y métricas ISO 25010",      dict(PM="A", LT="C", AF="C", FE="I", INT="I", QA="R", SPO="I", CLI="I")),
    ("7. Plan de riesgos y registro de riesgos",     dict(PM="A/R", LT="C", AF="C", FE="C", INT="C", QA="C", SPO="I", CLI="I")),
    ("8. Plan de comunicaciones",                    dict(PM="A/R", LT="I", AF="C", FE="I", INT="I", QA="I", SPO="C", CLI="C")),
    ("9. Plan de adquisiciones",                     dict(PM="A", LT="C", AF="I", FE="I", INT="R", QA="I", SPO="C", CLI="I")),
    ("10. Prototipos UX y validación",               dict(PM="I", LT="I", AF="A/R", FE="C", INT="I", QA="I", SPO="I", CLI="C")),
    ("11. Arquitectura y modelo de datos",           dict(PM="C", LT="A/R", AF="C", FE="C", INT="C", QA="C", SPO="I", CLI="I")),
    ("12. Base de datos y seguridad (RLS)",          dict(PM="I", LT="A/R", AF="I", FE="C", INT="C", QA="C", SPO="I", CLI="I")),
    ("13. Padrón, donaciones y aptitud (módulos 1-2)", dict(PM="I", LT="A", AF="C", FE="R", INT="I", QA="C", SPO="I", CLI="C")),
    ("14. Resultados, consentimiento y ARCO",        dict(PM="C", LT="A/R", AF="C", FE="C", INT="I", QA="C", SPO="I", CLI="C")),
    ("15. Correo, campañas y automatizaciones",      dict(PM="I", LT="A", AF="C", FE="I", INT="R", QA="C", SPO="I", CLI="C")),
    ("16. Portal del donante",                       dict(PM="C", LT="A", AF="C", FE="R", INT="I", QA="C", SPO="I", CLI="C")),
    ("17. Panel del personal",                       dict(PM="I", LT="A", AF="C", FE="R", INT="I", QA="C", SPO="I", CLI="C")),
    ("18. Despliegue en producción",                 dict(PM="I", LT="A", AF="I", FE="I", INT="R", QA="C", SPO="I", CLI="I")),
    ("19. Plan de pruebas y pruebas funcionales",    dict(PM="A", LT="C", AF="C", FE="C", INT="C", QA="R", SPO="I", CLI="I")),
    ("20. Pruebas de seguridad por rol",             dict(PM="I", LT="A", AF="I", FE="I", INT="C", QA="R", SPO="I", CLI="I")),
    ("21. Piloto interno",                           dict(PM="A", LT="C", AF="R", FE="C", INT="C", QA="C", SPO="I", CLI="C")),
    ("22. Manuales y ayuda integrada",               dict(PM="A", LT="C", AF="R", FE="C", INT="I", QA="C", SPO="I", CLI="C")),
    ("23. Video y guion de capacitación",            dict(PM="A", LT="I", AF="R", FE="C", INT="C", QA="I", SPO="I", CLI="C")),
    ("24. Informe de avance semanal",                dict(PM="A/R", LT="C", AF="C", FE="I", INT="I", QA="I", SPO="I", CLI="I")),
    ("25. Informe final y lecciones aprendidas",     dict(PM="R", LT="C", AF="C", FE="C", INT="C", QA="C", SPO="A", CLI="I")),
    ("26. Acta de cierre y de aceptación",           dict(PM="R", LT="C", AF="C", FE="I", INT="I", QA="I", SPO="A", CLI="C")),
]


def validar_raci():
    for nombre, fila in RACI:
        a = sum(1 for v in fila.values() if "A" in v)
        r = sum(1 for v in fila.values() if "R" in v)
        assert a == 1, (nombre, "A", a)
        assert r == 1, (nombre, "R", r)


validar_raci()

CARGOS = [
    ("PM", "Project Manager (Director del Proyecto)",
     ["Elaborar y mantener el Project Charter, la EDT, el cronograma y el presupuesto.", "Dirigir las reuniones semanales y reportar el avance al sponsor.",
      "Gestionar riesgos, cambios y comunicaciones.", "Coordinar con el Banco de Sangre y validar los entregables antes de entregarlos."],
     "Asignar tareas y recursos; aprobar cambios de bajo impacto; escalar riesgos críticos al sponsor.",
     "Estudiante de Ingeniería de Sistemas con formación en gestión de proyectos (PMBOK).", "Participación previa en proyectos de software o académicos integradores.",
     "Liderazgo, comunicación efectiva, negociación, gestión del tiempo.", "≈ 17 h/semana", "Reporta a la docente coordinadora (sponsor)."),
    ("LT", "Líder Técnico y Desarrollador de base de datos",
     ["Diseñar la arquitectura y el modelo de datos con seguridad por filas.", "Revisar el código de los demás desarrolladores y asegurar estándares.",
      "Configurar los despliegues y las migraciones.", "Resolver los problemas técnicos de mayor complejidad."],
     "Decidir sobre decisiones técnicas y de arquitectura; aceptar o rechazar código en revisión.",
     "Ingeniería de Sistemas, con base sólida en SQL y desarrollo web.", "Experiencia en PostgreSQL, API REST y control de versiones.",
     "Resolución de problemas, trabajo en equipo, comunicación técnica.", "≈ 16 h/semana", "Reporta al Project Manager."),
    ("AF", "Analista Funcional y UX",
     ["Levantar, documentar y validar los requisitos con el Banco de Sangre.", "Diseñar los prototipos y flujos de usuario.",
      "Redactar los manuales de usuario y la ayuda integrada.", "Coordinar el piloto interno y recoger observaciones."],
     "Proponer y priorizar requisitos; validar que cada módulo cumpla los criterios de aceptación.",
     "Ingeniería de Sistemas con conocimiento de análisis de requisitos y UX.", "Elaboración de casos de uso, prototipado en Figma y entrevistas a usuarios.",
     "Empatía, escucha, comunicación con personal de salud, redacción clara.", "≈ 15 h/semana", "Reporta al Project Manager."),
    ("FE", "Desarrolladora Frontend",
     ["Construir el portal del donante y el panel del personal.", "Implementar la importación y los formularios con validación.",
      "Asegurar que la interfaz funcione en celulares de gama baja.", "Corregir los defectos de interfaz detectados en pruebas."],
     "Decidir sobre detalles de implementación de la interfaz dentro de los criterios del Analista.",
     "Ingeniería de Sistemas con experiencia en desarrollo web.", "React, TypeScript y diseño responsive.",
     "Atención al detalle, creatividad, trabajo en equipo.", "≈ 14 h/semana", "Reporta al Líder Técnico."),
    ("INT", "Desarrollador de Integraciones y Automatizaciones",
     ["Implementar el envío de correo, las campañas y las plantillas.", "Programar las automatizaciones diarias y el reloj de recordatorios.",
      "Desplegar y monitorear el sistema en producción.", "Documentar las variables de entorno y los límites de los servicios."],
     "Decidir sobre configuración de servicios externos dentro de los límites del plan gratuito.",
     "Ingeniería de Sistemas con conocimiento de servicios en la nube.", "Servicios web, tareas programadas y correo SMTP.",
     "Autonomía, resolución de problemas, documentación.", "≈ 13 h/semana", "Reporta al Líder Técnico."),
    ("QA", "Especialista QA y Seguridad de datos",
     ["Elaborar el plan de pruebas y ejecutar las pruebas funcionales y de seguridad.", "Registrar y dar seguimiento a los defectos.",
      "Verificar los permisos de cada rol y la protección de resultados críticos.", "Medir las métricas de calidad."],
     "Detener un despliegue si no se cumplen los criterios de calidad.",
     "Ingeniería de Sistemas con conocimiento de pruebas y seguridad.", "Pruebas manuales, bases de datos y principios de seguridad web.",
     "Rigor, objetividad, comunicación de hallazgos sin culpar.", "≈ 14 h/semana", "Reporta al Project Manager."),
    ("CLI", "Usuaria clave del Banco de Sangre (HRDC)",
     ["Aportar los requisitos funcionales y validar prototipos.", "Validar los valores clínicos, el consentimiento y los textos.", "Participar en el piloto y en la capacitación."],
     "Aprobar o rechazar los textos y reglas que se aplican a los donantes.", "Personal de salud del Banco de Sangre.", "Conocimiento del proceso de donación y de la atención al donante.",
     "Comunicación, criterio clínico.", "≈ 20 % durante las sesiones de validación", "Reporta a la Jefatura del Banco de Sangre."),
]


def rrhh(doc):
    U.h1(doc, "10. Gestión de los recursos humanos")
    U.h2(doc, "10.1 Plan de gestión de recursos humanos")
    U.tabla(doc, ["Proceso", "Salida", "En HEMOCAX"], [
        ["Planificar los recursos humanos", "Plan de RR.HH. (OBS, RACI, plan de personal)", "Este capítulo."],
        ["Adquirir el equipo", "Asignaciones y calendario de recursos", "Equipo de seis estudiantes ya conformado; herramientas incorporadas en la semana 1."],
        ["Desarrollar el equipo", "Evaluaciones y mejoras de competencias", "Plan de capacitación, reunión semanal y retrospectivas por fase."],
        ["Dirigir el equipo", "Solicitudes de cambio y resolución de conflictos", "El PM hace seguimiento semanal y media en desacuerdos técnicos o de alcance."],
    ], anchos=[4.0, 5.4, 7.2], tam=9, primera_negrita=True, titulo="Procesos de gestión de recursos humanos")

    U.h2(doc, "10.2 Organigrama del proyecto (OBS)")
    U.figura(doc, FIG + "obs.png", 16.0, "Organigrama del proyecto (OBS) con cuatro niveles")
    U.tabla(doc, ["Nivel", "Rol", "Ocupante", "Función"], [
        ["1", "Patrocinador", D.DOCENTE, "Aprueba el presupuesto y las decisiones estratégicas."],
        ["—", "Cliente / usuario clave", "Dra. Marimar, Jefatura, OEI (HRDC)", "Valida requisitos, valores clínicos y textos; participa en el piloto."],
        ["2", "Director del proyecto", D.EQUIPO["PM"]["nombre"], "Planifica, ejecuta, controla y cierra; reporta al sponsor."],
        ["3", "Líder Técnico / Analista Funcional / QA", "J. Valdiviezo · A. Limay · D. Díaz", "Lideran las áreas técnica, funcional y de calidad."],
        ["4", "Equipo de ejecución", "S. Terrones · D. Pérez", "Desarrollo del frontend y de las integraciones."],
        ["—", "Soporte externo", "Supabase, Vercel, Render, Google", "Infraestructura bajo los términos de cada plan."],
    ], anchos=[1.2, 4.0, 5.6, 5.8], alinear=["c", "l", "l", "l"], tam=9, titulo="Niveles del OBS")
    U.caja(doc, "Se incluyó al **cliente** en el organigrama (usuaria clave del Banco de Sangre con ≈ 20 % de dedicación en las sesiones de validación). "
                "Omitir al usuario es un error frecuente: se corrigió desde el inicio.", color="FEF9E7")

    U.h2(doc, "10.3 Descripciones de cargo")
    for cod, nombre, resp, autoridad, formacion, experiencia, blandas, dedic, reporta in CARGOS:
        persona = D.EQUIPO[cod]["nombre"] if cod in D.EQUIPO else "Dra. Marimar (HRDC)"
        U.tabla(doc, ["Campo", f"{nombre} — {persona}"], [
            ["Nombre del cargo", nombre],
            ["Responsabilidades", "\n".join("• " + r for r in resp)],
            ["Autoridad dentro del proyecto", autoridad],
            ["Formación requerida", formacion],
            ["Experiencia requerida", experiencia],
            ["Habilidades blandas clave", blandas],
            ["Dedicación al proyecto", dedic],
            ["Línea de reporte", reporta],
        ], anchos=[4.0, 12.6], tam=8.5, primera_negrita=True, zebra=False)

    U.h2(doc, "10.4 Matriz RACI")
    U.parrafo(doc, "**R** = Responsable (hace el trabajo) · **A** = Aprobador (responde por el resultado; exactamente uno por fila) · **C** = Consultado · **I** = Informado · **A/R** = la misma persona aprueba y ejecuta. "
                   "Se verificó por programa que **cada fila tiene exactamente un A y exactamente un R**, y que el cliente está consultado en los módulos que lo afectan.", alineacion="justificado")
    U.seccion(doc, horizontal=True)
    filas = []
    for nombre, fila in RACI:
        filas.append([nombre] + [fila[c] for c in COLS])
    res = {}
    U.tabla(doc, ["Entregable / actividad", "PM", "LT", "AF", "FE", "INT", "QA", "Sponsor", "Cliente"], filas,
            anchos=[9.0, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 2.0, 2.0], alinear=["l"] + ["c"] * 8, tam=8.5, titulo="Matriz RACI de HEMOCAX (26 entregables)")
    U.parrafo(doc, "PM Project Manager · LT Líder Técnico · AF Analista Funcional · FE Desarrolladora Frontend · INT Desarrollador de Integraciones · QA Especialista QA y Seguridad · Sponsor: docente coordinadora · Cliente: Banco de Sangre del HRDC.", tam=9)
    U.seccion(doc, horizontal=False)

    U.h2(doc, "10.5 Plan para la dirección del personal")
    U.h3(doc, "a) Calendario de disponibilidad del equipo")
    horarios = {"PM": "Lun-Mar-Mié-Vie", "LT": "Mar-Jue mañanas, sáb.", "AF": "Mar-Jue tardes", "FE": "Lun-Mié tardes, dom.", "INT": "Mar-Jue-sáb.", "QA": "Lun-Mié mañanas"}
    filas = []
    for r in D.ORDEN_ROLES:
        e = D.EQUIPO[r]
        filas.append([e["nombre"], e["rol"], f"{D.HORAS_ROL[r] / D.SEMANAS_PROY:.0f} h/sem", str(D.HORAS_ROL[r]), horarios[r], "Carga académica en otros cursos"])
    U.tabla(doc, ["Integrante", "Rol", "Dedicación", "Horas totales", "Horario preferido", "Restricción"], filas,
            anchos=[4.6, 4.0, 1.9, 1.6, 2.7, 2.6], alinear=["l", "l", "c", "c", "l", "l"], tam=8, titulo="Disponibilidad semanal del equipo")
    U.figura(doc, FIG + "histograma_recursos.png", 15.0, "Histograma de recursos: horas planificadas por semana")
    pico = max(range(D.N_SEMANAS), key=lambda i: sum(D.HORAS_SEM[r][i] for r in D.ORDEN_ROLES))
    U.parrafo(doc, f"El pico de carga se da en la **semana {pico + 1}** ({sum(D.HORAS_SEM[r][pico] for r in D.ORDEN_ROLES):.0f} h), cuando coinciden el portal del donante, el panel del personal, las integraciones y las pruebas. "
                   "Esa sobreasignación es la causa principal de las horas extra descritas en el capítulo 8. Para próximos proyectos se recomienda adelantar el desarrollo del frontend a las semanas con baja carga.", alineacion="justificado")

    U.h3(doc, "b) Adquisición de personal y recursos")
    U.tabla(doc, ["Recurso", "Descripción", "Incorporación", "Costo"], [
        ["Equipo de 6 integrantes", "Ya conformado, estudiantes de la EPIS", f(D.INICIO), "Horas imputadas"],
        ["GitHub (repositorio y tablero)", "Plan gratuito", "21/07/2026", "S/ 0.00"],
        ["Figma", "Plan Education", "21/07/2026", "S/ 0.00"],
        ["Supabase (base de datos y autenticación)", "Plan Free", "17/08/2026", "S/ 0.00"],
        ["Vercel (portal web)", "Plan Hobby", "17/08/2026", "S/ 0.00"],
        ["Render (reloj de recordatorios)", "Plan Free", "09/09/2026", "S/ 0.00"],
        ["Cuenta de correo institucional del proyecto", "Contraseña de aplicación", "09/09/2026", "S/ 0.00"],
        ["Dispositivos de prueba", "Celulares personales del equipo", "Fase 4", "S/ 0.00"],
    ], anchos=[5.4, 5.2, 3.0, 3.0], alinear=["l", "l", "c", "c"], tam=8.5, titulo="Plan de adquisición de personal y recursos")

    U.h3(doc, "c) Brechas de conocimiento y plan de capacitación")
    U.tabla(doc, ["Integrante", "Área / tecnología", "Impacto", "Plan de capacitación / mitigación"], [
        [D.EQUIPO["LT"]["corto"], "Seguridad por filas en PostgreSQL", "Alto", "Documentación oficial y laboratorio de pruebas con roles (semanas 3 y 4)."],
        [D.EQUIPO["INT"]["corto"], "Envío por SMTP y tareas programadas", "Alto", "Prueba de concepto temprana y mentoría del Líder Técnico."],
        [D.EQUIPO["FE"]["corto"], "Next.js y diseño para zonas rurales", "Medio", "Tutorial oficial y revisión por pares con el Analista UX."],
        [D.EQUIPO["QA"]["corto"], "Pruebas de seguridad de aplicaciones web", "Medio", "Lista de verificación OWASP y pruebas con sesión de cada rol."],
        [D.EQUIPO["AF"]["corto"], "Entrevistas a personal de salud", "Bajo", "Guion de entrevistas y acompañamiento del PM en el kick-off."],
        ["Todo el equipo", "Ley N.° 29733 y GitHub Projects", "Bajo", "Sesión de inducción de 1 hora en la semana 1."],
    ], anchos=[3.4, 4.4, 1.6, 7.2], alinear=["l", "l", "c", "l"], tam=8.5, titulo="Brechas de conocimiento y capacitación")

    U.h3(doc, "d) Sistema de incentivos y reconocimientos")
    U.tabla(doc, ["Incentivo", "Aplica a", "Frecuencia", "Criterio"], [
        ["Reconocimiento verbal en la reunión semanal", "Todos", "Semanal", "Entregables a tiempo"],
        ["Rol rotativo de «líder de la semana»", "Desarrolladores", "Semanal", "Mayor aporte técnico o funcional"],
        ["Mención en el informe final", "Todos", "Cierre", "Participación en el proyecto"],
        ["Certificado de participación (EPIS-UNC)", "Todos", "Cierre", "Aprobación del proyecto"],
        ["Carta de recomendación de la docente", "Quien lo solicite", "Cierre", "Desempeño destacado"],
    ], anchos=[6.4, 3.0, 2.4, 4.8], tam=8.5, titulo="Incentivos no económicos")
    U.parrafo(doc, "Aplicación de las teorías de motivación: según **Herzberg**, la ausencia de factores de higiene (horario, herramientas, claridad de rol) desmotiva, pero lo que motiva es el reto, la autonomía y el reconocimiento; "
                   "por eso se prioriza el reconocimiento y la rotación de responsabilidades. Se aplica la **Teoría Y** de McGregor: el equipo se auto-organiza y el PM actúa como facilitador.", alineacion="justificado")

    U.h3(doc, "e) Desarrollo del equipo (Tuckman)")
    U.tabla(doc, ["Etapa", "Semanas esperadas", "Comportamiento", "Estilo del PM"], [
        ["Formación (*Forming*)", "S1 – S3", "Roles por definir, alta dependencia del PM.", "Directivo: claridad de objetivos, roles y reglas."],
        ["Tormenta (*Storming*)", "S6 – S8", "Diferencias de criterio sobre alcance y prioridades al aumentar la carga.", "Mediador: decisiones documentadas y control de cambios."],
        ["Normalización (*Norming*)", "S9", "Acuerdos de trabajo establecidos.", "Facilitador."],
        ["Desempeño (*Performing*)", "S10 – S11", "Autonomía y recuperación del plazo.", "Delegar y remover obstáculos."],
        ["Cierre (*Adjourning*)", "S12", "Transferencia de conocimiento.", "Reconocer y documentar lecciones."],
    ], anchos=[3.6, 2.8, 5.6, 4.6], tam=8.5, titulo="Etapas de desarrollo del equipo y estilo de liderazgo")

    U.h3(doc, "f) Plan de liberación del personal al cierre")
    fl = D.FIN_PLAN
    U.tabla(doc, ["Integrante", "Rol", "Fecha de liberación", "Condición de salida"], [
        [D.EQUIPO["PM"]["corto"], "PM", f(fl), "Informe final, lecciones aprendidas y acta de cierre firmada."],
        [D.EQUIPO["LT"]["corto"], "Líder Técnico", f(fl), "Repositorio, migraciones y documentación técnica entregados a la OEI."],
        [D.EQUIPO["INT"]["corto"], "Integraciones", f(fl), "Variables de entorno y procedimiento de despliegue documentados."],
        [D.EQUIPO["FE"]["corto"], "Frontend", f(fl), "Código del portal y del panel en el repositorio, sin trabajo pendiente."],
        [D.EQUIPO["QA"]["corto"], "QA", f(fl), "Informes de pruebas y registro de defectos entregados."],
        [D.EQUIPO["AF"]["corto"], "Analista", f(fl), "Manuales, ayuda integrada y video de capacitación entregados."],
    ], anchos=[3.8, 2.8, 3.2, 6.8], alinear=["l", "l", "c", "l"], tam=8.5, titulo="Liberación del personal")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def comunicaciones(doc):
    n_ = D.N_INTERESADOS
    U.h1(doc, "11. Gestión de las comunicaciones")
    U.h2(doc, "11.1 Canales de comunicación")
    U.parrafo(doc, f"Fórmula del PMBOK: **canales = n × (n − 1) / 2**, donde n es el número de interesados. Con {n_} interesados hay **{D.CANALES} canales** potenciales; "
                   f"si se agrega uno más ({n_ + 1}), pasan a {(n_ + 1) * n_ // 2} (+{n_} canales, +{100 * n_ / D.CANALES:.0f} %). "
                   f"Para controlar la complejidad, las comunicaciones externas se **centralizan en el PM**: en lugar de {D.CANALES} canales, cada interesado externo habla con una persona.", alineacion="justificado")
    U.h2(doc, "11.2 Matriz de requisitos de comunicación")
    U.seccion(doc, horizontal=True)
    U.tabla(doc, ["Interesado", "Información que necesita", "Frecuencia", "Formato / canal", "Responsable"], [
        ["Sponsor (docente coordinadora)", "Estado general: % de avance, EVM (PV, EV, AC, CPI, SPI), hitos, riesgos activos, decisiones requeridas, solicitudes de cambio.", "Semanal (viernes 5:00 p. m.) y demo por hito", "Informe ejecutivo PDF por correo + presentación en la demo", "PM"],
        ["Equipo del proyecto", "Tareas por semana, bloqueos técnicos, decisiones de arquitectura, resultados de pruebas, cambios de cronograma.", "Semanal (lunes 8:00 a. m.) y comunicación asíncrona diaria", "Google Meet 45 min, acta en Drive, tablero de GitHub Projects", "PM"],
        ["Banco de Sangre (usuarios clave y enfermería)", "Avance de los módulos que los afectan, prototipos por validar, cronograma del piloto, instrucciones de uso.", "Quincenal", "Reunión presencial o Google Meet; prototipos en Figma; manual en PDF", "PM y Analista"],
        ["Jefatura y Dirección General", "Resumen ejecutivo: objetivos, alcance, impacto, resultados y costo recurrente.", "Inicio, hitos críticos y cierre", "Correo formal + documento Word/PDF; presentación en el cierre", "PM y Sponsor"],
        ["OEI del HRDC (área de TI)", "Arquitectura, modelo de datos, seguridad, variables de entorno y requisitos de conectividad.", "Antes del despliegue y al cierre", "Documento técnico PDF + repositorio; reunión de entrega técnica", "Líder Técnico y QA"],
        ["Donantes", "Estado de aptitud, resultado liberado, campañas y avisos autorizados.", "Según evento", "Portal del donante y correo con consentimiento", "Sistema (PM define los textos)"],
        ["Proveedores en la nube", "Términos de uso, límites de los planes, incidencias y cambios de API.", "Mensual e inmediato ante incidencias", "Paneles y páginas de estado de cada proveedor", "Líder Técnico"],
    ], anchos=[4.6, 8.2, 3.6, 5.6, 3.0], tam=8, titulo="Matriz de requisitos de comunicación")
    U.seccion(doc, horizontal=False)

    U.h2(doc, "11.3 Plan de gestión de las comunicaciones")
    U.seccion(doc, horizontal=True)
    U.tabla(doc, ["ID", "Evento / artefacto", "Propósito", "Participantes", "Frecuencia", "Canal y almacenamiento", "Tiempo máx. de respuesta"], [
        ["COM-01", "Reunión de kick-off", "Alinear objetivos, alcance, roles, cronograma y reglas de trabajo.", "PM, equipo, sponsor", "Una vez (22/07/2026)", "Presencial/Meet; acta en Drive /Actas", "N/A"],
        ["COM-02", "Reunión semanal de equipo", "Revisar avance, bloqueos y replanificar (máx. 45 min).", "PM y los 6 integrantes", "Semanal (lunes 8:00)", "Google Meet; acta en Drive y tablero actualizado", "Acta en 24 h"],
        ["COM-03", "Informe de avance al sponsor", "Informar progreso, EVM, riesgos y decisiones pendientes.", "PM → sponsor", "Semanal (viernes 5:00 p. m.)", "Correo con PDF adjunto", "Respuesta en 48 h"],
        ["COM-04", "Validación con el Banco de Sangre", "Validar requisitos, prototipos y avance técnico.", "PM, Analista, usuarios del Banco", "Quincenal", "Presencial en el hospital/Meet; acta firmada", "Cambios aprobados en 5 días"],
        ["COM-05", "Alerta de riesgo crítico", "Notificar activaciones de riesgos con exposición ≥ 15.", "PM → sponsor y dueño del riesgo", "Inmediata", "Mensaje de coordinación + correo formal", "< 2 h"],
        ["COM-06", "Demo de avance (checkpoint)", "Mostrar módulos terminados y obtener aprobación para continuar.", "PM, desarrolladores, sponsor", "Por hito (3 veces)", "Google Meet con grabación", "Aprobación en 48 h"],
        ["COM-07", "Control de cambios", "Gestionar solicitudes de cambio de alcance, tiempo o costo.", "Solicitante, PM, sponsor", "Cuando se requiera", "Formulario digital + registro SCR", "PM 24 h; sponsor 48 h"],
        ["COM-08", "Informe del piloto interno", "Reportar resultados del piloto a sponsor y Banco de Sangre.", "PM → sponsor y Jefatura", "Una vez", "PDF formal + presentación", "—"],
        ["COM-09", "Retrospectiva de fase", "Qué salió bien, qué mejorar, lecciones aprendidas.", "Todo el equipo", "Al cierre de cada fase (5)", "Meet de 30 min; acta en /Retrospectivas", "Acta en 24 h"],
        ["COM-10", "Acta de cierre", "Formalizar la conclusión y la aceptación.", "PM y sponsor (copia al Banco de Sangre)", "Una vez", "Documento firmado físico y digital", "—"],
    ], anchos=[1.5, 3.4, 5.4, 3.6, 3.0, 5.2, 2.6], tam=7.8, titulo="Plan de comunicaciones")
    U.seccion(doc, horizontal=False)

    U.h2(doc, "11.4 Herramientas de comunicación y criterio de uso")
    U.tabla(doc, ["Herramienta", "Úsese para", "No se use para"], [
        ["Correo electrónico", "Comunicaciones formales, informes y decisiones (deja evidencia).", "Coordinación rápida del día a día."],
        ["Google Meet", "Reuniones semanales, demos y decisiones complejas.", "Informar algo que puede ir en un documento."],
        ["GitHub Projects", "Tareas, bloqueos y estado del desarrollo.", "Decisiones con el cliente."],
        ["Google Drive", "Actas, informes, formatos y registro de cambios (fuente única).", "Conversaciones."],
        ["Mensajería instantánea del equipo", "Avisos urgentes y coordinación inmediata.", "Decisiones: toda decisión se confirma por correo o acta."],
    ], anchos=[4.0, 7.2, 5.4], tam=9, primera_negrita=True, titulo="Criterios de uso de las herramientas")
    U.parrafo(doc, "**Regla:** una decisión que no está en un correo o un acta no existe formalmente. Se evita así el error de usar varios canales sin criterio, donde una solicitud urgente se pierde en una conversación.", tam=9.5)

    U.h2(doc, "11.5 Formatos de informe por audiencia")
    p11 = D.indicadores(D.S_CORTE)
    U.h3(doc, "a) Informe ejecutivo (1 página) — al sponsor")
    U.caja(doc,
           f"**Proyecto:** HEMOCAX · **PM:** {D.EQUIPO['PM']['corto']} · **Corte:** {f(D.CORTE)} (semana {D.S_CORTE} de {D.N_SEMANAS})\n"
           f"**Estado general:** 🟢 En tiempo · 🟡 Costo con desviación controlada\n"
           f"**Avance:** {pct(p11['pct'])} del valor planificado ({s(p11['ev'])} de {s(D.BAC)})\n"
           f"**Cronograma:** SPI {p11['spi']:.2f} (SV {s(p11['sv'])}) — el plazo se recuperó\n"
           f"**Costo:** CPI {p11['cpi']:.2f} (CV {s(p11['cv'])}) — EAC {s(p11['eac1'])}; cubierto con {pct(-p11['vac'] / D.RESERVA_CONTINGENCIA)} de la contingencia\n"
           f"**Riesgo crítico:** R04 límites de planes gratuitos (exposición 12) — monitoreo externo por configurar\n"
           f"**Próximos hitos:** informe final (02/10) · acta de cierre ({f(D.FIN_PLAN)})\n"
           f"**Decisión requerida del sponsor:** aprobar el uso de la contingencia ({s(-p11['vac'])}) y definir con la Dirección el costo recurrente.",
           titulo="Modelo de informe ejecutivo (datos al corte)", color="F4F6F7")
    U.h3(doc, "b) Informe técnico (5 a 15 páginas) — para el Líder Técnico, la OEI y el Banco de Sangre")
    U.viñetas(doc, [
        "Módulos completados y pendientes por actividad de la EDT.", "Defectos por severidad y módulo (Pareto); métricas de calidad.",
        "Decisiones técnicas y cambios de arquitectura (con fecha y motivo).", "Estado de la infraestructura: consumo de los límites gratuitos y disponibilidad.",
    ])
    U.h3(doc, "c) Informe de avance semanal (equipo y sponsor)")
    U.viñetas(doc, [
        "Actividades completadas y en curso, con porcentaje de avance y responsable.", "Impedimentos y acciones.", "SPI, CPI, riesgos activos y próximos hitos.", "Solicitudes de decisión.",
    ])
    U.h3(doc, "d) Acta de reunión (distribuir en máximo 24 horas)")
    U.tabla(doc, ["Campo", "Contenido"], [
        ["Reunión", "Nombre, fecha, hora, lugar o enlace"], ["Asistentes", "Nombres y roles"], ["Temas tratados", "Lista breve"],
        ["Decisiones", "Qué se decidió y quién lo aprobó"], ["Compromisos", "Quién · qué · para cuándo"], ["Próxima reunión", "Fecha y agenda"],
    ], anchos=[4.0, 12.6], tam=9, primera_negrita=True, titulo="Plantilla de acta de reunión")
    U.h3(doc, "e) Tablero de seguimiento (dashboard)")
    U.parrafo(doc, "Los indicadores se actualizan semanalmente en una hoja de cálculo (EVM) y en el módulo «Reportes» del propio sistema (donantes recurrentes, tiempo de entrega de resultados, donantes O negativo con consentimiento y mensajes de 30 días).")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def riesgos(doc):
    amen = [r for r in D.RIESGOS if r["tipo"] == "Amenaza"]
    opor = [r for r in D.RIESGOS if r["tipo"] == "Oportunidad"]
    rojos = [r for r in amen if r["pi"] >= 10]
    U.h1(doc, "12. Gestión de los riesgos")
    U.h2(doc, "12.1 Plan de gestión de riesgos")
    U.tabla(doc, ["Proceso", "Salida", "Cómo se aplicó"], [
        ["1. Planificar la gestión", "Plan de gestión de riesgos", "Esta sección: metodología, roles y umbrales."],
        ["2. Identificar los riesgos", "Registro de riesgos", "Lluvia de ideas del equipo, lista de verificación de riesgos de TI, revisión de supuestos del Charter y FODA."],
        ["3. Análisis cualitativo", "Prioridad (rojo/amarillo/verde)", "Probabilidad × impacto en escala 1-5 (sección 12.4)."],
        ["4. Análisis cuantitativo", "VME y reserva de contingencia", "Sección 12.5."],
        ["5. Planificar la respuesta", "Plan de respuesta", "Sección 12.6: estrategia, acciones, dueño, disparador y contingencia."],
        ["6. Implementar la respuesta", "Solicitudes de cambio", "Acciones asignadas a dueños; se verifican en la reunión semanal."],
        ["7. Monitorear los riesgos", "Información de desempeño", "Revisión semanal del registro; alerta en menos de 2 horas para exposición ≥ 15."],
    ], anchos=[4.0, 4.2, 8.4], tam=8.5, primera_negrita=True, titulo="Procesos de gestión de riesgos")
    U.tabla(doc, ["Escala", "1 · Muy bajo/improbable", "2 · Bajo", "3 · Medio/posible", "4 · Alto/probable", "5 · Muy alto/casi seguro"], [
        ["Probabilidad (VME)", "10 %", "30 %", "50 %", "70 %", "90 %"],
        ["Impacto en costo", "< S/ 50", "S/ 50 – 150", "S/ 150 – 250", "S/ 250 – 400", "> S/ 400 o daño legal"],
        ["Impacto en tiempo", "< 1 día", "1 – 2 días", "3 – 5 días", "1 – 2 semanas", "> 2 semanas"],
        ["Impacto en calidad/seguridad", "Cosmético", "Afecta una función menor", "Afecta una función", "Afecta un módulo", "Expone datos o resultados críticos"],
    ], anchos=[3.4, 2.6, 2.4, 2.8, 2.6, 2.8], alinear=["l", "c", "c", "c", "c", "c"], tam=8, primera_negrita=True, titulo="Escalas de probabilidad e impacto")
    U.parrafo(doc, "**Umbrales de prioridad (P × I):** verde ≤ 4 (solo monitorear) · amarillo 5-9 (plan y monitoreo) · **rojo ≥ 10 (acción inmediata)**. "
                   "Las amenazas con exposición ≥ 15 se escalan al sponsor en menos de 2 horas.", tam=9.5)
    U.h3(doc, "Estructura de desglose de riesgos (RBS)")
    U.tabla(doc, ["Categoría", "Riesgos"], [
        ["Personas", "R01"], ["Alcance", "R02"], ["Interesados", "R03, R13, R16"], ["Técnico", "R04, R05, R10"], ["Legal / Seguridad", "R06, R07, R12"],
        ["Usuarios", "R08"], ["Clínico", "R09"], ["Cronograma", "R11"], ["Costos y académico (oportunidades)", "R14, R15"],
    ], anchos=[6.0, 10.6], tam=9, titulo="Categorías de riesgo")
    U.h3(doc, "FODA del proyecto (apoyo a la identificación)")
    U.tabla(doc, ["Fortalezas", "Debilidades", "Oportunidades", "Amenazas"], [
        ["Equipo con roles definidos; seguridad en la base de datos; costo de operación cero.", "Equipo con poco tiempo disponible; sin pruebas automáticas; dependencia de planes gratuitos.",
         "Interés del Banco de Sangre; posibilidad de adopción y de tesis.", "Límites de servicios; cambios de requisitos; normativa de datos de salud."],
    ], anchos=[4.2, 4.2, 4.1, 4.1], tam=8.5, zebra=False)
    U.h2(doc, "12.2 Registro de riesgos")
    U.parrafo(doc, f"Se identificaron **{len(D.RIESGOS)} riesgos**: {len(amen)} amenazas y {len(opor)} oportunidades. Se identificaron en una sesión de lluvia de ideas con todo el equipo.")
    U.seccion(doc, horizontal=True)
    filas = []
    for r in D.RIESGOS:
        filas.append([r["id"], r["tipo"], r["cat"], r["desc"], r["causa"], str(r["p"]), str(r["i"]), str(r["pi"]), r["nivel"], D.EQUIPO[r["dueno"]]["corto"].split()[0], r["est"], r.get("estado", "Vigente")])
    res = {}
    for i, r in enumerate(D.RIESGOS):
        res[i] = "FADBD8" if r["pi"] >= 10 and r["tipo"] == "Amenaza" else ("FCF3CF" if r["pi"] >= 5 else "D5F5E3")
    U.tabla(doc, ["ID", "Tipo", "Categoría", "Descripción del riesgo", "Causa raíz", "P", "I", "P×I", "Nivel", "Dueño", "Estrategia", "Estado"], filas,
            anchos=[1.0, 1.7, 1.9, 6.4, 4.0, 0.8, 0.8, 1.0, 2.4, 1.7, 2.1, 3.2], alinear=["c", "l", "l", "l", "l", "c", "c", "c", "l", "l", "l", "l"], tam=7.5, zebra=False, resaltar=res,
            titulo="Registro de riesgos (P e I en escala 1-5)")
    U.seccion(doc, horizontal=False)
    U.h2(doc, "12.3 Identificación: técnicas utilizadas")
    U.viñetas(doc, [
        "**Lluvia de ideas** con los seis integrantes; se consolidaron los riesgos repetidos.",
        "**Lista de verificación de riesgos de TI:** tecnológicos, financieros, operativos, de seguridad física y legales.",
        "**Revisión de supuestos del Project Charter:** cada supuesto cuestionado generó un riesgo (R02, R03, R04, R09).",
        "**FODA** (tabla anterior) para ordenar fortalezas, debilidades, oportunidades y amenazas.",
    ])
    U.h2(doc, "12.4 Análisis cualitativo: matriz de probabilidad × impacto")
    U.figura(doc, FIG + "mapa_calor.png", 12.5, "Matriz P×I (verde ≤ 4, amarillo 5-9, rojo ≥ 10)")
    top = sorted(amen, key=lambda r: -r["pi"])[:5]
    U.parrafo(doc, "**Las amenazas de mayor puntaje** son: " + "; ".join(f"{r['id']} ({r['pi']})" for r in top) + f". En total, {len(rojos)} amenazas están en nivel rojo y requieren plan de respuesta.", alineacion="justificado")
    U.parrafo(doc, "**Un riesgo con probabilidad baja pero impacto muy alto puede ser más crítico** que uno frecuente y leve: por ejemplo, R06 (exposición de datos de salud, P=2, I=5) y R07 (un resultado crítico visible para el donante, P=1, I=5) reciben barreras desde el diseño aunque su puntaje sea bajo.", alineacion="justificado")
    U.h2(doc, "12.5 Análisis cuantitativo: Valor Monetario Esperado (VME)")
    U.parrafo(doc, "VME = probabilidad × impacto monetario. La reserva de contingencia es la **suma de los VME de las amenazas** con impacto monetario estimado; así queda fundamentada y no es un porcentaje arbitrario.")
    filas = []
    for r in D.RIESGOS_VME:
        filas.append([r["id"], CORTO[r["id"]], f"{r['p']} → {int(D.PROB_VME[r['p']] * 100)} %", f"{r['imp']:,.2f}", f"{r['vme']:,.2f}"])
    filas.append(["", "**RESERVA DE CONTINGENCIA**", "", "", f"**{D.RESERVA_CONTINGENCIA:,.2f}**"])
    U.tabla(doc, ["ID", "Amenaza", "Probabilidad", "Impacto (S/)", "VME (S/)"], filas, anchos=[1.2, 9.2, 2.2, 2.0, 2.0], alinear=["c", "l", "c", "r", "r"], tam=8.5, titulo="Cálculo del VME y de la reserva de contingencia")
    U.parrafo(doc, f"La reserva de contingencia ({s(D.RESERVA_CONTINGENCIA)}) equivale al {pct(D.RESERVA_CONTINGENCIA / D.BAC)} del costo base. Las oportunidades (R13 a R16) no reducen la reserva: se gestionan para aprovecharlas.", tam=9.5)
    U.h2(doc, "12.6 Plan de respuesta a los riesgos")
    U.parrafo(doc, f"Se elaboró el plan completo para las **{len(rojos)} amenazas en nivel rojo**. Estrategias para amenazas: escalar, evitar, transferir, mitigar y aceptar (activa o pasiva); para oportunidades: escalar, explotar, compartir, mejorar y aceptar.")
    U.seccion(doc, horizontal=True)
    filas = []
    for r in sorted(rojos, key=lambda x: -x["pi"]):
        filas.append([r["id"], r["desc"], r["est"], r["acc"], D.EQUIPO[r["dueno"]]["corto"], r["trig"], r["cont"], f"{r['costo']:,.2f}"])
    U.tabla(doc, ["ID", "Descripción completa", "Estrategia", "Acciones de respuesta", "Dueño", "Disparador", "Plan de contingencia", "Costo (S/)"], filas,
            anchos=[1.0, 5.0, 1.9, 5.6, 2.3, 3.4, 4.4, 1.5], alinear=["c", "l", "l", "l", "l", "l", "l", "r"], tam=7.5, titulo="Plan de respuesta a las amenazas de nivel rojo")
    U.parrafo(doc, f"El costo de las respuestas suma {s(sum(r['costo'] for r in rojos))} y está incluido en las horas de las actividades de la línea base (por ejemplo 2.6, 3.1, 4.3 y 4.5); no se agrega al presupuesto.", tam=9.5)
    filas = [[r["id"], r["desc"], r["est"], r["acc"], D.EQUIPO[r["dueno"]]["corto"], r["trig"]] for r in opor]
    U.tabla(doc, ["ID", "Oportunidad", "Estrategia", "Acciones", "Dueño", "Disparador"], filas, anchos=[1.0, 7.8, 2.2, 7.0, 2.8, 4.8], alinear=["c", "l", "l", "l", "l", "l"], tam=7.8, titulo="Respuesta a las oportunidades")
    U.seccion(doc, horizontal=False)
    U.h2(doc, "12.7 Monitoreo y control de riesgos")
    U.tabla(doc, ["Riesgo", "Evento en el proyecto", "Respuesta aplicada"], [
        ["R05 · Bloqueo de correo (SMTP) en el alojamiento", "**Se materializó en la semana 9:** el reloj alojado en el plan gratuito no podía enviar correos.", "Se movió el envío al portal; el reloj quedó solo como planificador. Costo: 16 horas de rehacer (CoQ, fallas internas)."],
        ["R02 · Cambios de requisitos", "Se registraron cambios de alcance durante el desarrollo (SCR-01 a SCR-09, capítulo 14).", "Proceso de control de cambios; sin impacto mayor al sponsor."],
        ["R01 · Indisponibilidad de integrantes", "Sobrecarga en las semanas 8 a 10 (histograma de recursos).", "Reasignación de tareas y horas extra; fue la causa principal del CPI < 1."],
        ["R04 · Límites de planes gratuitos", "En seguimiento; sin interrupciones.", "Monitor externo de disponibilidad (por configurar) y registro de consumo."],
    ], anchos=[4.6, 6.2, 5.8], tam=8.5, titulo="Riesgos materializados o con eventos")
    U.h3(doc, "Riesgo residual")
    filas = []
    for r in sorted(rojos, key=lambda x: -x["pi"]):
        p2, i2 = r["res"]
        filas.append([r["id"], f"{r['p']} × {r['i']} = {r['pi']}", f"{p2} × {i2} = {p2 * i2}", "Verde/Amarillo" if p2 * i2 < 10 else "Aún rojo"])
    U.tabla(doc, ["Riesgo", "Exposición inicial", "Exposición residual", "Nivel residual"], filas, anchos=[3.0, 4.6, 4.6, 4.4], alinear=["c", "c", "c", "c"], tam=9, titulo="Exposición antes y después de la respuesta")
    U.salto_pagina(doc)


def construir(doc):
    rrhh(doc)
    comunicaciones(doc)
    riesgos(doc)
