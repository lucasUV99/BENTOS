"""
Sistema de Auto-Actualización para BENTOS
==========================================
Permite al desarrollador publicar nuevas versiones y que todos los clientes
se actualicen automáticamente al iniciar la aplicación.

Flujo:
1. Desarrollador ejecuta `publicar_version.py` → sube nueva versión a Firebase
2. Cliente inicia la app → compara versión local vs Firebase
3. Si hay actualización → descarga el nuevo .exe/.app y reemplaza el actual
"""

import os
import sys
import json
import shutil
import hashlib
import platform
import subprocess
import tempfile
from datetime import datetime
from typing import Optional, Dict, Tuple
from packaging import version as pkg_version

# Versión actual de la aplicación
APP_VERSION = "1.0.3"

# Colección de Firebase para configuración de versiones
VERSION_COLLECTION = "config"
VERSION_DOCUMENT = "app_version"


def aplicar_actualizacion_pendiente() -> bool:
    """
    Verifica si hay una actualización pendiente (descargada pero no aplicada)
    y la aplica al inicio de la aplicación.
    
    Esto actúa como fallback si el script .bat/.sh no logró reemplazar el exe.
    
    Debe llamarse MUY TEMPRANO en el arranque, antes de crear la ventana.
    
    Returns:
        True si se aplicó una actualización y hay que reiniciar
    """
    if not getattr(sys, 'frozen', False):
        return False  # Solo en modo compilado
    
    exe_actual = sys.executable
    exe_dir = os.path.dirname(exe_actual)
    exe_name = os.path.basename(exe_actual)
    base_name = os.path.splitext(exe_name)[0]
    
    # Limpiar exe antiguo de una actualización previa exitosa
    old_exe = os.path.join(exe_dir, f"{base_name}_old.exe")
    if os.path.exists(old_exe):
        try:
            os.remove(old_exe)
            print(f"🧹 Limpiado exe antiguo: {old_exe}")
        except Exception:
            pass  # No importa si falla, se limpia la próxima vez
    
    # Buscar actualización pendiente
    update_exe = os.path.join(exe_dir, f"{base_name}_update.exe")
    if not os.path.exists(update_exe):
        return False  # No hay actualización pendiente
    
    # Verificar que el archivo de actualización es válido (> 1MB)
    update_size = os.path.getsize(update_exe)
    if update_size < 1_000_000:
        print(f"⚠️ Archivo de actualización muy pequeño ({update_size} bytes), eliminando")
        try:
            os.remove(update_exe)
        except Exception:
            pass
        return False
    
    print(f"🔄 Actualización pendiente encontrada: {update_exe} ({update_size:,} bytes)")
    
    try:
        # Paso 1: Renombrar el exe actual (se puede renombrar un exe en ejecución en Windows)
        if os.path.exists(old_exe):
            os.remove(old_exe)
        os.rename(exe_actual, old_exe)
        print(f"  → Renombrado {exe_name} → {os.path.basename(old_exe)}")
        
        # Paso 2: Mover la actualización al nombre correcto
        shutil.move(update_exe, exe_actual)
        print(f"  → Movido actualización → {exe_name}")
        
        # Paso 3: Iniciar el nuevo exe
        print(f"  → Reiniciando {exe_name}...")
        subprocess.Popen([exe_actual], close_fds=True)
        
        return True  # Indicar al llamador que debe salir
        
    except Exception as e:
        print(f"❌ Error aplicando actualización pendiente: {e}")
        # Intentar restaurar si algo falló
        if not os.path.exists(exe_actual) and os.path.exists(old_exe):
            try:
                os.rename(old_exe, exe_actual)
                print("  → Restaurado exe original")
            except Exception:
                pass
        # Limpiar el archivo de update si sigue ahí
        if os.path.exists(update_exe):
            try:
                os.remove(update_exe)
            except Exception:
                pass
        return False


