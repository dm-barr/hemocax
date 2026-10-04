# -*- coding: utf-8 -*-
"""
Modelo único de datos del proyecto HEMOCAX para el informe de Gestión de Proyectos.

Todo lo que aparece en el informe (cronograma, presupuesto, curva S, EVM, CoQ, riesgos, RACI, etc.)
se calcula desde este archivo, de modo que las cifras sean siempre coherentes entre sí.
Para cambiar un dato (horas reales, fechas, costos) edita aquí y vuelve a ejecutar `python informe.py`.

Los valores marcados como SUPUESTO son estimaciones del equipo para el ejercicio académico y deben
reemplazarse por los registros reales (hoja de horas, comprobantes) si el docente los solicita.
"""
from __future__ import annotations
from datetime import date, timedelta

# ----------------------------------------------------------------------------------------------
# 1. Identificación
# ----------------------------------------------------------------------------------------------
PROYECTO = "HEMOCAX"
TITULO = ("Implementación de la plataforma digital HEMOCAX para la fidelización y retención del donante "
          "voluntario de sangre en el Hospital Regional Docente de Cajamarca — 2026")
CURSO = "Gestión de Proyectos de Sistemas I"
CICLO = "2026-I"
UNIVERSIDAD = "Universidad Nacional de Cajamarca"
FACULTAD = "Facultad de Ingeniería"
ESCUELA = "Escuela Académico Profesional de Ingeniería de Sistemas"
DOCENTE = "Ing. Ena Mirella Cacho Chávez"
CLIENTE = "Hospital Regional Docente de Cajamarca (HRDC) — Servicio de Hemoterapia y Banco de Sangre"
FECHA_INFORME = "octubre de 2026"
CORTE = date(2026, 10, 4)           # fecha de corte de los datos de seguimiento (domingo, fin de la semana 11)
INICIO = date(2026, 7, 21)          # firma del Project Charter
FIN_PLAN = None                     # se calcula con el CPM (firma del acta de cierre)
TARIFA = 8.00                       # S/ por hora-persona imputada (tarifa referencial del curso)

# Personas / roles del equipo ---------------------------------------------------------------
EQUIPO = {
    "PM":  dict(nombre="Diana Michelle Barrantes Gallardo",  corto="Diana Barrantes G.",  rol="Project Manager"),
    "LT":  dict(nombre="Jesús Arturo Valdiviezo Zavaleta",    corto="Jesús Valdiviezo Z.", rol="Líder Técnico y Desarrollador de base de datos"),
    "FE":  dict(nombre="Scarlet Sahori Terrones Cerna",       corto="Scarlet Terrones C.", rol="Desarrolladora Frontend"),
    "INT": dict(nombre="Darick André Pérez Briceño",          corto="Darick Pérez B.",     rol="Desarrollador de Integraciones y Automatizaciones"),
    "QA":  dict(nombre="Dider Anthony Díaz Becerra",          corto="Dider Díaz B.",       rol="Especialista QA y Seguridad de datos"),
    "AF":  dict(nombre="Adriana Anthonela Limay Rodríguez",   corto="Adriana Limay R.",    rol="Analista Funcional y UX"),
}
ORDEN_ROLES = ["PM", "LT", "AF", "FE", "INT", "QA"]

# ----------------------------------------------------------------------------------------------
# 2. Calendario laboral
# ----------------------------------------------------------------------------------------------
FERIADOS = {date(2026, 7, 28), date(2026, 7, 29)}   # Fiestas Patrias
SEMANA1 = date(2026, 7, 20)                          # lunes de la semana 1
N_SEMANAS = 12


def es_laborable(d: date) -> bool:
    return d.weekday() < 5 and d not in FERIADOS


def sig_laborable(d: date) -> date:
    d += timedelta(days=1)
    while not es_laborable(d):
        d += timedelta(days=1)
    return d


def sumar_laborables(inicio: date, n: int) -> date:
    """Devuelve la fecha del día laborable número n (n>=1) contando `inicio` como el día 1."""
    d = inicio
    while not es_laborable(d):
        d += timedelta(days=1)
    for _ in range(n - 1):
        d = sig_laborable(d)
    return d


def dias_laborables(desde: date, hasta: date) -> list[date]:
    out, d = [], desde
    while d <= hasta:
        if es_laborable(d):
            out.append(d)
        d += timedelta(days=1)
    return out


def semana_de(d: date) -> int:
    return (d - SEMANA1).days // 7 + 1


def rango_semana(s: int) -> tuple[date, date]:
    ini = SEMANA1 + timedelta(days=7 * (s - 1))
    return ini, ini + timedelta(days=6)


# ----------------------------------------------------------------------------------------------
# 3. Actividades (EDT nivel 3): horas por rol, duración, precedencias
# ----------------------------------------------------------------------------------------------
# id, nombre, fase, duración (días laborables), snet (inicio no antes de), predecesoras, horas por rol,
# entregable. Datos de seguimiento: (desfase de inicio en días laborables, factor de duración, factor de costo)
FASES = {
    "1": "Inicio",
    "2": "Planificación y diseño",
    "3": "Desarrollo",
    "4": "Pruebas, piloto y capacitación",
    "5": "Cierre",
}

_A = []   # se completa abajo


def _act(i, nombre, dur, snet, preds, horas, entregable, seg=(0, 1.0, 1.0)):
    _A.append(dict(id=i, nombre=nombre, fase=i.split(".")[0], dur=dur, snet=snet, preds=preds,
                   horas=horas, entregable=entregable, seg=seg,
                   h=sum(horas.values())))


