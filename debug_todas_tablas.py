"""
Debug detallado: Mostrar TODAS las tablas de la bitácora 27072
"""
import sys
import os
sys.path.append('backend')

import pdfplumber
import re

def debug_todas_las_tablas(pdf_path):
    """Muestra todas las tablas encontradas en el PDF con sus headers"""
    print("\n" + "="*80)
    print(f"DEBUG: Todas las tablas del PDF")
    print(f"PDF: {os.path.basename(pdf_path)}")
    print("="*80)
    
    with pdfplumber.open(pdf_path) as pdf:
        # Buscar bloques de LANCE # en todas las páginas
        patron_lance = r'LANCE\s*#\s*(\d+)'
        
        for num_pagina, page in enumerate(pdf.pages):
            texto = page.extract_text()
            
            # Buscar lances en esta página
            lances_en_pagina = re.findall(patron_lance, texto)
            
            if lances_en_pagina:
                print(f"\n{'='*80}")
                print(f"PÁGINA {num_pagina + 1}")
                print(f"Lances encontrados: {', '.join(lances_en_pagina)}")
                print(f"{'='*80}\n")
                
                # Extraer tablas
                tablas = page.extract_tables()
                
                if not tablas:
                    print("  ⚠️  No se encontraron tablas en esta página")
                    continue
                
                print(f"  📊 Total de tablas: {len(tablas)}\n")
                
                for idx_tabla, tabla in enumerate(tablas):
                    print(f"  {'-'*76}")
                    print(f"  TABLA #{idx_tabla + 1} ({len(tabla)} filas)")
                    print(f"  {'-'*76}")
                    
                    # Mostrar primeras 5 filas para identificar la tabla
                    for i, fila in enumerate(tabla[:5]):
                        fila_str = ' || '.join([str(c)[:20] if c else 'None' for c in fila])
                        print(f"    Fila {i}: {fila_str}")
                        
                        # Detectar tipo de tabla
                        fila_completa = ' '.join([str(c) for c in fila if c])
                        if 'DETALLE DE LANCE' in fila_completa:
                            print(f"      👉 TABLA 'DETALLE DE LANCE' - SERÁ FILTRADA")
                        if 'Retenida' in fila_completa and 'TON' in fila_completa:
                            # Encontrar columnas
                            for col_idx, celda in enumerate(fila):
                                celda_str = str(celda) if celda else ''
                                if 'Retenida' in celda_str and 'TON' in celda_str:
                                    print(f"      👉 HEADER: Retenida en columna [{col_idx}]")
                                elif 'Descartada' in celda_str and 'TON' in celda_str:
                                    print(f"      👉 HEADER: Descartada en columna [{col_idx}]")
                    
                    print()

if __name__ == "__main__":
    pdf_folder = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo"
    pdf_path = os.path.join(pdf_folder, "doc-4.pdf")
    
    if os.path.exists(pdf_path):
        debug_todas_las_tablas(pdf_path)
    else:
        print(f"❌ No se encontró: {pdf_path}")
