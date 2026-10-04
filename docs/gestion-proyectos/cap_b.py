# -*- coding: utf-8 -*-
"""Parte II (1): requisitos, alcance, EDT y cronograma."""
import datos as D
import docx_utils as U
from fmt import f, s, n, pct

FIG = "fig/"

RF = [  # código, requisito, prioridad, OE, fuente, EDT, criterio de aceptación
    ("RF-01", "Registrar y mantener el padrón de donantes (datos personales, contacto, grupo sanguíneo opcional, estado).", "Alta", "OE-01", "Dra. Marimar; enfermería", "3.2",
     "DNI único de 8 dígitos; el grupo «No sé» es válido; el alta toma menos de 2 minutos."),
    ("RF-02", "Importar donantes desde Excel/CSV con validación fila por fila y reporte de errores.", "Media", "OE-01", "Enfermería", "3.3",
     "Solo se importan filas válidas; cada error indica la fila y el motivo en lenguaje claro."),
    ("RF-03", "Buscar por DNI o nombre y mostrar la ficha con el estado de aptitud.", "Alta", "OE-01, OE-02", "Enfermería", "3.2",
     "La búsqueda responde en menos de 2 s con 1 000 donantes; la ficha indica si puede donar hoy."),
    ("RF-04", "Calcular la aptitud (APTO, ESPERA, MÁXIMO, INACTIVO) según el intervalo y el máximo anual por sexo.", "Alta", "OE-02", "Médico responsable", "3.2, 3.4",
     "El resultado coincide con 100 % de los casos de prueba (hombre y mujer, año calendario)."),
    ("RF-05", "Registrar donaciones haciendo cumplir el máximo anual y permitiendo excepciones al intervalo solo con autorización del médico.", "Alta", "OE-02", "Médico responsable", "3.4",
     "La base de datos rechaza la donación que supera el máximo; la excepción queda anotada."),
    ("RF-06", "Gestionar resultados: pendiente → liberado → avisado; marca de crítico; solo el médico libera.", "Alta", "OE-05", "Jefatura; médico", "3.5",
     "Un resultado crítico no puede liberarse; solo quien tiene el permiso libera; queda el responsable."),
    ("RF-07", "Portal del donante con: ¿puedo donar?, resultado y recomendaciones, historial, campañas y dónde donar.", "Alta", "OE-04, OE-05", "Dra. Marimar; donantes", "3.9",
     "En una sola pantalla; el donante no ve resultados críticos ni datos de otros."),
    ("RF-08", "Consentimiento informado versionado, con historial y posibilidad de revocarlo.", "Alta", "OE-07", "Jefatura; Ley N.° 29733", "3.6",
     "Se guarda versión, fecha y quién lo registró; sin consentimiento no se envía ningún mensaje."),
    ("RF-09", "Enviar un correo individual a un donante que dio su consentimiento.", "Media", "OE-04", "Enfermería", "3.7",
     "El envío queda registrado con estado, responsable y error si falla."),
    ("RF-10", "Campañas dirigidas por grupo sanguíneo y aptitud, e información educativa publicada en el portal.", "Alta", "OE-04, OE-06", "Dra. Marimar", "3.7",
     "Vista previa de destinatarios antes de confirmar; nadie recibe dos veces la misma campaña."),
    ("RF-11", "Automatizaciones diarias: cumpleaños, recordatorio de retorno, agradecimiento y reconocimiento anual.", "Alta", "OE-02, OE-03", "Dra. Marimar", "3.8",
     "Se ejecutan a las 08:00, 08:15, 08:30 y 08:45 (hora de Lima) sin duplicados."),
    ("RF-12", "Plantillas de los mensajes automáticos que la Jefatura debe aprobar antes de su uso.", "Alta", "OE-03, OE-07", "Jefatura", "3.8, 3.10",
     "Sin aprobación no sale ningún automático; al editar un texto, vuelve a quedar sin aprobar."),
    ("RF-13", "Parámetros editables: intervalos, máximos anuales, recomendaciones y datos de contacto.", "Media", "OE-02", "Médico responsable", "3.10",
     "Los cambios se reflejan en pantalla y quedan en la bitácora."),
    ("RF-14", "Cuentas por puesto (enfermería, médico, administrador, donante): crear, restablecer contraseña, activar/desactivar, permiso de liberar.", "Alta", "OE-07", "OEI; Jefatura", "3.10",
     "Solo el administrador gestiona cuentas; siempre queda al menos un administrador activo."),
    ("RF-15", "Reportes e indicadores del proyecto con descarga en CSV.", "Media", "OE-05, OE-06", "Jefatura", "3.10",
     "Muestra donantes recurrentes, tiempo de entrega de resultados, O negativo con consentimiento y mensajes de 30 días."),
    ("RF-16", "Bitácora de auditoría automática (quién, qué y cuándo) sin guardar valores sensibles.", "Alta", "OE-07", "Ley N.° 29733", "3.1, 3.10",
     "Solo el administrador la consulta; registra los nombres de los campos modificados."),
    ("RF-17", "Derechos del titular: descarga de datos y anonimización a pedido, con confirmación.", "Alta", "OE-07", "Ley N.° 29733", "3.6",
     "El donante obtiene un archivo con sus datos; la anonimización requiere escribir el DNI y conserva las donaciones sin identificar a la persona."),
]