d = date
_act("1.1", "Redacción y aprobación del Project Charter", 4, d(2026, 7, 21), [],
     dict(PM=8, AF=2), "Project Charter firmado")
_act("1.2", "Registro y análisis de stakeholders", 4, d(2026, 7, 22), [],
     dict(PM=4, AF=8), "Registro de stakeholders y estrategia de involucramiento")
_act("1.3", "Reunión de inicio (kick-off) con equipo y sponsor", 1, d(2026, 7, 22), [],
     dict(PM=3, LT=1, AF=1, FE=1, INT=1, QA=1), "Acta de kick-off")
_act("1.4", "Reunión inicial con la Jefatura del Banco de Sangre (levantamiento)", 3, d(2026, 7, 22), ["1.1", "1.3"],
     dict(PM=8, AF=8), "Acta de levantamiento y necesidades priorizadas")
_act("1.5", "Dirección y seguimiento del proyecto (reuniones semanales, informes, control de cambios)", 0, d(2026, 7, 21), [],
     dict(PM=40, LT=4, AF=4, FE=4, INT=4, QA=4), "Actas semanales, informes de avance y registro de cambios")
_act("2.1", "Entrevistas y talleres de requisitos con el Banco de Sangre", 5, d(2026, 7, 22), ["1.4"],
     dict(AF=16, PM=4, LT=4), "Notas de entrevistas y lista de requisitos", seg=(0, 1.3, 1.10))
_act("2.2", "Documentación de requisitos y Scope Statement", 5, d(2026, 7, 22), ["2.1"],
     dict(AF=20, PM=4), "Documento de requisitos y definición del alcance", seg=(1, 1.2, 1.05))
_act("2.3", "Wireframes y prototipos de alta fidelidad (Figma)", 6, d(2026, 7, 22), ["2.1"],
     dict(AF=14, FE=20), "Prototipos validables", seg=(0, 1.1, 1.0))
_act("2.4", "Validación de prototipos con el personal del Banco de Sangre", 3, d(2026, 7, 22), ["2.3"],
     dict(AF=8, FE=2, PM=2), "Informe de validación de usabilidad", seg=(1, 1.0, 1.0))
_act("2.5", "EDT, cronograma y línea base de costos", 4, d(2026, 7, 22), ["2.2"],
     dict(PM=16, LT=4), "EDT, cronograma y presupuesto aprobados")
_act("2.6", "Planes de calidad, riesgos, RR.HH., comunicaciones y adquisiciones", 6, d(2026, 7, 22), ["2.5"],
     dict(PM=10, QA=6, AF=4, LT=3, INT=3), "Planes subsidiarios aprobados", seg=(0, 1.0, 0.95))
_act("2.7", "Diseño de arquitectura y modelo de datos (ERD, seguridad)", 6, d(2026, 7, 22), ["2.1"],
     dict(LT=20, INT=8, QA=6, FE=6), "Documento de arquitectura y ERD")
_act("2.8", "Propuesta formal al HRDC (documento de aprobación)", 6, d(2026, 8, 24), ["2.5"],
     dict(PM=10, AF=6, LT=4), "Propuesta entregada a la Dirección General", seg=(2, 1.0, 1.0))
_act("3.1", "Esquema de base de datos, seguridad (RLS), triggers y funciones", 6, d(2026, 7, 22), ["2.7"],
     dict(LT=26, QA=10, INT=10), "Migraciones SQL aplicadas", seg=(1, 1.2, 1.15))
_act("3.2", "Padrón de donantes y ficha (registro, búsqueda, aptitud)", 10, d(2026, 7, 22), ["3.1"],
     dict(FE=24, LT=8, QA=6, INT=7, AF=3), "Módulo de donantes", seg=(1, 1.1, 1.0))
_act("3.3", "Importación masiva desde Excel/CSV", 4, d(2026, 7, 22), ["3.2"],
     dict(FE=12, QA=6), "Importador con validación por fila", seg=(1, 1.0, 1.25))
_act("3.4", "Registro de donaciones y reglas (máximo anual, intervalo)", 7, d(2026, 7, 22), ["3.1"],
     dict(LT=16, QA=8, INT=10), "Módulo de donaciones con reglas en la base", seg=(1, 1.0, 1.05))
_act("3.5", "Resultados: liberación, marca de crítico y aviso", 7, d(2026, 7, 22), ["3.4"],
     dict(LT=14, FE=14, QA=6, PM=4), "Módulo de resultados", seg=(1, 1.0, 1.0))
_act("3.6", "Consentimiento versionado y derechos del titular (ARCO)", 5, d(2026, 7, 22), ["3.4"],
     dict(LT=14, AF=6, QA=6, PM=4), "Consentimiento, historial y anonimización", seg=(1, 1.0, 1.0))
_act("3.7", "Correo institucional, plantillas y campañas", 10, d(2026, 7, 22), ["3.1"],
     dict(INT=32, LT=4, AF=6, QA=4), "Envío de correo y campañas dirigidas", seg=(1, 1.25, 1.30))
_act("3.8", "Automatizaciones diarias (cumpleaños, recordatorio, gracias, reconocimiento)", 8, d(2026, 7, 22), ["3.7"],
     dict(INT=26, LT=6), "Reloj de recordatorios y rutas automáticas", seg=(2, 1.0, 1.10))
_act("3.9", "Portal del donante (diseño para zonas rurales)", 9, d(2026, 7, 22), ["3.2"],
     dict(FE=32, AF=10, QA=4, PM=2), "Portal del donante", seg=(1, 1.2, 1.10))
