# Informe de Gestión de Proyectos — HEMOCAX

`HEMOCAX_Informe_Gestion_de_Proyectos.docx` es el informe completo (charter, interesados, requisitos, alcance, EDT, cronograma, costos y EVM, calidad, RR.HH., comunicaciones, riesgos, adquisiciones, cambios, cierre y lectura PMBOK 7).

## Cómo se genera

Todo sale de **un solo modelo de datos** (`datos.py`) para que las cifras sean coherentes entre capítulos.

```bash
pip install python-docx matplotlib      # una sola vez (y Graphviz instalado: comando `dot`)
python informe.py                       # regenera fig/*.png y el .docx
```

| Archivo | Qué contiene |
|---|---|
| `datos.py` | Actividades, horas por rol, fechas, riesgos, interesados, CoQ, gastos. **Aquí se editan los datos.** |
| `graficos.py`, `graf_extra.py` | Curva S, Gantt, matriz P×I, Pareto, Ishikawa, EDT, OBS, etc. |
| `cap_a.py` … `cap_f.py` | Texto y tablas de cada capítulo. |
| `docx_utils.py`, `fmt.py` | Estilos de Word y formatos de números y fechas. |

Al abrir el Word por primera vez, acepta **actualizar los campos** (o presiona `F9`) para generar el índice y los números de página.

## Datos que son supuestos y deben confirmarse

Estos valores se construyeron para ser coherentes con el sistema; **reemplázalos por los registros reales** si el docente los pide:

- **Horas por persona y por actividad** (`datos.py`, tabla `_act`) y la tarifa de S/ 8.00 por hora.
- **Seguimiento (EV y AC)**: desfases, estiramientos y factores de costo por actividad (`seg=`). Determinan SPI, CPI y EAC.
- **Fechas del cronograma** (calculadas con CPM desde la fecha de inicio 21/07/2026).
- **Probabilidades, impactos en soles y VME** de los riesgos (`RIESGOS`), que fijan la reserva de contingencia.
- **Registro de defectos** por módulo (`DEFECTOS`) y los supuestos del análisis costo-beneficio (`CB_*`).
- **Estado de las pruebas** (`PRUEBAS` en `cap_c.py`), fechas y contenido de las solicitudes de cambio (`SCR` en `cap_e.py`).
- **Roles del equipo** (quién es Líder Técnico, Integraciones, Frontend, QA, Analista).
- **Actitud, interés e influencia** de los interesados.
