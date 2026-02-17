"""
Verificar datos de viajes en Firebase
"""
import sys
sys.path.append('backend')

from firebase_manager import FirebaseManager

def verificar_viajes():
    print("\n" + "="*80)
    print("VERIFICACIÓN DE DATOS EN FIREBASE")
    print("="*80)
    
    firebase = FirebaseManager()
    
    if not firebase.db:
        print("❌ Error: No se pudo conectar a Firebase")
        return
    
    # Obtener todos los viajes
    viajes = firebase.listar_viajes(limite=100)
    
    print(f"\n✓ Total de viajes en Firebase: {len(viajes)}")
    print("\n" + "-"*80)
    
    for i, viaje in enumerate(viajes, 1):
        print(f"\n📋 VIAJE #{i}")
        print(f"   ID Viaje: {viaje.get('id_viaje', 'N/A')}")
        print(f"   Folio Interno: {viaje.get('folio_interno', 'N/A')}")
        print(f"   Nave: {viaje.get('nave_nombre', 'N/A')}")
        print(f"   Capitán: {viaje.get('capitan', 'N/A')}")
        print(f"   Armador: {viaje.get('armador', 'N/A')}")
        print(f"   Fecha Zarpe: {viaje.get('fecha_zarpe', 'N/A')}")
        print(f"   Aviso Recalada: {viaje.get('aviso_recalada', 'N/A')}")
        print(f"   RPA: {viaje.get('rpa', 'N/A')}")
        
        # Mostrar TODOS los campos disponibles
        print(f"\n   📝 Campos disponibles:")
        for key, value in viaje.items():
            if key not in ['id_viaje', 'folio_interno', 'nave_nombre', 'capitan', 'armador', 'fecha_zarpe', 'aviso_recalada', 'rpa']:
                print(f"      {key}: {value}")
        
        print("-"*80)
    
    print("\n✓ Verificación completada")

if __name__ == "__main__":
    verificar_viajes()
