"""
Analizar el formato de los PDFs nuevos
"""
import pdfplumber
import re

pdf_path = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo\doc.pdf"

print("="*80)
print("ANÁLISIS DEL PDF NUEVO")
print("="*80)

with pdfplumber.open(pdf_path) as pdf:
    texto = pdf.pages[0].extract_text()
    
    print("\nPRIMERAS 60 LÍNEAS:")
    print("-"*80)
    
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas[:60], 1):
        print(f"{i:3d}| {linea}")
    
    print("\n" + "="*80)
    print("BÚSQUEDA DE PATRONES:")
    print("-"*80)
    
    # Buscar CAPITÁN
    print("\n1. CAPITÁN:")
    matches = re.findall(r'CAPIT[ÁA]N[:\s]+([^\n]+)', texto, re.IGNORECASE)
    for match in matches:
        print(f"   ✓ Encontrado: {match}")
    
    # Buscar FOLIO
    print("\n2. FOLIO:")
    matches = re.findall(r'(SERNAPESCA-[A-Z0-9-]+)', texto)
    for match in matches:
        print(f"   ✓ Encontrado: {match}")
    
    # Buscar RPA
    print("\n3. RPA:")
    matches = re.findall(r'RPA[:\s]+([^\n]+)', texto, re.IGNORECASE)
    for match in matches:
        print(f"   ✓ Encontrado: {match}")
    
    # Buscar AVISO RECALADA
    print("\n4. AVISO RECALADA:")
    matches = re.findall(r'AVISO.*?RECALADA[:\s]+([^\n]+)', texto, re.IGNORECASE)
    for match in matches:
        print(f"   ✓ Encontrado: {match}")
    
    # Buscar EMBARCACIÓN
    print("\n5. EMBARCACIÓN:")
    matches = re.findall(r'EMBARCACI[ÓO]N[:\s]+([^\n]+)', texto, re.IGNORECASE)
    for match in matches:
        print(f"   ✓ Encontrado: {match}")
    
    # Buscar ARMADOR
    print("\n6. ARMADOR:")
    matches = re.findall(r'ARMADOR[:\s]+([^\n]+)', texto, re.IGNORECASE)
    for match in matches:
        print(f"   ✓ Encontrado: {match}")
