"""
Script para debug - Imprimir estructura de tablas del PDF
"""
import sys
import os
sys.path.append('backend')

import pdfplumber

def debug_lance_table(pdf_path, lance_numero=3):
    """Muestra la estructura exacta de la tabla del lance especificado"""
    print("\n" + "="*80)
    print(f"DEBUG: Estructura de tabla del lance #{lance_numero}")
    print(f"PDF: {os.path.basename(pdf_path)}")
    print("="*80)
    
    with pdfplumber.open(pdf_path) as pdf:
        # Buscar el texto "LANCE #{numero}" en las páginas
        for num_pagina, page in enumerate(pdf.pages):
            texto = page.extract_text()
            
            if f"LANCE # {lance_numero}" in texto or f"LANCE #{lance_numero}" in texto:
                print(f"\n✅ Encontrado LANCE #{lance_numero} en página {num_pagina + 1}")
                print("-"*80)
                
                # Extraer todas las tablas de esta página
                tablas = page.extract_tables()
                
                if not tablas:
                    print("⚠️  No se encontraron tablas en esta página")
                    continue
                
                print(f"📊 Total de tablas en página: {len(tablas)}\n")
                
                # Mostrar cada tabla
                for idx_tabla, tabla in enumerate(tablas):
                    print(f"\n{'='*80}")
                    print(f"TABLA #{idx_tabla + 1} ({len(tabla)} filas)")
                    print(f"{'='*80}\n")
                    
                    for idx_fila, fila in enumerate(tabla):
                        # Mostrar índices de columnas
                        if idx_fila == 0:
                            indices = [f"[{i}]" for i in range(len(fila))]
                            print("ÍNDICES:", " || ".join(f"{idx:^15}" for idx in indices))
                            print("-"*80)
                        
                        # Mostrar contenido de cada celda
                        celdas_str = []
                        for i, celda in enumerate(fila):
                            valor = str(celda) if celda is not None else "None"
                            # Truncar si es muy largo
                            if len(valor) > 15:
                                valor = valor[:12] + "..."
                            celdas_str.append(f"{valor:^15}")
                        
                        print(f"Fila {idx_fila:2d}:", " || ".join(celdas_str))
                        
                        # Buscar la fila con "Camarón nailon"
                        fila_str = ' '.join([str(c) for c in fila if c])
                        if 'Camarón' in fila_str or 'camarón' in fila_str:
                            print(" " * 8 + "👆 FILA CON CAMARÓN")
                            print(" " * 8 + f"Posible retenida en [{2}]: {fila[2] if len(fila) > 2 else 'N/A'}")
                            print(" " * 8 + f"Posible descartada en [{3}]: {fila[3] if len(fila) > 3 else 'N/A'}")
                        
                        # Buscar header
                        if 'Retenida' in fila_str and 'Descartada' in fila_str:
                            print(" " * 8 + "👆 HEADER ROW")
                            print(" " * 8 + "Columnas encontradas:")
                            for i, celda in enumerate(fila):
                                if celda:
                                    print(f" " * 12 + f"[{i}]: {celda}")
                    
                    print("\n" + "="*80)
                
                return  # Terminamos después de encontrar el lance
        
        print(f"\n❌ No se encontró el lance #{lance_numero} en el PDF")

if __name__ == "__main__":
    # Buscar el PDF de la bitácora 27072
    pdf_folder = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo"
    
    # Buscar doc-4.pdf que contiene la bitácora 27072
    pdf_path = os.path.join(pdf_folder, "doc-4.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"❌ No se encontró el archivo: {pdf_path}")
        print("\nBuscando todos los PDFs en la carpeta...")
        import glob
        pdfs = glob.glob(os.path.join(pdf_folder, "*.pdf"))
        for pdf in pdfs:
            print(f"  - {os.path.basename(pdf)}")
    else:
        # Debug del lance 3 (el problemático)
        debug_lance_table(pdf_path, lance_numero=3)
        
        print("\n" + "="*80)
        print("COMPARACIÓN: Lance 4 (que muestra correctamente 0.9 TON)")
        print("="*80)
        debug_lance_table(pdf_path, lance_numero=4)