RNF = [
    ("RNF-01", "Disponibilidad", "≥ 99 % mensual, con un monitor externo recomendado (/health cada 5 minutos).", "Alta"),
    ("RNF-02", "Rendimiento", "Portal del donante visible en ≤ 3 s en una red 4G; listas del personal en ≤ 2 s con 1 000 registros.", "Alta"),
    ("RNF-03", "Usabilidad rural", "Una sola pantalla, letra grande, íconos y colores; funciona en Android de gama baja; 1 columna en celular y 2 en escritorio.", "Alta"),
    ("RNF-04", "Seguridad", "Seguridad por filas (RLS) en todas las tablas; claves privadas solo en el servidor; HTTPS; sin auto-registro.", "Alta"),
    ("RNF-05", "Privacidad", "Cumplimiento de la Ley N.° 29733: consentimiento expreso, minimización y mensajes sin datos médicos.", "Alta"),
    ("RNF-06", "Mantenibilidad", "Arquitectura modular, migraciones versionadas y documentación técnica (README) para la OEI.", "Media"),
    ("RNF-07", "Compatibilidad", "Chrome, Edge y Firefox recientes y Chrome para Android.", "Media"),
    ("RNF-08", "Costo de operación", "S/ 0 de infraestructura en el piloto (planes gratuitos); costo recurrente informado a la Dirección.", "Alta"),
    ("RNF-09", "Trazabilidad", "Toda acción relevante queda registrada con responsable y fecha.", "Media"),
]

RC = [
    ("RC-01", "Pruebas de cada flujo crítico con una sesión de cada rol (enfermería, médico, administrador y donante)."),
    ("RC-02", "0 resultados críticos legibles para el donante, verificado con una cuenta de donante."),
    ("RC-03", "Compilación sin errores de tipos antes de cada despliegue."),
    ("RC-04", "Piloto interno con 6 cuentas de donante y 3 perfiles de personal."),
    ("RC-05", "Manuales de usuario, ayuda integrada por puesto y documentación técnica entregados con el sistema."),
    ("RC-06", "Valoración de usabilidad ≥ 4.0 sobre 5 en la encuesta del piloto interno."),
]

REGLAS = [
    ("RN-01", "Máximo anual de donaciones de sangre total: 4 en hombres y 3 en mujeres (aplicado por la base de datos)."),
    ("RN-02", "Intervalo mínimo entre donaciones: 90 días (valor provisional por sexo, pendiente de validación clínica)."),
    ("RN-03", "Un resultado crítico nunca se muestra al donante ni se comunica por correo."),
    ("RN-04", "Solo el médico con permiso de liberar puede liberar resultados y quitar la marca de crítico."),
    ("RN-05", "Sin consentimiento vigente y correo registrado no se envía ningún mensaje (manual, campaña o automático)."),
    ("RN-06", "Los mensajes automáticos solo salen si la plantilla está aprobada por la Jefatura."),
    ("RN-07", "No se repite el mismo mensaje: cumpleaños y reconocimiento una vez al año; recordatorio y agradecimiento una vez por donación."),
    ("RN-08", "Los mensajes no contienen diagnóstico, reactividad ni resultados."),
]

