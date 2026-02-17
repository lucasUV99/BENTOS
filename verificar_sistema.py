"""
Script de Verificación del Sistema
Verifica que todo está correctamente instalado y configurado
"""

import sys
import os
from pathlib import Path


def print_header(title):
    """Imprime un encabezado"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def check_python_version():
    """Verifica la versión de Python"""
    print("\n🐍 Verificando versión de Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requiere Python 3.8+")
        return False


def check_dependencies():
    """Verifica las dependencias instaladas"""
    print("\n📦 Verificando dependencias...")
    
    dependencies = [
        ('pdfplumber', 'Para leer PDFs'),
        ('firebase_admin', 'Para conectar con Firebase'),
        ('pandas', 'Para procesar datos'),
        ('numpy', 'Para cálculos numéricos'),
        ('python-dotenv', 'Para variables de entorno')
    ]
    
    all_ok = True
    
    for module, description in dependencies:
        try:
            __import__(module.replace('-', '_'))
            print(f"   ✅ {module:20} - OK ({description})")
        except ImportError:
            print(f"   ❌ {module:20} - FALTA ({description})")
            all_ok = False
    
    if not all_ok:
        print("\n   💡 Para instalar dependencias faltantes:")
        print("      pip install -r requirements.txt")
    
    return all_ok


def check_directories():
    """Verifica la estructura de directorios"""
    print("\n📁 Verificando estructura de directorios...")
    
    directories = [
        'backend',
        'data/pdfs',
        'data/output',
        'config',
        'docs'
    ]
    
    all_ok = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory:20} - Existe")
        else:
            print(f"   ❌ {directory:20} - No existe")
            all_ok = False
    
    return all_ok


def check_files():
    """Verifica archivos esenciales"""
    print("\n📄 Verificando archivos esenciales...")
    
    files = [
        ('main.py', 'Script principal'),
        ('requirements.txt', 'Dependencias'),
        ('backend/pdf_parser.py', 'Parser de PDF'),
        ('backend/firebase_manager.py', 'Gestor de Firebase'),
        ('backend/coordinate_converter.py', 'Conversor de coordenadas'),
        ('backend/especies_config.py', 'Configuración de especies'),
        ('.env', 'Variables de entorno')
    ]
    
    all_ok = True
    
    for file, description in files:
        if os.path.exists(file):
            print(f"   ✅ {file:35} - OK ({description})")
        else:
            print(f"   ⚠️  {file:35} - FALTA ({description})")
            if file != '.env' and file != 'config/firebase-credentials.json':
                all_ok = False
    
    return all_ok


def check_firebase():
    """Verifica configuración de Firebase"""
    print("\n🔥 Verificando configuración de Firebase...")
    
    credentials_path = 'config/firebase-credentials.json'
    
    if os.path.exists(credentials_path):
        print(f"   ✅ Credenciales encontradas en {credentials_path}")
        print(f"   ✅ Firebase configurado")
        return True
    else:
        print(f"   ⚠️  Credenciales NO encontradas en {credentials_path}")
        print(f"   ℹ️  El sistema funcionará en MODO LOCAL")
        print(f"   ℹ️  Para habilitar Firebase, ver: docs/FIREBASE_SETUP.md")
        return False


def test_modules():
    """Prueba los módulos principales"""
    print("\n🧪 Probando módulos del sistema...")
    
    sys.path.insert(0, 'backend')
    
    tests = []
    
    # Test 1: Conversión de coordenadas
    try:
        from coordinate_converter import convert_coordinate
        lat = convert_coordinate("33° 51.21588' S")
        
        if abs(lat - (-33.853598)) < 0.0001:
            print("   ✅ coordinate_converter - OK")
            tests.append(True)
        else:
            print(f"   ❌ coordinate_converter - Error en cálculo (esperado: -33.853598, obtenido: {lat})")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ coordinate_converter - Error: {e}")
        tests.append(False)
    
    # Test 2: Configuración de especies
    try:
        from especies_config import ESPECIES_CONFIG, obtener_tipo_especie
        
        if len(ESPECIES_CONFIG) > 0:
            tipo = obtener_tipo_especie("Camarón nailon")
            if tipo == "OBJETIVO":
                print("   ✅ especies_config - OK")
                tests.append(True)
            else:
                print(f"   ❌ especies_config - Error en categorización")
                tests.append(False)
        else:
            print("   ❌ especies_config - No hay especies configuradas")
            tests.append(False)
    except Exception as e:
        print(f"   ❌ especies_config - Error: {e}")
        tests.append(False)
    
    # Test 3: Firebase Manager
    try:
        from firebase_manager import FirebaseManager
        manager = FirebaseManager()
        print("   ✅ firebase_manager - OK (conexión depende de credenciales)")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ firebase_manager - Error: {e}")
        tests.append(False)
    
    return all(tests)


def show_summary(results):
    """Muestra resumen final"""
    print_header("RESUMEN DE VERIFICACIÓN")
    
    total = len(results)
    passed = sum(results.values())
    
    for check, result in results.items():
        status = "✅ OK" if result else "❌ ERROR"
        print(f"   {status:10} - {check}")
    
    print("\n" + "-"*70)
    print(f"   Total: {passed}/{total} verificaciones pasadas")
    
    if passed == total:
        print("\n   🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("\n   Próximos pasos:")
        print("   1. Leer INICIO_RAPIDO.md para comenzar")
        print("   2. Generar datos de ejemplo: python generar_datos_ejemplo.py")
        print("   3. Ejecutar tests: python main.py --test")
    elif passed >= total - 1:  # Firebase es opcional
        print("\n   ✅ Sistema funcional en MODO LOCAL")
        print("\n   Próximos pasos:")
        print("   1. Para habilitar Firebase, ver docs/FIREBASE_SETUP.md")
        print("   2. Generar datos de ejemplo: python generar_datos_ejemplo.py")
        print("   3. Ejecutar tests: python main.py --test")
    else:
        print("\n   ⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("\n   Acciones recomendadas:")
        print("   1. Instalar dependencias: pip install -r requirements.txt")
        print("   2. Verificar estructura de carpetas")
        print("   3. Revisar README.md para más información")


def main():
    """Función principal"""
    print_header("VERIFICACIÓN DEL SISTEMA DE BITÁCORAS MSC")
    print("Pesquera Quintero S.A. - Certificación MSC")
    
    results = {}
    
    # Ejecutar verificaciones
    results['Python 3.8+'] = check_python_version()
    results['Dependencias'] = check_dependencies()
    results['Estructura de carpetas'] = check_directories()
    results['Archivos esenciales'] = check_files()
    results['Firebase (opcional)'] = check_firebase()
    results['Módulos del sistema'] = test_modules()
    
    # Mostrar resumen
    show_summary(results)
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
