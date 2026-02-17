#!/usr/bin/env python3
"""Verificar estructura de tablas en diferentes páginas"""

import pdfplumber
import json

# Verificar doc-2.pdf (BE-26682)
print("="*80)
print("PDF: doc-2.pdf (SERNAPESCA-BE-26682)")
print("="*80)

pdf = pdfplumber.open('data/pdfs_ejemplo/doc-2.pdf')

# Página 1 (resumen total)
print("\n--- PÁGINA 1 (Resumen Total) ---")
page1 = pdf.pages[0]
tables1 = page1.extract_tables()
print(f"Total tablas: {len(tables1)}")

if len(tables1) > 1:
    print("\nTabla de CAPTURA TOTAL:")
    print("Headers:", tables1[1][2])  # Fila con headers
    print("Fila 1 (Camarón nailon):", tables1[1][3])

# Página 2 (primer lance)
print("\n--- PÁGINA 2 (Lance #1) ---")
if len(pdf.pages) > 1:
    page2 = pdf.pages[1]
    tables2 = page2.extract_tables()
    print(f"Total tablas: {len(tables2)}")
    
    if len(tables2) > 0:
        print("\nPrimera tabla:")
        for i, fila in enumerate(tables2[0][:8]):
            print(f"Fila {i}: {fila}")

# Verificar doc.pdf (BE-26601)
print("\n" + "="*80)
print("PDF: doc.pdf (SERNAPESCA-BE-26601)")
print("="*80)

pdf2 = pdfplumber.open('data/pdfs_ejemplo/doc.pdf')

# Página 1
print("\n--- PÁGINA 1 (Resumen Total) ---")
page1 = pdf2.pages[0]
tables1 = page1.extract_tables()
print(f"Total tablas: {len(tables1)}")

if len(tables1) > 1:
    print("\nTabla de CAPTURA TOTAL:")
    print("Headers:", tables1[1][2])
    print("Fila 1 (Camarón nailon):", tables1[1][3])

pdf.close()
pdf2.close()
