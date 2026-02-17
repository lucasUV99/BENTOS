# Carpeta de Salida de Datos

Esta carpeta contiene los archivos JSON generados por el sistema cuando opera en modo local (sin Firebase).

## Archivos que encontrarás aquí:

- `ejemplo_viaje_RAUTEN_3088.json` - Datos de ejemplo generados
- `SERNAPESCA-BE2021-XXXX-X.json` - Datos procesados de PDFs reales

## Formato de archivos:

Cada archivo JSON contiene:
- **viaje:** Información de la cabecera del viaje
- **lances:** Array con todos los lances del viaje
- **validacion:** Resultados de validación y estadísticas

## Visualización:

Para ver el contenido de forma amigable:
```bash
python visualizar_datos.py data/output/nombre_archivo.json
```

---

**NOTA:** Esta carpeta NO se sincroniza con Git (está en .gitignore)
