"""
Script para listar todas las bitácoras disponibles en Firebase
"""
import sys
import os
sys.path.append('backend')

from firebase_manager import FirebaseManager

def listar_bitacoras():
    print("\n" + "="*80)
    print("BITÁCORAS EN FIREBASE")
    print("="*80)
    
    # Inicializar Firebase
    firebase = FirebaseManager()
    if not firebase.db:
        print("❌ Error: No se pudo conectar a Firebase")
        return
    
    print("✓ Firebase conectado\n")
    
    # Listar todos los viajes
    viajes = firebase.listar_viajes(limite=1000)
    
    if not viajes:
        print("⚠️  No se encontraron bitácoras en Firebase")
        print("\nPara cargar bitácoras, ejecutar:")
        print("   python reprocesar_pdfs.py")
        return
    
    print(f"📊 Total de bitácoras: {len(viajes)}\n")
    print("-"*80)
    
    for i, viaje in enumerate(viajes, 1):
        id_viaje = viaje.get('id_viaje', 'N/A')
        nave = viaje.get('nave_nombre', 'N/A')
        capitan = viaje.get('capitan', 'N/A')
        fecha_salida = viaje.get('fecha_salida', 'N/A')
        total_ton = viaje.get('total_camaron_ton', 0)
        
        # Destacar la 27072 si existe
        if id_viaje == '27072':
            print(f"\n🔍 [{i}] ID: {id_viaje} ⭐")
        else:
            print(f"\n[{i}] ID: {id_viaje}")
        
        print(f"    🚢 Nave: {nave}")
        print(f"    👨‍✈️ Capitán: {capitan}")
        print(f"    📅 Salida: {fecha_salida}")
        print(f"    🦐 Camarón: {total_ton:.3f} TON")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    listar_bitacoras()
