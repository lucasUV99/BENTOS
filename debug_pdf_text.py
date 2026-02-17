"""
Extraer las primeras líneas de un PDF para ver el formato
"""
import pdfplumber

pdf_path = r"C:\Users\lucas\Desktop\Practica Pesquera\SOFTWARE TI\data\pdfs_ejemplo\SERNAPESCA-BE2021-3088-1.pdf"

print("="*80)
print("EXTRACCIÓN DE TEXTO DEL PDF")
print("="*80)

with pdfplumber.open(pdf_path) as pdf:
    # Primera página
    texto = pdf.pages[0].extract_text()
    
    # Mostrar las primeras 100 líneas
    lineas = texto.split('\n')
    
    print(f"\nTotal de líneas en la página 1: {len(lineas)}\n")
    print("PRIMERAS 50 LÍNEAS:")
    print("-"*80)
    
    for i, linea in enumerate(lineas[:50], 1):
        print(f"{i:3d}| {linea}")

print("\n" + "="*80)
print("Buscar patrón CAPITAN:")
import re
matches = re.findall(r'CAPITAN.*', texto, re.IGNORECASE)
for match in matches:
    print(f"  Encontrado: {match}")

print("\nBuscar patrón con variaciones:")
matches = re.findall(r'CAP[ÍI]T[ÁA]N.*', texto, re.IGNORECASE)
for match in matches:
    print(f"  Encontrado: {match}")
