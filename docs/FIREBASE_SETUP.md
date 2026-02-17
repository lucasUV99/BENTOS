# Configuración Firebase - Pasos Restantes

Tu proyecto: **BENTOS** (ID: bentos-a0be7)

---

## 1️⃣ Habilitar Firestore Database

1. En el menú lateral, ir a **"Firestore Database"**
2. Clic en **"Crear base de datos"** o **"Create database"**
3. Seleccionar modo:
   - **Producción:** Para uso real
   - **Prueba:** Para desarrollo (expira en 30 días)
   
   👉 Recomendación: Empezar en **modo prueba**, luego cambiar a producción

4. Seleccionar ubicación del servidor:
   - Para Chile, elegir: **`southamerica-east1` (São Paulo)**
   - O usar: **`us-central1`** si no está disponible

5. Clic en **"Habilitar"**

---

## 2️⃣ Configurar Reglas (Modo Desarrollo)

1. En Firestore, ir a la pestaña **"Reglas"**
2. Para desarrollo, usar estas reglas (⚠️ **TEMPORAL**):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // REGLAS DE DESARROLLO - Permitir todo
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

---

## 3️⃣ Descargar Credenciales

Esta es la parte más importante para conectar Python con Firebase.

1. Ir a **Configuración del proyecto** (ícono de engranaje ⚙️ arriba a la izquierda)
2. Ir a la pestaña **"Cuentas de servicio"** o **"Service accounts"**
3. Seleccionar **"Python"** como lenguaje
4. Hacer clic en **"Generar nueva clave privada"** o **"Generate new private key"**
5. Confirmar en el diálogo
6. Se descargará un archivo JSON con un nombre como:
   ```
   pesquera-quintero-msc-a1b2c3d4e5f6.json
   ```

---

## 4️⃣ Colocar Credenciales en el Proyecto

1. Renombrar el archivo descargado a:
   ```
   firebase-credentials.json
   ```

2. Mover el archivo a la carpeta del proyecto:
   ```
   SOFTWARE TI/
   └── config/
       └── firebase-credentials.json  ← Aquí
   ```

3. ⚠️ **IMPORTANTE:** Nunca subir este archivo a GitHub
   - Ya está en el `.gitignore`
   - Contiene claves privadas

---

## 5️⃣ Probar Conexión

```powershell
python backend\firebase_manager.py
```

**Salida esperada:**
```
✓ Conexión establecida
✓ Escritura exitosa  
✓ Test completado
```

Si hay errores:
- Verificar que `firebase-credentials.json` está en `config\`
- Verificar que instalaste dependencias: `pip install firebase-admin`

