"""
Buscar en qué página están las especies del Lance #3
"""
import sys
import os
sys.path.append('backend')

import pdfplumber

def buscar_especies_lance3(pdf_path):
    """Buscar en todas las páginas las especies del Lance #3"""
    print("\n" + "="*80)
    print("Buscando especies del LANCE #3 en todas las páginas")
    print("="*80)
    
    with pdfplumber.open(pdf_path) as pdf:
        for num_pagina, page in enumerate(pdf.pages):
            texto = page.extract_text()
            
            # Buscar referencias al Lance #3
            if 'LANCE # 3' in texto or 'LANCE #3' in texto or 'Lance 3' in texto:
                print(f"\n📄 Página {num_pagina + 1} - Menciona Lance #3")
                print("-"*80)
                
                tablas = page.extract_tables()
                print(f"Tablas en esta página: {len(tablas)}")
                
                for idx_tabla, tabla in enumerate(tablas):
                    print(f"\n  TABLA #{idx_tabla + 1}:")
                    
                    # Buscar "LANCE # 3" o "LANCE #3" en la tabla
                    tabla_str = ' '.join([' '.join([str(c) for c in fila if c]) for fila in tabla[:5]])
                    
                    if '3' in tabla_str and ('LANCE' in tabla_str.upper()):
                        print(f"    ✓ Tabla contiene referencia al lance 3")
                        
                        # Buscar headers y especies
                        for i, fila in enumerate(tabla):
                            fila_str = ' '.join([str(c) for c in fila if c])
                            
                            if 'Retenida' in fila_str and 'TON' in fila_str:
                                print(f"    ✓ Header encontrado en fila {i}")
                                
                                # Mostrar especies (filas siguientes)
                                print(f"    Especies:")
                                for j in range(i+1, min(i+10, len(tabla))):
                                    esp_fila = tabla[j]
                                    if esp_fila and esp_fila[1]:
                                        nombre = str(esp_fila[1])
                                        if 'OBSERV' not in nombre.upper():
                                            # Mostrar valores TON
                                            vals = [str(c) if c else '-' for c in esp_fila[:6]]
                                            print(f"      {nombre}: {' | '.join(vals)}")
                                break

if __name__ == "__main__":
    pdf_folder = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo"
    pdf_path = os.path.join(pdf_folder, "doc-4.pdf")
    
    if os.path.exists(pdf_path):
        buscar_especies_lance3(pdf_path)
    else:
        print(f"❌ No se encontró: {pdf_path}")
