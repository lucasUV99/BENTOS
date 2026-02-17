"""
Verificar especies de bitácora 26886
"""
import sys
sys.path.append('backend')

from firebase_manager import FirebaseManager

firebase = FirebaseManager()
if not firebase.db:
    print("❌ Error: No se pudo conectar a Firebase")
    exit()

viaje_id = "SERNAPESCA-BE-26886"
lances = firebase.obtener_lances_viaje(viaje_id)

if lances:
    print(f"\n{'='*80}")
    print(f"BITÁCORA: {viaje_id}")
    print(f"{'='*80}\n")
    
    for lance in lances:
        especies = lance.get('especies', [])
        print(f"Total especies: {len(especies)}\n")
        
        # Separar por tipo
        retenidas = [e for e in especies if e.get('tipo_captura') == 'retenida']
        descartadas = [e for e in especies if e.get('tipo_captura') == 'descartada']
        incidentales = [e for e in especies if e.get('tipo_captura') == 'incidental']
        
        print(f"RETENIDAS ({len(retenidas)}):")
        for e in retenidas:
            print(f"  • {e['nombre']}: {e.get('cantidad_ton', 0)} TON")
        
        print(f"\nDESCARTADAS ({len(descartadas)}):")
        for e in descartadas:
            ton = e.get('cantidad_ton', 0)
            unidades = e.get('cantidad_unidades', 0)
            if ton > 0:
                print(f"  • {e['nombre']}: {ton} TON")
            if unidades > 0:
                print(f"  • {e['nombre']}: {unidades} U")
        
        print(f"\nINCIDENTALES ({len(incidentales)}):")
        for e in incidentales:
            print(f"  • {e['nombre']}: {e.get('cantidad_unidades', 0)} U")
else:
    print(f"No se encontró el viaje {viaje_id}")
