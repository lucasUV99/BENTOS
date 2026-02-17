import sys
sys.path.append('backend')
from firebase_manager import FirebaseManager

fb = FirebaseManager()
lances = fb.obtener_lances_viaje('SERNAPESCA-BE-26601')
especies = lances[0].get('especies', [])
descartadas = [e for e in especies if e.get('tipo_captura') == 'descartada']

print(f'\nBE-26601 - Especies descartadas: {len(descartadas)}')
for e in descartadas:
    print(f"  {e['nombre']}: {e.get('cantidad_ton', 0)} TON, {e.get('cantidad_unidades', 0)} U")