CRITERIOS_ACT = {   # criterio de aceptación breve por actividad (diccionario de la EDT)
    "1.1": "Charter firmado por el sponsor con objetivos, alcance y presupuesto.",
    "1.2": "Quince interesados clasificados con estrategia de involucramiento.",
    "1.3": "Acta de kick-off con roles, reglas de trabajo y canales de comunicación.",
    "1.4": "Necesidades del Banco de Sangre priorizadas y firmadas en acta.",
    "1.5": "Reunión semanal registrada; informes semanales entregados al sponsor.",
    "2.1": "Entrevistas con Banco de Sangre documentadas; requisitos priorizados.",
    "2.2": "Documento de requisitos y alcance aprobado, con criterios de aceptación.",
    "2.3": "Prototipos de las pantallas principales de donante y personal.",
    "2.4": "Validación con al menos 3 personas del Banco de Sangre; ajustes registrados.",
    "2.5": "EDT, cronograma y presupuesto aprobados como línea base.",
    "2.6": "Cinco planes subsidiarios aprobados por el sponsor.",
    "2.7": "ERD y arquitectura revisados; modelo de seguridad definido.",
    "2.8": "Propuesta recibida por la Dirección General del HRDC.",
    "3.1": "Migraciones aplicadas; seguridad por filas activa en todas las tablas.",
    "3.2": "Alta, búsqueda y ficha con aptitud funcionando para enfermería.",
    "3.3": "Importación con reporte de errores por fila.",
    "3.4": "Máximo anual aplicado por la base; excepción de intervalo con autorización.",
    "3.5": "Liberación solo por médico; crítico oculto; aviso por correo.",
    "3.6": "Consentimiento con historial; descarga y anonimización de datos.",
    "3.7": "Correo con diseño institucional; campañas con vista previa.",
    "3.8": "Cuatro automatizaciones sin duplicados y con plantilla aprobada.",
    "3.9": "Portal de una pantalla utilizable en celular de gama baja.",
    "3.10": "Reportes, cuentas, parámetros y bitácora operativos.",
    "3.11": "Portal accesible en producción con variables de entorno protegidas.",
    "4.1": "Plan de pruebas aprobado con casos por rol.",
    "4.2": "Casos funcionales ejecutados; defectos registrados.",
    "4.3": "El donante no accede a críticos, plantillas ni bitácora.",
    "4.4": "Flujos de enfermería, médico, administrador y donante aprobados.",
    "4.5": "Defectos de severidad alta corregidos.",
    "4.6": "Manuales y ayuda integrada; README técnico completo.",
    "4.7": "Video de demostración y guion de capacitación.",
    "5.1": "Informe final con resultados frente a los objetivos y lecciones aprendidas.",
    "5.2": "Repositorio y documentación técnica entregados a la OEI y al sponsor.",
    "5.3": "Acta de cierre y de aceptación firmada por el PM y el sponsor.",
}


def _resp(a):
    h = a["horas"]
    k = max(h, key=lambda r: h[r])
    return D.EQUIPO[k]["corto"].split()[0] + " " + D.EQUIPO[k]["corto"].split()[1]


