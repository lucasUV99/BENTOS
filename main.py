"""
Script Principal - Procesamiento de Bitácoras Electrónicas
Pesquera Quintero S.A. - Sistema MSC

Uso:
    python main.py <ruta_pdf>
    python main.py --test
"""

import sys
import os
from pathlib import Path

# Asegurar que el backend esté en el path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from pdf_parser import BitacoraParser
from firebase_manager import FirebaseManager
from coordinate_converter import convert_coordinate
from especies_config import ESPECIES_CONFIG


def procesar_bitacora(pdf_path: str, guardar_firebase: bool = True):
    """
    Procesa una bitácora electrónica completa.
    
    Args:
        pdf_path: Ruta al archivo PDF
        guardar_firebase: Si True, guarda en Firebase. Si False, solo local.
    """
    print("\n" + "="*70)
    print("SISTEMA DE PROCESAMIENTO DE BITÁCORAS ELECTRÓNICAS")
    print("Pesquera Quintero S.A. - Certificación MSC")
    print("="*70 + "\n")
    
    # Verificar que el archivo existe
    if not os.path.exists(pdf_path):
        print(f"✗ ERROR: No se encontró el archivo: {pdf_path}")
        return False
    
    print(f"📄 Archivo: {os.path.basename(pdf_path)}")
    print(f"📊 Iniciando procesamiento...\n")
    
    # 1. PARSEAR PDF
    try:
        with BitacoraParser(pdf_path) as parser:
            resultado = parser.parsear_completo()
    except Exception as e:
        print(f"\n✗ ERROR en parsing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. MOSTRAR RESULTADOS
    mostrar_resumen(resultado)
    
    # 3. GUARDAR EN FIREBASE (opcional)
    if guardar_firebase:
        print("\n📤 Guardando en Firebase...")
        firebase = FirebaseManager()
        exito = firebase.guardar_viaje_completo(resultado)
        
        if not exito:
            print("⚠️ No se guardó en Firebase (modo local activado)")
    else:
        print("\n💾 Modo local - No se guardó en Firebase")
    
    print("\n✓ Procesamiento completado\n")
    return True


def mostrar_resumen(resultado: dict):
    """Muestra un resumen del procesamiento"""
    viaje = resultado.get('viaje', {})
    lances = resultado.get('lances', [])
    validacion = resultado.get('validacion', {})
    
    print("\n" + "="*70)
    print("RESUMEN DEL VIAJE")
    print("="*70)
    
    print(f"\n🚢 NAVE:")
    print(f"  Nombre:           {viaje.get('nave_nombre', 'N/A')}")
    print(f"  Matrícula/Folio:  {viaje.get('folio_interno', 'N/A')}")
    print(f"  Armador:          {viaje.get('armador', 'N/A')}")
    print(f"  Capitán:          {viaje.get('capitan', 'N/A')}")
    
    print(f"\n📍 PUERTOS:")
    print(f"  Zarpe:            {viaje.get('puerto_zarpe', 'N/A')}")
    print(f"  Desembarque:      {viaje.get('puerto_desembarque', 'N/A')}")
    
    print(f"\n📅 FECHAS:")
    print(f"  Zarpe:            {viaje.get('fecha_zarpe', 'N/A')}")
    print(f"  Recalada:         {viaje.get('fecha_recalada', 'N/A')}")
    
    print(f"\n🎣 LANCES:")
    print(f"  Total declarados: {len(lances)}")
    
    # Análisis de lances
    lances_validos = [l for l in lances if not l.get('observaciones', '').lower().__contains__('rota')]
    lances_problemas = len(lances) - len(lances_validos)
    
    if lances_problemas > 0:
        print(f"  ⚠️ Con problemas:  {lances_problemas}")
    
    print(f"\n🦐 VALIDACIÓN:")
    total_camaron = validacion.get('total_camaron_ton', 0)
    es_valido = validacion.get('es_valido', False)
    
    print(f"  Total Camarón nailon: {total_camaron} TON")
    print(f"  Estado: {'✓ VÁLIDO' if es_valido else '✗ ERROR - Revisar datos'}")
    
    # Indicadores MSC
    print(f"\n📊 INDICADORES MSC:")
    alertas = {'VERDE': 0, 'AMARILLO': 0, 'ROJO': 0}
    
    for lance in lances:
        alerta = lance.get('alerta_ecosistema', 'VERDE')
        alertas[alerta] = alertas.get(alerta, 0) + 1
    
    print(f"  🟢 Lances VERDES:    {alertas['VERDE']}")
    if alertas['AMARILLO'] > 0:
        print(f"  🟡 Lances AMARILLOS: {alertas['AMARILLO']}")
    if alertas['ROJO'] > 0:
        print(f"  🔴 Lances ROJOS:     {alertas['ROJO']}")
    
    print("\n" + "="*70)


def modo_test():
    """Ejecuta pruebas del sistema"""
    print("\n" + "="*70)
    print("MODO TEST - Verificación de Módulos")
    print("="*70 + "\n")
    
    # Test 1: Conversión de coordenadas
    print("📍 Test 1: Conversión de Coordenadas")
    try:
        lat = convert_coordinate("33° 51.21588' S")
        lng = convert_coordinate("72° 8.14188' W")
        print(f"  ✓ Latitud:  {lat}")
        print(f"  ✓ Longitud: {lng}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 2: Configuración de especies
    print("\n🐟 Test 2: Configuración de Especies")
    print(f"  Especies configuradas: {len(ESPECIES_CONFIG)}")
    print(f"  Ejemplo - Camarón nailon: {ESPECIES_CONFIG['Camarón nailon']['tipo'].value}")
    print(f"  ✓ Configuración cargada")
    
    # Test 3: Firebase (sin guardar datos reales)
    print("\n🔥 Test 3: Conexión Firebase")
    try:
        firebase = FirebaseManager()
        if firebase.db:
            print("  ✓ Firebase conectado")
        else:
            print("  ⚠️ Firebase en modo local")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\n" + "="*70)
    print("✓ Tests completados")
    print("="*70 + "\n")


def mostrar_ayuda():
    """Muestra la ayuda del programa"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║  Sistema de Procesamiento de Bitácoras Electrónicas               ║
║  Pesquera Quintero S.A. - Certificación MSC                        ║
╚════════════════════════════════════════════════════════════════════╝

USO:
    python main.py <ruta_pdf>              - Procesa una bitácora
    python main.py --test                  - Ejecuta tests del sistema
    python main.py --help                  - Muestra esta ayuda

EJEMPLOS:
    python main.py data/pdfs/Rauten_3088.pdf
    python main.py ../bitacoras/enero_2025.pdf

REQUISITOS:
    1. Archivo PDF de bitácora electrónica de Sernapesca
    2. Credenciales de Firebase (opcional, ver README)
    3. Python 3.8+ con dependencias instaladas

CONFIGURACIÓN FIREBASE:
    1. Crear proyecto en https://console.firebase.google.com
    2. Descargar credenciales (Service Account Key)
    3. Guardar en: config/firebase-credentials.json
    4. Copiar .env.example a .env y configurar

CONTACTO:
    Para soporte técnico, consultar documentación en docs/
    """)


def main():
    """Función principal"""
    
    # Sin argumentos o --help
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        mostrar_ayuda()
        return
    
    # Modo test
    if '--test' in sys.argv:
        modo_test()
        return
    
    # Procesar PDF
    pdf_path = sys.argv[1]
    
    # Opciones adicionales
    guardar_firebase = '--local-only' not in sys.argv
    
    procesar_bitacora(pdf_path, guardar_firebase)


if __name__ == "__main__":
    main()
