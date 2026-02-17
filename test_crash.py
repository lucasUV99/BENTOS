"""
Script para reproducir el crash del botón de bitácoras individuales
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from firebase_manager import FirebaseManager

def test_obtener_lances():
    print("=" * 80)
    print("TEST: Obteniendo lances de Firebase")
    print("=" * 80)
    
    firebase = FirebaseManager()
    
    # IDs de viajes a probar
    viajes_ids = [
        'SERNAPESCA-BE-26682',
        'SERNAPESCA-BE-26601',
        'SERNAPESCA-BE-26886'
    ]
    
    for viaje_id in viajes_ids:
        print(f"\n{'=' * 80}")
        print(f"Viaje: {viaje_id}")
        print(f"{'=' * 80}")
        
        try:
            # Obtener viaje
            viaje = firebase.obtener_viaje(viaje_id)
            if not viaje:
                print(f"❌ Viaje no encontrado")
                continue
            
            print(f"✅ Viaje encontrado:")
            print(f"  - Nave: {viaje.get('nave_nombre')}")
            print(f"  - Capitán: {viaje.get('capitan')}")
            
            # Obtener lances
            lances = firebase.obtener_lances_viaje(viaje_id)
            print(f"\n📊 Lances obtenidos: {len(lances)}")
            
            for i, lance in enumerate(lances, 1):
                print(f"\n  Lance #{i}:")
                print(f"    - numero_lance: {lance.get('numero_lance')}")
                print(f"    - arte_pesca: {lance.get('arte_pesca')}")
                print(f"    - es_captura_total: {lance.get('es_captura_total', False)}")
                print(f"    - especies: {len(lance.get('especies', []))} especies")
                
                # Listar especies
                especies = lance.get('especies', [])
                for esp in especies[:5]:  # Solo primeras 5
                    nombre = esp.get('nombre', 'SIN NOMBRE')
                    cantidad = esp.get('cantidad_ton', 0)
                    tipo = esp.get('tipo_captura', 'N/A')
                    print(f"      • {nombre}: {cantidad:.3f} TON ({tipo})")
                
                if len(especies) > 5:
                    print(f"      ... y {len(especies) - 5} especies más")
        
        except Exception as e:
            print(f"\n❌ ERROR procesando {viaje_id}:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_obtener_lances()
