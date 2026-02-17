# Sistema de Bitácoras MSC - Instrucciones Rápidas

## ⚡ INICIO RÁPIDO (5 minutos)

### 1. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 2. Verificar sistema
```powershell
python verificar_sistema.py
```

### 3. Ejecutar tests
```powershell
python main.py --test
```

---

## 🔥 CONFIGURAR FIREBASE

**Tu proyecto:** BENTOS (ID: bentos-a0be7)

📄 Ver pasos detallados en: `QUE_FALTA.md`

Resumen:
1. Descargar credenciales desde Firebase Console
2. Guardar como `config\firebase-credentials.json`
3. Habilitar Firestore Database
4. Probar: `python backend\firebase_manager.py`

---

## 🧪 GENERAR DATOS DE EJEMPLO

```powershell
# Genera JSON local
python generar_datos_ejemplo.py

# Genera y sube a Firebase
python generar_datos_ejemplo.py --firebase
```

---

## 📄 PROCESAR UN PDF

Cuando tengas un PDF de bitácora:

```powershell
# Colocar PDF en data\pdfs\

# Procesar
python main.py data\pdfs\nombre.pdf
```

---

## 👁️ VISUALIZAR DATOS

```powershell
python visualizar_datos.py
```

---

## 📚 ARCHIVOS IMPORTANTES

- `QUE_FALTA.md` - Pasos pendientes para Firebase
- `README.md` - Documentación completa
- `docs\FIREBASE_SETUP.md` - Detalles de Firebase

---

## 🆘 PROBLEMAS COMUNES

**Error al instalar:** `pip install -r requirements.txt`  
**Firebase no conecta:** Ver `QUE_FALTA.md`  
**PDF no se lee:** El parser necesita ajustes (normal)
