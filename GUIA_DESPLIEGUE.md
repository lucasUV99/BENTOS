# BENTOS — Guía de Despliegue y Actualización

## Índice
1. [Construir el Instalador](#1-construir-el-instalador)
2. [Preparar el Pendrive](#2-preparar-el-pendrive)
3. [Instalar en Equipos](#3-instalar-en-equipos)
4. [Sistema de Auto-Actualización](#4-sistema-de-auto-actualización)
5. [Publicar una Nueva Versión](#5-publicar-una-nueva-versión)
6. [Flujo Completo de Actualización](#6-flujo-completo-de-actualización)
7. [Solución de Problemas](#7-solución-de-problemas)

---

## 1. Construir el Instalador

### Windows (desde tu PC)

```powershell
# Opción 1: Solo construir
.\construir_windows.ps1

# Opción 2: Construir y copiar al pendrive (ej: unidad E:)
.\construir_windows.ps1 -CopiarA "E:\BENTOS"
```

El ejecutable se genera en `dist/BENTOS.exe`.

### macOS (desde un Mac)

> ⚠️ **IMPORTANTE**: El .app para macOS DEBE compilarse desde un equipo macOS.
> No se puede generar desde Windows.

```bash
# Copiar el proyecto al Mac (USB, red, git, etc.)
# Crear entorno virtual en el Mac:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller

# Construir
chmod +x construir_macos.sh
./construir_macos.sh

# O construir y copiar a pendrive
./construir_macos.sh /Volumes/USB/BENTOS
```

El resultado se genera en `dist/BENTOS.app`.

---

## 2. Preparar el Pendrive

Estructura recomendada del pendrive:

```
USB/
├── Windows/
│   ├── BENTOS.exe
│   └── INSTRUCCIONES.txt
├── macOS/
│   ├── BENTOS.app/
│   └── INSTRUCCIONES.txt
└── README.txt
```

Los scripts de construcción crean esta estructura automáticamente si usas el parámetro de destino.

---

## 3. Instalar en Equipos

### Windows
1. Copiar `BENTOS.exe` al escritorio del equipo
2. Doble clic para ejecutar
3. Si aparece Windows SmartScreen: *"Más información"* → *"Ejecutar de todos modos"*

### macOS
1. Arrastrar `BENTOS.app` a la carpeta Aplicaciones
2. Primera ejecución: clic derecho → *"Abrir"* → *"Abrir"* (para pasar Gatekeeper)

---

## 4. Sistema de Auto-Actualización

### ¿Cómo funciona?

1. Al iniciar la app, consulta Firebase (`config/app_version`) para ver si hay una versión más nueva
2. Si hay actualización, muestra un diálogo al usuario
3. Si el usuario acepta, descarga el nuevo .exe/.app desde la URL configurada
4. Reemplaza el ejecutable actual y reinicia la app

### Arquitectura

```
Tu PC (Desarrollador)                    Firebase Firestore
  │                                        ┌──────────────────────┐
  │  publicar_version.py                   │ config/app_version   │
  │──────────────────────────────────────→ │  version: "1.1.0"    │
  │                                        │  url_windows: "..."  │
                                           │  url_macos: "..."    │
                                           │  obligatoria: false  │
                                           └──────┬───────────────┘
                                                   │
                              ┌─────────────────────┤
                              │                     │
                         Equipo A              Equipo B
                         (Windows)             (macOS)
                         BENTOS.exe            BENTOS.app
                         v1.0.0                v1.0.0
                              │                     │
                              ▼                     ▼
                         "¿Actualizar?"        "¿Actualizar?"
                              │                     │
                              ▼                     ▼
                         Descarga .exe         Descarga .app
                         → v1.1.0              → v1.1.0
```

---

## 5. Publicar una Nueva Versión

### Paso 1: Hacer los cambios en el código

Editar `backend/updater.py` y cambiar:
```python
APP_VERSION = "1.1.0"  # ← Nueva versión
```

### Paso 2: Reconstruir los ejecutables

```powershell
# Windows
.\construir_windows.ps1

# macOS (en un Mac)
./construir_macos.sh
```

### Paso 3: Subir los ejecutables a un servidor

Opciones:
- **GitHub Releases** (recomendado, gratuito)
- **Google Drive** (enlace directo de descarga)
- **Firebase Storage**
- Cualquier URL directa de descarga

### Paso 4: Publicar la versión en Firebase

```powershell
python publicar_version.py
```

El script te pedirá:
- Número de versión (ej: `1.1.0`)
- Notas del cambio
- Si es obligatoria
- URL del .exe de Windows
- URL del .app de macOS

### Ejemplo con GitHub Releases

1. Crea un repositorio privado en GitHub
2. Ve a *Releases* → *Create new release*
3. Tag: `v1.1.0`
4. Sube `BENTOS.exe` y `BENTOS.app` como assets
5. Copia las URLs de descarga directa
6. Ejecuta `publicar_version.py` con esas URLs

---

## 6. Flujo Completo de Actualización

```
1. Corriges un bug en app.py
2. Cambias APP_VERSION a "1.1.0" en backend/updater.py
3. Ejecutas: .\construir_windows.ps1
4. (En Mac) Ejecutas: ./construir_macos.sh
5. Subes BENTOS.exe y BENTOS.app a GitHub Releases
6. Ejecutas: python publicar_version.py
   → Ingresas versión: 1.1.0
   → Ingresas URL de Windows
   → Ingresas URL de macOS
   → Confirmas publicación
7. ¡Listo! La próxima vez que cualquier equipo abra BENTOS,
   verá el diálogo de actualización.
```

---

## 7. Solución de Problemas

### "Windows SmartScreen bloqueó la aplicación"
→ Clic en *"Más información"* → *"Ejecutar de todos modos"*

### "macOS no permite abrir la aplicación"
→ Clic derecho en BENTOS.app → *"Abrir"* → *"Abrir"*
→ O: Preferencias del Sistema → Seguridad → *"Abrir de todos modos"*

### La actualización no aparece
- Verificar conexión a internet
- Verificar que se publicó correctamente: revisar Firebase Console → Firestore → `config/app_version`
- Verificar que `APP_VERSION` en el ejecutable actual es menor que la versión publicada

### Error al descargar actualización
- Verificar que la URL de descarga es accesible (directa, no requiere login)
- Para GitHub: usar URL del tipo `https://github.com/USUARIO/REPO/releases/download/vX.X.X/BENTOS.exe`

### El .exe es muy grande
- Es normal, PyInstaller empaqueta Python + todas las dependencias
- Típicamente 80-150 MB
- Se puede reducir excluyendo dependencias innecesarias en el .spec

### Error de Firebase al compilar
- Asegurarse de que `config/firebase-credentials.json` existe
- El archivo se empaqueta dentro del .exe automáticamente
