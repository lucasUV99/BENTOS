"""
Script de Datos de Ejemplo
Genera datos de prueba para el sistema sin necesidad de PDF

Útil para:
- Testing sin tener PDFs reales
- Demostración del sistema
- Desarrollo de frontend
"""

import json
from datetime import datetime, timedelta


def generar_viaje_ejemplo():
    """Genera un viaje de ejemplo basado en el PDF de Sernapesca"""
    
    viaje = {
        "id_viaje": "SERNAPESCA-BE2021-3088-1",
        "folio_interno": "3088",
        "nave_nombre": "RAUTEN",
        "armador": "QUINTERO S.A., PESQ.",
        "capitan": "JUAN MANUEL CASTRO GALDAMES",
        "puerto_zarpe": "QUINTERO",
        "puerto_desembarque": "QUINTERO",
        "fecha_zarpe": "2021-01-02T10:54:58",
        "fecha_recalada": "2021-01-06T07:19:11",
        "total_lances_declarados": 14,
        "estado_procesamiento": "COMPLETADO",
        "fecha_procesamiento": datetime.now().isoformat(),
        "version_sistema": "1.0.0"
    }
    
    return viaje


def generar_lances_ejemplo():
    """Genera lances de ejemplo con diferentes escenarios"""
    
    lances = []
    
    # Lance 1: Normal, con buena captura
    lances.append({
        "numero_lance": 1,
        "arte_pesca": "ARRASTRE FONDO",
        "inicio_lance": "2021-01-02T14:30:00",
        "fin_lance": "2021-01-02T17:45:00",
        "posicion_inicial": {
            "raw_lat": "33° 45.123' S",
            "raw_lng": "72° 10.456' W",
            "lat": -33.752050,
            "lng": -72.174267
        },
        "posicion_final": {
            "raw_lat": "33° 47.890' S",
            "raw_lng": "72° 12.234' W",
            "lat": -33.798167,
            "lng": -72.203900
        },
        "capturas": [
            {
                "especie": "Camarón nailon",
                "retenida_ton": 2.456,
                "descartada_ton": 0.0,
                "tipo_calculado": "OBJETIVO"
            },
            {
                "especie": "Merluza común",
                "retenida_ton": 0.12,
                "descartada_ton": 0.0,
                "tipo_calculado": "DEPREDADOR_INCIDENTAL"
            },
            {
                "especie": "Jaiba paco",
                "descartada_unidades": 450,
                "tipo_calculado": "FAUNA_ACOMPANANTE"
            }
        ],
        "ratio_merluza_vs_objetivo": 0.049,
        "alerta_ecosistema": "VERDE"
    })
    
    # Lance 2: Con merluza alta (alerta amarilla)
    lances.append({
        "numero_lance": 2,
        "arte_pesca": "ARRASTRE FONDO",
        "inicio_lance": "2021-01-02T19:15:00",
        "fin_lance": "2021-01-02T22:30:00",
        "posicion_inicial": {
            "raw_lat": "33° 50.000' S",
            "raw_lng": "72° 15.000' W",
            "lat": -33.833333,
            "lng": -72.250000
        },
        "posicion_final": {
            "raw_lat": "33° 52.500' S",
            "raw_lng": "72° 17.500' W",
            "lat": -33.875000,
            "lng": -72.291667
        },
        "capturas": [
            {
                "especie": "Camarón nailon",
                "retenida_ton": 1.800,
                "descartada_ton": 0.0,
                "tipo_calculado": "OBJETIVO"
            },
            {
                "especie": "Merluza común",
                "retenida_ton": 0.28,  # 15.5% - Alerta amarilla
                "descartada_ton": 0.0,
                "tipo_calculado": "DEPREDADOR_INCIDENTAL"
            },
            {
                "especie": "Congrio negro",
                "retenida_ton": 0.05,
                "descartada_ton": 0.0,
                "tipo_calculado": "FAUNA_ACOMPANANTE"
            }
        ],
        "ratio_merluza_vs_objetivo": 0.156,
        "alerta_ecosistema": "AMARILLO"
    })
    
    # Lance 3: Lance con problemas (red rota)
    lances.append({
        "numero_lance": 3,
        "arte_pesca": "ARRASTRE FONDO",
        "inicio_lance": "2021-01-03T08:00:00",
        "fin_lance": "2021-01-03T10:30:00",
        "posicion_inicial": {
            "raw_lat": "33° 48.000' S",
            "raw_lng": "72° 14.000' W",
            "lat": -33.800000,
            "lng": -72.233333
        },
        "posicion_final": {
            "raw_lat": "33° 49.000' S",
            "raw_lng": "72° 15.000' W",
            "lat": -33.816667,
            "lng": -72.250000
        },
        "observaciones": "Red rota sin pesca",
        "capturas": [],
        "alerta_ecosistema": "VERDE"
    })
    
    # Lance 4: Captura excelente
    lances.append({
        "numero_lance": 4,
        "arte_pesca": "ARRASTRE FONDO",
        "inicio_lance": "2021-01-03T12:00:00",
        "fin_lance": "2021-01-03T15:30:00",
        "posicion_inicial": {
            "raw_lat": "33° 51.216' S",
            "raw_lng": "72° 08.142' W",
            "lat": -33.853600,
            "lng": -72.135700
        },
        "posicion_final": {
            "raw_lat": "33° 46.318' S",
            "raw_lng": "72° 04.621' W",
            "lat": -33.771967,
            "lng": -72.077017
        },
        "capturas": [
            {
                "especie": "Camarón nailon",
                "retenida_ton": 3.234,
                "descartada_ton": 0.0,
                "tipo_calculado": "OBJETIVO"
            },
            {
                "especie": "Merluza común",
                "retenida_ton": 0.15,
                "descartada_ton": 0.0,
                "tipo_calculado": "DEPREDADOR_INCIDENTAL"
            },
            {
                "especie": "Jaiba paco",
                "descartada_unidades": 1000,
                "tipo_calculado": "FAUNA_ACOMPANANTE"
            },
            {
                "especie": "Lenguado de ojo grande",
                "retenida_ton": 0.08,
                "descartada_ton": 0.0,
                "tipo_calculado": "FAUNA_ACOMPANANTE"
            }
        ],
        "ratio_merluza_vs_objetivo": 0.046,
        "alerta_ecosistema": "VERDE"
    })
    
    # Lance 5: Con especies sensibles
    lances.append({
        "numero_lance": 5,
        "arte_pesca": "ARRASTRE FONDO",
        "inicio_lance": "2021-01-03T17:00:00",
        "fin_lance": "2021-01-03T20:15:00",
        "posicion_inicial": {
            "raw_lat": "33° 55.000' S",
            "raw_lng": "72° 20.000' W",
            "lat": -33.916667,
            "lng": -72.333333
        },
        "posicion_final": {
            "raw_lat": "33° 57.000' S",
            "raw_lng": "72° 22.000' W",
            "lat": -33.950000,
            "lng": -72.366667
        },
        "capturas": [
            {
                "especie": "Camarón nailon",
                "retenida_ton": 1.950,
                "descartada_ton": 0.0,
                "tipo_calculado": "OBJETIVO"
            },
            {
                "especie": "Tollo negro raspa",
                "descartada_unidades": 3,  # Tiburón de profundidad - sensible
                "tipo_calculado": "FAUNA_ACOMPANANTE"
            },
            {
                "especie": "Jaiba limón",
                "descartada_unidades": 800,
                "tipo_calculado": "FAUNA_ACOMPANANTE"
            }
        ],
        "ratio_merluza_vs_objetivo": 0.0,
        "alerta_ecosistema": "VERDE",
        "especies_sensibles_detectadas": True
    })
    
    return lances


