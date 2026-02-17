"""
Verificar especies en Firebase vs PDFs
"""
import sys
sys.path.append('backend')

from pdf_parser_v2 import BitacoraParser
from firebase_manager import FirebaseManager
import os

def verificar_especies():
    print("\n" + "="*80)
    print("VERIFICACIÓN DE ESPECIES: FIREBASE vs PDF")
    print("="*80)
    
    # Conectar a Firebase
    firebase = FirebaseManager()
    if not firebase.db:
        print("❌ Error: No se pudo conectar a Firebase")
        return
    
    pdf_folder = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo"
    pdfs = [
        "doc.pdf",
        "doc-2.pdf",
        "doc-3.pdf",
        "doc-4.pdf",
        "doc-5.pdf"
    ]
    
    necesita_reprocesar = False
    
    for pdf_name in pdfs:
        pdf_path = os.path.join(pdf_folder, pdf_name)
        if not os.path.exists(pdf_path):
            print(f"\n⚠️  PDF no encontrado: {pdf_name}")
            continue
        
        print(f"\n📄 Analizando: {pdf_name}")
        print("-" * 60)
        
        try:
            # Parsear PDF con el NUEVO parser
            with BitacoraParser(pdf_path) as parser:
                resultado = parser.parsear_completo()
            
            id_viaje = resultado['viaje'].get('id_viaje', 'N/A')
            
            # Contar especies únicas del PDF
            especies_pdf = resultado['lances'][0]['especies'] if resultado['lances'] else []
            especies_unicas_pdf = set(e['nombre'] for e in especies_pdf)
            
            print(f"ID Viaje: {id_viaje}")
            print(f"Especies en PDF (nuevo parser): {len(especies_unicas_pdf)}")
            
            # Obtener datos de Firebase
            lances_fb = firebase.obtener_lances_viaje(id_viaje)
            
            if lances_fb:
                especies_fb = lances_fb[0]['especies'] if lances_fb else []
                especies_unicas_fb = set(e['nombre'] for e in especies_fb)
                print(f"Especies en Firebase (actual): {len(especies_unicas_fb)}")
                
                # Comparar
                if len(especies_unicas_pdf) != len(especies_unicas_fb):
                    print(f"⚠️  DIFERENCIA DETECTADA: PDF tiene {len(especies_unicas_pdf)}, Firebase tiene {len(especies_unicas_fb)}")
                    necesita_reprocesar = True
                    
                    # Mostrar especies que faltan en Firebase
                    faltantes = especies_unicas_pdf - especies_unicas_fb
                    if faltantes:
                        print(f"   Especies faltantes en Firebase: {', '.join(list(faltantes)[:5])}")
                else:
                    print("✅ Firebase está actualizado")
            else:
                print("⚠️  No hay datos en Firebase para este viaje")
                necesita_reprocesar = True
                
        except Exception as e:
            print(f"❌ Error procesando {pdf_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    if necesita_reprocesar:
        print("⚠️  SE NECESITA REPROCESAR - Hay diferencias entre PDF y Firebase")
        print("\nEjecuta: python reprocesar_pdfs.py")
    else:
        print("✅ Todos los PDFs están sincronizados con Firebase")
    print("="*80)

if __name__ == "__main__":
    verificar_especies()
