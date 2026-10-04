# Guion del video de HEMOCAX (máx. 20 min)

Todo se graba en el sistema real (https://hemocax.vercel.app) con cuentas y donantes **DEMO**.
Las cuentas y contraseñas están en `demo/CREDENCIALES_DEMO.txt`.
Cuando termines de grabar, ejecuta `node demo/limpiar-demo.js` (borra todo lo DEMO).

---

## Tiempos (límite: 20 min)

| Parte | Escenas | Tiempo |
|---|---|---|
| Introducción e ingreso | 1–2 | 1 min |
| A. Enfermería | 3–9 | 6 min |
| B. Médico | 10–15 | 6 min |
| C. Administrador | 16–20 | 4,5 min |
| D. Donante | 21–24 | 3 min |
| E. Automatización y cierre | 25–27 | 2 min |
| **Total** | | **≈ 22 min hablando con calma** |

Los tiempos de cada escena son *con pausas*. Si grabas fluido y corriges al editar, queda en 16–18 min. **Para no pasarte de 20:** si vas largo, quita primero las escenas 6, 9, 12, 20 y 23 (ahorran ≈ 3 min). Las **escenas extra** del final solo úsalas si te sobra tiempo.

---

## 0. Antes de grabar (10 min)

1. **Navegador limpio:** ventana de incógnito (sin barras de marcadores ni extensiones). Zoom 100 %. Cierra WhatsApp, correo personal y notificaciones (modo «No molestar» de Windows: `Win + N`).
2. **Dos perfiles/ventanas:** una de escritorio (pantalla completa) y, para la parte del donante, una ventana angosta o el modo celular de las herramientas de desarrollador (`F12` → icono de celular → «iPhone SE»).
3. **Bandeja de entrada:** abre `hemocax26@gmail.com` en otra pestaña. Los correos de los donantes DEMO con consentimiento llegan ahí (usan `hemocax26+nombre@gmail.com`).
4. **Grabadora:** `Win + Alt + R` (Xbox Game Bar) graba la ventana activa; o OBS Studio si quieres grabar la pantalla completa y el micrófono. Prueba 10 segundos y revisa que se oiga la voz.
5. Ten abierto `demo/donantes_demo.csv` (se abre con Excel) para la escena de importación.

### ⚠️ Pantallas que muestran datos REALES de tu equipo

Hoy la base tiene 6 personas reales (Diana, Dider, Scarlet, Jesús, Darick, Adriana) además de lo DEMO.

| Pantalla | Qué se ve | Qué hacer |
|---|---|---|
| Donantes (lista completa) | Nombres, DNI y correos reales | **Escribe «Demo» en el buscador antes de mostrar la lista** y no la limpies |
| Cuentas de acceso | Cuentas reales | Muestra solo la parte de «Crear cuenta» y recorta/difumina la tabla al editar el video |
| Correos enviados | Pocos o ninguno real | Filtra por tipo; si ves nombres reales, difumina |
| Reportes | Cifras agregadas | Sin problema (sin nombres) |
| Actividad | Nombres de campos, DNI de quien actuó | Sin problema (todo DEMO si no entras con tu cuenta real) |
| Inicio → «Requieren atención» | Puede listar a alguien real sin dato | Si aparece, muéstralo rápido o corta |

### ⛔ Qué NO hacer durante la grabación (afecta al sistema real)

- **No aprobar las plantillas automáticas** de verdad: si el reloj de Render está activo, empezarían a salir correos a tu equipo. Muéstralas y **no** pulses «Aprobar» (o, si lo muestras, el script de limpieza las vuelve a dejar sin aprobar).
- **No guardar cambios** en Parámetros (intervalo, máximos, consentimiento, «Dónde donar»): solo muéstralos.
- **No publicar una versión nueva del consentimiento.**
- **No usar la campaña real «Campaña B+»** ni enviar campañas a B+/O+ (tu equipo tiene esas sangres y tiene consentimiento). **Usa solo las campañas «DEMO…»**, dirigidas a **O negativo**: nadie real tiene O-.
- No anonimizar a nadie real. Para la escena de derechos ARCO usa un donante DEMO (por ejemplo `Pedro Quispe Demo`).

---

## Escena 1 — Introducción (30 s) · sin pantalla o con la pantalla de ingreso

> «HEMOCAX es un sistema web para el Banco de Sangre del Hospital Regional Docente de Cajamarca. Tiene dos partes: un panel para el personal —enfermería, médicos y administración— y un portal sencillo para el donante. Sirve para llevar el registro de donantes y donaciones, entregar resultados de forma segura y mantener comunicación por correo. Todo lo que veremos son datos de demostración.»

## Escena 2 — Ingreso por DNI (30 s)

Pantalla de ingreso, sin iniciar sesión todavía.

> «Se ingresa solo con DNI y contraseña, sin correo. Si el DNI o la contraseña están mal, el mensaje es claro y en lenguaje sencillo. Además, se puede ver lo que se escribe con “Mostrar contraseña”.»

Haz un intento fallido (DNI `99000001`, contraseña mala) → muestra el mensaje → ingresa bien.

---

## PARTE A — Enfermería (`99000001` · Enfermera Demo)

### Escena 3 — Inicio y búsqueda (1 min)

> «Esta es la pantalla de inicio de enfermería. Arriba hay un buscador grande: “Atender a un donante”. Se escribe el DNI o el apellido y aparece la persona.»

Escribe `99000101` (Ana) → aparece → clic.

### Escena 4 — Ficha del donante y estado de elegibilidad (1 min)

> «La ficha resume todo: datos, tipo de sangre, historial de donaciones y, lo más importante, si puede donar hoy. Ana donó hace más de 200 días, así que está **Apta**. El sistema calcula el intervalo según el sexo y vigila el máximo anual: 4 donaciones al año para hombres y 3 para mujeres.»

Muestra: estado «Apta», historial, consentimiento, botones. Luego vuelve a Inicio y busca `99000103` (Rosa).

> «Rosa ya donó 3 veces este año. Está en **Máximo anual** y el sistema no deja registrar otra donación.»

### Escena 5 — Registrar una donación (1 min)

Busca `99000109` (Lucía, donó hace 300 días: está apta) → «Registrar donación» → guardar.

> «Registrar una donación toma segundos. Se crea automáticamente un resultado en estado pendiente. Si intentáramos registrar una donación antes del intervalo, el sistema avisa y pide una razón. Si se supera el máximo anual, la base de datos lo impide.»

*(Opcional: intenta registrar otra donación a Luis `99000102`, donó hace 20 días → muestra el aviso de intervalo.)*

### Escena 6 — Registrar donante nuevo (45 s)

Donantes → «Registrar donante». Rellena: DNI `99000301`, Lucas / Soto Demo, M, 1990-05-05, teléfono `987000301`, correo `hemocax26+lucas@gmail.com`. Deja el grupo sanguíneo como «No sé».

> «Si el donante no conoce su tipo de sangre, se puede dejar como “No sé” y completarlo después con el resultado.»

### Escena 7 — Consentimiento por correo (45 s)

En la ficha de Lucas → «Registrar su autorización de correos» → marcar → guardar.

> «Antes de enviar cualquier correo hace falta el consentimiento del donante. Queda registrado con la versión del texto, quién lo registró y la fecha, y también se registra si lo retira.»

### Escena 8 — Importar desde Excel (1 min)

Donantes → «Importar» → elige `demo/donantes_demo.csv` (también puedes mostrar el botón «Descargar plantilla», que baja un archivo de ejemplo con las columnas).

> «Para cargar muchos donantes de golpe se usa un archivo de Excel guardado como CSV. El sistema revisa fila por fila: aquí detecta que hay 5 filas correctas y 2 con errores, y explica cada error en lenguaje sencillo, por ejemplo “DNI inválido (8 números)”. Solo se importan las correctas.»

Confirma la importación (se cargan solo las 5 filas correctas).

*(Recuerda: escribe «Demo» en el buscador de Donantes para no mostrar nombres reales.)*

### Escena 9 — Enviar un aviso individual (30 s)

Menú «Correos enviados» → «Enviar un correo a un donante» → elige a Ana Quispe Demo → mensaje corto (puedes escribir `{{nombre}}`) → «Enviar correo».

> «También se puede escribir un correo individual a un donante que dio su consentimiento. Queda registrado quién lo envió.»

*(Cambia a la pestaña del correo y muestra que llegó, con el diseño del correo.)*

Cierra sesión.

---

## PARTE B — Médico responsable (`99000002` · Médico Demo)

### Escena 10 — Resultados pendientes (1 min 30 s)

Menú «Resultados».

> «Solo el médico responsable puede liberar resultados. Aquí aparecen los pendientes, con el tiempo que llevan esperando. Carlos y Elena llevan más de 24 horas.»

Pulsa «Liberar resultado» en Carlos (mensaje: «Tus resultados están normales. Gracias por donar.») y confirma.

> «Al liberarlo, el donante puede verlo en su portal con un mensaje y recomendaciones en lenguaje claro.»

### Escena 11 — Resultado crítico (1 min)

En Elena → «Marcar como crítico» → «Sí, marcar como crítico». (Muestra también «Quitar marca».)

> «Si hay un hallazgo delicado, se marca como **crítico**. Un resultado crítico **nunca** se muestra al donante: ni en la pantalla ni por correo. Eso está protegido desde la base de datos, no solo en la pantalla. El donante debe ser contactado por el personal de salud. Si fue un error, se puede quitar la marca.»

### Escena 12 — Avisar al donante (30 s)

En un resultado ya liberado de un donante con correo y consentimiento (por ejemplo Ana o Luis) aparece el botón «Avisar por correo». *(Carlos no tiene correo ni consentimiento: ahí no aparece y el sistema lo explica.)*

> «El aviso por correo no incluye el resultado; solo invita al donante a ingresar al portal para verlo.»

### Escena 13 — Campañas e información (1 min 30 s)

«Campañas e información». **Solo las DEMO.**

> «Hay dos tipos de contenido. Las **campañas** son convocatorias por correo, por ejemplo cuando hace falta sangre O negativo. La **información** son textos educativos que los donantes ven en su portal, como los requisitos para donar.»

En «DEMO · Se necesita sangre O negativo» pulsa «Vista previa» (solo los O- con consentimiento) → «Enviar por correo» → confirma → en la bandeja de `hemocax26@gmail.com` llegan los correos.

> «Solo recibe el correo quien tiene consentimiento, correo válido, está activo y es del grupo pedido. Nadie recibe dos veces la misma campaña.»

### Escena 14 — Correos enviados (45 s)

«Correos enviados».

> «Aquí queda el historial: a quién, de qué tipo —manual, campaña, aviso de resultado, recordatorio, cumpleaños—, si salió bien o falló y por qué, y quién lo envió. Si falló, aparece el motivo debajo del estado.»

*(Busca la fila en rojo «Fallido» de Ana para mostrar cómo se ve un error y su motivo.)*

### Escena 15 — Reportes (1 min)

«Reportes».

> «Aquí están los indicadores del proyecto: donantes registrados, activos, donaciones del periodo, quiénes pueden volver a donar, distribución por tipo de sangre, resultados que tardan más de 24 horas y cuántos correos salieron o fallaron. Se pueden descargar en Excel.»

Pulsa «Descargar en Excel (CSV)».

Cierra sesión.

---

## PARTE C — Administrador (`99000003` · Administrador Demo)

### Escena 16 — Cuentas de acceso (1 min) ⚠️ difuminar la tabla

«Cuentas de acceso» → «Crear cuenta».

> «Solo el administrador crea cuentas. Se elige el puesto: enfermería, médico responsable, administrador o donante. El sistema genera una contraseña fácil de dictar para donantes y más fuerte para el personal. Si alguien la olvida, se restablece aquí; también se puede desactivar una cuenta sin borrarla.»

Crea una cuenta DEMO: DNI `99000302`, «Prueba Demo», puesto Enfermería. *(La limpieza la borra.)*

### Escena 17 — Parámetros (1 min 30 s) · solo mostrar, no guardar

«Parámetros».

> «Los valores clínicos no están fijos en el código: se pueden ajustar sin tocar el sistema. Aquí están los máximos por año, el intervalo mínimo entre donaciones —hoy provisional, pendiente de confirmar con el médico—, las recomendaciones que ven los donantes, el texto de “¿Dónde y cuándo donar?”, el texto del consentimiento versionado y las plantillas de los correos automáticos. Esas plantillas **necesitan la aprobación de la Jefatura antes de salir**: mientras no estén aprobadas, el sistema no envía nada automático.»

### Escena 18 — Actividad (45 s)

«Actividad».

> «Todo cambio queda registrado: quién, cuándo y qué campos cambiaron. No guarda los valores, solo qué se tocó, para proteger los datos. Esta bitácora solo la ve el administrador.»

### Escena 19 — Derechos ARCO (45 s)

Donantes → busca `Pedro` → ficha → «Datos y privacidad» → «Descargar archivo» (copia de sus datos) y luego «Eliminar datos personales» (hay que escribir el DNI para confirmar).

> «Cumpliendo la ley de protección de datos personales, el donante puede pedir una copia de sus datos o que se eliminen. El administrador descarga sus datos o los anonimiza: se borran nombre, DNI, teléfono y correo y se elimina su cuenta, pero se conserva lo clínico sin identificar a la persona.»

### Escena 20 — Ayuda y Mi cuenta (30 s)

«Ayuda» → muestra que cambia según el puesto. «Mi cuenta» → cambio de contraseña.

> «Cada puesto tiene una guía corta con las tareas más comunes, y cada persona puede cambiar su propia contraseña.»

Cierra sesión.

---

## PARTE D — Donante (celular, modo móvil de 375 px)

### Escena 21 — Portal del donante, con resultado (1 min 30 s)

Ingresa con `99000012` (Juan Ramos Demo) / `demo-luna-mar-12` (ya tiene avisos activados). Más adelante usa a Carmen para la escena del consentimiento.

> «Así lo ve una persona que dona sangre. La pantalla es una sola, con letra grande y colores claros. Arriba dice si hoy puede donar —con un ícono y un color, para que se entienda aunque no se sepa leer bien— y cuántos días faltan.»

Muestra: estado, tipo de sangre, «Tu resultado» con mensaje y recomendaciones, «Mis donaciones», «¿Dónde y cuándo donar?», campañas/información.

> «Si el resultado fuera crítico, aquí simplemente no aparece nada: lo gestiona el personal.»

### Escena 22 — Avisos por correo y consentimiento (45 s)

Pulsa «Quiero recibir avisos» → se abre el texto de consentimiento → marca que lo aceptas → confirma. (Usa a Carmen `99000011`, que aún no activó avisos; luego puedes pulsar «Dejar de recibir avisos».)

> «El donante decide si quiere recibir avisos. Lee el texto, acepta, y puede quitar el permiso cuando quiera.»

### Escena 23 — Más opciones: contraseña y datos (30 s)

«Más opciones» → cambiar contraseña y «Descargar una copia de mis datos».

### Escena 24 — Vista de escritorio del donante (30 s)

Quita el modo celular y recarga.

> «En computadora el mismo portal se ordena en dos columnas.»

Entra también con `99000011` (Carmen) para ver a una donante que aún no activó avisos.

---

## PARTE E — Automatización y cierre

### Escena 25 — Recordatorios automáticos (1 min) · explicación, sin ejecutar

Pantalla del diagrama del README (mermaid, sección «Cómo funciona por dentro») o una diapositiva.

> «Cuatro correos salen solos: cumpleaños a las 8:00, recordatorio de que ya puede volver a donar a las 8:15, agradecimiento por la donación a las 8:30 y reconocimiento al donante frecuente a las 8:45, hora de Lima. Un reloj en Render llama al portal en Vercel, que revisa quién cumple las reglas, envía los correos y los registra. Solo salen correos con plantilla aprobada, solo a quien dio su consentimiento, y nadie recibe el mismo correo dos veces.»

### Escena 26 — Correo recibido (30 s)

Muestra la bandeja de `hemocax26@gmail.com` con los correos de la campaña y el aviso.

> «Este es el correo que recibe el donante: con el nombre del hospital, un mensaje claro y un botón para entrar al portal.»

### Escena 27 — Alcance y límites (45 s)

> «Esta versión cubre los objetivos del proyecto con correo electrónico como canal único. Queda pendiente, para una siguiente etapa, el envío por mensaje de texto (SMS) pensando en donantes sin correo, la programación de campañas a futuro, la validación clínica de los valores —como el intervalo entre donaciones— y la revisión legal del consentimiento por parte del hospital. Gracias.»

---

## Escenas extra (solo si te sobra tiempo; ≈ 3 min en total)

**E1 — Objetivos del proyecto (1 min 30 s).** Muestra en el README de GitHub la tabla «Objetivos específicos OE-01 a OE-07».

> «Cada objetivo del proyecto tiene su función en el sistema: registro de donantes y donaciones, control de máximos e intervalos, resultados con control de acceso, comunicación por correo con consentimiento, automatizaciones y reportes. Esta tabla relaciona cada objetivo con la pantalla que lo cumple.»

**E2 — Panel de personal en el celular (45 s).** Entra como enfermería con el modo celular (375 px) y busca a un donante.

> «El panel del personal también funciona desde el celular, por si el equipo atiende en una campaña fuera del hospital.»

**E3 — Seguridad de los datos (45 s).** Muestra el diagrama de seguridad del README o explica en pantalla de «Actividad».

> «Los permisos se aplican en la base de datos, no solo en la pantalla: un donante solo puede ver sus propios datos, un resultado crítico no es legible para él ni por error, y la enfermería no puede liberar resultados ni crear cuentas. Los cambios importantes quedan en la bitácora.»

---

## Consejos de edición

- Habla pausado; es mejor grabar por escenas y unirlas.
- Si te equivocas, no repitas todo: haz una pausa de 3 segundos, repite la frase y corta después.
- Acelera (1.5×) los momentos de espera o de escritura.
- Difumina: la tabla de «Cuentas de acceso» y cualquier nombre real que aparezca.
- Duración: ver el cuadro de tiempos del inicio (máximo 20 min).

## Al terminar

```bash
node demo/limpiar-demo.js
```

Debe imprimir: `Listo. Cuentas que quedan: 00000001, 60879417, …` y solo 6 donantes. Si quieres volver a grabar, ejecuta primero la limpieza y luego `node demo/seed-demo.js`.
