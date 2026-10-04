# Guion del video por procesos (máx. 20 min)

Este guion **reemplaza el orden por rol** de `GUION_VIDEO.md` por un orden **por proceso**, siguiendo el mapa de `docs/PROCESOS.md`. Casi todo se graba con **una sola cuenta: Administrador Demo** (`99000003`), porque el administrador puede ejecutar casi todos los procesos. Solo cambias de cuenta una vez, para ver el portal como donante.

Las cuentas y contraseñas están en `demo/CREDENCIALES_DEMO.txt`. Las reglas de seguridad de la grabación (qué pantallas muestran datos reales, qué no pulsar) siguen siendo las de `GUION_VIDEO.md`, sección 0.

---

## La idea: un hilo que une los procesos

Cada proceso entrega algo al siguiente, y se graba **en ese orden**. Un solo donante, **Lucas Soto Demo**, recorre casi toda la cadena:

```
P-01 Acceso ─► P-02 Cuentas ─► P-12 Parámetros                  (el administrador prepara el sistema)
                                   │
        P-03 Registro (Lucas) ─► P-04 Consentimiento ─► P-05 Donación ─► P-06 Resultado
                                                                              │
                          P-02 Cuenta para Lucas ◄────────────────────────────┘
                                   │
                          P-10 Portal: Lucas ve su resultado
                                   │
        P-07/P-08 Correos y campañas ─► P-09 Automatizaciones (se explica)
                                   │
        P-11 Reportes ─► P-13 Auditoría (aparece todo lo que hicimos) ─► P-14 Derechos ARCO
```

**Frase de enlace.** Termina cada toma con una frase que nombre el siguiente proceso (está en cada ficha, en *Enlace*). Así el video se entiende como una cadena y no como pantallas sueltas.

---

## Tiempos

| Bloque | Tomas | Tiempo |
|---|---|---|
| Introducción | T0 | 0:45 |
| 1. Preparar el sistema (administrador) | T1–T3 | 3:30 |
| 2. El hilo de Lucas | T4–T10 | 10:00 |
| 3. Comunicación | T11–T12 | 2:45 |
| 4. Control y cumplimiento | T13–T15 | 2:45 |
| Cierre | T16 | 0:45 |
| **Total** | | **≈ 20:30 con pausas; 17–18 min editado** |

**Si te pasas, quita en este orden:** T12 (automatizaciones, se puede decir en el cierre), T14 (reportes), T7 (crítico) y la importación de T4. Ahorran ≈ 4 min.

---

## Cómo grabar por procesos

1. **Una toma = un archivo.** Pon el nombre antes de grabar: `T04_P03_registro.mp4`. Las tomas se unen al editar. Si te equivocas, repites **solo esa toma**.
2. **Rótulo al inicio de cada toma** (2 segundos, texto en pantalla al editar): `P-03 · Registro del donante · Actor: Administrador`. Con eso el espectador sabe en qué proceso está.
3. **Orden obligatorio de T4 a T10:** cada toma deja datos que usa la siguiente (Lucas existe, tiene consentimiento, tiene una donación y un resultado liberado). Si repites una toma de ese tramo y ya avanzaste, hay que **reiniciar el hilo**:

```bash
node demo/limpiar-demo.js
node demo/seed-demo.js
```

   y regrabar desde T4. Las tomas T1–T3 y T11–T16 se pueden repetir sin reiniciar.
4. **Antes de empezar:** ejecuta `node demo/seed-demo.js` (si ya hay datos, primero `limpiar-demo.js`). Ventana de incógnito, zoom 100 %, modo «No molestar», bandeja de `hemocax26@gmail.com` abierta en otra pestaña.
5. **Al terminar:** `node demo/limpiar-demo.js`.

### Datos del hilo (para no improvisar)

| Dato | Valor |
|---|---|
| Donante nuevo | DNI `99000301` · Lucas / Soto Demo · M · 1990-05-05 · tel. `987000301` · correo `hemocax26+lucas@gmail.com` · tipo de sangre «No sé» |
| Cuenta de personal nueva | DNI `99000302` · «Prueba Demo» · Enfermería |
| Archivo de importación | `demo/donantes_demo.csv` (5 filas correctas y 2 con error) |
| Donantes para mostrar reglas | Rosa `99000103` (máximo anual) · Luis `99000102` (donó hace 20 días) |
| Resultados pendientes | Carlos `99000104` (sin correo), Elena `99000105` (se marca crítico), Marta `99000107` |
| Derechos ARCO | Pedro Quispe Demo `99000108` |

