"""
Script para reprocesar todos los PDFs y actualizar Firebase
"""
import sys
import os
sys.path.append('backend')

from pdf_parser_v2 import BitacoraParser
from firebase_manager import FirebaseManager
import glob

def reprocesar_pdfs():
    print("\n" + "="*80)
    print("REPROCESAMIENTO DE PDFs")
    print("="*80)
    
    # Inicializar Firebase
    firebase = FirebaseManager()
    if not firebase.db:
        print("❌ Error: No se pudo conectar a Firebase")
        return
    
    print("✓ Firebase conectado")
    
    # Obtener todos los PDFs
    pdf_folder = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo"
    pdfs = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    
    print(f"\n📁 Encontrados {len(pdfs)} archivos PDF:")
    for pdf in pdfs:
        print(f"   - {os.path.basename(pdf)}")
    
    print("\n" + "-"*80)
    
    # Procesar cada PDF
    exitosos = 0
    errores = 0
    
    for i, pdf_path in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}] Procesando: {os.path.basename(pdf_path)}")
        print("-"*80)
        
        try:
            # Parsear PDF
            with BitacoraParser(pdf_path) as parser:
                resultado = parser.parsear_completo()
            
            # Verificar que tenga ID
            if not resultado['viaje'].get('id_viaje'):
                print(f"❌ Error: No se pudo extraer ID del viaje")
                errores += 1
                continue
            
            print(f"   📋 ID: {resultado['viaje']['id_viaje']}")
            print(f"   🚢 Nave: {resultado['viaje']['nave_nombre']}")
            print(f"   👨‍✈️ Capitán: {resultado['viaje']['capitan']}")
            print(f"   🎣 Lances: {len(resultado['lances'])}")
            print(f"   🦐 Total Camarón: {resultado['validacion'].get('total_camaron_ton', 0):.3f} TON")
            
            # Guardar en Firebase (actualiza si ya existe)
            exito = firebase.guardar_viaje_completo(resultado)
            
            if exito:
                print(f"   ✅ Guardado/Actualizado en Firebase")
                exitosos += 1
            else:
                print(f"   ⚠️ No se pudo guardar en Firebase")
                errores += 1
                
        except Exception as e:
            print(f"   ❌ Error procesando PDF: {str(e)}")
            errores += 1
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Errores: {errores}")
    print(f"📊 Total: {len(pdfs)}")
    print("="*80)

if __name__ == "__main__":
    reprocesar_pdfs()