def requisitos(doc):
    U.h1(doc, "PARTE II · PLANIFICACIÓN")
    U.h1(doc, "4. Documentación de requisitos")
    U.h2(doc, "4.1 Necesidad del negocio y objetivos")
    U.parrafo(doc, "El Banco de Sangre del HRDC no cuenta con una herramienta propia para sostener la relación con el donante: cada donación es un hecho aislado, no se recuerda cuándo el donante puede volver, "
                   "la comunicación se hace desde celulares personales y los resultados tardan entre 48 horas y cinco días. HEMOCAX digitaliza ese vínculo sin tocar el sistema asistencial.", alineacion="justificado")
    U.h2(doc, "4.2 Requisitos funcionales")
    U.tabla(doc, ["Código", "Requisito", "Prioridad", "Objetivo", "Fuente", "EDT", "Criterio de aceptación"],
            [[a, b, c, d, e, g, h] for (a, b, c, d, e, g, h) in RF],
            anchos=[1.3, 5.0, 1.3, 1.5, 2.2, 1.0, 4.6], alinear=["c", "l", "c", "c", "l", "c", "l"], tam=7.5, titulo="Requisitos funcionales")
    U.h2(doc, "4.3 Requisitos no funcionales")
    U.tabla(doc, ["Código", "Atributo", "Descripción", "Prioridad"], [list(x) for x in RNF],
            anchos=[1.6, 2.8, 10.4, 1.8], alinear=["c", "l", "l", "c"], tam=8.5, titulo="Requisitos no funcionales")
    U.h2(doc, "4.4 Requisitos de calidad")
    U.tabla(doc, ["Código", "Requisito"], [list(x) for x in RC], anchos=[1.8, 14.8], alinear=["c", "l"], tam=9, titulo="Requisitos de calidad")
    U.h2(doc, "4.5 Requisitos legales y reglas del negocio")
    U.parrafo(doc, "Aplican la **Ley N.° 29733** (Protección de Datos Personales) y su reglamento, el **D.S. N.° 016-2024-JUS**, que clasifica los datos de salud como sensibles. "
                   "El hospital es el titular y responsable del tratamiento; el equipo ejecutor actúa como encargado y suscribirá acuerdos de confidencialidad.")
    U.tabla(doc, ["Código", "Regla del negocio"], [list(x) for x in REGLAS], anchos=[1.8, 14.8], alinear=["c", "l"], tam=9, titulo="Reglas del negocio")
    U.h2(doc, "4.6 Impacto en otras áreas y requerimientos de soporte")
    U.tabla(doc, ["Área / entidad", "Impacto"], [
        ["Banco de Sangre del HRDC", "Nuevo canal institucional y nuevas tareas de registro y liberación de resultados; requiere capacitación."],
        ["OEI del HRDC", "Recibe documentación técnica y de seguridad; no hay integración con sus sistemas."],
        ["Dirección General", "Debe decidir quién asume el costo recurrente después de la transferencia."],
        ["Escuela de Ingeniería de Sistemas (UNC)", "Proyecto académico con impacto real; fortalece el vínculo con el sector salud."],
        ["Donantes", "Menos fricción para saber cuándo donar y acceder a su resultado; control sobre sus avisos."],
    ], anchos=[5.0, 11.6], tam=9, titulo="Impacto en otras áreas")
    U.viñetas(doc, [
        "Sesión de capacitación al personal del Banco de Sangre (guion y video de demostración) y ayuda integrada por puesto en el propio sistema.",
        "Manual de usuario y manual técnico en PDF; repositorio de código documentado.",
        "Soporte posterior al cierre por un periodo acordado con la docente (garantía académica).",
    ])
    U.h2(doc, "4.7 Matriz de trazabilidad de requisitos")
    oe_nombres = {
        "OE-01": "Padrón digital", "OE-02": "Recordatorio de retorno", "OE-03": "Fidelización", "OE-04": "Campañas e información",
        "OE-05": "Resultados en 48 h", "OE-06": "Convocatoria dirigida", "OE-07": "Datos seguros",
    }
    pruebas = {"RF-01": "PF-01", "RF-02": "PF-02", "RF-03": "PF-01", "RF-04": "PF-03", "RF-05": "PF-04", "RF-06": "PF-05, PS-02", "RF-07": "PF-06, PS-02",
               "RF-08": "PF-07", "RF-09": "PF-08", "RF-10": "PF-09", "RF-11": "PF-10", "RF-12": "PF-10", "RF-13": "PF-11", "RF-14": "PS-03", "RF-15": "PF-12",
               "RF-16": "PS-04", "RF-17": "PS-05"}
    def _clave(x):
        return [int(p) for p in x.split(".")]
    filas = []
    for oe, nom in oe_nombres.items():
        rfs = [r for r in RF if oe in r[3]]
        edts = sorted({e.strip() for r in rfs for e in r[5].split(",")}, key=_clave)
        prs = sorted({x.strip() for r in rfs for x in pruebas[r[0]].split(",")})
        filas.append([f"**{oe}** {nom}", ", ".join(r[0] for r in rfs), ", ".join(edts), ", ".join(prs)])
    U.tabla(doc, ["Objetivo específico", "Requisitos funcionales", "Actividades de la EDT", "Pruebas (capítulo 9)"], filas,
            anchos=[4.4, 4.6, 3.6, 4.0], tam=8.5, titulo="Trazabilidad: objetivo → requisito → EDT → prueba")
    U.salto_pagina(doc)


