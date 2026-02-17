# Carpeta de PDFs de Bitácoras

Esta carpeta es para almacenar los PDFs de bitácoras electrónicas generados por Sernapesca.

## Instrucciones:

1. **Colocar aquí los PDFs** de bitácoras electrónicas
2. Formato esperado: "Representación Impresa de Bitácora Electrónica"
3. Nombre recomendado: `Nave_Folio.pdf` (ejemplo: `Rauten_3088.pdf`)

## Procesamiento:

```bash
python main.py data/pdfs/tu_bitacora.pdf
```

## Estructura esperada del PDF:

El PDF debe contener:
- ✓ Cabecera con datos de la nave
- ✓ Fechas de zarpe y recalada
- ✓ Tabla de detalle de lances
- ✓ Coordenadas en formato grados/minutos
- ✓ Capturas por especie

---

**NOTA:** Por seguridad, los PDFs NO se sincronizan con Git (están en .gitignore)
