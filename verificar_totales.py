"""Script para verificar totales guardados en Firebase"""
import sys
sys.path.append('backend')

from firebase_manager import FirebaseManager

# Inicializar Firebase
firebase = FirebaseManager()

# IDs de viajes
viajes_ids = [
    'SERNAPESCA-BE-26601',
    'SERNAPESCA-BE-26886', 
    'SERNAPESCA-BE-26682',
    'SERNAPESCA-BE-27072',
    'SERNAPESCA-BE-27232'
]

print("=" * 80)
print("VERIFICACIÓN DE TOTALES EN FIREBASE")
print("=" * 80)

# Totales generales
total_lances_individuales = 0
especies_global = {}
total_captura_global = 0

for viaje_id in viajes_ids:
    print(f"\n📋 {viaje_id}")
    print("-" * 80)
    
    # Obtener lances
    lances = firebase.obtener_lances_viaje(viaje_id)
    print(f"   Total lances guardados: {len(lances)}")
    
    # Buscar lance CAPTURA TOTAL
    lance_captura_total = None
    lances_individuales = []
    
    for lance in lances:
        if lance.get('es_captura_total', False):
            lance_captura_total = lance
        else:
            lances_individuales.append(lance)
    
    if lance_captura_total:
        print(f"   ✅ Lance CAPTURA TOTAL encontrado")
        especies = lance_captura_total.get('especies', [])
        print(f"   📊 Especies en CAPTURA TOTAL: {len(especies)}")
        
        # Calcular totales del viaje
        total_viaje = 0
        for especie in especies:
            nombre = especie.get('nombre', '')
            cantidad_ton = especie.get('cantidad_ton', 0)
            tipo_captura = especie.get('tipo_captura', 'retenida')
            
            total_viaje += cantidad_ton
            
            # Acumular global
            if nombre not in especies_global:
                especies_global[nombre] = 0
            especies_global[nombre] += cantidad_ton
            
            # Mostrar especies objetivo
            if 'camarón' in nombre.lower() or 'camaron' in nombre.lower():
                print(f"      - {nombre}: {cantidad_ton:.3f} TON ({tipo_captura})")
            elif 'langostino' in nombre.lower():
                print(f"      - {nombre}: {cantidad_ton:.3f} TON ({tipo_captura})")
        
        print(f"   ⚖️  Total viaje: {total_viaje:.3f} TON")
        total_captura_global += total_viaje
    else:
        print(f"   ❌ NO se encontró lance CAPTURA TOTAL")
    
    print(f"   🎣 Lances individuales: {len(lances_individuales)}")
    total_lances_individuales += len(lances_individuales)

print("\n" + "=" * 80)
print("RESUMEN TOTAL")
print("=" * 80)
print(f"📊 Lances individuales totales: {total_lances_individuales}")
print(f"🐟 Especies diferentes: {len(especies_global)}")
print(f"⚖️  Captura total: {total_captura_global:.2f} TON")

print("\n🎯 ESPECIES OBJETIVO:")
camaron_nilon = especies_global.get('Camarón nailon', 0)
if camaron_nilon > 0:
    porcentaje = (camaron_nilon / total_captura_global * 100) if total_captura_global > 0 else 0
    print(f"   Camarón nailon: {camaron_nilon:.3f} TON ({porcentaje:.1f}%)")

# Top 5 especies por volumen
print("\n📈 TOP 5 ESPECIES POR VOLUMEN:")
top_especies = sorted(especies_global.items(), key=lambda x: x[1], reverse=True)[:5]
for i, (nombre, cantidad) in enumerate(top_especies, 1):
    porcentaje = (cantidad / total_captura_global * 100) if total_captura_global > 0 else 0
    print(f"   {i}. {nombre}: {cantidad:.3f} TON ({porcentaje:.1f}%)")

print("\n" + "=" * 80)
