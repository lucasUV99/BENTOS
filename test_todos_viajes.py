"""
Test específico para verificar si algún viaje causa crash
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from firebase_manager import FirebaseManager

firebase = FirebaseManager()

# Obtener TODOS los viajes
print("Obteniendo todos los viajes...")
viajes = firebase.obtener_viajes()
print(f"Total viajes: {len(viajes)}")

for viaje in viajes:
    viaje_id = viaje.get('id_viaje')
    print(f"\n{'=' * 60}")
    print(f"Viaje: {viaje_id}")
    
    try:
        lances = firebase.obtener_lances_viaje(viaje_id)
        print(f"  ✅ Lances: {len(lances)}")
        
        if len(lances) == 0:
            print(f"  ⚠️  VIAJE SIN LANCES - Esto podría causar crash")
            continue
        
        # Simular el código de crear_tarjeta_resultado
        total_camaron = 0
        total_merluza = 0
        especies_totales = {}
        
        for lance in lances:
            especies = lance.get('especies', [])
            if not especies:
                print(f"    ⚠️  Lance sin especies")
            
            for especie in especies:
                nombre = especie.get('nombre', '')
                cantidad = especie.get('cantidad_ton', 0)
                
                if not nombre:
                    print(f"    ⚠️  Especie sin nombre: {especie}")
                    continue
                
                if nombre not in especies_totales:
                    especies_totales[nombre] = 0
                especies_totales[nombre] += cantidad
                
                nombre_lower = nombre.lower()
                if 'camarón' in nombre_lower or 'camaron' in nombre_lower:
                    total_camaron += cantidad
                elif 'merluza' in nombre_lower:
                    total_merluza += cantidad
        
        print(f"  📊 Especies totales: {len(especies_totales)}")
        print(f"  🦐 Camarón: {total_camaron:.3f} TON")
        print(f"  🐟 Merluza: {total_merluza:.3f} TON")
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 60}")
print("Test completado sin crashes")