_act("3.10", "Panel del personal: reportes, cuentas, parámetros y auditoría", 8, d(2026, 7, 22), ["3.6", "3.5"],
     dict(FE=22, LT=12, QA=6, PM=2, AF=4), "Panel de reportes y administración", seg=(2, 1.0, 1.05))
_act("3.11", "Despliegue en producción (Vercel, Supabase, Render)", 2, d(2026, 7, 22), ["3.8", "3.9", "3.10"],
     dict(INT=20, LT=6, QA=4), "Sistema en producción", seg=(0, 1.0, 1.20))
_act("4.1", "Plan de pruebas", 3, d(2026, 9, 1), ["2.6"],
     dict(QA=10, AF=2), "Plan de pruebas aprobado")
_act("4.2", "Pruebas funcionales y de integración", 8, d(2026, 7, 22), ["3.5", "4.1"],
     dict(QA=22, FE=4, LT=2, INT=2, PM=2), "Informe de pruebas funcionales", seg=(1, 1.1, 1.0))
_act("4.3", "Pruebas de seguridad de datos (permisos por rol)", 5, d(2026, 7, 22), ["3.6", "4.1"],
     dict(QA=16, LT=8), "Informe de pruebas de seguridad", seg=(1, 1.0, 1.0))
_act("4.4", "Piloto interno con cuentas de cada rol", 2, d(2026, 7, 22), ["3.11"],
     dict(QA=8, AF=8, PM=4, FE=2, INT=2), "Informe del piloto interno", seg=(0, 1.0, 1.0))
_act("4.5", "Correcciones posteriores a las pruebas", 5, d(2026, 7, 22), ["4.3"],
     dict(LT=6, FE=6, INT=8, QA=6), "Defectos corregidos", seg=(1, 1.3, 1.1))
_act("4.6", "Manuales, ayuda integrada y documentación técnica", 8, d(2026, 7, 22), ["3.5"],
     dict(AF=16, LT=4, FE=2, QA=4, PM=2), "Manuales de usuario y README técnico", seg=(0, 1.1, 1.0))
_act("4.7", "Capacitación: guion y video de demostración", 2, d(2026, 7, 22), ["3.11"],
     dict(AF=8, PM=4, INT=4), "Video y guion de capacitación", seg=(0, 1.0, 1.0))
_act("5.1", "Informe final y lecciones aprendidas", 2, d(2026, 7, 22), ["4.4", "4.6", "4.7"],
     dict(PM=14, AF=4, LT=1, QA=1), "Informe final del proyecto")
_act("5.2", "Entrega de repositorio y documentación técnica", 1, d(2026, 7, 22), ["4.6"],
     dict(LT=8, INT=2, QA=2), "Repositorio y documentación entregados")
_act("5.3", "Acta de cierre y de aceptación", 1, d(2026, 7, 22), ["5.1", "5.2"],
     dict(PM=6, AF=2), "Acta de cierre firmada")
ACT = {a["id"]: a for a in _A}
ORDEN = [a["id"] for a in _A]


def _calcular_cronograma():
    """CPM sobre días laborables: fechas tempranas, tardías, holgura y ruta crítica."""
    for a in _A:   # pasada hacia adelante (el orden de la lista respeta las precedencias)
        if a["dur"] == 0:
            continue
        ini = a["snet"]
        for p in a["preds"]:
            ini = max(ini, sig_laborable(ACT[p]["fin"]))
        a["ini"] = ini if es_laborable(ini) else sig_laborable(ini)
        a["fin"] = sumar_laborables(a["ini"], a["dur"])
    fin_proy = max(a["fin"] for a in _A if a["dur"] > 0)
    for a in _A:   # esfuerzo continuo: abarca todo el proyecto
        if a["dur"] == 0:
            a.update(ini=INICIO, fin=fin_proy, ini_tarde=INICIO, fin_tarde=fin_proy, holgura=0, critica=False, continua=True)
    sucesores = {a["id"]: [b["id"] for b in _A if a["id"] in b["preds"]] for a in _A}
    for a in reversed(_A):   # pasada hacia atrás
        if a["dur"] == 0:
            continue
        if not sucesores[a["id"]]:
            a["fin_tarde"] = fin_proy
        else:
            a["fin_tarde"] = min(_retroceder(ACT[s]["ini_tarde"]) for s in sucesores[a["id"]])
        a["ini_tarde"] = _retroceder_n(a["fin_tarde"], a["dur"])
        a["holgura"] = len([x for x in dias_laborables(a["fin"], a["fin_tarde"])]) - 1 if a["fin_tarde"] >= a["fin"] else 0
        a["critica"] = a["holgura"] <= 0
    return fin_proy


def _retroceder(dia: date) -> date:
    dia -= timedelta(days=1)
    while not es_laborable(dia):
        dia -= timedelta(days=1)
    return dia


def _retroceder_n(fin: date, n: int) -> date:
    dia = fin
    for _ in range(n - 1):
        dia = _retroceder(dia)
    return dia


FIN_REAL_PLAN = _calcular_cronograma()
FIN_PLAN = FIN_REAL_PLAN
HORAS_TOTALES = sum(a["h"] for a in _A)

# Horas por persona -------------------------------------------------------------------------
HORAS_ROL = {r: sum(a["horas"].get(r, 0) for a in _A) for r in ORDEN_ROLES}
SEMANAS_PROY = (FIN_REAL_PLAN - INICIO).days / 7

