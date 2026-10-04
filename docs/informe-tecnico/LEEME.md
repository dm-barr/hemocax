# Informe técnico — HEMOCAX

`HEMOCAX_Informe_Tecnico.docx` describe la arquitectura, el modelo de datos, la seguridad, los algoritmos, el despliegue, las pruebas y los hallazgos del sistema.

```bash
pip install python-docx matplotlib      # y tener Graphviz instalado (comando `dot`)
python informe_tecnico.py               # regenera fig/*.png y el .docx
```

- Las cifras de código (líneas, archivos) se recuentan al generar el informe.
- Las cifras de la base de datos (13 tablas, 23 políticas, 14 funciones, 9 triggers, 30 índices) y del build (22 s + 16 s, 276 KB gzip) se midieron el 04/10/2026; si cambian, edita `tec_a.py`, `tec_b.py` y `tec_c.py`.
- Reutiliza las utilidades de Word de `../gestion-proyectos/docx_utils.py`.
- `probar_migracion_donante.js` prueba la migración `20261004000400` dentro de una transacción que se deshace.
