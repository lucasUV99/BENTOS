"""
Verifica que los datos en Firebase ahora tengan las capturas RETENIDAS correctamente
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from firebase_manager import FirebaseManager

def main():
    print("=" * 80)
    print("VERIFICACIÓN DE DATOS CORREGIDOS EN FIREBASE")
    print("=" * 80)
    
    # Inicializar Firebase
    firebase = FirebaseManager()
    
    # Viajes a verificar con sus valores esperados
    viajes_esperados = {
        'SERNAPESCA-BE-26682': {
            'camaron_retenida': 17.54,
            'camaron_descartada': 0.0
        },
        'SERNAPESCA-BE-26601': {
            'camaron_retenida': 10.92,
            'camaron_descartada': 0.0  # Esperamos 0 según el usuario
        },
        'SERNAPESCA-BE-26886': {
            'camaron_retenida': 13.66,
            'camaron_descartada': 0.0
        },
        'SERNAPESCA-BE-27072': {
            'camaron_retenida': 20.08,
            'camaron_descartada': 0.0
        },
        'SERNAPESCA-BE-27232': {
            'camaron_retenida': 19.66,
            'camaron_descartada': 0.0
        }
    }
    
    errores = []
    
    for id_viaje, esperado in viajes_esperados.items():
        print(f"\n{'=' * 80}")
        print(f"🔍 Verificando: {id_viaje}")
        print(f"{'=' * 80}")
        
        # Obtener viaje de Firebase
        viaje_data = firebase.obtener_viaje(id_viaje)
        
        if not viaje_data:
            print(f"❌ ERROR: Viaje no encontrado en Firebase")
            errores.append(f"{id_viaje}: No encontrado")
            continue
        
        # Obtener lances con especies
        lances = firebase.obtener_lances_viaje(id_viaje)
        
        # Calcular totales de camarón
        camaron_retenida = 0.0
        camaron_descartada = 0.0
        
        for lance in lances:
            especies = lance.get('especies', [])
            for esp in especies:
                nombre = esp.get('nombre', '').lower()
                if 'camar' in nombre and 'nailon' in nombre:
                    tipo_captura = esp.get('tipo_captura', '')
                    cantidad = esp.get('cantidad_ton', 0.0)
                    
                    if tipo_captura == 'retenida':
                        camaron_retenida += cantidad
                    elif tipo_captura == 'descartada':
                        camaron_descartada += cantidad
        
        # Verificar contra valores esperados
        print(f"\n📊 Resultados:")
        print(f"  Camarón RETENIDA:")
        print(f"    Esperado:    {esperado['camaron_retenida']:.2f} TON")
        print(f"    En Firebase: {camaron_retenida:.2f} TON")
        
        if abs(camaron_retenida - esperado['camaron_retenida']) < 0.01:
            print(f"    ✅ CORRECTO")
        else:
            print(f"    ❌ ERROR: Diferencia de {abs(camaron_retenida - esperado['camaron_retenida']):.2f} TON")
            errores.append(f"{id_viaje}: Retenida incorrecta ({camaron_retenida:.2f} vs {esperado['camaron_retenida']:.2f})")
        
        print(f"\n  Camarón DESCARTADA:")
        print(f"    Esperado:    {esperado['camaron_descartada']:.2f} TON")
        print(f"    En Firebase: {camaron_descartada:.2f} TON")
        
        if abs(camaron_descartada - esperado['camaron_descartada']) < 0.01:
            print(f"    ✅ CORRECTO")
        else:
            print(f"    ❌ ERROR: Diferencia de {abs(camaron_descartada - esperado['camaron_descartada']):.2f} TON")
            errores.append(f"{id_viaje}: Descartada incorrecta ({camaron_descartada:.2f} vs {esperado['camaron_descartada']:.2f})")
        
        # Mostrar todas las especies
        print(f"\n  📦 Todas las especies capturadas:")
        especies_totales = {}
        for lance in lances:
            for esp in lance.get('especies', []):
                nombre = esp['nombre']
                tipo = esp['tipo_captura']
                cantidad = esp['cantidad_ton']
                
                key = f"{nombre} ({tipo})"
                especies_totales[key] = especies_totales.get(key, 0.0) + cantidad
        
        for esp_key, total in sorted(especies_totales.items(), key=lambda x: -x[1]):
            print(f"    • {esp_key}: {total:.3f} TON")
    
    print(f"\n{'=' * 80}")
    print("RESUMEN FINAL")
    print(f"{'=' * 80}")
    
    if errores:
        print(f"\n❌ Se encontraron {len(errores)} errores:")
        for error in errores:
            print(f"  • {error}")
    else:
        print("\n✅ ¡TODOS LOS DATOS SON CORRECTOS!")
        print("   Todos los viajes tienen las capturas retenidas/descartadas correctas")

if __name__ == '__main__':
    main()