# ----------------------------------------------------------------------------------------------
# 4. Gastos directos (desembolso real en efectivo) y presupuesto
# ----------------------------------------------------------------------------------------------
GASTOS = [  # descripción, cantidad, unitario, fase, semana, justificación
    ("Materiales de oficina (papel, lapiceros, folder, archivador)", "1 global", 50.00, "2", 1, "Documentación y reuniones de coordinación"),
    ("Transporte al Hospital Regional (6 visitas × S/ 10.00)", "6 visitas", 60.00, "1-5", None, "Reunión inicial, entrevistas, validación, propuesta, piloto y cierre"),
    ("Impresión y encuadernación de manuales de usuario y técnico (3 juegos)", "3 juegos", 80.00, "4", 12, "Entrega física al Banco de Sangre, a la OEI y a la docente"),
    ("Impresión de documentación de gestión para la docente (2 ejemplares)", "2 ejemplares", 30.00, "5", 12, "Entrega física del informe final"),
    ("Refrigerios en sesiones con el Banco de Sangre (4 sesiones × S/ 10.00)", "4 sesiones", 40.00, "2-4", None, "Talleres de requisitos, validación, piloto y cierre"),
]
GASTOS_TOTAL = sum(g[2] for g in GASTOS)                       # 260.00
# semanas en que se desembolsa el efectivo (PV de efectivo)
EFECTIVO_SEM = {1: 50.0, 2: 10.0, 3: 20.0, 4: 20.0, 6: 10.0, 11: 20.0, 12: 130.0}
assert abs(sum(EFECTIVO_SEM.values()) - GASTOS_TOTAL) < 1e-9, sum(EFECTIVO_SEM.values())

COSTO_RRHH = HORAS_TOTALES * TARIFA
BAC = COSTO_RRHH + GASTOS_TOTAL                                # costo base (línea base sin reservas)


