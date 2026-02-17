# Sistema de Bitácoras MSC
## Pesquera Quintero S.A.

Sistema para procesar bitácoras electrónicas y facilitar certificación MSC.

---

## ⚡ INICIO RÁPIDO

```powershell
# 1. Instalar
pip install -r requirements.txt

# 2. Verificar
python verificar_sistema.py

# 3. Probar
python main.py --test
```

---

## 📁 ARCHIVOS CLAVE

- **`QUE_FALTA.md`** ← EMPIEZA AQUÍ (pasos pendientes Firebase)
- **`INSTRUCCIONES_RAPIDAS.md`** ← Comandos principales
- **`docs\FIREBASE_SETUP.md`** ← Configuración Firebase detallada

---

## 🔥 TU FIREBASE

- Proyecto: **BENTOS**
- ID: **bentos-a0be7**
- Estado: ⚠️ Pendiente descargar credenciales

Ver: `QUE_FALTA.md` para completar setup

---

## 📊 USO DEL SISTEMA

### Generar datos de ejemplo:
```powershell
python generar_datos_ejemplo.py --firebase
```

### Procesar un PDF:
```powershell
python main.py data\pdfs\bitacora.pdf
```

### Visualizar resultados:
```powershell
python visualizar_datos.py
```

---

## 🛠️ MÓDULOS PRINCIPALES

- **`backend\pdf_parser.py`** - Extrae datos de PDFs
- **`backend\firebase_manager.py`** - Maneja Firebase
- **`backend\coordinate_converter.py`** - Convierte coordenadas
- **`backend\especies_config.py`** - Categorización MSC

---

## 📦 ESTRUCTURA

```
SOFTWARE TI/
├── main.py                    - Script principal
├── QUE_FALTA.md              - Pasos pendientes
├── backend/                   - Código Python
├── data/pdfs/                - PDFs de entrada
├── data/output/              - JSONs generados
└── config/                    - Credenciales Firebase
```

---

## ✅ CARACTERÍSTICAS

- Extracción automática de datos desde PDFs
- Conversión de coordenadas GPS
- Categorización de especies según MSC
- Cálculo de indicadores de sostenibilidad
- Validación automática de totales
- Almacenamiento en Firebase/JSON

---

## 🆘 AYUDA

**Error instalando:** Ejecutar `pip install -r requirements.txt`  
**Firebase no funciona:** Ver `QUE_FALTA.md`  
**Parser no lee PDF:** Normal, requiere ajuste con PDF real  
**Otros problemas:** Ejecutar `python verificar_sistema.py`