---

## T0 · Introducción (0:45) · pantalla: diapositiva «Cómo funciona» o el mapa de `PROCESOS.md`

> «HEMOCAX es un sistema web para el Banco de Sangre del Hospital Regional Docente de Cajamarca. Lo vamos a recorrer **proceso por proceso**, en el orden en que ocurren en la vida real. Cada proceso entrega algo al siguiente: se prepara el sistema, se registra a un donante, se atiende su donación, se libera su resultado y él lo ve en su portal. Casi todo lo haremos con una cuenta de administrador, y al final veremos cómo queda todo registrado. Los datos son de demostración.»

---

# BLOQUE 1 · El administrador prepara el sistema

## T1 · P-01 Acceso y sesión (0:40) · Actor: Administrador

Pantalla de ingreso. Haz un intento fallido (DNI `99000003`, contraseña incorrecta), muestra el mensaje y entra bien. Pulsa «Mostrar lo que escribo» una vez.

> «Todo empieza con el acceso. Se entra solo con DNI y contraseña; no hay registro libre, las cuentas las crea el administrador. Si algo está mal, el mensaje es claro y no revela si el DNI existe. Según el puesto, cada persona ve solo sus pantallas.»

**Enlace:** «Entonces, lo primero que hace el administrador es crear esas cuentas.»

## T2 · P-02 Gestión de cuentas (1:15) · Actor: Administrador ⚠️ difuminar la tabla de cuentas

«Cuentas de acceso». Muestra el formulario «Crear cuenta» sin enseñar la lista. Crea la cuenta `99000302` «Prueba Demo», puesto Enfermería, y muestra la contraseña sugerida (se ve **una sola vez**). Muestra los botones de nueva contraseña, desactivar y permiso de liberar resultados (sin pulsarlos en cuentas reales).

> «El administrador crea las cuentas y elige el puesto: enfermería, médico responsable, administrador o donante. El sistema sugiere una contraseña que se muestra una sola vez y nunca se guarda en claro. También se puede restablecer, desactivar sin borrar, y dar o quitar el permiso de liberar resultados. Hay reglas de protección: nadie puede desactivarse a sí mismo y siempre queda un administrador activo.»

**Enlace:** «Con las personas listas, el administrador define las reglas con las que van a trabajar.»

## T3 · P-12 Parámetros y aprobaciones (1:30) · Actor: Administrador · **solo mostrar, no guardar**

«Parámetros». Recorre: máximos por año, intervalo, recomendaciones, «Dónde y cuándo donar», texto del consentimiento y plantillas automáticas. **No pulses Guardar ni Aprobar.**

> «Los valores clínicos no están en el código; se ajustan aquí. Máximo anual de 4 donaciones en hombres y 3 en mujeres, el intervalo mínimo —hoy provisional hasta que el médico lo confirme—, las recomendaciones que ve el donante y los datos de dónde donar. El consentimiento tiene versiones. Y los cuatro mensajes automáticos tienen una plantilla que la Jefatura debe **aprobar**: mientras no esté aprobada, el sistema no envía nada solo.»

**Enlace:** «Con el sistema configurado, empieza la vida del donante. Seguiremos a uno: Lucas.»

---

# BLOQUE 2 · El hilo de Lucas

## T4 · P-03 Registro del donante (1:45) · Actor: Administrador

Escribe «Demo» en el buscador de Donantes. Busca `99000301` en Inicio → no existe → «Registrar donante nuevo» (el DNI se rellena solo). Completa los datos de Lucas, deja el tipo de sangre en «No sé» y guarda.
*(Si hay tiempo)* «Importar» → `donantes_demo.csv` → muestra el resumen de 5 correctas y 2 con error y confirma.

> «Una persona nueva se registra desde el buscador: si no existe, se crea con su DNI. El sistema valida DNI de 8 números, fecha, sexo y correo. Si no conoce su tipo de sangre, se deja “No sé” y se completa después. Para muchas personas se usa un Excel guardado como CSV: el sistema revisa fila por fila y explica cada error en lenguaje simple; solo importa las correctas.»

**Enlace:** «Lucas ya está en el padrón, pero todavía no podemos escribirle: falta su consentimiento.»

## T5 · P-04 Consentimiento (0:45) · Actor: Administrador

Ficha de Lucas → «Correos y consentimiento» → «Registrar su autorización de correos» → guardar. Muestra versión, fecha y quién lo registró.

