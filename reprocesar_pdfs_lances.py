"""
Script para reprocesar PDFs y extraer lances individuales con coordenadas
"""
import sys
sys.path.insert(0, 'backend')

from pdf_parser_v2 import BitacoraParser
from firebase_manager import FirebaseManager
import os

# Inicializar Firebase
firebase = FirebaseManager()

# PDFs a procesar
pdfs_ejemplo = [
    ('data/pdfs_ejemplo/doc.pdf', 'SERNAPESCA-BE-26601'),
    ('data/pdfs_ejemplo/doc-2.pdf', 'SERNAPESCA-BE-26886'),
    ('data/pdfs_ejemplo/doc-3.pdf', 'SERNAPESCA-BE-26682'),
    ('data/pdfs_ejemplo/doc-4.pdf', 'SERNAPESCA-BE-27072'),
    ('data/pdfs_ejemplo/doc-5.pdf', 'SERNAPESCA-BE-27232'),
]

print("="*60)
print("🔄 REPROCESANDO PDFs PARA EXTRAER LANCES INDIVIDUALES")
print("="*60)

for pdf_path, id_viaje in pdfs_ejemplo:
    if not os.path.exists(pdf_path):
        print(f"\n❌ PDF no encontrado: {pdf_path}")
        continue
    
    print(f"\n📄 Procesando: {id_viaje}")
    print(f"   Archivo: {pdf_path}")
    
    try:
        # Parsear PDF
        with BitacoraParser(pdf_path) as parser:
            resultado = parser.parsear_completo()
        
        viaje_data = resultado['viaje']
        lances_data = resultado['lances']
        
        # Contar lances por tipo
        lance_captura_total = [l for l in lances_data if l.get('es_captura_total', False)]
        lances_individuales = [l for l in lances_data if not l.get('es_captura_total', False)]
        
        print(f"   ✅ Parseado exitoso:")
        print(f"      - CAPTURA TOTAL: {'Sí' if lance_captura_total else 'No'}")
        print(f"      - Lances individuales: {len(lances_individuales)}")
        
        # Actualizar en Firebase
        print(f"   💾 Actualizando en Firebase...")
        
        # Actualizar viaje (guardar_viaje ya hace merge)
        firebase.guardar_viaje(viaje_data)
        
        # Guardar lances (elimina antiguos automáticamente)
        firebase.guardar_lances(id_viaje, lances_data)
        
        print(f"   ✅ Actualizado: {len(lances_data)} lances guardados")
        
        # Mostrar algunos lances con coordenadas
        lances_con_coords = [l for l in lances_individuales if l.get('latitud_inicio') and l.get('longitud_inicio')]
        if lances_con_coords:
            print(f"   📍 Lances con coordenadas: {len(lances_con_coords)}/{len(lances_individuales)}")
            # Mostrar primero como ejemplo
            primer_lance = lances_con_coords[0]
            print(f"      Ejemplo Lance #{primer_lance.get('numero_lance')}:")
            print(f"        Inicio: {primer_lance.get('latitud_inicio')}, {primer_lance.get('longitud_inicio')}")
            print(f"        Fin: {primer_lance.get('latitud_fin')}, {primer_lance.get('longitud_fin')}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("✅ REPROCESAMIENTO COMPLETADO")
print("="*60)
