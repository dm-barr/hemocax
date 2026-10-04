# -*- coding: utf-8 -*-
"""Parte IV (PMBOK 7) y anexos."""
import datos as D
import docx_utils as U
from fmt import f, s, n, pct

FIG = "fig/"


def pmbok7(doc):
    p11 = D.indicadores(D.S_CORTE)
    U.h1(doc, "PARTE IV · LECTURA DESDE EL PMBOK 7")
    U.h1(doc, "17. Dominios de desempeño, principios y valor")
    U.parrafo(doc, "El PMBOK 7 organiza la dirección de proyectos en **12 principios** y **8 dominios de desempeño** en lugar de procesos secuenciales, con enfoque en la entrega de **valor**. "
                   "Este capítulo muestra cómo la documentación de los capítulos anteriores cubre cada dominio y cada principio.", alineacion="justificado")
    U.h2(doc, "17.1 Los ocho dominios de desempeño")
    U.tabla(doc, ["Dominio", "Qué abarca", "Aplicación en HEMOCAX", "Evidencia"], [
        ["**Interesados**", "Comprender, involucrar y mantener relaciones con quienes afectan o son afectados.", "15 interesados clasificados; plan de involucramiento; validación quincenal con el Banco de Sangre.", "Cap. 2, 11"],
        ["**Equipo**", "Establecer la cultura, el liderazgo y el desarrollo del equipo.", "OBS con 4 niveles, 7 descripciones de cargo, RACI de 26 entregables, plan de incentivos y Tuckman.", "Cap. 10"],
        ["**Enfoque de desarrollo y ciclo de vida**", "Elegir el enfoque y la cadencia de entrega.", "Enfoque híbrido: planificación predictiva y entregas iterativas semanales; factores de adaptación.", "Sec. 3.2"],
        ["**Planificación**", "Organizar el trabajo, el tiempo, el costo y los recursos.", "Alcance, EDT, CPM, presupuesto con reservas, plan de calidad, adquisiciones y comunicaciones.", "Cap. 4 a 9, 13"],
        ["**Trabajo del proyecto**", "Establecer procesos, gestionar comunicaciones, adquisiciones y aprendizaje.", "Reunión semanal, control de cambios (9 SCR), adquisiciones, lecciones aprendidas continuas.", "Cap. 11, 13, 14, 16"],
        ["**Entrega**", "Producir el valor esperado cumpliendo requisitos y calidad.", "17 requisitos funcionales trazables a objetivos, criterios de aceptación y piloto interno.", "Cap. 4, 5, 9, 16"],
        ["**Medición**", "Evaluar el desempeño y tomar acciones correctivas.", "EVM semanal (SPI, CPI, EAC), métricas ISO/IEC 25010, indicadores de beneficios y reportes del sistema.", "Cap. 8, 9, 17.4"],
        ["**Incertidumbre**", "Gestionar riesgo, ambigüedad, complejidad y volatilidad.", "16 riesgos con VME, reserva de contingencia y gestión de la ambigüedad clínica con valores parametrizables.", "Cap. 12, 17.5"],
    ], anchos=[3.2, 4.4, 6.6, 2.4], tam=8, titulo="Cobertura de los dominios de desempeño")

    U.h2(doc, "17.2 Los doce principios de la dirección de proyectos")
    U.tabla(doc, ["N.°", "Principio", "Cómo se aplicó en HEMOCAX"], [
        ["1", "Ser un administrador diligente, respetuoso y cuidadoso", "Tratamiento de datos de salud con consentimiento, mínimo privilegio y mensajes sin datos médicos; uso de planes gratuitos sin comprometer datos."],
        ["2", "Crear un entorno colaborativo del equipo", "Roles claros, reunión semanal, rotación del «líder de la semana» y retrospectivas por fase."],
        ["3", "Involucrarse eficazmente con los interesados", "Validación quincenal con el Banco de Sangre y decisión explícita de la Jefatura sobre valores y textos."],
        ["4", "Enfocarse en el valor", "Cada requisito se vincula a un objetivo (trazabilidad) y los beneficios se miden (sec. 17.4)."],
        ["5", "Reconocer, evaluar y responder a las interacciones del sistema", "El sistema se diseñó como un conjunto: reloj, portal, base de datos y correo, con dependencias identificadas."],
        ["6", "Demostrar comportamientos de liderazgo", "El PM facilita, documenta decisiones y media en desacuerdos."],
        ["7", "Adaptar según el contexto", "Enfoque híbrido y cambios de canal y de arquitectura tramitados por control de cambios."],
        ["8", "Incorporar la calidad en los procesos y entregables", "Plan de calidad, pruebas por rol, revisión entre pares y lista de verificación de despliegue."],
        ["9", "Navegar en la complejidad", "Separación de responsabilidades (quién decide y quién envía) y reglas críticas en la base de datos."],
        ["10", "Optimizar las respuestas a los riesgos", "VME para fundamentar la contingencia; respuestas con dueño y disparador; riesgo R05 gestionado cuando se materializó."],
        ["11", "Adoptar la adaptabilidad y la resiliencia", "El reloj se vigila con un monitor externo; se recuperó el plazo tras el atraso de las semanas 6 a 9."],
        ["12", "Permitir el cambio para lograr el estado futuro previsto", "Capacitación, ayuda integrada por puesto y plan de transferencia para que el Banco de Sangre adopte el sistema."],
    ], anchos=[0.9, 5.2, 10.5], alinear=["c", "l", "l"], tam=8.5, titulo="Principios del PMBOK 7 y evidencia")

    U.h2(doc, "17.3 Modelos, métodos y artefactos utilizados")
    U.tabla(doc, ["Tipo", "Utilizados"], [
        ["Modelos de ciclo de vida", "Híbrido: predictivo en planificación y gobierno; iterativo e incremental en el desarrollo."],
        ["Métodos", "Descomposición del trabajo (EDT), método de la ruta crítica (CPM), estimación PERT, valor ganado (EVM), análisis de Pareto e Ishikawa, VME."],
        ["Artefactos de planificación", "Project Charter, registro de stakeholders, documento de requisitos y alcance, EDT y diccionario, cronograma, presupuesto, planes subsidiarios."],
        ["Artefactos de seguimiento", "Informe ejecutivo y de avance, curva S, registro de riesgos, registro de cambios, registro de lecciones aprendidas."],
        ["Tableros", "GitHub Projects para tareas; módulo «Reportes» del sistema para indicadores del producto."],
    ], anchos=[4.0, 12.6], tam=9, primera_negrita=True, titulo="Modelos, métodos y artefactos")

    U.h2(doc, "17.4 Medición y plan de gestión de beneficios")
    U.parrafo(doc, "El **valor** de HEMOCAX se mide por el cambio que produce en el Banco de Sangre. Los valores de línea base se establecerán con los datos que el servicio ponga a disposición; mientras tanto se muestra el valor objetivo y cómo se medirá.", alineacion="justificado")
    U.tabla(doc, ["Beneficio esperado", "Indicador", "Línea base", "Meta", "Fuente de medición", "Responsable", "Cuándo"], [
        ["Más donantes que vuelven a donar", "% de donantes con 2 o más donaciones", "Por levantar con datos del HRDC", "Aumento sostenido", "Reportes → «Donantes recurrentes»", "Jefatura", "Trimestral"],
        ["Resultados entregados más rápido", "Tiempo medio desde la donación hasta la liberación", "48 h a 5 días (referencia del servicio)", "≤ 48 h", "Reportes → «Tiempo medio de entrega»", "Médico responsable", "Mensual"],
        ["Reserva de grupos poco frecuentes", "Donantes O negativo con consentimiento", "Por levantar", "Aumento sostenido", "Reportes → «Donantes O negativo»", "Jefatura", "Mensual"],
        ["Canal institucional de comunicación", "Mensajes enviados con bitácora y tasa de envío exitoso", "0 (canal personal)", "≥ 95 % exitosos", "Correos enviados y Reportes", "Enfermería", "Mensual"],
        ["Tratamiento seguro de datos", "Incidentes de acceso indebido", "No medido", "0", "Bitácora de actividad", "Administrador", "Mensual"],
    ], anchos=[3.6, 3.6, 2.8, 1.9, 3.0, 1.9, 1.8], tam=7.8, titulo="Plan de gestión de beneficios")
    U.tabla(doc, ["Indicador del proyecto", "Valor al corte"], [
        ["SPI / CPI", f"{p11['spi']:.2f} / {p11['cpi']:.2f}"],
        ["Costo final proyectado frente al presupuesto total", f"{s(p11['eac1'])} de {s(D.PRESUPUESTO_TOTAL)} ({pct(p11['eac1'] / D.PRESUPUESTO_TOTAL)})"],
        ["Requisitos funcionales implementados", "17 de 17"],
        ["Tablas con seguridad por filas", "13 de 13"],
        ["Solicitudes de cambio aprobadas / diferidas", "7 / 2"],
        ["Defectos registrados / que llegaron al piloto interno", f"{sum(v for _, v in D.DEFECTOS)} / {D.CB_DEFECTOS_CON_PLAN}"],
        ["Riesgos materializados", "1 de 12 amenazas (R05)"],
    ], anchos=[9.4, 7.2], tam=9, titulo="Tablero de desempeño del proyecto")

    U.h2(doc, "17.5 Incertidumbre: ambigüedad, complejidad y volatilidad")
    U.tabla(doc, ["Tipo", "Ejemplo en el proyecto", "Respuesta"], [
        ["Riesgo (incertidumbre sobre eventos)", "Bloqueo del envío de correo en el plan gratuito.", "Registro de riesgos, VME y reserva de contingencia."],
        ["Ambigüedad", "Los valores clínicos (intervalo, máximos) y los textos no estaban validados.", "Parametrizar, documentar como supuesto y validar con el médico."],
        ["Complejidad", "Interacción entre reloj, portal, base de datos y correo; reglas legales y clínicas.", "Separar responsabilidades; reglas críticas en la base de datos; diagramas de arquitectura."],
        ["Volatilidad", "Cambios de canal, de arquitectura y de diseño durante el desarrollo.", "Control de cambios y entregas semanales con validación."],
    ], anchos=[4.0, 6.6, 6.0], tam=8.5, primera_negrita=True, titulo="Tipos de incertidumbre")
    U.salto_pagina(doc)


