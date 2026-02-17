"""
Script para debuggear extracción de PDF
"""

import sys
sys.path.insert(0, 'backend')

from pdf_parser_v2 import BitacoraParser
import pdfplumber

# Pide la ruta del PDF
pdf_path = input("Ingresa la ruta del PDF (o presiona Enter para usar el de ejemplo): ").strip()
if not pdf_path:
    pdf_path = "data/pdfs_ejemplo/SERNAPESCA-BE2021-3088-1.pdf"

print(f"\n📄 Analizando: {pdf_path}\n")
print("="*80)

# Extraer texto completo
with pdfplumber.open(pdf_path) as pdf:
    texto_completo = ""
    for i, pagina in enumerate(pdf.pages, 1):
        texto = pagina.extract_text()
        texto_completo += texto + "\n"
        print(f"\n--- PÁGINA {i} (primeros 500 caracteres) ---")
        print(texto[:500])

print("\n" + "="*80)
print("\n🔍 BUSCANDO FOLIO...\n")

import re

# Probar diferentes patrones
patrones = [
    r'Folio:\s*(SERNAPESCA-[^\s\n]+)',
    r'Folio[:\s]+(SERNAPESCA[^\s\n]+)',
    r'(SERNAPESCA-[A-Z0-9-]+)',
    r'Folio[:\s]+([^\s\n]+)',
]

for i, patron in enumerate(patrones, 1):
    match = re.search(patron, texto_completo, re.IGNORECASE)
    if match:
        print(f"✅ Patrón {i} encontró: '{match.group(1)}'")
    else:
        print(f"❌ Patrón {i} no encontró nada")

print("\n" + "="*80)
print("\n📊 PARSEANDO COMPLETO...\n")

# Parsear completo
with BitacoraParser(pdf_path) as parser:
    resultado = parser.parsear_completo()

print(f"ID Viaje: {resultado['viaje'].get('id_viaje')}")
print(f"Nave: {resultado['viaje'].get('nave_nombre')}")
print(f"Armador: {resultado['viaje'].get('armador')}")
print(f"Capitán: {resultado['viaje'].get('capitan')}")
print(f"Lances: {len(resultado['lances'])}")
