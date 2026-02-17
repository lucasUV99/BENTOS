"""
Visualizador de Datos JSON
Muestra de forma amigable los datos procesados
"""

import json
import os
from datetime import datetime


def cargar_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def mostrar_viaje(viaje_data):
    """Muestra información del viaje"""
    print("\n" + "="*70)
    print("🚢 INFORMACIÓN DEL VIAJE")
    print("="*70)
    
    print(f"\n📋 Identificación:")
    print(f"  ID:                {viaje_data.get('id_viaje', 'N/A')}")
    print(f"  Folio:             {viaje_data.get('folio_interno', 'N/A')}")
    
    print(f"\n🚢 Embarcación:")
    print(f"  Nombre:            {viaje_data.get('nave_nombre', 'N/A')}")
    print(f"  Armador:           {viaje_data.get('armador', 'N/A')}")
    print(f"  Capitán:           {viaje_data.get('capitan', 'N/A')}")
    
    print(f"\n📍 Puertos:")
    print(f"  Zarpe:             {viaje_data.get('puerto_zarpe', 'N/A')}")
    print(f"  Desembarque:       {viaje_data.get('puerto_desembarque', 'N/A')}")
    
    print(f"\n📅 Fechas:")
    fecha_zarpe = viaje_data.get('fecha_zarpe', 'N/A')
    fecha_recalada = viaje_data.get('fecha_recalada', 'N/A')
    print(f"  Zarpe:             {fecha_zarpe}")
    print(f"  Recalada:          {fecha_recalada}")
    
    # Calcular duración
    if fecha_zarpe != 'N/A' and fecha_recalada != 'N/A':
        try:
            dt_zarpe = datetime.fromisoformat(fecha_zarpe)
            dt_recalada = datetime.fromisoformat(fecha_recalada)
            duracion = dt_recalada - dt_zarpe
            print(f"  Duración:          {duracion.days} días, {duracion.seconds // 3600} horas")
        except:
            pass
    
    print(f"\n🎣 Actividad:")
    print(f"  Total de lances:   {viaje_data.get('total_lances_declarados', 'N/A')}")
    print(f"  Estado:            {viaje_data.get('estado_procesamiento', 'N/A')}")


def mostrar_lances(lances_data):
    """Muestra resumen de lances"""
    print("\n" + "="*70)
    print("🎣 DETALLE DE LANCES")
    print("="*70)
    
    total_lances = len(lances_data)
    print(f"\nTotal de lances: {total_lances}")
    
    # Estadísticas
    lances_con_pesca = sum(1 for l in lances_data if len(l.get('capturas', [])) > 0)
    lances_sin_pesca = total_lances - lances_con_pesca
    
    alertas = {'VERDE': 0, 'AMARILLO': 0, 'ROJO': 0}
    for lance in lances_data:
        alerta = lance.get('alerta_ecosistema', 'VERDE')
        alertas[alerta] = alertas.get(alerta, 0) + 1
    
    print(f"\nEstadísticas:")
    print(f"  Lances con pesca:        {lances_con_pesca}")
    print(f"  Lances sin pesca:        {lances_sin_pesca}")
    print(f"  🟢 Alertas VERDE:        {alertas['VERDE']}")
    if alertas['AMARILLO'] > 0:
        print(f"  🟡 Alertas AMARILLO:     {alertas['AMARILLO']}")
    if alertas['ROJO'] > 0:
        print(f"  🔴 Alertas ROJO:         {alertas['ROJO']}")
    
    # Detalle de cada lance
    print("\n" + "-"*70)
    for i, lance in enumerate(lances_data, 1):
        num_lance = lance.get('numero_lance', i)
        print(f"\nLance #{num_lance}")
        print("-" * 30)
        
        # Tiempo
        inicio = lance.get('inicio_lance', 'N/A')
        fin = lance.get('fin_lance', 'N/A')
        print(f"  ⏰ Inicio:          {inicio}")
        print(f"  ⏰ Fin:             {fin}")
        
        # Coordenadas
        pos_ini = lance.get('posicion_inicial', {})
        pos_fin = lance.get('posicion_final', {})
        
        if pos_ini:
            print(f"  📍 Posición inicial: {pos_ini.get('raw_lat', 'N/A')}, {pos_ini.get('raw_lng', 'N/A')}")
            print(f"     (Decimal: {pos_ini.get('lat', 'N/A')}, {pos_ini.get('lng', 'N/A')})")
        
        if pos_fin:
            print(f"  📍 Posición final:   {pos_fin.get('raw_lat', 'N/A')}, {pos_fin.get('raw_lng', 'N/A')}")
            print(f"     (Decimal: {pos_fin.get('lat', 'N/A')}, {pos_fin.get('lng', 'N/A')})")
        
        # Observaciones
        obs = lance.get('observaciones', '')
        if obs:
            print(f"  ⚠️  Observaciones:   {obs}")
        
        # Capturas
        capturas = lance.get('capturas', [])
        if capturas:
            print(f"  🐟 Capturas:")
            for captura in capturas:
                especie = captura.get('especie', 'Desconocida')
                tipo = captura.get('tipo_calculado', '')
                
                if 'retenida_ton' in captura:
                    cantidad = f"{captura['retenida_ton']} TON"
                elif 'descartada_unidades' in captura:
                    cantidad = f"{captura['descartada_unidades']} unidades (descarte)"
                else:
                    cantidad = "N/A"
                
                print(f"     • {especie:25} {cantidad:15} [{tipo}]")
        else:
            print(f"  🐟 Sin capturas")
        
        # Indicadores MSC
        ratio = lance.get('ratio_merluza_vs_objetivo')
        if ratio is not None:
            print(f"  📊 Ratio Merluza:    {ratio:.3f} ({ratio*100:.1f}%)")
        
        alerta = lance.get('alerta_ecosistema', 'VERDE')
        emoji_alerta = {'VERDE': '🟢', 'AMARILLO': '🟡', 'ROJO': '🔴'}.get(alerta, '⚪')
        print(f"  {emoji_alerta} Alerta:          {alerta}")
        
        if lance.get('especies_sensibles_detectadas'):
            print(f"  ⚠️  Especies sensibles detectadas (tiburones, rayas)")


