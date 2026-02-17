"""
Debug específico: Ver la tabla completa del Lance #3 en página 3
"""
import sys
import os
sys.path.append('backend')

import pdfplumber

def debug_lance_3_completo(pdf_path):
    """Muestra la estructura completa de las tablas en la página del Lance #3"""
    print("\n" + "="*80)
    print("DEBUG: Lance #3 - Página 3 - Estructura completa de tablas")
    print("="*80)
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[2]  # Página 3 (índice 2)
        
        print(f"\n📄 Texto de la página (primeros 500 caracteres):")
        print("-"*80)
        texto = page.extract_text()
        print(texto[:500])
        print("-"*80)
        
        tablas = page.extract_tables()
        
        print(f"\n📊 Total de tablas en página 3: {len(tablas)}\n")
        
        for idx_tabla, tabla in enumerate(tablas):
            print(f"\n{'='*80}")
            print(f"TABLA #{idx_tabla + 1} ({len(tabla)} filas)")
            print(f"{'='*80}")
            
            # Primera fila para identificación
            primera_fila_str = ' '.join([str(c) for c in tabla[0] if c])
            if 'DETALLE' in primera_fila_str:
                print("⚠️  TABLA 'DETALLE DE LANCE'")
            
            # Mostrar TODAS las filas de esta tabla
            for i, fila in enumerate(tabla):
                # Buscar indicadores
                fila_str = ' '.join([str(c) for c in fila if c])
                
                # Buscar número de lance
                if 'LANCE #' in fila_str or 'LANCE#' in fila_str:
                    for celda in fila:
                        if celda and str(celda).strip().isdigit():
                            num_lance = str(celda).strip()
                            print(f"\n>>> FILA {i}: LANCE #{num_lance} <<<")
                
                # Buscar headers
                if 'Retenida' in fila_str and 'TON' in fila_str:
                    print(f"\n>>> FILA {i}: HEADER ROW <<<")
                    for col_idx, celda in enumerate(fila):
                        if celda:
                            print(f"    Columna [{col_idx}]: {celda}")
                
                # Mostrar la fila completa
                celdas_str = []
                for j, celda in enumerate(fila):
                    valor = str(celda) if celda is not None else "None"
                    if len(valor) > 20:
                        valor = valor[:17] + "..."
                    celdas_str.append(f"[{j}]:{valor}")
                
                print(f"Fila {i:2d}: {' | '.join(celdas_str)}")
                
                # Destacar filas con especies
                if 'Camarón' in fila_str or 'camarón' in fila_str:
                    print(f"    ^^^ CAMARÓN ENCONTRADO - Columna [3]={fila[3] if len(fila) > 3 else 'N/A'}")

if __name__ == "__main__":
    pdf_folder = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo"
    pdf_path = os.path.join(pdf_folder, "doc-4.pdf")
    
    if os.path.exists(pdf_path):
        debug_lance_3_completo(pdf_path)
    else:
        print(f"❌ No se encontró: {pdf_path}")
