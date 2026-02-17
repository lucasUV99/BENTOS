"""
Script de verificación: Compara PDF vs Firebase
"""
import sys
sys.path.insert(0, 'backend')

from pdf_parser_v2 import BitacoraParser
from firebase_manager import FirebaseManager
import pdfplumber

# PDF a verificar
pdf_path = "data/pdfs/bitacora_rauten_02-06_01_2021.pdf"
viaje_id = "SERNAPESCA-BE2021-3088-1"

print("="*80)
print("VERIFICACIÓN DE INTEGRIDAD DE DATOS")
print("="*80)
print(f"\nPDF: {pdf_path}")
print(f"ID Viaje: {viaje_id}\n")

# 1. Extraer datos del PDF
print("📄 Extrayendo datos del PDF...")
with BitacoraParser(pdf_path) as parser:
    datos_pdf = parser.parsear_completo()

# 2. Obtener datos de Firebase
print("☁️  Consultando Firebase...")
firebase = FirebaseManager()
viaje_fb = firebase.obtener_viaje(viaje_id)
lances_fb = firebase.obtener_lances_viaje(viaje_id)

if not viaje_fb:
    print(f"❌ ERROR: No se encontró el viaje {viaje_id} en Firebase")
    sys.exit(1)

print(f"✅ Encontrado en Firebase: {viaje_id}")
print(f"   Lances en Firebase: {len(lances_fb)}")
print(f"   Lances en PDF: {len(datos_pdf['lances'])}\n")

# 3. Comparar CABECERA
print("="*80)
print("VERIFICACIÓN DE CABECERA DEL VIAJE")
print("="*80)

campos_viaje = [
    'id_viaje', 'folio_interno', 'nave_nombre', 'nave_matricula',
    'armador', 'capitan', 'pais_abanderamiento', 
    'puerto_zarpe', 'puerto_recalada',
    'fecha_zarpe', 'fecha_recalada', 'total_lances_declarados'
]

errores_cabecera = []

for campo in campos_viaje:
    valor_pdf = datos_pdf['viaje'].get(campo)
    valor_fb = viaje_fb.get(campo)
    
    match = valor_pdf == valor_fb
    status = "✅" if match else "❌"
    
    print(f"\n{status} {campo}:")
    print(f"   PDF:      {repr(valor_pdf)}")
    print(f"   Firebase: {repr(valor_fb)}")
    
    if not match:
        errores_cabecera.append({
            'campo': campo,
            'pdf': valor_pdf,
            'firebase': valor_fb
        })

# 4. Comparar LANCES
print("\n" + "="*80)
print("VERIFICACIÓN DE LANCES")
print("="*80)

print(f"\nTotal lances PDF: {len(datos_pdf['lances'])}")
print(f"Total lances Firebase: {len(lances_fb)}")

if len(datos_pdf['lances']) != len(lances_fb):
    print(f"❌ ERROR: Número de lances NO coincide")
else:
    print(f"✅ Número de lances coincide")

# Verificar cada lance
errores_lances = []

for i, lance_pdf in enumerate(datos_pdf['lances']):
    num_lance = lance_pdf['numero_lance']
    
    # Buscar lance correspondiente en Firebase
    lance_fb = next((l for l in lances_fb if l.get('numero_lance') == num_lance), None)
    
    if not lance_fb:
        print(f"\n❌ Lance #{num_lance}: NO encontrado en Firebase")
        errores_lances.append({
            'lance': num_lance,
            'error': 'No encontrado en Firebase'
        })
        continue
    
    print(f"\n--- Lance #{num_lance} ---")
    
    # Comparar campos clave
    campos_lance = ['fecha_inicio', 'fecha_fin', 'arte_pesca', 'latitud_inicio', 
                    'longitud_inicio', 'latitud_fin', 'longitud_fin']
    
    for campo in campos_lance:
        valor_pdf = lance_pdf.get(campo)
        valor_fb = lance_fb.get(campo)
        
        if valor_pdf != valor_fb:
            print(f"  ❌ {campo}: PDF={valor_pdf} vs FB={valor_fb}")
            errores_lances.append({
                'lance': num_lance,
                'campo': campo,
                'pdf': valor_pdf,
                'firebase': valor_fb
            })
        else:
            print(f"  ✅ {campo}: OK")
    
    # Comparar especies
    especies_pdf = lance_pdf.get('especies', [])
    especies_fb = lance_fb.get('especies', [])
    
    print(f"  Especies PDF: {len(especies_pdf)}, Firebase: {len(especies_fb)}")
    
    if len(especies_pdf) != len(especies_fb):
        print(f"  ❌ Número de especies NO coincide")
        errores_lances.append({
            'lance': num_lance,
            'error': f'Especies: PDF={len(especies_pdf)} vs FB={len(especies_fb)}'
        })