def mostrar_validacion(validacion_data):
    """Muestra información de validación"""
    print("\n" + "="*70)
    print("✅ VALIDACIÓN DE DATOS")
    print("="*70)
    
    total_camaron = validacion_data.get('total_camaron_ton', 0)
    es_valido = validacion_data.get('es_valido', False)
    
    print(f"\nTotal Camarón nailon capturado: {total_camaron} TON")
    
    if es_valido:
        print("Estado: ✅ VÁLIDO - Los datos coinciden con el resumen del PDF")
    else:
        print("Estado: ❌ ERROR - Hay discrepancias en los totales")
    
    print(f"\nOtras estadísticas:")
    print(f"  Total de lances:              {validacion_data.get('total_lances', 'N/A')}")
    
    problemas = validacion_data.get('lances_con_problemas', 0)
    if problemas > 0:
        print(f"  Lances con problemas:         {problemas}")
    
    sensibles = validacion_data.get('lances_con_especies_sensibles', 0)
    if sensibles > 0:
        print(f"  Lances con especies sensibles: {sensibles}")


def visualizar_json(filepath):
    """Visualiza un archivo JSON de forma amigable"""
    print("\n" + "="*70)
    print("📊 VISUALIZADOR DE DATOS DE BITÁCORA")
    print("="*70)
    print(f"\nArchivo: {filepath}")
    
    try:
        datos = cargar_json(filepath)
        
        # Mostrar viaje
        if 'viaje' in datos:
            mostrar_viaje(datos['viaje'])
        
        # Mostrar lances
        if 'lances' in datos:
            mostrar_lances(datos['lances'])
        
        # Mostrar validación
        if 'validacion' in datos:
            mostrar_validacion(datos['validacion'])
        
        print("\n" + "="*70)
        print("✅ Visualización completada")
        print("="*70 + "\n")
        
    except FileNotFoundError:
        print(f"\n❌ Error: No se encontró el archivo {filepath}")
    except json.JSONDecodeError:
        print(f"\n❌ Error: El archivo no es un JSON válido")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def listar_archivos_output():
    """Lista todos los archivos JSON en data/output"""
    output_dir = "data/output"
    
    if not os.path.exists(output_dir):
        print(f"⚠️ No existe la carpeta {output_dir}")
        return []
    
    archivos = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    
    if not archivos:
        print(f"⚠️ No hay archivos JSON en {output_dir}")
        return []
    
    print(f"\n📁 Archivos disponibles en {output_dir}:")
    for i, archivo in enumerate(archivos, 1):
        print(f"  {i}. {archivo}")
    
    return archivos


def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1:
        # Archivo especificado por argumento
        filepath = sys.argv[1]
        visualizar_json(filepath)
    else:
        # Buscar archivos en data/output
        archivos = listar_archivos_output()
        
        if archivos:
            print("\nSelecciona un archivo (1-{}) o presiona Enter para salir: ".format(len(archivos)), end='')
            try:
                seleccion = input()
                if seleccion.strip():
                    idx = int(seleccion) - 1
                    if 0 <= idx < len(archivos):
                        filepath = os.path.join("data/output", archivos[idx])
                        visualizar_json(filepath)
                    else:
                        print("❌ Selección inválida")
            except (ValueError, KeyboardInterrupt):
                print("\nCancelado")
        else:
            print("\n💡 Uso:")
            print("  python visualizar_datos.py <ruta_al_json>")
            print("\nEjemplo:")
            print("  python visualizar_datos.py data/output/ejemplo_viaje_RAUTEN_3088.json")
            print("\nO genera datos de ejemplo primero:")
            print("  python generar_datos_ejemplo.py")


if __name__ == "__main__":
    main()