# ----------------------------------------------------------------------------------------------
# 5. Riesgos
# ----------------------------------------------------------------------------------------------
PROB_VME = {1: 0.10, 2: 0.30, 3: 0.50, 4: 0.70, 5: 0.90}       # equivalencia de la escala 1-5 (clase de Gestión de Riesgos)
RIESGOS = [
    dict(id="R01", tipo="Amenaza", cat="Personas", desc="Indisponibilidad de un integrante clave por carga académica concurrente (exámenes y trabajos de otros cursos).",
         causa="Seis estudiantes con otros cursos en paralelo.", p=4, i=4, imp=320.0, dueno="PM", est="Mitigar",
         acc="Calendario académico del equipo al inicio; tareas críticas con un suplente asignado; documentación de cada módulo para transferencia.",
         trig="Una tarea asignada sin avance durante 3 días hábiles.", cont="Reasignar la tarea en 48 horas y renegociar horas con el PM.", costo=40.0, res=(2, 3)),
    dict(id="R02", tipo="Amenaza", cat="Alcance", desc="Cambios en los requisitos del Banco de Sangre después de validar los prototipos (canal, textos, reglas).",
         causa="Requisitos validados de forma verbal o sin criterios de aceptación firmados.", p=4, i=3, imp=256.0, dueno="AF", est="Mitigar",
         acc="Aprobación formal del alcance; congelar requisitos funcionales tras la validación; todo cambio pasa por control de cambios.",
         trig="Solicitud de cambio con impacto mayor a 1 día.", cont="Evaluar impacto en triple restricción y decidir según nivel (PM o Sponsor).", costo=24.0, res=(2, 3)),
    dict(id="R03", tipo="Amenaza", cat="Interesados", desc="Baja disponibilidad de la Jefatura o del médico para validar valores clínicos y textos (intervalo, recomendaciones, consentimiento).",
         causa="Alta carga asistencial del personal de salud.", p=3, i=4, imp=160.0, dueno="PM", est="Mitigar",
         acc="Valores clínicos como parámetros editables; reuniones calendarizadas; textos marcados como provisionales hasta su aprobación.",
         trig="Más de 10 días sin respuesta a una solicitud de validación.", cont="Entregar con valores provisionales y registrar la aprobación pendiente como supuesto.", costo=16.0, res=(2, 3)),
    dict(id="R04", tipo="Amenaza", cat="Técnico", desc="Los límites de los planes gratuitos (correo ≈ 500 envíos/día, base de datos 500 MB, reloj que se duerme tras 15 min) interrumpen el servicio.",
         causa="El proyecto no tiene presupuesto de infraestructura.", p=4, i=3, imp=240.0, dueno="LT", est="Mitigar",
         acc="Monitoreo externo del servicio (/health cada 5 min); registro de consumo; plan de ampliación documentado para el hospital.",
         trig="Consumo mayor al 70 % del límite o interrupciones repetidas.", cont="Migrar al plan de pago correspondiente; costo recurrente informado a la Dirección.", costo=32.0, res=(3, 2)),
    dict(id="R05", tipo="Amenaza", cat="Técnico", desc="El proveedor de alojamiento bloquea puertos de correo (SMTP) en el plan gratuito y el envío de correos falla.",
         causa="Política anti-spam de los planes gratuitos de alojamiento.", p=4, i=3, imp=128.0, dueno="INT", est="Mitigar",
         acc="Prueba de concepto de envío real desde el inicio del desarrollo; separar quién decide (reloj) de quién envía (portal).",
         trig="Error de red al enviar el primer correo desde el servidor del reloj.", cont="Enviar desde el portal (Vercel) y dejar el reloj solo como planificador.", costo=40.0, res=(2, 2),
         estado="Materializado en la semana 9; respuesta ejecutada"),
    dict(id="R06", tipo="Amenaza", cat="Legal / Seguridad", desc="Exposición de datos personales de salud por permisos mal configurados (incumplimiento de la Ley N.° 29733).",
         causa="Datos de grupo sanguíneo y donaciones son datos sensibles.", p=2, i=5, imp=400.0, dueno="QA", est="Evitar",
         acc="Seguridad por filas (RLS) en todas las tablas; mínimo privilegio; pruebas con una sesión de cada rol; mensajes sin datos médicos.",
         trig="Una prueba de rol devuelve datos que no corresponden.", cont="Bloquear el módulo afectado, corregir la política y repetir las pruebas.", costo=56.0, res=(1, 5)),
    dict(id="R07", tipo="Amenaza", cat="Seguridad", desc="Un resultado crítico llega al donante por el portal o por correo por error de configuración.",
         causa="Un resultado reactivo no debe comunicarse por canal digital.", p=1, i=5, imp=0.0, dueno="LT", est="Evitar",
         acc="Triple barrera: la interfaz no ofrece liberarlo, la función de liberación lo rechaza y la política de seguridad lo oculta.",
         trig="Prueba con cuenta de donante que lee un resultado crítico.", cont="Desactivar la liberación y revisar manualmente los resultados.", costo=0.0, res=(1, 5)),
    dict(id="R08", tipo="Amenaza", cat="Usuarios", desc="Baja adopción del donante de zona rural (sin correo, poca conectividad, poca familiaridad digital).",
         causa="Parte de los donantes proviene de zonas rurales.", p=4, i=3, imp=0.0, dueno="AF", est="Mitigar",
         acc="Portal liviano y de una sola pantalla; contraseñas fáciles de dictar; el personal puede contactar por teléfono.",
         trig="Menos del 30 % de donantes con correo autorizado en el primer mes.", cont="Priorizar el canal SMS como siguiente etapa.", costo=0.0, res=(3, 2)),
    dict(id="R09", tipo="Amenaza", cat="Clínico", desc="Los valores clínicos provisionales (intervalo de 90 días, máximos anuales) no coinciden con el criterio del médico.",
         causa="Los valores aún no tienen validación clínica formal.", p=3, i=4, imp=0.0, dueno="PM", est="Transferir",
         acc="Parametrizar los valores y trasladar su validación al médico responsable antes de producción.",
         trig="Observación del médico sobre los valores.", cont="Ajustar el parámetro (y la regla en la base si cambia el máximo anual).", costo=0.0, res=(2, 3)),
    dict(id="R10", tipo="Amenaza", cat="Técnico", desc="Pérdida de código o de datos por error humano (borrado accidental, sobrescritura).",
         causa="Trabajo concurrente de seis personas.", p=2, i=4, imp=0.0, dueno="LT", est="Mitigar",
         acc="Control de versiones en Git con revisión; respaldo automático de la base de datos.",
         trig="Commit que elimina archivos críticos.", cont="Restaurar desde el repositorio o el respaldo.", costo=0.0, res=(1, 3)),
    dict(id="R11", tipo="Amenaza", cat="Cronograma", desc="Retraso en la documentación de cierre por la carga de la última semana.",
         causa="Concentración de entregables en la semana 12.", p=3, i=2, imp=0.0, dueno="PM", est="Aceptar (activa)",
         acc="Avanzar el informe final desde la semana 9 y registrar lecciones aprendidas de forma continua.",
         trig="Informe final con menos del 50 % de avance en la semana 11.", cont="Priorizar acta de cierre e informe; diferir anexos opcionales.", costo=0.0, res=(2, 2)),
    dict(id="R12", tipo="Amenaza", cat="Legal", desc="Cambios normativos sobre protección de datos de salud durante el proyecto.",
         causa="La normativa de datos personales puede actualizarse.", p=1, i=3, imp=0.0, dueno="PM", est="Aceptar (pasiva)",
         acc="Monitoreo mensual de normas; arquitectura modular para adaptar el consentimiento.",
         trig="Publicación de una norma que afecte el tratamiento.", cont="Actualizar el texto de consentimiento y las políticas.", costo=0.0, res=(1, 3)),
    dict(id="R13", tipo="Oportunidad", cat="Interesados", desc="El HRDC (o la DIRESA) decide adoptar el sistema más allá de la etapa académica.",
         causa="Necesidad expresada por el Banco de Sangre y bajo costo de operación.", p=3, i=4, imp=0.0, dueno="PM", est="Explotar",
         acc="Dejar documentación, manuales y código listos para transferencia; presentar resultados a la Dirección.",
         trig="La Dirección solicita una reunión de continuidad.", cont="Plan de transición y acompañamiento.", costo=0.0, res=(4, 4)),
    dict(id="R14", tipo="Oportunidad", cat="Costos", desc="Los planes educativos gratuitos de las herramientas (GitHub, Figma, Supabase) reducen el costo recurrente.",
         causa="Programas educativos de los proveedores.", p=4, i=2, imp=0.0, dueno="LT", est="Mejorar",
         acc="Registrar la cuenta institucional en los programas educativos.",
         trig="Aprobación de la cuenta educativa.", cont="Mantener los planes gratuitos actuales.", costo=0.0, res=(4, 2)),
    dict(id="R15", tipo="Oportunidad", cat="Académico", desc="El proyecto puede constituirse en tesis o publicación académica del equipo.",
         causa="Problema real de salud pública con solución funcionando.", p=3, i=3, imp=0.0, dueno="PM", est="Explotar",
         acc="Documentar la metodología y los resultados con criterio de reproducibilidad.",
         trig="Docente asesora confirma el interés.", cont="Proponer línea de investigación.", costo=0.0, res=(3, 3)),
    dict(id="R16", tipo="Oportunidad", cat="Interesados", desc="Otros bancos de sangre u organizaciones (p. ej. Cruz Roja) muestran interés en replicar la plataforma.",
         causa="La solución es modular y de código abierto en su base.", p=2, i=4, imp=0.0, dueno="PM", est="Compartir",
         acc="Publicar documentación técnica reutilizable.",
         trig="Consulta formal de otra institución.", cont="Evaluar una alianza.", costo=0.0, res=(2, 4)),
]
for r in RIESGOS:
    r["pi"] = r["p"] * r["i"]
    r["nivel"] = "Alto (rojo)" if r["pi"] >= 10 else ("Moderado (amarillo)" if r["pi"] >= 5 else "Bajo (verde)")
    r["vme"] = round(PROB_VME[r["p"]] * r["imp"], 2) if r["tipo"] == "Amenaza" else 0.0

