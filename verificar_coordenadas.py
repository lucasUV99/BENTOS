"""Script para verificar coordenadas de lances en Firebase"""
import sys
sys.path.append('backend')

from firebase_manager import FirebaseManager

# Inicializar Firebase
firebase = FirebaseManager()

# Verificar un viaje
viaje_id = 'SERNAPESCA-BE-26886'  # El que tiene 20 lances

print(f"Verificando lances de {viaje_id}...")
print("=" * 80)

lances = firebase.obtener_lances_viaje(viaje_id)
print(f"\nTotal lances: {len(lances)}")

for lance in lances[:5]:  # Mostrar primeros 5
    num = lance.get('numero_lance', 'N/A')
    es_captura_total = lance.get('es_captura_total', False)
    
    print(f"\n📍 Lance #{num} (CAPTURA TOTAL: {es_captura_total})")
    print(f"   Claves disponibles: {list(lance.keys())}")
    
    # Buscar campos de coordenadas
    coords_fields = [k for k in lance.keys() if 'lat' in k.lower() or 'lon' in k.lower() or 'coord' in k.lower()]
    if coords_fields:
        print(f"   Campos de coordenadas encontrados: {coords_fields}")
        for field in coords_fields:
            print(f"      - {field}: {lance.get(field)}")
    else:
        print(f"   ⚠️ NO se encontraron campos de coordenadas")
