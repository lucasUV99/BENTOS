"""
Script para verificar los datos de la bitácora 27072
Especialmente el lance 3 que debería mostrar 0.9 TON, no 2.080 TON
"""
import sys
import os
sys.path.append('backend')

from firebase_manager import FirebaseManager

def verificar_bitacora_27072():
    print("\n" + "="*80)
    print("VERIFICACIÓN BITÁCORA 27072")
    print("="*80)
    
    # Inicializar Firebase
    firebase = FirebaseManager()
    if not firebase.db:
        print("❌ Error: No se pudo conectar a Firebase")
        return
    
    print("✓ Firebase conectado\n")
    
    # Buscar bitácora 27072
    id_viaje = "SERNAPESCA-BE-27072"  # ID completo en Firebase
    viaje = firebase.obtener_viaje(id_viaje)
    
    if not viaje:
        print(f"❌ No se encontró la bitácora {id_viaje} en Firebase")
        print("\nPosibles soluciones:")
        print("1. Verificar que el PDF esté en data/pdfs_ejemplo/")
        print("2. Ejecutar reprocesar_pdfs.py para cargar todas las bitácoras")
        return
    
    print(f"✅ Bitácora encontrada: {id_viaje}")
    print(f"   🚢 Nave: {viaje.get('nave_nombre', 'N/A')}")
    print(f"   👨‍✈️ Capitán: {viaje.get('capitan', 'N/A')}")
    print(f"   📅 Fecha salida: {viaje.get('fecha_salida', 'N/A')}")
    print(f"   📅 Fecha arribo: {viaje.get('fecha_arribo', 'N/A')}")
    
    # Obtener lances
    lances = firebase.obtener_lances_viaje(id_viaje)
    
    if not lances:
        print(f"\n⚠️  No se encontraron lances para la bitácora {id_viaje}")
        return
    
    # Filtrar lance de CAPTURA TOTAL
    lances_individuales = [l for l in lances if l.get('numero_lance', -1) != 0]
    lance_captura_total = next((l for l in lances if l.get('numero_lance') == 0), None)
    
    print(f"\n📊 Total de lances individuales: {len(lances_individuales)}")
    
    if lance_captura_total:
        print("\n" + "-"*80)
        print("CAPTURA TOTAL (Lance 0 - Resumen oficial)")
        print("-"*80)
        especies_ct = lance_captura_total.get('especies', [])
        for especie in especies_ct:
            nombre = especie.get('nombre', 'N/A')
            cantidad = especie.get('cantidad_ton', 0)
            tipo = especie.get('tipo_captura', 'N/A')
            print(f"   {nombre}: {cantidad:.3f} TON ({tipo})")
    
    # Mostrar todos los lances individuales
    print("\n" + "="*80)
    print("LANCES INDIVIDUALES")
    print("="*80)
    
    for lance in sorted(lances_individuales, key=lambda x: x.get('numero_lance', 0)):
        num_lance = lance.get('numero_lance', 'N/A')
        fecha = lance.get('fecha_virado', 'N/A')
        especies = lance.get('especies', [])
        
        # Destacar el lance 3
        if num_lance == 3:
            print("\n" + "🔍 " + "="*76)
            print(f"LANCE #{num_lance} ⭐ (LANCE REPORTADO CON ERROR)")
            print("="*80)
        else:
            print(f"\nLance #{num_lance}")
            print("-"*80)
        
        print(f"   📅 Fecha: {fecha}")
        print(f"   📍 Lat inicio: {lance.get('latitud_inicio', 'N/A')}")
        print(f"   📍 Lon inicio: {lance.get('longitud_inicio', 'N/A')}")
        
        if especies:
            print(f"   🐟 Especies capturadas:")
            total_lance = 0
            camaron_encontrado = False
            
            for especie in especies:
                nombre = especie.get('nombre', 'N/A')
                cantidad = especie.get('cantidad_ton', 0)
                tipo = especie.get('tipo_captura', 'N/A')
                total_lance += cantidad
                
                # Destacar camarón en el lance 3
                if num_lance == 3 and ('camarón' in nombre.lower() or 'camaron' in nombre.lower()):
                    camaron_encontrado = True
                    print(f"      🦐 {nombre}: {cantidad:.3f} TON ({tipo})")
                    if abs(cantidad - 0.9) < 0.01:
                        print(f"         ✅ CORRECTO: Valor esperado era 0.9 TON")
                    else:
                        print(f"         ❌ ERROR: Valor esperado era 0.9 TON, pero se encontró {cantidad:.3f} TON")
                else:
                    print(f"      • {nombre}: {cantidad:.3f} TON ({tipo})")
            
            print(f"   📊 Total lance: {total_lance:.3f} TON")
            
            # Verificación adicional para lance 3
            if num_lance == 3 and not camaron_encontrado:
                print(f"      ⚠️ ADVERTENCIA: No se encontró camarón en este lance")
        else:
            print(f"   ⚠️  Sin especies registradas")
        
        if num_lance == 3:
            print("="*80)
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*80)
    print(f"Bitácora ID: {id_viaje}")
    print(f"Lances individuales: {len(lances_individuales)}")
    print(f"Lance de CAPTURA TOTAL: {'✅ Presente' if lance_captura_total else '❌ No encontrado'}")
    print("\n⚠️ IMPORTANTE:")
    print("Si los valores aún son incorrectos, ejecutar:")
    print("   python reprocesar_pdfs.py")
    print("Para reprocesar todos los PDFs con el parser corregido.")
    print("="*80)

if __name__ == "__main__":
    verificar_bitacora_27072()