RIESGOS_VME = [r for r in RIESGOS if r["imp"] > 0 and r["tipo"] == "Amenaza"]
RESERVA_CONTINGENCIA = round(sum(r["vme"] for r in RIESGOS_VME), 2)
RESERVA_GESTION = round(0.03 * BAC, 2)
PRESUPUESTO_TOTAL = round(BAC + RESERVA_CONTINGENCIA + RESERVA_GESTION, 2)

# ----------------------------------------------------------------------------------------------
# 6. Valor Planificado, Valor Ganado y Costo Real por semana (EVM)
# ----------------------------------------------------------------------------------------------


def _frac_plan(a, dia: date) -> float:
    dias = dias_laborables(a["ini"], a["fin"])
    hechos = len([x for x in dias if x <= dia])
    return min(1.0, hechos / len(dias))


def _frac_real(a, dia: date) -> float:
    """Avance real acumulado de la actividad al `dia`: inicio desplazado y duración estirada."""
    if a["dur"] == 0:
        return _frac_plan(a, dia)
    shift, stretch, _k = a["seg"]
    ini = a["ini"]
    for _ in range(shift):
        ini = sig_laborable(ini)
    dur_real = max(1, round(a["dur"] * stretch))
    dias = dias_laborables(ini, ini + timedelta(days=int(dur_real * 2.2) + 14))[:dur_real]
    hechos = len([x for x in dias if x <= dia])
    return min(1.0, hechos / dur_real)


def _fin_real(a) -> date:
    if a["dur"] == 0:
        return a["fin"]
    shift, stretch, _k = a["seg"]
    ini = a["ini"]
    for _ in range(shift):
        ini = sig_laborable(ini)
    return sumar_laborables(ini, max(1, round(a["dur"] * stretch)))


for a in _A:
    a["fin_real"] = _fin_real(a)


def evm_semanal():
    """Devuelve una lista (semana, PV, EV, AC) con valores acumulados al final de cada semana."""
    filas = []
    efectivo_acum = 0.0
    for s in range(1, N_SEMANAS + 1):
        _, fin_sem = rango_semana(s)
        corte = min(fin_sem, CORTE)
        pv = ev = ac = 0.0
        for a in _A:
            pv += a["h"] * TARIFA * _frac_plan(a, fin_sem)
            if fin_sem <= CORTE:
                f = _frac_real(a, fin_sem)
                ev += a["h"] * TARIFA * f
                ac += a["h"] * TARIFA * f * a["seg"][2]
        efectivo_acum += EFECTIVO_SEM.get(s, 0.0)
        pv += efectivo_acum
        if fin_sem <= CORTE:
            ev += efectivo_acum
            ac += efectivo_acum
        filas.append(dict(semana=s, pv=round(pv, 2), ev=round(ev, 2) if fin_sem <= CORTE else None,
                          ac=round(ac, 2) if fin_sem <= CORTE else None))
    return filas


EVM = evm_semanal()
S_CORTE = semana_de(CORTE) - 1 if CORTE.weekday() == 6 else semana_de(CORTE)   # semana 11
S_CORTE = semana_de(CORTE - timedelta(days=1))


def indicadores(sem: int):
    fila = next(f for f in EVM if f["semana"] == sem)
    pv, ev, ac = fila["pv"], fila["ev"], fila["ac"]
    sv, cv = ev - pv, ev - ac
    spi, cpi = ev / pv, ev / ac
    eac1 = BAC / cpi                      # desempeño de costo continúa
    eac2 = ac + (BAC - ev)                # variación atípica
    eac3 = ac + (BAC - ev) / (cpi * spi)  # costo y cronograma influyen
    return dict(sem=sem, pv=pv, ev=ev, ac=ac, sv=sv, cv=cv, spi=spi, cpi=cpi,
                eac1=eac1, eac2=eac2, eac3=eac3, etc=eac1 - ac, vac=BAC - eac1,
                tcpi=(BAC - ev) / (BAC - ac), pct=ev / BAC)