> «Sin consentimiento no se envía ningún correo. Queda registrado con la versión del texto, la fecha y quién lo anotó, y el donante puede retirarlo cuando quiera.»

**Enlace:** «Ahora Lucas se presenta a donar.»

## T6 · P-05 Atención y donación (1:30) · Actor: Administrador

1. Rosa (`99000103`): ficha → «Máximo anual». Muestra que no se puede registrar otra donación.
2. Luis (`99000102`): donó hace 20 días → el aviso de intervalo.
3. Lucas: «Registrar donación» → guardar. Muestra que se crea un **resultado pendiente**.

> «Al atender, el sistema dice si la persona puede donar hoy. Rosa ya donó 3 veces este año, es mujer, y la base de datos no permite una cuarta. A Luis le falta intervalo: avisa y pide una razón. Lucas sí puede: se registra la donación y automáticamente nace un resultado en estado pendiente.»

**Enlace:** «Ese resultado pendiente lo recoge el siguiente proceso: la liberación.»

## T7 · P-06 Resultados (2:00) · Actor: Administrador (con permiso de liberar)

«Resultados»: se ven los pendientes, los más antiguos primero.
1. **Liberar** el de Lucas con el mensaje «Tus resultados están normales. Gracias por donar.»
2. **Marcar como crítico** el de Elena → «Sí, marcar como crítico». Muestra «Quitar marca».
3. En el resultado liberado de Lucas, pulsa **«Avisar por correo»**. *(Carlos, sin correo, no tiene el botón: el sistema lo explica.)*

> «Los resultados pendientes aparecen con el tiempo que llevan esperando; los de más de 24 horas se destacan. Solo quien tiene permiso puede liberarlos, y el donante verá un mensaje claro con recomendaciones. Si hay un hallazgo delicado se marca como **crítico**: ese resultado nunca se muestra al donante, ni en pantalla ni por correo, y eso lo garantiza la base de datos. El personal contacta a la persona. El aviso por correo no lleva el resultado: solo invita a entrar al portal.»

**Enlace:** «Falta que Lucas pueda entrar a verlo. Eso otra vez lo hace el administrador.»

## T8 · P-02 (continuación) Cuenta para el donante (0:45) · Actor: Administrador ⚠️ difuminar la tabla

«Cuentas de acceso» → «Crear cuenta» → puesto **Donante** → elige a **Lucas Soto Demo** ya registrado → contraseña sugerida (**anótala o déjala a la vista**: es la que usarás en T9).

> «La cuenta de un donante se crea sobre una persona ya registrada. La contraseña es fácil de dictar por teléfono, porque muchos donantes no usan correo a diario.»

**Enlace:** «Ahora veamos el sistema desde el otro lado: el del donante.»

## T9 · P-10 Portal del donante (2:00) · Actor: Donante (Lucas) · modo celular 375 px

Cierra sesión. `F12` → ícono de celular → iPhone SE. Ingresa con el DNI `99000301` y la contraseña de T8.

Muestra: el estado de hoy (con ícono y color), el resultado liberado con su mensaje y recomendaciones, «Mis donaciones», «¿Dónde y cuándo donar?», las campañas activas y «Quiero recibir avisos». *(Opcional, 20 s)* «Más opciones»: cambiar contraseña y descargar sus datos.

> «Así lo ve Lucas. Una sola pantalla, letra grande y colores: arriba dice si hoy puede donar o cuántos días faltan. Aquí está el resultado que el administrador liberó hace un momento, con recomendaciones. Si fuera crítico, aquí simplemente no habría nada. Puede ver dónde y cuándo donar, las campañas, y decidir si quiere recibir avisos por correo. Todo lo que hizo el personal llegó hasta aquí.»

**Enlace:** «Y cuando el Banco de Sangre necesita llamar a muchos donantes, usa la comunicación por correo.»

*(Quita el modo celular y cierra sesión. Vuelve a entrar como `99000003`.)*

## T10 · Reserva de la toma (hasta 1:00)

Tiempo de margen para regrabar un tramo del hilo (T4–T9) sin pasarte de 20 min. Si no lo usas, no se graba nada.

---

# BLOQUE 3 · Comunicación

## T11 · P-07 y P-08 Correos y campañas (1:45) · Actor: Administrador

