"""
Script para verificar extracción de coordenadas del parser
"""
import sys
sys.path.insert(0, 'backend')

from pdf_parser_v2 import BitacoraParser
import os

# Probar con un PDF
pdf_path = 'data/pdfs_ejemplo/doc-2.pdf'
id_viaje = 'SERNAPESCA-BE-26886'

print("="*80)
print(f"Verificando extracción de coordenadas de: {pdf_path}")
print("="*80)

with BitacoraParser(pdf_path) as parser:
    resultado = parser.parsear_completo()

viaje_data = resultado['viaje']
lances_data = resultado['lances']

print(f"\nTotal lances: {len(lances_data)}")

# Mostrar primeros 5 lances
for lance in lances_data[:5]:
    num = lance.get('numero_lance', 'N/A')
    es_captura_total = lance.get('es_captura_total', False)
    
    print(f"\n📍 Lance #{num} (CAPTURA TOTAL: {es_captura_total})")
    print(f"   Claves: {list(lance.keys())}")
    
    # Verificar coordenadas
    lat_inicio = lance.get('latitud_inicio')
    lon_inicio = lance.get('longitud_inicio')
    lat_fin = lance.get('latitud_fin')
    lon_fin = lance.get('longitud_fin')
    
    if lat_inicio and lon_inicio:
        print(f"   ✅ Coordenadas INICIO: {lat_inicio}, {lon_inicio}")
    else:
        print(f"   ❌ NO tiene coordenadas de inicio")
    
    if lat_fin and lon_fin:
        print(f"   ✅ Coordenadas FIN: {lat_fin}, {lon_fin}")
    else:
        print(f"   ⚠️  NO tiene coordenadas de fin")