# ----------------------------------------------------------------------------------------------
# 7. Costo de la calidad (CoQ)
# ----------------------------------------------------------------------------------------------
COQ = [   # categoría, actividad, HH
    ("Prevención", "Talleres de requisitos y validación con el Banco de Sangre", 28),
    ("Prevención", "Diseño UX y validación de prototipos", 22),
    ("Prevención", "Diseño de arquitectura y modelo de datos con seguridad por filas", 30),
    ("Prevención", "Definición de consentimiento y requisitos de la Ley N.° 29733", 12),
    ("Prevención", "Capacitación del equipo (seguridad por filas, Next.js, Supabase)", 12),
    ("Prevención", "Plan de calidad y estándares (ISO/IEC 25010)", 8),
    ("Evaluación", "Pruebas funcionales y de integración", 46),
    ("Evaluación", "Pruebas de seguridad (sesión de cada rol)", 24),
    ("Evaluación", "Revisión de código entre pares", 22),
    ("Evaluación", "Piloto interno con cuentas de cada rol", 20),
    ("Evaluación", "Verificación de correos, plantillas y aprobaciones", 8),
    ("Fallas internas", "Corrección de defectos de importación de archivos", 10),
    ("Fallas internas", "Rehacer el envío de correo (migración del reloj al portal)", 16),
    ("Fallas internas", "Ajustes de interfaz tras revisión interna", 10),
    ("Fallas internas", "Corrección de permisos detectada en pruebas por rol", 6),
    ("Fallas externas", "Atención de incidencias reportadas en el piloto interno", 6),
    ("Fallas externas", "Corrección de textos observados por el Banco de Sangre", 4),
    ("Fallas externas", "Ajuste de plantillas de correo tras la validación", 2),
]
COQ_CAT = ["Prevención", "Evaluación", "Fallas internas", "Fallas externas"]
COQ_HH = {c: sum(h for k, _, h in COQ if k == c) for c in COQ_CAT}
COQ_COSTO = {c: COQ_HH[c] * TARIFA for c in COQ_CAT}
COQ_TOTAL = sum(COQ_COSTO.values())
COQ_CC = COQ_COSTO["Prevención"] + COQ_COSTO["Evaluación"]
COQ_CNC = COQ_COSTO["Fallas internas"] + COQ_COSTO["Fallas externas"]

# Análisis costo-beneficio de la calidad (método de la clase: C-B = beneficio / inversión)
CB_DEFECTOS_SIN_PLAN = 64          # SUPUESTO: defectos que llegarían al usuario sin plan de calidad
CB_DEFECTOS_CON_PLAN = 12          # defectos que sí llegaron (según el registro de pruebas)
CB_HORAS_POR_DEFECTO = 5           # horas promedio de corrección en producción
CB_RETRABAJO_REQUISITOS = 120      # SUPUESTO: horas de rediseño evitadas con prototipos validados
CB_FALLAS_SIN = (CB_DEFECTOS_SIN_PLAN * CB_HORAS_POR_DEFECTO + CB_RETRABAJO_REQUISITOS) * TARIFA
CB_FALLAS_CON = CB_DEFECTOS_CON_PLAN * CB_HORAS_POR_DEFECTO * TARIFA
CB_INVERSION = COQ_CC
CB_BENEFICIO = CB_FALLAS_SIN - CB_FALLAS_CON
CB_RATIO = CB_BENEFICIO / CB_INVERSION

# Registro de defectos por módulo (para Pareto)
DEFECTOS = [
    ("Comunicaciones y automatizaciones", 13),
    ("Importación y registro de donantes", 10),
    ("Portal del donante", 9),
    ("Panel del personal", 7),
    ("Seguridad y permisos", 4),
    ("Reportes", 3),
    ("Despliegue y configuración", 2),
]

# ----------------------------------------------------------------------------------------------
# 8. Interesados
# ----------------------------------------------------------------------------------------------
# id, nombre, organización/rol, rol en el proyecto, expectativas, interés(1-5), influencia(1-5), actitud, fase, estrategia
INTERESADOS = [
    ("S01", "Ing. Ena Mirella Cacho Chávez", "UNC — Docente coordinadora", "Sponsor académico y supervisora",
     "Proyecto entregado con documentación PMI completa y evidencias del producto.", 5, 5, "Apoya", "Todas", "Gestionar de cerca"),
    ("S02", "Diana M. Barrantes Gallardo", "Equipo HEMOCAX", "Project Manager",
     "Liderar un proyecto real con impacto social medible.", 5, 5, "Apoya", "Todas", "Gestionar de cerca"),
    ("S03", "Jesús A. Valdiviezo Zavaleta", "Equipo HEMOCAX", "Líder Técnico y base de datos",
     "Arquitectura segura y mantenible.", 5, 4, "Apoya", "Diseño y desarrollo", "Gestionar de cerca"),
    ("S04", "Scarlet S. Terrones Cerna", "Equipo HEMOCAX", "Desarrolladora Frontend",
     "Requisitos y diseño aprobados antes de construir.", 5, 3, "Apoya", "Desarrollo", "Mantener informada"),
    ("S05", "Darick A. Pérez Briceño", "Equipo HEMOCAX", "Integraciones y automatizaciones",
     "Servicios externos estables y documentados.", 5, 3, "Apoya", "Desarrollo y despliegue", "Mantener informado"),
    ("S06", "Dider A. Díaz Becerra", "Equipo HEMOCAX", "QA y seguridad de datos",
     "Criterios de aceptación claros y tiempo para pruebas.", 5, 3, "Apoya", "Pruebas", "Mantener informado"),
    ("S07", "Adriana A. Limay Rodríguez", "Equipo HEMOCAX", "Analista funcional y UX",
     "Acceso a usuarios reales para validar prototipos.", 5, 3, "Apoya", "Requisitos y pruebas", "Mantener informada"),
    ("S08", "Dra. Marimar", "HRDC — Encargada del Banco de Sangre", "Contraparte funcional y usuaria clave",
     "Sistema sencillo que mantenga vigente la relación con el donante.", 5, 5, "Apoya", "Todas", "Gestionar de cerca"),
    ("S09", "Jefatura del Servicio y médico responsable", "HRDC — Servicio de Hemoterapia y Banco de Sangre", "Validador clínico y aprobador de textos",
     "Confidencialidad, resultados críticos fuera del canal digital, valores clínicos validados.", 4, 5, "Neutral", "Diseño, pruebas y cierre", "Gestionar de cerca"),
    ("S10", "Personal de enfermería y apoyo", "HRDC — Banco de Sangre", "Usuarios del panel del personal",
     "Herramienta rápida e intuitiva para atender donantes.", 5, 2, "Apoya", "Pruebas y capacitación", "Mantener informado"),
    ("S11", "Oficina de Estadística e Informática (OEI)", "HRDC", "Contraparte técnica",
     "No intervenir los sistemas actuales; documentación técnica y transferencia.", 3, 4, "Neutral", "Despliegue y cierre", "Mantener satisfecha"),
    ("S12", "Dirección General", "HRDC", "Aprobador institucional",
     "Cero costo de desarrollo, riesgo operativo nulo y definición del costo recurrente.", 3, 5, "Neutral", "Inicio y cierre", "Mantener satisfecha"),
    ("S13", "Donantes voluntarios (incluye zonas rurales)", "Comunidad de Cajamarca", "Usuarios finales del portal",
     "Saber cuándo pueden volver a donar, ver su resultado y no recibir mensajes que no autorizaron.", 4, 2, "Apoya", "Piloto y operación", "Mantener informados"),
    ("S14", "Proveedores de servicios en la nube", "Supabase, Vercel, Render, Google", "Proveedores de infraestructura",
     "Uso dentro de los términos de cada plan.", 1, 3, "Neutral", "Desarrollo y operación", "Monitorear"),
    ("S15", "DIRESA Cajamarca / MINSA", "Sector salud regional", "Regulador y aliado potencial",
     "Alineación con normas sanitarias y de protección de datos.", 2, 4, "Neutral", "Cierre y escalamiento", "Mantener satisfecha"),
]
N_INTERESADOS = len(INTERESADOS)
CANALES = N_INTERESADOS * (N_INTERESADOS - 1) // 2

