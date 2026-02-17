# ✅ LO QUE TE FALTA HACER

## Tu Firebase:
- ✅ Proyecto creado: BENTOS
- ✅ ID: bentos-a0be7
- ✅ .env actualizado

---

## 🔥 PASOS QUE FALTAN:

### 1. Descargar credenciales de Firebase (5 minutos)

1. Ve a: https://console.firebase.google.com
2. Selecciona tu proyecto **BENTOS**
3. Click en el engranaje ⚙️ (arriba izquierda) → **Configuración del proyecto**
4. Pestaña **"Cuentas de servicio"**
5. Click en **"Generar nueva clave privada"**
6. Se descarga un archivo JSON (ej: `bentos-a0be7-firebase-adminsdk-xxxxx.json`)

### 2. Mover el archivo de credenciales

1. **Renombrar** el archivo descargado a: `firebase-credentials.json`
2. **Mover** a: `SOFTWARE TI\config\firebase-credentials.json`

### 3. Habilitar Firestore Database

1. En Firebase Console → **Firestore Database** (menú izquierdo)
2. Click **"Crear base de datos"**
3. Modo: **"Prueba"** (por ahora)
4. Ubicación: **southamerica-east1** (São Paulo - más cerca de Chile)
5. Click **"Habilitar"**

### 4. Configurar reglas (modo desarrollo)

En Firestore → Pestaña **"Reglas"**, pega esto:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

Click **"Publicar"**

---

## 🧪 PROBAR QUE FUNCIONA:

```powershell
# 1. Instalar dependencias (si no lo hiciste)
pip install -r requirements.txt

# 2. Probar Firebase
python backend\firebase_manager.py
```

**Deberías ver:**
```
✓ Conexión establecida
✓ Escritura exitosa
✓ Test completado
```

---

## 🚀 USAR EL SISTEMA:

### Generar datos de ejemplo:
```powershell
python generar_datos_ejemplo.py --firebase
```

### Ver datos en Firebase:
1. Ve a Firebase Console
2. Firestore Database
3. Verás la colección **"viajes"** con datos

### Procesar un PDF real (cuando lo tengas):
```powershell
python main.py data\pdfs\tu_bitacora.pdf
```

---

## ⚠️ SI HAY ERRORES:

**Error: "Could not automatically determine credentials"**
→ El archivo `config\firebase-credentials.json` no existe o está mal ubicado

**Error: "Project bentos-a0be7 was not found"**
→ Verificar que el ID en `.env` es correcto

**Error: "Permission denied"**
→ Verificar que las reglas de Firestore están configuradas

---

## 📋 CHECKLIST:

- [ ] Credenciales descargadas de Firebase
- [ ] Archivo renombrado a `firebase-credentials.json`
- [ ] Archivo movido a `config\firebase-credentials.json`
- [ ] Firestore Database habilitado
- [ ] Reglas de Firestore configuradas
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Test de Firebase exitoso (`python backend\firebase_manager.py`)

---

**Cuando completes estos pasos, el sistema estará 100% funcional.**
