import sys
sys.path.insert(0, 'backend')

from pdf_parser_v2 import BitacoraParser

pdf_path = "data/pdfs/bitacora_rauten_02-06_01_2021.pdf"

print(f"Procesando: {pdf_path}\n")

with BitacoraParser(pdf_path) as parser:
    resultado = parser.parsear_completo()

print("\n✅ RESULTADO:")
print(f"ID Viaje: {resultado['viaje']['id_viaje']}")
print(f"Nave: {resultado['viaje']['nave_nombre']}")
print(f"Armador: {resultado['viaje']['armador']}")
print(f"Capitán: {resultado['viaje']['capitan']}")
print(f"Fecha zarpe: {resultado['viaje']['fecha_zarpe']}")
print(f"Total lances procesados: {len(resultado['lances'])}")
print(f"Total lances declarados: {resultado['viaje']['total_lances_declarados']}")
print(f"\nTotal camarón: {resultado['validacion']['total_camaron_ton']} TON")
print(f"Total merluza: {resultado['validacion']['total_merluza_ton']} TON")
print(f"Ratio: {resultado['validacion']['ratio_merluza_camaron']}")
print(f"🚦 Alerta: {resultado['validacion']['alerta_ecosistema']}")
