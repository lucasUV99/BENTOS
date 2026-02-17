"""
Simular la lógica de la tarjeta para bitácora 26886
"""
import sys
sys.path.append('backend')

from firebase_manager import FirebaseManager

firebase = FirebaseManager()
viaje_id = "SERNAPESCA-BE-26886"
lances = firebase.obtener_lances_viaje(viaje_id)

print(f"\n{'='*80}")
print(f"SIMULACIÓN DE TARJETA PARA: {viaje_id}")
print(f"{'='*80}\n")

# Lógica de la tarjeta
especies_retenidas = {}
especies_descartadas = {}

for lance in lances:
    for especie in lance.get('especies', []):
        nombre = especie.get('nombre', '')
        if not nombre:
            continue
        cantidad = especie.get('cantidad_ton', 0)
        cantidad_unidades = especie.get('cantidad_unidades', 0)
        tipo_captura = especie.get('tipo_captura', 'retenida')
        
        if tipo_captura == 'retenida':
            if nombre not in especies_retenidas:
                especies_retenidas[nombre] = 0
            especies_retenidas[nombre] += cantidad
        elif tipo_captura == 'descartada':
            if nombre not in especies_descartadas:
                especies_descartadas[nombre] = {'ton': 0, 'unidades': 0}
            especies_descartadas[nombre]['ton'] += cantidad
            especies_descartadas[nombre]['unidades'] += cantidad_unidades

# Ordenar
top_retenidas = sorted(especies_retenidas.items(), key=lambda x: x[1], reverse=True)[:5]
top_descartadas = sorted(especies_descartadas.items(), 
                        key=lambda x: (x[1]['ton'], x[1]['unidades']), 
                        reverse=True)[:15]

print(f"ESPECIES RETENIDAS (Top 5):")
for especie, cantidad in top_retenidas:
    print(f"  • {especie}: {cantidad:.3f} TON")

print(f"\nESPECIES DESCARTADAS (Top 10):")
for especie, datos in top_descartadas:
    ton = datos['ton']
    unidades = datos['unidades']
    if ton > 0:
        print(f"  • {especie}: {ton:.3f} TON")
    else:
        print(f"  • {especie}: {int(unidades)} U")

print(f"\nTotal especies descartadas mostradas: {len(top_descartadas)}")
print(f"Total especies descartadas en DB: {len(especies_descartadas)}")