# ------------------------------------------------------------------------------------------------
def anexos(doc):
    U.h1(doc, "ANEXOS")
    U.h2(doc, "Anexo A. Registro de supuestos y restricciones")
    U.seccion(doc, horizontal=True)
    U.tabla(doc, ["ID", "Categoría", "Supuesto", "Fundamento", "Responsable", "Estado", "Si se invalida", "Contingencia"], [
        ["SUP-01", "Equipo", "Cada integrante dedica ≈ 14 horas semanales.", "Compromiso en el kick-off y calendario académico.", "PM", "Parcialmente válido", "Retraso en actividades críticas.", "Horas extra y renegociación (aplicado en semanas 8 a 10)."],
        ["SUP-02", "Tecnología", "Los servicios gratuitos estarán disponibles y estables.", "Documentación de cada proveedor.", "Líder Técnico", "Válido", "Interrupción en periodo crítico.", "Plan de ampliación y proveedor alterno."],
        ["SUP-03", "Interesados", "El Banco de Sangre participa en las sesiones de validación.", "Contraparte funcional designada.", "PM", "Válido", "Requisitos sin validar.", "Valores provisionales y reuniones adicionales."],
        ["SUP-04", "Clínico", "Los valores clínicos provisionales serán confirmados por el médico.", "Práctica del servicio.", "PM", "Pendiente", "Reglas inadecuadas.", "Parámetros editables; ajuste de la regla en la base."],
        ["SUP-05", "Legal", "El consentimiento versionado cumple la Ley N.° 29733.", "Revisión del texto por el equipo.", "QA", "Pendiente de revisión legal", "Rediseño del consentimiento.", "Consulta con la oficina jurídica; nueva versión del texto."],
        ["SUP-06", "Usuarios", "Los donantes aportan datos veraces y consienten su uso.", "Registro por personal del Banco de Sangre.", "Analista", "Válido", "Datos erróneos.", "Rectificación de datos desde la ficha."],
        ["SUP-07", "Costos", "No se requiere gasto en infraestructura durante el proyecto.", "Planes gratuitos.", "PM", "Válido", "Presupuesto adicional.", "Uso de la reserva de contingencia."],
        ["RES-01", "Restricción", f"Plazo máximo {f(D.FIN_PLAN)}.", "Calendario académico.", "PM", "Vigente", "—", "—"],
        ["RES-02", "Restricción", "Sin presupuesto externo ni personal adicional.", "Condición del curso.", "PM", "Vigente", "—", "—"],
        ["RES-03", "Restricción", "Sin integración con el sistema actual del hospital.", "Alcance acordado.", "PM", "Vigente", "—", "—"],
    ], anchos=[1.4, 2.0, 5.6, 4.0, 2.0, 2.6, 3.6, 5.2], tam=7.8, titulo="Supuestos y restricciones")
    U.seccion(doc, horizontal=False)

    U.h2(doc, "Anexo B. Registro de problemas (issues)")
    U.tabla(doc, ["ID", "Problema", "Impacto", "Acción", "Estado"], [
        ["P-01", "El reloj en el plan gratuito no puede enviar correo (SMTP bloqueado).", "Correos fallidos; 16 h de rehacer.", "Enviar desde el portal (SCR-02).", "Cerrado"],
        ["P-02", "El importador rechazaba el grupo sanguíneo «No sé».", "Filas válidas descartadas.", "Aceptar «No sé» como grupo desconocido.", "Cerrado"],
        ["P-03", "La regla del máximo anual está fija (4 y 3) en la base de datos aunque la pantalla permite editarla.", "Posible discrepancia si cambian los valores.", "Migración futura que lea el parámetro desde la base.", "Abierto (trabajo futuro)"],
        ["P-04", "En modo simulación, el correo manual queda como pendiente.", "Estado confuso en simulación; no afecta el modo real.", "Ajustar el estado permitido en la base.", "Abierto (menor)"],
        ["P-05", "Sobrecarga de recursos en las semanas 8 a 10.", "Horas extra y CPI < 1.", "Nivelar recursos en próximos proyectos.", "Cerrado (lección)"],
        ["P-06", "Las plantillas automáticas están sin aprobar.", "No salen recordatorios hasta que la Jefatura las apruebe.", "Gestionar la aprobación del hospital.", "Abierto (depende del hospital)"],
    ], anchos=[1.2, 5.8, 3.4, 4.4, 2.0], tam=8, titulo="Registro de problemas")

    U.h2(doc, "Anexo C. Plantilla de solicitud de cambio")
    U.tabla(doc, ["Campo", "Contenido"], [
        ["ID de solicitud", "SCR-___"], ["Fecha y solicitante", ""], ["Descripción del cambio y justificación", ""],
        ["Área afectada (alcance, tiempo, costo, calidad, riesgo)", ""], ["Impacto en días / en soles", ""], ["Clasificación (bajo / medio / alto)", ""],
        ["Decisión (aprobada / rechazada / diferida) y quién decide", ""], ["Fecha de decisión y firma", ""],
    ], anchos=[7.0, 9.6], tam=9, primera_negrita=True, zebra=False)

    # Contratos modelo ---------------------------------------------------------------------
    U.salto_pagina(doc)
    U.h2(doc, "Anexo D. Contratos modelo")
    U.parrafo(doc, "Los siguientes contratos son **modelos ilustrativos** basados en los formatos entregados en el curso. Los datos del proveedor están entre corchetes porque aún no se selecciona.", tam=9.5)
    U.h3(doc, "D.1 Contrato de precio fijo cerrado (FFP) — impresión de manuales")
    U.parrafo(doc, "**CONTRATO DE SERVICIO DE IMPRESIÓN Y ENCUADERNACIÓN — PRECIO FIJO CERRADO (FFP)**", alineacion="centro")
    U.parrafo(doc, f"**FECHA DE VIGENCIA:** [fecha de firma, semana 12]\n**ENTRE:** EL COMPRADOR: Universidad Nacional de Cajamarca — Escuela de Ingeniería de Sistemas, equipo del proyecto HEMOCAX. "
                   "EL PROVEEDOR: [Razón social y RUC del servicio de impresión — por seleccionar].")
    U.numerada(doc, [
        "**OBJETO.** EL PROVEEDOR imprimirá y encuadernará 3 juegos del manual de usuario y del manual técnico y 2 ejemplares anillados del informe de gestión, conforme al Anexo A (archivos PDF finales).",
        "**PRECIO.** S/ 110.00 (ciento diez soles), fijo y no sujeto a ajustes por variación de costos de papel, tinta u otros insumos.",
        "**PLAN DE PAGOS.** 50 % (S/ 55.00) a la aceptación de la cotización y 50 % (S/ 55.00) a la entrega y conformidad.",
        "**CRONOGRAMA.** Entrega en un máximo de 3 días hábiles desde la recepción de los archivos finales.",
        "**GESTIÓN DE CAMBIOS.** Cualquier cambio de cantidad, formato o páginas se solicitará por escrito y se atenderá con una orden de cambio que indique el efecto en precio y plazo.",
        "**GARANTÍA.** EL PROVEEDOR reimprimirá sin costo cualquier ejemplar con defectos de impresión dentro de los 7 días posteriores a la entrega.",
        "**CONFIDENCIALIDAD.** EL PROVEEDOR no conservará copias digitales ni reproducirá el contenido; la obligación rige por 2 años.",
        "**LEY APLICABLE.** Leyes de la República del Perú; jurisdicción de los tribunales de Cajamarca.",
    ])
    U.firmas(doc, [("Representante del equipo HEMOCAX", "Comprador"), ("[Representante del proveedor]", "Proveedor")])

    U.h3(doc, "D.2 Contrato de precio fijo más incentivos (FPIF) — servicio de mensajería (etapa futura)")
    U.parrafo(doc, "**CONTRATO DE SERVICIO DE MENSAJERÍA — PRECIO FIJO MÁS INCENTIVOS (FPIF)**", alineacion="centro")
    U.parrafo(doc, "**ENTRE:** EL COMPRADOR: Hospital Regional Docente de Cajamarca — Banco de Sangre. EL PROVEEDOR: [Proveedor de mensajería — por seleccionar]. "
                   "**Vigencia:** 12 meses desde la firma. Los importes son **referenciales** y deben cotizarse.")
    U.numerada(doc, [
        "**OBJETO.** Servicio de envío de correos transaccionales y SMS desde el sistema HEMOCAX, con reporte de entrega, soporte de nivel 1 y 2 y cumplimiento de la Ley N.° 29733 (Anexo A: especificaciones).",
        "**PRECIO Y ESTRUCTURA DE INCENTIVOS.** Precio objetivo S/ 2,400.00; costo objetivo del proveedor S/ 2,000.00; cuota objetivo S/ 400.00; **precio máximo (techo) S/ 2,700.00**; proporción de reparto de ahorros o sobrecostos: **70 % comprador / 30 % proveedor**.",
        "**PLAN DE PAGOS BASE.** Doce cuotas mensuales iguales del precio objetivo, más los incentivos ganados al cierre del contrato.",
        "**INCENTIVOS POR DESEMPEÑO.** Tasa de entrega ≥ 98 %: S/ 120.00 · Latencia de entrega al 95 % ≤ 60 segundos: S/ 80.00 · Disponibilidad ≥ 99.5 %: S/ 100.00 (medidos por reporte mensual).",
        "**AJUSTE DEL PRECIO FINAL.** Precio final = costo real del proveedor + (cuota objetivo ± reparto del ahorro o sobrecosto) + incentivos; nunca mayor al precio máximo.",
        "**GESTIÓN DE CAMBIOS.** Todo cambio de alcance se formaliza con una orden de cambio sin exceder el precio máximo.",
        "**GARANTÍA Y SOPORTE.** Soporte técnico de nivel 1 y 2 durante la vigencia del contrato.",
        "**CONFIDENCIALIDAD.** Los datos de los donantes no se utilizan para otro fin; la obligación se extiende por 5 años posteriores al término.",
        "**LEY APLICABLE.** Leyes de la República del Perú; jurisdicción de los tribunales de Cajamarca.",
    ])
    precio_obj, costo_obj, cuota, techo, prov = 2400.0, 2000.0, 400.0, 2700.0, 0.30
    bonos = 120.0 + 80.0 + 100.0
    ejemplos = []
    for etiqueta, costo_real, bono in (("Ahorro", 1900.0, bonos), ("Sobrecosto", 2200.0, 120.0), ("Sobrecosto alto", 2900.0, bonos)):
        diff = costo_obj - costo_real
        cuota_final = cuota + prov * diff
        precio = min(costo_real + cuota_final + bono, techo)
        ejemplos.append([etiqueta, f"{costo_real:,.2f}", f"{diff:+,.2f}", f"{cuota_final:,.2f}", f"{bono:,.2f}", f"{precio:,.2f}"])
    U.tabla(doc, ["Escenario", "Costo real (S/)", "Ahorro (+) / sobrecosto (−)", "Cuota final del proveedor (S/)", "Incentivos (S/)", "Precio final (S/)"], ejemplos,
            anchos=[3.2, 2.6, 3.2, 3.4, 2.2, 2.4], alinear=["l", "r", "r", "r", "r", "r"], tam=8.5, titulo="Ejemplos de cálculo del precio final (con tope en S/ 2,700.00)")
    U.firmas(doc, [("Director del Hospital / representante autorizado", "Comprador"), ("[Representante del proveedor]", "Proveedor")])

    U.h2(doc, "Anexo E. Glosario")
    U.tabla(doc, ["Término", "Significado"], [
        ["AC / EV / PV", "Costo real / Valor ganado / Valor planificado."],
        ["BAC / EAC / ETC / VAC", "Presupuesto al concluir / Estimado al concluir / Estimado hasta la conclusión / Variación al concluir."],
        ["CPI / SPI / TCPI", "Índices de desempeño del costo, del cronograma y del trabajo por completar."],
        ["CoQ", "Costo de la calidad: prevención, evaluación, fallas internas y fallas externas."],
        ["CPM", "Método de la ruta crítica."],
        ["EDT (WBS)", "Estructura de desglose del trabajo."],
        ["OBS / RACI", "Estructura de desglose de la organización / matriz de responsabilidades."],
        ["RLS", "Seguridad a nivel de filas en la base de datos: cada usuario ve solo lo que su rol permite."],
        ["VME", "Valor monetario esperado = probabilidad × impacto económico."],
        ["ARCO", "Derechos de acceso, rectificación, cancelación y oposición del titular de datos."],
        ["FFP / FPIF", "Contrato de precio fijo cerrado / de precio fijo más incentivos."],
        ["SOW", "Declaración del trabajo de una adquisición."],
    ], anchos=[4.0, 12.6], tam=9, primera_negrita=True)

    U.h2(doc, "Anexo F. Referencias")
    for ref in [
        "Project Management Institute. (2021). *A Guide to the Project Management Body of Knowledge (PMBOK® Guide)* (7th ed.). PMI.",
        "Project Management Institute. (2017). *Guía de los fundamentos para la dirección de proyectos (Guía del PMBOK®)* (6.ª ed.). PMI.",
        "Guido, J. y Clements, J. (2012). *Administración exitosa de proyectos* (5.ª ed.). Cengage Learning.",
        "ISO/IEC 25010:2011. *Systems and software engineering — SQuaRE — System and software quality models*. ISO.",
        "Crosby, P. B. (1979). *Quality Is Free: The Art of Making Quality Certain*. McGraw-Hill.",
        "Ishikawa, K. (1986). *Guide to Quality Control* (2nd ed.). Asian Productivity Organization.",
        "Congreso de la República del Perú. Ley N.° 29733, Ley de Protección de Datos Personales; y su reglamento aprobado por D.S. N.° 016-2024-JUS.",
        "Cacho Chávez, E. M. (2026). Sesiones de Gestión de Proyectos de Sistemas I, semanas 6, 7, 9, 10 y 11 (costos y EVM, calidad, recursos humanos, comunicaciones y riesgos). Universidad Nacional de Cajamarca.",
        "Cacho Chávez, E. M. (2026). *Gestión de las adquisiciones del proyecto* y *Gestión de riesgos del proyecto* (diapositivas); modelos de contrato FFP y FPIF. Universidad Nacional de Cajamarca.",
        "Zocón Alva, O. (2026). *Introducción a la dirección de proyectos* e *Inicio del proyecto* (material del curso). Universidad Nacional de Cajamarca.",
    ]:
        U.parrafo(doc, ref, tam=9.5, despues=3)


def construir(doc):
    pmbok7(doc)
    anexos(doc)
