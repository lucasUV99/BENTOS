import sys
sys.path.append('backend')

from pdf_parser_v2 import BitacoraParser
import os

# Buscar primer PDF
pdfs = [f for f in os.listdir('data/pdfs') if f.endswith('.pdf')]
print(f'PDFs encontrados: {pdfs[:2]}')

if pdfs:
    pdf_path = f'data/pdfs/{pdfs[0]}'
    print(f'\nProbando parser con: {pdf_path}')
    
    with BitacoraParser(pdf_path) as parser:
        result = parser.parsear_completo()
        
        if result['lances']:
            especies = result['lances'][0]['especies']
            print(f'\nTotal entradas de especies: {len(especies)}')
            
            # Contar especies únicas
            especies_unicas = set(e['nombre'] for e in especies)
            print(f'Especies únicas: {len(especies_unicas)}')
            
            # Mostrar algunas especies
            print('\nPrimeras 10 especies:')
            for i, esp in enumerate(especies[:10]):
                print(f"  {i+1}. {esp['nombre']} - {esp.get('cantidad_ton', 0)} TON - {esp.get('tipo_captura', 'N/A')}")