def alcance(doc):
    U.h1(doc, "5. Definición del alcance (Scope Statement)")
    U.h2(doc, "5.1 Descripción del alcance del producto")
    U.parrafo(doc, "HEMOCAX es una plataforma web responsive con base de datos propia, desplegada en la nube, con dos interfaces y un reloj de recordatorios:", alineacion="justificado")
    U.tabla(doc, ["Módulo", "Características principales"], [
        ["1. Padrón de donantes", "Registro, búsqueda y ficha; importación desde Excel/CSV; grupo sanguíneo opcional; baja voluntaria."],
        ["2. Donaciones y aptitud", "Registro con máximo anual impuesto por la base de datos; intervalo con excepción autorizada; cuatro estados de aptitud."],
        ["3. Resultados", "Pendiente → liberado → avisado; marca de crítico; solo el médico libera; alertas a las 36 y 48 horas."],
        ["4. Consentimiento y derechos del titular", "Consentimiento versionado con historial; descarga de datos; anonimización a pedido."],
        ["5. Comunicación por correo", "Correo individual, campañas dirigidas por grupo sanguíneo y aptitud, información educativa; diseño institucional."],
        ["6. Automatizaciones", "Cumpleaños, recordatorio de retorno, agradecimiento y reconocimiento anual; plantillas aprobadas; sin duplicados."],
        ["7. Portal del donante", "Una pantalla: ¿puedo donar?, resultado y recomendaciones, historial, campañas, dónde donar y avisos."],
        ["8. Panel del personal", "Inicio con buscador, reportes con descarga CSV, cuentas por puesto, parámetros, bitácora y ayuda por puesto."],
    ], anchos=[4.6, 12.0], tam=9, primera_negrita=True, titulo="Módulos del producto")
    U.figura(doc, FIG + "arquitectura.png", 16.0, "Contexto y arquitectura del producto")
    U.figura(doc, FIG + "flujo_resultados.png", 9.0, "Flujo del resultado de una donación (los críticos nunca se muestran ni se envían)")
    U.h2(doc, "5.2 Criterios de aceptación del producto")
    U.tabla(doc, ["Tipo", "Criterio de aceptación"], [
        ["Técnicos", "Sistema desplegado en la nube con los 8 módulos operativos y accesible desde computadora y celular."],
        ["De calidad", "Métricas ISO/IEC 25010 del plan de calidad cumplidas; 0 resultados críticos visibles para el donante; seguridad por filas en el 100 % de las tablas."],
        ["Administrativos", "Documentación de gestión completa; EDT y cronograma ejecutados; actas de inicio y cierre firmadas."],
        ["Sociales", "Piloto interno aprobado con cuentas de cada rol; ayuda y manuales entregados al Banco de Sangre."],
        ["Comerciales", "No aplica (proyecto sin fines de lucro, de proyección universitaria)."],
    ], anchos=[3.4, 13.2], tam=9, primera_negrita=True, titulo="Criterios de aceptación")
    U.h2(doc, "5.3 Exclusiones del proyecto")
    U.tabla(doc, ["N.°", "Exclusión"], [
        ["1", "No reemplaza ni modifica el sistema informático actual del Banco de Sangre; el acceso, como máximo, sería de solo lectura."],
        ["2", "No comunica resultados críticos por canal digital: continúan por llamada telefónica y consulta presencial."],
        ["3", "No interviene en procesos asistenciales (solicitud transfusional, toma de muestra, compatibilidad, entrega de hemocomponentes)."],
        ["4", "No trata datos de pacientes receptores ni información de historia clínica."],
        ["5", "No realiza migración masiva ni altera los registros históricos del hospital."],
        ["6", "No incluye mensajería por SMS ni WhatsApp en esta etapa; el único canal es el correo electrónico."],
        ["7", "No incluye la programación de campañas a una fecha futura ni una aplicación móvil nativa."],
    ], anchos=[1.4, 15.2], alinear=["c", "l"], tam=9, titulo="Exclusiones")
    U.h2(doc, "5.4 Restricciones")
    U.tabla(doc, ["Internas a la organización", "Ambientales / externas"], [
        [f"Plazo máximo: {f(D.FIN_PLAN)} (calendario académico).", "Disponibilidad del Banco de Sangre para sesiones de validación."],
        ["Presupuesto externo S/ 0: solo recursos propios y herramientas gratuitas.", "Límites de los planes gratuitos (correo, base de datos, reloj)."],
        ["Equipo de 6 estudiantes con carga académica simultánea.", "Conectividad limitada en zonas rurales de Cajamarca."],
        ["No se puede subcontratar desarrollo ni contratar personal.", "Ley N.° 29733 y su reglamento sobre datos de salud."],
        ["La documentación debe seguir el formato PMI del curso.", "Valores clínicos pendientes de validación por el médico."],
    ], anchos=[8.3, 8.3], tam=9, titulo="Restricciones del proyecto")
    U.h2(doc, "5.5 Supuestos")
    U.tabla(doc, ["Internos", "Externos"], [
        ["Cada integrante dedica ≈ 14 horas semanales.", "El Banco de Sangre participa en las sesiones de levantamiento y validación."],
        ["Las herramientas gratuitas estarán disponibles y estables.", "La Jefatura aprobará los textos automáticos antes de producción."],
        ["La docente revisa los avances semanalmente.", "Los donantes aportarán datos veraces y darán su consentimiento libre."],
        ["El equipo domina las tecnologías web y de base de datos.", "No habrá cambios normativos que invaliden el alcance."],
    ], anchos=[8.3, 8.3], tam=9, titulo="Supuestos del proyecto")
    U.salto_pagina(doc)


