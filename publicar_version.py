"""
Publicar Nueva Versión de BENTOS
=================================
Ejecuta este script desde tu PC de desarrollo para publicar
una nueva versión que se actualizará en todos los equipos.

Uso:
    python publicar_version.py

El script te pedirá:
1. Número de versión (ej: 1.1.0)
2. Notas del cambio
3. Ruta al .exe de Windows (opcional)
4. Ruta al .app/.dmg de macOS (opcional)
5. URLs de descarga (donde subiste los archivos)
"""

import os
import sys
import hashlib

# Agregar path del backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from firebase_manager import FirebaseManager
from updater import UpdateManager, APP_VERSION


def calcular_sha256(filepath: str) -> str:
    """Calcula el SHA256 de un archivo"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def main():
    print("=" * 60)
    print("  BENTOS — Publicar Nueva Versión")
    print("=" * 60)
    print(f"\n  Versión actual instalada: {APP_VERSION}\n")
    
    # Conectar a Firebase
    firebase = FirebaseManager()
    if not firebase.db:
        print("❌ No se pudo conectar a Firebase.")
        print("   Asegúrate de tener config/firebase-credentials.json")
        input("\nPresiona Enter para salir...")
        return
    
    updater = UpdateManager(firebase)
    
    # Verificar versión actual en la nube
    info_remota = updater.obtener_version_remota()
    if info_remota:
        print(f"  Versión actual en la nube: {info_remota.get('version', 'N/A')}")
        print(f"  Última publicación: {info_remota.get('fecha', 'N/A')}")
    else:
        print("  No hay versión publicada en la nube aún.")
    
    print("-" * 60)
    
    # Pedir datos de la nueva versión
    nueva_version = input("\n📌 Nueva versión (ej: 1.1.0): ").strip()
    if not nueva_version:
        print("❌ Versión no puede estar vacía.")
        return
    
    notas = input("📝 Notas del cambio: ").strip()
    
    obligatoria_str = input("⚡ ¿Actualización obligatoria? (s/n) [n]: ").strip().lower()
    obligatoria = obligatoria_str == 's'
    
    # URLs de descarga
    print("\n--- URLs de descarga ---")
    print("(Puedes usar GitHub Releases, Google Drive, Firebase Storage, etc.)")
    url_windows = input("🪟 URL del .exe Windows: ").strip()
    url_macos = input("🍎 URL del .app/.dmg macOS: ").strip()
    
    # Calcular hashes si hay archivos locales
    sha256_windows = ""
    sha256_macos = ""
    
    if url_windows:
        ruta_local_win = input("   Ruta local del .exe (para calcular hash, Enter para omitir): ").strip()
        if ruta_local_win:
            # Si pasaron una carpeta, buscar BENTOS.exe dentro
            if os.path.isdir(ruta_local_win):
                ruta_local_win = os.path.join(ruta_local_win, "BENTOS.exe")
            if os.path.isfile(ruta_local_win):
                sha256_windows = calcular_sha256(ruta_local_win)
                print(f"   SHA256 Windows: {sha256_windows}")
            else:
                print(f"   ⚠️ No se encontró: {ruta_local_win}")
    
    if url_macos:
        ruta_local_mac = input("   Ruta local del .app (para calcular hash, Enter para omitir): ").strip()
        if ruta_local_mac:
            if os.path.isdir(ruta_local_mac) and not ruta_local_mac.endswith('.app'):
                ruta_local_mac = os.path.join(ruta_local_mac, "BENTOS.app")
            if os.path.exists(ruta_local_mac):
                sha256_macos = calcular_sha256(ruta_local_mac)
                print(f"   SHA256 macOS: {sha256_macos}")
            else:
                print(f"   ⚠️ No se encontró: {ruta_local_mac}")
    
    # Confirmar
    print("\n" + "=" * 60)
    print("  RESUMEN DE PUBLICACIÓN")
    print("=" * 60)
    print(f"  Versión:      {nueva_version}")
    print(f"  Notas:        {notas}")
    print(f"  Obligatoria:  {'Sí' if obligatoria else 'No'}")
    print(f"  URL Windows:  {url_windows or '(sin URL)'}")
    print(f"  URL macOS:    {url_macos or '(sin URL)'}")
    print("=" * 60)
    
    confirmar = input("\n¿Publicar esta versión? (s/n): ").strip().lower()
    if confirmar != 's':
        print("❌ Publicación cancelada.")
        return
    
    # Publicar
    exito = updater.publicar_version(
        nueva_version=nueva_version,
        url_windows=url_windows,
        url_macos=url_macos,
        notas=notas,
        obligatoria=obligatoria,
        sha256_windows=sha256_windows,
        sha256_macos=sha256_macos
    )
    
    if exito:
        print("\n🎉 ¡Versión publicada exitosamente!")
        print("   Todos los clientes se actualizarán al iniciar la app.")
    else:
        print("\n❌ Error al publicar la versión.")
    
    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
