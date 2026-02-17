"""
Buscar el valor 0.9 TON en todo el PDF
"""
import sys
import os
sys.path.append('backend')

import pdfplumber

def buscar_valor_09(pdf_path):
    """Buscar todas las ocurrencias de 0.9 en el PDF"""
    print("\n" + "="*80)
    print("Buscando valor 0.9 en todo el PDF")
    print("="*80)
    
    with pdfplumber.open(pdf_path) as pdf:
        for num_pagina, page in enumerate(pdf.pages):
            tablas = page.extract_tables()
            
            for idx_tabla, tabla in enumerate(tablas):
                for i, fila in enumerate(tabla):
                    # Buscar 0.9 en cualquier celda
                    fila_str = ' '.join([str(c) if c else '' for c in fila])
                    if '0.9' in fila_str or '0,9' in fila_str:
                        print(f"\n📄 Página {num_pagina + 1}, Tabla #{idx_tabla + 1}, Fila {i}")
                        
                        # Contexto: mostrar filas alrededor
                        print("  Contexto (-2 a +2):")
                        for j in range(max(0, i-2), min(len(tabla), i+3)):
                            row_vals = [str(c)[:20] if c else '-' for c in tabla[j][:6]]
                            marker = "  >>> " if j == i else "      "
                            print(f"{marker}Fila {j}: {' | '.join(row_vals)}")
                        
                        # Buscar número de lance en la tabla
                        tabla_str = ' '.join([' '.join([str(c) for c in r if c]) for r in tabla[:5]])
                        import re
                        match = re.search(r'LANCE\s*#?\s*(\d+)', tabla_str, re.IGNORECASE)
                        if match:
                            print(f"  ⚠️  Esta tabla pertenece a Lance #{match.group(1)}")

if __name__ == "__main__":
    pdf_folder = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo"
    pdf_path = os.path.join(pdf_folder, "doc-4.pdf")
    
    if os.path.exists(pdf_path):
        buscar_valor_09(pdf_path)
    else:
        print(f"❌ No se encontró: {pdf_path}")