# 5. RESUMEN FINAL
print("\n" + "="*80)
print("RESUMEN DE VERIFICACIÓN")
print("="*80)

if errores_cabecera:
    print(f"\n❌ ERRORES EN CABECERA: {len(errores_cabecera)}")
    for error in errores_cabecera:
        print(f"   - {error['campo']}: PDF='{error['pdf']}' ≠ FB='{error['firebase']}'")
else:
    print(f"\n✅ CABECERA: Todos los campos coinciden")

if errores_lances:
    print(f"\n❌ ERRORES EN LANCES: {len(errores_lances)}")
    for error in errores_lances[:10]:  # Mostrar primeros 10
        if 'campo' in error:
            print(f"   - Lance {error['lance']}, {error['campo']}: PDF='{error['pdf']}' ≠ FB='{error['firebase']}'")
        else:
            print(f"   - Lance {error['lance']}: {error['error']}")
else:
    print(f"\n✅ LANCES: Todos los lances coinciden")

# 6. Verificar totales
print("\n" + "="*80)
print("VERIFICACIÓN DE TOTALES")
print("="*80)

validacion_pdf = datos_pdf['validacion']

print(f"\nTotal camarón (PDF):     {validacion_pdf['total_camaron_ton']} TON")
print(f"Total merluza (PDF):     {validacion_pdf['total_merluza_ton']} TON")
print(f"Ratio merluza/camarón:   {validacion_pdf['ratio_merluza_camaron']}")
print(f"Alerta ecosistema:       {validacion_pdf['alerta_ecosistema']}")

# Verificar contra PDF original
print("\n" + "="*80)
print("VERIFICACIÓN CONTRA TEXTO DEL PDF")
print("="*80)

with pdfplumber.open(pdf_path) as pdf:
    texto_completo = ""
    for pagina in pdf.pages:
        texto_completo += pagina.extract_text() + "\n"

# Buscar tabla de captura total
import re
print("\nBuscando CAPTURA TOTAL en PDF...")
captura_match = re.search(r'CAPTURA TOTAL.*?TIPO DE CAPTURA(.*?)(?=DETALLE|LANCE|$)', texto_completo, re.DOTALL)

if captura_match:
    print("✅ Sección de CAPTURA TOTAL encontrada")
    captura_texto = captura_match.group(1)
    print("\nPrimeras 500 caracteres de CAPTURA TOTAL:")
    print(captura_texto[:500])
else:
    print("❌ No se encontró sección CAPTURA TOTAL")

print("\n" + "="*80)
print("CONCLUSIÓN")
print("="*80)

if not errores_cabecera and not errores_lances:
    print("\n✅ ✅ ✅ VERIFICACIÓN EXITOSA ✅ ✅ ✅")
    print("Todos los datos coinciden exactamente entre PDF y Firebase")
else:
    print("\n❌ ❌ ❌ SE ENCONTRARON DISCREPANCIAS ❌ ❌ ❌")
    print(f"Errores en cabecera: {len(errores_cabecera)}")
    print(f"Errores en lances: {len(errores_lances)}")
    print("\n⚠️  ACCIÓN REQUERIDA: Revisar y corregir el parser")