# ----------------------------------------------------------------------------------------------
# 9. Adquisiciones: criterios ponderados
# ----------------------------------------------------------------------------------------------
# (decisión, criterios[(nombre, peso)], alternativas{nombre: [puntajes 1-5 en el orden de criterios]}, elegida)
SELECCION = [
    ("Base de datos y autenticación",
     [("Seguridad por filas (RLS) en la base", 0.30), ("Costo (plan gratuito suficiente)", 0.25), ("Modelo relacional y SQL estándar", 0.20),
      ("Facilidad de uso para el equipo", 0.15), ("Salida de datos / portabilidad", 0.10)],
     {"Supabase (PostgreSQL)": [5, 4, 5, 4, 5], "Firebase (NoSQL)": [3, 4, 2, 4, 2], "Servidor propio (Node + PostgreSQL)": [4, 2, 5, 2, 5]},
     "Supabase (PostgreSQL)"),
    ("Alojamiento del portal",
     [("Soporte nativo de Next.js", 0.30), ("Envío de correo (SMTP) permitido", 0.25), ("Costo (plan gratuito)", 0.25),
      ("Despliegue automático desde GitHub", 0.20)],
     {"Vercel": [5, 5, 4, 5], "Render": [3, 1, 4, 4], "Railway": [4, 4, 2, 4]},
     "Vercel"),
    ("Servicio de correo",
     [("Costo", 0.35), ("Facilidad de configuración", 0.25), ("Límite diario de envíos", 0.25), ("Reputación de entrega", 0.15)],
     {"Gmail (SMTP, contraseña de aplicación)": [5, 5, 2, 4], "Servicio transaccional de pago": [2, 4, 5, 5], "Servidor de correo propio": [3, 1, 4, 2]},
     "Gmail (SMTP, contraseña de aplicación)"),
]

def horas_semana_rol():
    """Horas planificadas por semana y rol (distribuidas uniformemente entre los días laborables de cada actividad)."""
    out = {r: [0.0] * N_SEMANAS for r in ORDEN_ROLES}
    for a in _A:
        dias = dias_laborables(a["ini"], a["fin"])
        for r, h in a["horas"].items():
            for dia in dias:
                s = semana_de(dia) - 1
                if 0 <= s < N_SEMANAS:
                    out[r][s] += h / len(dias)
    return out


HORAS_SEM = horas_semana_rol()


if __name__ == "__main__":
    print("Horas totales:", HORAS_TOTALES, "| RR.HH.:", COSTO_RRHH, "| Gastos:", GASTOS_TOTAL, "| BAC:", BAC)
    print("Fin de proyecto (CPM):", FIN_REAL_PLAN, "| semanas:", round(SEMANAS_PROY, 1))
    print("Horas por rol:", HORAS_ROL)
    print("Reserva contingencia:", RESERVA_CONTINGENCIA, "| gestión:", RESERVA_GESTION, "| total:", PRESUPUESTO_TOTAL,
          "| cont/BAC: {:.1f}%".format(100 * RESERVA_CONTINGENCIA / BAC))
    print("Ruta crítica:", [a["id"] for a in _A if a["critica"]])
    for a in _A:
        print(a["id"], a["ini"], a["fin"], "hol", a["holgura"], "real fin", a["fin_real"], a["nombre"][:40])
    for f in EVM:
        print(f)
    print("S_CORTE", S_CORTE)
    for s in (6, S_CORTE):
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in indicadores(s).items()})
    print("CoQ:", COQ_COSTO, COQ_TOTAL, "CC", COQ_CC, "CNC", COQ_CNC, "| CoQ/BAC: {:.1f}%".format(100 * COQ_TOTAL / BAC))
    print("C-B: sin plan", CB_FALLAS_SIN, "con plan", CB_FALLAS_CON, "inversión", CB_INVERSION, "beneficio", CB_BENEFICIO, "ratio %.2f" % CB_RATIO)
    print("Canales:", CANALES, "defectos:", sum(n for _, n in DEFECTOS))