1. «Correos enviados» → «Enviar un correo a un donante» → Ana Quispe Demo → mensaje corto con `{{nombre}}` → enviar.
2. «Campañas e información» → **solo «DEMO · Se necesita sangre O negativo»** → «Vista previa» → «Enviar por correo» → confirmar.
3. «Correos enviados»: muestra el historial y la fila **Fallido** de Ana con su motivo.
4. Cambia a la bandeja de `hemocax26@gmail.com` y muestra que llegaron.

> «Hay dos formas de escribir: un correo individual, y una campaña dirigida a un grupo, por ejemplo cuando falta sangre O negativo. Antes de enviar hay una vista previa de quiénes lo recibirán: solo los del grupo pedido, con consentimiento, correo válido y activos. Nadie recibe dos veces la misma campaña. Todo queda en el historial: a quién, de qué tipo, si salió o falló y por qué, y quién lo envió. Y este es el correo que recibe el donante.»

**Enlace:** «Estos envíos los decide una persona. Otros salen solos.»

## T12 · P-09 Automatizaciones diarias (1:00) · Actor: el sistema · **se explica, no se ejecuta**

Pantalla: diapositiva «Recordatorios automáticos» del pitch, o el diagrama de `PROCESOS.md`. Pulsa los cuatro horarios.

> «Cuatro correos salen solos, a las 8:00, 8:15, 8:30 y 8:45, hora de Lima: cumpleaños, recordatorio de que ya puede volver a donar, agradecimiento por la donación y reconocimiento al donante frecuente. Un reloj en Render avisa al portal en Vercel, que revisa quién cumple las reglas, envía y registra. Solo con plantilla aprobada, solo con consentimiento, y una sola vez por periodo. Por defecto el sistema simula y no envía nada hasta que se active.»

**Enlace:** «Todo esto se puede medir.»

---

# BLOQUE 4 · Control y cumplimiento

## T13 · P-11 Reportes (0:45) · Actor: Administrador

«Reportes». Muestra los indicadores y pulsa «Descargar en Excel (CSV)».

> «Los reportes dan las cifras del servicio: donantes registrados y activos, donaciones del periodo, quiénes pueden volver a donar, distribución por tipo de sangre, resultados que tardan más de 24 horas y correos enviados o fallidos. Se descargan en Excel.»

## T14 · P-13 Auditoría (1:00) · Actor: Administrador

«Actividad». Filtra o desplázate para que se vean las acciones de este video: creación de cuentas, registro de Lucas, consentimiento, donación, liberación y marca crítica.

> «Todo lo que hicimos quedó registrado: quién, cuándo y qué campos cambiaron. La bitácora no guarda los valores, solo qué se tocó, para no duplicar datos personales. Solo el administrador la consulta.»

**Enlace:** «Y por último, qué pasa cuando una persona ejerce sus derechos sobre sus datos.»

## T15 · P-14 Derechos del titular (ARCO) (1:00) · Actor: Administrador

Donantes → «Pedro» → ficha → «Datos y privacidad» → «Descargar sus datos» → «Eliminar datos personales» (se escribe el DNI para confirmar) → confirmar.

> «La ley de protección de datos personales da derecho a pedir una copia y a pedir que se eliminen. El administrador descarga los datos de la persona, o los anonimiza: se borran nombre, DNI, teléfono y correo y se elimina su cuenta, pero se conserva lo clínico sin identificar a nadie. El donante también puede descargar su copia desde su portal.»

---

## T16 · Cierre (0:45) · diapositiva «Cierre» del pitch

> «Recorrimos la cadena completa: se prepara el sistema, se registra al donante con su consentimiento, se atiende la donación, se libera el resultado y el donante lo ve en su portal; se comunica por correo, se mide y todo queda auditado. Queda para la siguiente etapa el envío por SMS, validar con el médico los valores clínicos, aprobar las plantillas y la revisión legal del consentimiento. Gracias.»

---

## Extra (solo si sobra tiempo) · Qué NO ve enfermería (0:40)

Cierra sesión, entra como Enfermera Demo (`99000001`). Muestra que el menú **no tiene** «Cuentas de acceso», «Parámetros» ni «Actividad», y que en «Resultados» no aparece «Liberar».

> «Los permisos no son solo del menú: la base de datos los aplica. Enfermería registra y atiende, pero no crea cuentas, no cambia reglas y no libera resultados.»

---

## Después de grabar

1. `node demo/limpiar-demo.js` (debe quedar solo lo real).
2. Une las tomas y agrega el rótulo de proceso al inicio de cada una.
3. Sube el video a **YouTube como «No listado»** y pásame el enlace para colocarlo en la diapositiva 5.