def edt(doc):
    U.h1(doc, "6. Estructura de desglose del trabajo (EDT)")
    U.parrafo(doc, f"La EDT descompone el proyecto en cinco fases y {len(D._A)} actividades (nivel 3). Cada actividad es un paquete de trabajo con un responsable, un esfuerzo estimado y un criterio de aceptación.")
    U.seccion(doc, horizontal=True)
    U.figura(doc, FIG + "edt.png", 25.0, "Estructura de desglose del trabajo (EDT) de HEMOCAX")
    U.seccion(doc, horizontal=False)
    U.h2(doc, "6.1 Diccionario de la EDT")
    U.seccion(doc, horizontal=True)
    filas = []
    for fase, nombre in D.FASES.items():
        filas.append([f"**{fase}.0**", f"**{fase}.0 {nombre.upper()}**", "", "", "", ""])
        for a in D._A:
            if a["fase"] == fase:
                filas.append([a["id"], a["nombre"], a["entregable"], CRITERIOS_ACT[a["id"]], _resp(a), str(a["h"])])
    resaltar = {i: "DDE8F4" for i, fila in enumerate(filas) if fila[2] == "" and fila[0].startswith("**")}
    U.tabla(doc, ["Código", "Paquete de trabajo", "Entregable", "Criterio de aceptación", "Responsable principal", "Horas"], filas,
            anchos=[1.3, 8.0, 5.3, 7.6, 3.2, 1.2], alinear=["c", "l", "l", "l", "l", "c"], tam=8, zebra=False, resaltar=resaltar, titulo="Diccionario de la EDT (nivel 3)")
    U.seccion(doc, horizontal=False)
    U.parrafo(doc, f"Esfuerzo total: **{D.HORAS_TOTALES} horas-persona**. Distribución por fase: " +
              ", ".join(f"{D.FASES[k]} {sum(a['h'] for a in D._A if a['fase'] == k)} h" for k in D.FASES) + ".")
    U.salto_pagina(doc)