def generar_datos_completos():
    """Genera un conjunto completo de datos de prueba"""
    
    viaje = generar_viaje_ejemplo()
    lances = generar_lances_ejemplo()
    
    # Calcular validación
    total_camaron = sum(
        captura.get("retenida_ton", 0.0)
        for lance in lances
        for captura in lance.get("capturas", [])
        if captura.get("especie") == "Camarón nailon"
    )
    
    datos_completos = {
        "viaje": viaje,
        "lances": lances,
        "validacion": {
            "total_camaron_ton": round(total_camaron, 3),
            "es_valido": True,
            "total_lances": len(lances),
            "lances_con_problemas": 1,
            "lances_con_especies_sensibles": 1
        }
    }
    
    return datos_completos


def guardar_ejemplo_local():
    """Guarda los datos de ejemplo en un archivo JSON"""
    import os
    
    datos = generar_datos_completos()
    
    # Crear directorio si no existe
    os.makedirs("data/output", exist_ok=True)
    
    # Guardar JSON
    filename = "data/output/ejemplo_viaje_RAUTEN_3088.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Datos de ejemplo guardados en: {filename}")
    print(f"\nResumen:")
    print(f"  Nave: {datos['viaje']['nave_nombre']}")
    print(f"  Lances: {len(datos['lances'])}")
    print(f"  Total camarón: {datos['validacion']['total_camaron_ton']} TON")
    
    return filename


def guardar_ejemplo_firebase():
    """Guarda los datos de ejemplo en Firebase"""
    import sys
    import os
    
    # Añadir backend al path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    from firebase_manager import FirebaseManager
    
    datos = generar_datos_completos()
    
    print("Guardando datos de ejemplo en Firebase...")
    firebase = FirebaseManager()
    
    exito = firebase.guardar_viaje_completo(datos)
    
    if exito:
        print("\n✓ Datos de ejemplo guardados en Firebase")
    else:
        print("\n⚠️ No se guardó en Firebase (modo local)")
        guardar_ejemplo_local()


def main():
    """Función principal"""
    import sys
    
    print("="*70)
    print("GENERADOR DE DATOS DE EJEMPLO")
    print("Sistema de Bitácoras MSC - Pesquera Quintero")
    print("="*70 + "\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--firebase':
        guardar_ejemplo_firebase()
    else:
        filename = guardar_ejemplo_local()
        print(f"\nPara guardar en Firebase, ejecutar:")
        print(f"  python {__file__} --firebase")


if __name__ == "__main__":
    main()
