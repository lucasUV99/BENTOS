"""Script para verificar datos del lance 1 de la bitácora 27232"""
import sys
sys.path.append('backend')

from firebase_manager import FirebaseManager

firebase = FirebaseManager()

viaje_id = 'SERNAPESCA-BE-27232'
lances = firebase.obtener_lances_viaje(viaje_id)

print("Buscando lance #1...")
for lance in lances:
    if lance.get('numero_lance') == 1:
        print("\n📍 LANCE #1 ENCONTRADO")
        print("=" * 80)
        print(f"Arte de pesca: {lance.get('arte_pesca')}")
        print(f"\nEspecies ({len(lance.get('especies', []))}):")
        
        for esp in lance.get('especies', []):
            nombre = esp.get('nombre', 'N/A')
            cantidad_ton = esp.get('cantidad_ton', 0)
            tipo_captura = esp.get('tipo_captura', 'N/A')
            print(f"  - {nombre}: {cantidad_ton:.3f} TON ({tipo_captura})")
        
        break