def cronograma(doc):
    U.h1(doc, "7. Cronograma del proyecto")
    U.h2(doc, "7.1 Calendario y método")
    U.parrafo(doc, f"El proyecto se planificó para **{D.SEMANAS_PROY:.1f} semanas** (del {f(D.INICIO)} al {f(D.FIN_PLAN)}), con jornada de lunes a viernes y excluyendo los feriados del 28 y 29 de julio. "
                   "Las duraciones se estimaron en días laborables y las fechas se calcularon con el **método de la ruta crítica (CPM)** a partir de las precedencias de fin a inicio. "
                   "La actividad 1.5 (dirección y seguimiento) es de esfuerzo continuo y abarca todo el proyecto.", alineacion="justificado")
    U.h2(doc, "7.2 Lista de actividades, precedencias y ruta crítica")
    U.seccion(doc, horizontal=True)
    filas = []
    for a in D._A:
        d = "continua" if a["dur"] == 0 else str(a["dur"])
        hol = "—" if a["dur"] == 0 else str(a["holgura"])
        filas.append([a["id"], a["nombre"], d, f(a["ini"]), f(a["fin"]), ", ".join(a["preds"]) or "—", hol, "Sí" if a.get("critica") else "", _resp(a)])
    res = {i: "FADBD8" for i, a in enumerate(D._A) if a.get("critica")}
    U.tabla(doc, ["ID", "Actividad", "Dur. (d)", "Inicio", "Fin", "Predecesoras", "Holgura (d)", "Crítica", "Responsable"], filas,
            anchos=[1.1, 9.2, 1.4, 2.2, 2.2, 2.6, 1.6, 1.4, 3.6], alinear=["c", "l", "c", "c", "c", "c", "c", "c", "l"], tam=8, zebra=False, resaltar=res,
            titulo="Cronograma de actividades (rojo = ruta crítica)")
    U.figura(doc, FIG + "gantt.png", 17.5, "Diagrama de Gantt con la ruta crítica y la ejecución real")
    U.seccion(doc, horizontal=False)
    crit = [a["id"] for a in D._A if a.get("critica")]
    U.h2(doc, "7.3 Ruta crítica")
    U.parrafo(doc, "La ruta crítica está formada por: **" + " → ".join(crit) + "**. Cualquier retraso en estas actividades retrasa el cierre del proyecto. "
                   "Las demás actividades tienen holgura (columna «Holgura») y se utilizaron para balancear la carga del equipo.", alineacion="justificado")
    U.h2(doc, "7.4 Estimación por tres puntos (PERT) de actividades inciertas")
    pert = [("3.1", 5, 6, 9), ("3.7", 6, 8, 12), ("3.9", 5, 7, 10), ("3.11", 1, 2, 4), ("4.2", 6, 8, 12)]
    filas = []
    for i, o, m, p in pert:
        e = (o + 4 * m + p) / 6
        sd = (p - o) / 6
        filas.append([i, D.ACT[i]["nombre"], str(o), str(m), str(p), f"{e:.1f}", f"{sd:.2f}"])
    U.tabla(doc, ["ID", "Actividad", "O", "M", "P", "E = (O+4M+P)/6", "σ = (P−O)/6"], filas,
            anchos=[1.1, 9.2, 1.0, 1.0, 1.0, 2.6, 2.2], alinear=["c", "l", "c", "c", "c", "c", "c"], tam=8.5,
            titulo="Estimación PERT en días laborables (O optimista, M más probable, P pesimista)")
    U.parrafo(doc, "La duración planificada de cada actividad coincide con la estimación más probable (M); la diferencia con E se absorbe en la holgura o en la reserva de gestión del cronograma.", tam=9.5)
    U.h2(doc, "7.5 Ejecución real frente a la línea base")
    filas = []
    from datetime import timedelta
    for a in D._A:
        if a["dur"] == 0:
            continue
        var = len(D.dias_laborables(a["fin"] + timedelta(days=1), a["fin_real"])) if a["fin_real"] > a["fin"] else 0
        filas.append([a["id"], a["nombre"][:62], f(a["fin"]), f(a["fin_real"]), f"+{var}" if var else "0"])
    U.tabla(doc, ["ID", "Actividad", "Fin planificado", "Fin real / proyectado", "Variación (d)"], filas,
            anchos=[1.1, 9.4, 2.4, 2.8, 2.0], alinear=["c", "l", "c", "c", "c"], tam=8, titulo="Comparación de fechas de fin (línea base vs. ejecución)")
    U.parrafo(doc, "Las desviaciones se concentraron en la base de datos (3.1, por las iteraciones de seguridad), el correo (3.7, por el cambio de dónde se envía) y el portal del donante (3.9). "
                   "El PM recuperó el plazo con horas adicionales de integración, lo que explica el sobrecosto descrito en el capítulo 8.", tam=9.5)
    U.salto_pagina(doc)


def construir(doc):
    requisitos(doc)
    alcance(doc)
    edt(doc)
    cronograma(doc)