class UpdateManager:
    """Gestor de actualizaciones automáticas"""
    
    def __init__(self, firebase_manager):
        """
        Args:
            firebase_manager: Instancia de FirebaseManager con conexión activa
        """
        self.firebase = firebase_manager
        self.db = firebase_manager.db if firebase_manager else None
        self._base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def obtener_version_local(self) -> str:
        """Retorna la versión actual de la aplicación"""
        return APP_VERSION
    
    def obtener_version_remota(self) -> Optional[Dict]:
        """
        Consulta Firebase para obtener la última versión disponible.
        
        Returns:
            Dict con info de versión o None si no se puede consultar.
            Ejemplo: {
                'version': '1.1.0',
                'url_windows': 'https://...',
                'url_macos': 'https://...',
                'notas': 'Corrección de bugs...',
                'obligatoria': False,
                'fecha': datetime,
                'sha256_windows': '...',
                'sha256_macos': '...'
            }
        """
        if not self.db:
            return None
        
        try:
            doc = self.db.collection(VERSION_COLLECTION).document(VERSION_DOCUMENT).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"⚠️ Error consultando versión remota: {e}")
            return None
    
    def hay_actualizacion(self) -> Tuple[bool, Optional[Dict]]:
        """
        Verifica si hay una actualización disponible.
        
        Returns:
            Tuple (hay_update: bool, info_version: dict o None)
        """
        info_remota = self.obtener_version_remota()
        if not info_remota:
            return False, None
        
        version_remota = info_remota.get('version', '0.0.0')
        version_local = self.obtener_version_local()
        
        try:
            hay_update = pkg_version.parse(version_remota) > pkg_version.parse(version_local)
        except Exception:
            # Fallback a comparación de strings
            hay_update = version_remota > version_local
        
        return hay_update, info_remota if hay_update else None
    
    def obtener_url_descarga(self, info_version: Dict) -> Optional[str]:
        """Obtiene la URL de descarga según el SO actual"""
        sistema = platform.system()
        if sistema == "Windows":
            return info_version.get('url_windows')
        elif sistema == "Darwin":
            return info_version.get('url_macos')
        return None
    
    def obtener_hash_esperado(self, info_version: Dict) -> Optional[str]:
        """Obtiene el hash SHA256 esperado según el SO actual"""
        sistema = platform.system()
        if sistema == "Windows":
            return info_version.get('sha256_windows')
        elif sistema == "Darwin":
            return info_version.get('sha256_macos')
        return None
    
    def descargar_actualizacion(self, url: str, destino: str, hash_esperado: Optional[str] = None) -> bool:
        """
        Descarga la actualización desde la URL proporcionada.
        
        Args:
            url: URL de descarga del archivo
            destino: Ruta local donde guardar el archivo
            hash_esperado: Hash SHA256 esperado (opcional, para verificación)
        
        Returns:
            True si la descarga fue exitosa
        """
        try:
            import urllib.request
            import urllib.error
            import ssl
            
            print(f"📥 Descargando actualización desde: {url}")
            
            # Crear contexto SSL que acepte certificados
            ctx = ssl.create_default_context()
            
            # Crear request con User-Agent (GitHub requiere uno)
            req = urllib.request.Request(url, headers={
                'User-Agent': 'BENTOS-Updater/1.0',
                'Accept': 'application/octet-stream'
            })
            
            # Descargar con manejo de redirecciones
            with urllib.request.urlopen(req, context=ctx, timeout=180) as response:
                # Verificar Content-Type (GitHub devuelve application/octet-stream)
                content_type = response.headers.get('Content-Type', '')
                print(f"  Content-Type: {content_type}")
                if 'text/html' in content_type or 'application/json' in content_type:
                    print(f"❌ El servidor devolvió {content_type} en vez de un binario")
                    print("   La URL no apunta a un archivo descargable")
                    return False
                
                total = response.headers.get('Content-Length')
                if total:
                    total_mb = int(total) / (1024 * 1024)
                    print(f"  Tamaño esperado: {total_mb:.1f} MB")
                    # El exe de BENTOS pesa ~80 MB, rechazar si es < 10 MB
                    if int(total) < 10_000_000:
                        print(f"❌ Archivo demasiado pequeño ({total_mb:.1f} MB). Se esperan ~80 MB")
                        print("   Posible página de error o archivo incorrecto")
                        return False
                
                descargado = 0
                block_size = 65536  # 64KB bloques para mayor velocidad
                
                with open(destino, 'wb') as f:
                    while True:
                        bloque = response.read(block_size)
                        if not bloque:
                            break
                        f.write(bloque)
                        descargado += len(bloque)
                        if total:
                            pct = descargado * 100 / int(total)
                            print(f"\r  Progreso: {pct:.0f}% ({descargado // (1024*1024)} MB)", end="", flush=True)
                
                print()  # Nueva línea después del progreso
            
            # === VALIDACIÓN ESTRICTA DEL ARCHIVO DESCARGADO ===
            
            # 1. Verificar existencia y tamaño mínimo (10 MB)
            if not os.path.exists(destino):
                print("❌ El archivo descargado no existe")
                return False
            
            file_size = os.path.getsize(destino)
            file_size_mb = file_size / (1024 * 1024)
            print(f"  Archivo descargado: {file_size_mb:.1f} MB")
            
            if file_size < 10_000_000:
                print(f"❌ Archivo demasiado pequeño ({file_size_mb:.1f} MB)")
                # Intentar leer contenido para diagnosticar
                with open(destino, 'rb') as f:
                    inicio = f.read(500)
                if b'<!DOCTYPE' in inicio or b'<html' in inicio or b'<HTML' in inicio:
                    print("   → Se descargó una página HTML (probablemente error 404)")
                    print("   → Verifica que el repositorio de GitHub sea PÚBLICO")
                elif b'{"' in inicio or b'Not Found' in inicio:
                    print("   → Se recibió una respuesta JSON/texto de error")
                else:
                    print(f"   → Primeros bytes: {inicio[:50]}")
                os.unlink(destino)
                return False
            
            # 2. Verificar que es un ejecutable Windows válido (cabecera MZ/PE)
            with open(destino, 'rb') as f:
                header = f.read(2)
            if header != b'MZ':
                print(f"❌ El archivo descargado NO es un ejecutable válido")
                print(f"   Cabecera: {header!r} (se esperaba b'MZ')")
                os.unlink(destino)
                return False
            print("✅ Cabecera PE válida (MZ)")
            
            # 3. Verificar integridad con hash SHA256
            if hash_esperado:
                hash_real = self._calcular_sha256(destino)
                if hash_real != hash_esperado:
                    print(f"❌ Hash no coincide:")
                    print(f"   Esperado: {hash_esperado}")
                    print(f"   Real:     {hash_real}")
                    os.unlink(destino)
                    return False
                print("✅ Integridad verificada (SHA256)")
            else:
                print("⚠️ No se proporcionó hash SHA256 — no se puede verificar integridad")
            
            print(f"✅ Descarga completada y validada: {destino} ({file_size_mb:.1f} MB)")
            return True
            
        except Exception as e:
            print(f"❌ Error descargando actualización: {e}")
            # Limpiar archivo parcial
            if os.path.exists(destino):
                try:
                    os.unlink(destino)
                except Exception:
                    pass
            return False
    
    def aplicar_actualizacion(self, ruta_nuevo_exe: str) -> bool:
        """
        Aplica la actualización reemplazando el ejecutable actual.
        
        En Windows: Crea un script .bat que espera a que el proceso actual termine,
        reemplaza el .exe y lo reinicia.
        
        En macOS: Usa un script shell equivalente.
        
        Args:
            ruta_nuevo_exe: Ruta al nuevo ejecutable descargado
            
        Returns:
            True si el proceso de actualización se inició correctamente
        """
        exe_actual = sys.executable
        
        # Si estamos ejecutando desde Python (no frozen/compiled), no reemplazar
        if not getattr(sys, 'frozen', False):
            print("⚠️ Modo desarrollo: no se reemplaza el ejecutable")
            print(f"   Nuevo archivo disponible en: {ruta_nuevo_exe}")
            return True
        
        sistema = platform.system()
        
        try:
            if sistema == "Windows":
                return self._aplicar_windows(exe_actual, ruta_nuevo_exe)
            elif sistema == "Darwin":
                return self._aplicar_macos(exe_actual, ruta_nuevo_exe)
            else:
                print(f"❌ Sistema operativo no soportado: {sistema}")
                return False
        except Exception as e:
            print(f"❌ Error aplicando actualización: {e}")
            return False
    
    def _aplicar_windows(self, exe_actual: str, ruta_nuevo: str) -> bool:
        """
        Aplica actualización en Windows usando el truco de renombrar.
        
        En Windows se puede renombrar un .exe en ejecución (no borrar ni sobrescribir).
        Flujo:
        1. Renombrar exe actual → BENTOS_old.exe (funciona aunque esté en ejecución)
        2. Mover el nuevo → BENTOS.exe
        3. Lanzar el nuevo BENTOS.exe
        4. El viejo se limpia al próximo inicio (aplicar_actualizacion_pendiente)
        
        No necesita .bat, no depende de timings ni de procesos externos.
        """
        exe_dir = os.path.dirname(exe_actual)
        exe_name = os.path.basename(exe_actual)
        base_name = os.path.splitext(exe_name)[0]
        old_path = os.path.join(exe_dir, f"{base_name}_old.exe")
        
        print(f"📦 Aplicando actualización...")
        print(f"   Exe actual: {exe_actual} ({os.path.getsize(exe_actual):,} bytes)")
        print(f"   Nuevo exe:  {ruta_nuevo} ({os.path.getsize(ruta_nuevo):,} bytes)")
        
        try:
            # Paso 1: Limpiar _old.exe si existe de una actualización anterior
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    print(f"   🧹 Limpiado: {os.path.basename(old_path)}")
                except Exception:
                    # Si no se puede borrar, intentar otro nombre
                    old_path = os.path.join(exe_dir, f"{base_name}_old2.exe")
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except Exception:
                            pass
            
            # Paso 2: Renombrar el exe en ejecución (Windows lo permite)
            os.rename(exe_actual, old_path)
            print(f"   ✅ Renombrado {exe_name} → {os.path.basename(old_path)}")
            
            # Paso 3: Mover el nuevo exe al nombre correcto
            shutil.move(ruta_nuevo, exe_actual)
            new_size = os.path.getsize(exe_actual)
            print(f"   ✅ Nuevo exe en posición: {exe_name} ({new_size:,} bytes)")
            
            # Paso 4: Validar que el nuevo exe tiene cabecera PE válida
            with open(exe_actual, 'rb') as f:
                header = f.read(2)
            if header != b'MZ':
                print(f"   ❌ Nuevo exe no tiene cabecera PE válida, restaurando...")
                os.remove(exe_actual)
                os.rename(old_path, exe_actual)
                return False
            
            # Paso 5: Lanzar el nuevo exe
            print(f"   🚀 Lanzando nueva versión...")
            subprocess.Popen(
                [exe_actual],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                close_fds=True
            )
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            # Intentar restaurar si algo falló
            if not os.path.exists(exe_actual) and os.path.exists(old_path):
                try:
                    os.rename(old_path, exe_actual)
                    print(f"   ↩️ Restaurado exe original")
                except Exception as e2:
                    print(f"   ❌ No se pudo restaurar: {e2}")
            return False
    
    def _aplicar_macos(self, exe_actual: str, ruta_nuevo: str) -> bool:
        """Aplica actualización en macOS usando un script shell"""
        sh_path = os.path.join(tempfile.gettempdir(), "bentos_update.sh")
        
        sh_content = f'''#!/bin/bash
echo "Actualizando BENTOS..."
sleep 2
while kill -0 {os.getpid()} 2>/dev/null; do
    sleep 1
done
cp -f "{ruta_nuevo}" "{exe_actual}"
chmod +x "{exe_actual}"
rm -f "{ruta_nuevo}"
echo "Actualización completada. Reiniciando..."
open "{exe_actual}"
rm -f "{sh_path}"
'''
        
        with open(sh_path, 'w') as f:
            f.write(sh_content)
        
        os.chmod(sh_path, 0o755)
        subprocess.Popen(['bash', sh_path])
        
        return True
    
    def _calcular_sha256(self, filepath: str) -> str:
        """Calcula el hash SHA256 de un archivo"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    # ===== MÉTODOS PARA EL DESARROLLADOR =====
    
    def publicar_version(self, nueva_version: str, url_windows: str = "",
                         url_macos: str = "", notas: str = "",
                         obligatoria: bool = False,
                         sha256_windows: str = "", sha256_macos: str = "") -> bool:
        """
        Publica una nueva versión en Firebase (para uso del desarrollador).
        
        Args:
            nueva_version: Número de versión (ej: "1.1.0")
            url_windows: URL de descarga del .exe de Windows
            url_macos: URL de descarga del .app de macOS
            notas: Notas de la actualización
            obligatoria: Si la actualización es obligatoria
            sha256_windows: Hash SHA256 del archivo Windows
            sha256_macos: Hash SHA256 del archivo macOS
            
        Returns:
            True si se publicó correctamente
        """
        if not self.db:
            print("❌ No hay conexión a Firebase")
            return False
        
        try:
            data = {
                'version': nueva_version,
                'url_windows': url_windows,
                'url_macos': url_macos,
                'notas': notas,
                'obligatoria': obligatoria,
                'sha256_windows': sha256_windows,
                'sha256_macos': sha256_macos,
                'fecha': datetime.now(),
                'publicado_por': platform.node()
            }
            
            self.db.collection(VERSION_COLLECTION).document(VERSION_DOCUMENT).set(data)
            print(f"✅ Versión {nueva_version} publicada correctamente en Firebase")
            return True
            
        except Exception as e:
            print(f"❌ Error publicando versión: {e}")
            return False
