"""
Módulo mejorado de extracción de datos desde PDF de Bitácora Electrónica
Parsea el formato real de PDFs de Sernapesca
"""

import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Optional
from coordinate_converter import convert_position
from especies_config import (
    obtener_tipo_especie, 
    calcular_ratio_merluza, 
    calcular_alerta_ecosistema
)


class BitacoraParser:
    """Parser optimizado para PDFs reales de Bitácora Electrónica de Sernapesca"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf = None
        
    def __enter__(self):
        self.pdf = pdfplumber.open(self.pdf_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pdf:
            self.pdf.close()
    
    def parsear_completo(self) -> Dict:
        """
        Parsea todo el PDF y retorna estructura completa
        """
        texto_completo = self._extraer_texto_completo()
        
        # Extraer cabecera del viaje
        viaje = self._extraer_cabecera(texto_completo)
        
        # PRIMERO: Intentar extraer CAPTURA TOTAL de la primera página (dato oficial)
        especies_totales = self._extraer_captura_total()
        
        # SEGUNDO: Extraer lances individuales (con coordenadas)
        lances_individuales = self._extraer_lances()
        
        # Estrategia: Guardar AMBOS
        # 1. Si hay CAPTURA TOTAL, agregar un lance virtual con ID 0
        # 2. Agregar todos los lances individuales con sus coordenadas
        lances = []
        
        if especies_totales:
            print(f"✅ CAPTURA TOTAL encontrada: {len(especies_totales)} especies")
            # Lance virtual para resumen (ID = 0)
            lances.append({
                'numero_lance': 0,  # ID especial para CAPTURA TOTAL
                'arte_pesca': 'CAPTURA TOTAL',
                'especies': especies_totales,
                'fecha_inicio': viaje.get('fecha_zarpe'),
                'fecha_fin': viaje.get('fecha_recalada'),
                'es_captura_total': True
            })
        
        # Agregar lances individuales (con coordenadas)
        if lances_individuales:
            print(f"✅ Lances individuales encontrados: {len(lances_individuales)}")
            lances.extend(lances_individuales)
        else:
            print(f"⚠️  No se encontraron lances individuales en el PDF")
        
        # Calcular validaciones
        validacion = self._validar_datos(viaje, lances)
        
        return {
            'viaje': viaje,
            'lances': lances,
            'validacion': validacion
        }
    
    def _extraer_texto_completo(self) -> str:
        """Extrae todo el texto del PDF"""
        texto_completo = ""
        for pagina in self.pdf.pages:
            texto_completo += pagina.extract_text() + "\n"
        return texto_completo
    
    def _extraer_captura_total(self) -> List[Dict]:
        """
        Extrae la tabla de CAPTURA TOTAL de todas las páginas necesarias
        
        Esta es la fuente de verdad - contiene el resumen oficial de todas las capturas
        La tabla puede continuar en múltiples páginas
        Estructura de la tabla (6 columnas):
        [0] # (número)
        [1] ESPECIE (nombre)
        [2] Retenida (TON) ← COLUMNA CORRECTA
        [3] Descartada (TON) ← COLUMNA CORRECTA
        [4] Descartada (N°) - unidades (ignorar)
        [5] Incidental (N°) - unidades (ignorar)
        """
        especies = []
        
        if not self.pdf.pages:
            return especies
        
        try:
            # Buscar tabla CAPTURA TOTAL en todas las páginas
            especies_procesadas = set()  # Evitar duplicados
            
            for num_pagina, pagina in enumerate(self.pdf.pages):
                tablas = pagina.extract_tables()
                
                if not tablas:
                    continue
                
                # Buscar la tabla que contiene "CAPTURA TOTAL" o tiene headers correctos
                for tabla in tablas:
                    tabla_captura = None
                    inicio_datos = 0
                    
                    # Verificar headers
                    for i, fila in enumerate(tabla):
                        if not fila:
                            continue
                        
                        fila_str = ' '.join([str(c) for c in fila if c])
                        
                        # Buscar fila con headers característicos
                        if 'Retenida' in fila_str and 'Descartada' in fila_str and 'TON' in fila_str:
                            tabla_captura = tabla
                            inicio_datos = i + 1  # Datos comienzan después del header
                            print(f"✅ Encontrada tabla CAPTURA TOTAL en página {num_pagina + 1}, fila {i}")
                            break
                        # También detectar continuación de tabla (sin headers)
                        elif num_pagina > 0 and fila[0] and str(fila[0]).strip().isdigit():
                            # Es continuación de tabla de página anterior
                            tabla_captura = tabla
                            inicio_datos = i
                            print(f"✅ Continuación de tabla CAPTURA TOTAL en página {num_pagina + 1}")
                            break
                    
                    if not tabla_captura:
                        continue
                    
                    # Procesar filas de datos de esta página
                    for fila in tabla_captura[inicio_datos:]:
                        if not fila or len(fila) < 4:
                            continue
                        
                        # Extraer columnas
                        numero = str(fila[0]).strip() if fila[0] else ''
                        nombre = str(fila[1]).strip() if fila[1] else ''
                        retenida_str = str(fila[2]).strip() if len(fila) > 2 and fila[2] else ''
                        descartada_str = str(fila[3]).strip() if len(fila) > 3 and fila[3] else ''
                        descartada_unidades_str = str(fila[4]).strip() if len(fila) > 4 and fila[4] else ''
                        incidental_unidades_str = str(fila[5]).strip() if len(fila) > 5 and fila[5] else ''
                        
                        # Validar que es fila de datos válida
                        if not numero or not nombre:
                            continue
                        
                        # Saltar headers repetidos
                        if 'ESPECIE' in nombre.upper() or 'CAPTURA' in nombre.upper():
                            continue
                        
                        # Limpiar nombre
                        if ';' in nombre:
                            nombre = nombre.replace(';', ' / ')
                        
                        # Evitar duplicados
                        if nombre in especies_procesadas:
                            continue
                        especies_procesadas.add(nombre)
                        
                        # Procesar RETENIDA (columna [2])
                        if retenida_str:
                            try:
                                retenida_ton = float(retenida_str)
                                if retenida_ton >= 0.001:
                                    especies.append({
                                        'nombre': nombre,
                                        'cantidad_ton': retenida_ton,
                                        'cantidad_unidades': 0,
                                        'tipo_captura': 'retenida',
                                        'tipo_especie': obtener_tipo_especie(nombre)
                                    })
                                    print(f"  ✅ {nombre}: {retenida_ton} TON retenida")
                            except (ValueError, TypeError) as e:
                                print(f"  ⚠️  Error parseando retenida '{retenida_str}' para {nombre}: {e}")
                        
                        # Procesar DESCARTADA (columna [3] - TON)
                        if descartada_str:
                            try:
                                descartada_ton = float(descartada_str)
                                if descartada_ton >= 0.001:
                                    especies.append({
                                        'nombre': nombre,
                                        'cantidad_ton': descartada_ton,
                                        'cantidad_unidades': 0,
                                        'tipo_captura': 'descartada',
                                        'tipo_especie': obtener_tipo_especie(nombre)
                                    })
                                    print(f"  ✅ {nombre}: {descartada_ton} TON descartada")
                            except (ValueError, TypeError) as e:
                                print(f"  ⚠️  Error parseando descartada '{descartada_str}' para {nombre}: {e}")
                        
                        # Procesar DESCARTADA en UNIDADES (columna [4] - N°)
                        if descartada_unidades_str:
                            try:
                                descartada_unidades = int(descartada_unidades_str)
                                if descartada_unidades > 0:
                                    especies.append({
                                        'nombre': nombre,
                                        'cantidad_ton': 0,
                                        'cantidad_unidades': descartada_unidades,
                                        'tipo_captura': 'descartada',
                                        'tipo_especie': obtener_tipo_especie(nombre)
                                    })
                                    print(f"  ✅ {nombre}: {descartada_unidades} unidades descartadas")
                            except (ValueError, TypeError) as e:
                                pass  # Silenciar errores de unidades vacías
                        
                        # Procesar INCIDENTAL en UNIDADES (columna [5] - N°)
                        if incidental_unidades_str:
                            try:
                                incidental_unidades = int(incidental_unidades_str)
                                if incidental_unidades > 0:
                                    especies.append({
                                        'nombre': nombre,
                                        'cantidad_ton': 0,
                                        'cantidad_unidades': incidental_unidades,
                                        'tipo_captura': 'incidental',
                                        'tipo_especie': obtener_tipo_especie(nombre)
                                    })
                                    print(f"  ✅ {nombre}: {incidental_unidades} unidades incidentales")
                            except (ValueError, TypeError) as e:
                                pass  # Silenciar errores de unidades vacías
        
        except Exception as e:
            print(f"❌ Error extrayendo CAPTURA TOTAL: {e}")
            import traceback
            traceback.print_exc()
        
        return especies
    
    def _extraer_cabecera(self, texto: str) -> Dict:
        """
        Extrae información de la cabecera del viaje
        Formato real: REPRESENTACIÓN IMPRESA DE BITÁCORA ELECTRÓNICA DE PESCA
        """
        # Extraer Folio (ID único del viaje)
        # Formato antiguo: "SERNAPESCA-BE2021-3088-1"
        # Formato nuevo: "N° BITÁCORA 26601"
        
        # Intentar primero con el formato antiguo
        folio = self._buscar_patron(texto, r'(SERNAPESCA-BE\d{4}-\d+-\d+)', None)
        
        # Si no hay folio antiguo, buscar N° BITÁCORA
        if not folio:
            num_bitacora = self._buscar_patron(texto, r'N°\s+BIT[ÁA]CORA\s+(\d+)', None)
            if num_bitacora:
                folio = f'SERNAPESCA-BE-{num_bitacora}'
                print(f"📋 Usando N° Bitácora: {num_bitacora} → {folio}")
        
        # Si aún no hay folio, generar uno temporal
        if not folio:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            folio = f'SERNAPESCA-BE-TEMP-{timestamp}'
            print(f"⚠️  Advertencia: No se encontró Folio en PDF, usando temporal: {folio}")
        
        # Debug: mostrar folio extraído
        print(f"📋 Folio final: {folio}")
        
        # Extraer información general (formato real: mayúsculas, sin dos puntos)
        cabecera = {
            'id_viaje': folio,
            'folio_interno': folio,
            'armador': (self._buscar_patron(texto, r'ARMADOR\s+([^\n]+)', None) or 'DESCONOCIDO').strip(),
            'nave_nombre': (self._buscar_patron(texto, r'EMBARCACIÓN\s+([A-ZÁÉÍÓÚÑ]+)', None) or 'DESCONOCIDA').strip(),
            'nave_matricula': self._buscar_patron(texto, r'MATRÍCULA\s+(\d+)', None),
            # Intentar con y sin tilde
            'capitan': (
                self._buscar_patron(texto, r'CAPITÁN\s+([^\n]+)', None) or 
                self._buscar_patron(texto, r'CAPITAN\s+([^\n]+)', None) or 
                'DESCONOCIDO'
            ).strip(),
            'pais_abanderamiento': self._buscar_patron(texto, r'PAÍS\s+ABANDERAMIENTO\s+(\w+)', 'CL'),
            'señal_llamada': self._buscar_patron(texto, r'SEÑAL\s+DE\s+LLAMADA\s+([A-Z0-9-]+)', None),
            'puerto_zarpe': (self._buscar_patron(texto, r'ZARPE\s+([A-ZÁÉÍÓÚÑ]+)', None) or 'QUINTERO').strip(),
            'puerto_recalada': (
                self._buscar_patron(texto, r'DESEMBARQUE\s+([A-ZÁÉÍÓÚÑ]+)', None) or 
                self._buscar_patron(texto, r'RECALADA\s+([A-ZÁÉÍÓÚÑ]+)', None) or 
                'QUINTERO'
            ).strip(),
            'fecha_zarpe': self._parsear_fecha(self._buscar_patron(texto, r'ZARPE\s+(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})', None)),
            'fecha_recalada': self._parsear_fecha(self._buscar_patron(texto, r'RECALADA\s+(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})', None)),
            'total_lances_declarados': int(self._buscar_patron(texto, r'TOTAL\s+DE\s+LANCES\s+(\d+)', '0')),
            # Campos adicionales de PDFs nuevos
            'rpa': self._buscar_patron(texto, r'RPA\s+([^\n]+)', None),
            'aviso_recalada': self._buscar_patron(texto, r'AVISO\s+(?:DE\s+)?RECALADA\s+([^\n]+)', None),
        }
        
        return cabecera
    
    def _extraer_lances(self) -> List[Dict]:
        """
        Extrae todos los lances del PDF usando páginas
        Formato real: "LANCE # X ARTE PESCA"
        """
        lances = []
        
        # Procesar cada página
        for page_index, page in enumerate(self.pdf.pages):
            texto_pagina = page.extract_text()
            
            # Buscar bloques de lances (formato: "LANCE # X ARTE PESCA")
            # IMPORTANTE: Capturar TODO el bloque incluyendo "ARTE PESCA"
            patron_lance = r'(LANCE\s*#\s*(\d+)\s+ARTE\s+PESCA.*?)(?=LANCE\s*#|$)'
            bloques = re.finditer(patron_lance, texto_pagina, re.DOTALL | re.IGNORECASE)
            
            for bloque in bloques:
                contenido_completo = bloque.group(1)  # Contenido completo del lance
                num_lance = int(bloque.group(2))  # Número del lance
                
                lance = self._parsear_lance(num_lance, contenido_completo, page, page_index)
                if lance:
                    lances.append(lance)
        
        return lances
    
    def _parsear_lance(self, num_lance: int, contenido: str, page=None, page_index=None) -> Optional[Dict]:
        """
        Parsea un bloque de lance individual
        Formato real:
        LANCE # X ARTE PESCA ARRASTRE FONDO
        INICIO 03-01-2021 06:43:15 FIN 03-01-2021 08:43:45
        Latitud (dd mm.mmm) 35º 2.1593999999999' S ...
        """
        # Arte de pesca - buscar después de "ARTE PESCA"
        arte_match = re.search(r'ARTE\s+PESCA\s+([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|INICIO)', contenido, re.IGNORECASE)
        arte_pesca = arte_match.group(1).strip() if arte_match else 'ARRASTRE FONDO'
        
        lance = {
            'numero_lance': num_lance,
            'arte_pesca': arte_pesca,
            'fecha_inicio': self._parsear_fecha(self._buscar_patron(contenido, r'INICIO\s+(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})', None)),
            'fecha_fin': self._parsear_fecha(self._buscar_patron(contenido, r'FIN\s+(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})', None)),
            'observaciones': self._buscar_patron(contenido, r'OBSERVACIONES\s*([^\n]+)', None),
        }
        
        # Extraer coordenadas (formato: "Latitud (dd mm.mmm) 35º 2.1593999999999' S")
        # Buscar las dos latitudes
        latitudes = re.findall(r'Latitud\s+\([^)]+\)\s+([\d.º\'\s]+[NS])', contenido, re.IGNORECASE)
        longitudes = re.findall(r'Longitud\s+\([^)]+\)\s+([\d.º\'\s]+[EW])', contenido, re.IGNORECASE)
        
        if len(latitudes) >= 1 and len(longitudes) >= 1:
            coords_inicio = self._parsear_coordenadas_gms(f"{latitudes[0]} / {longitudes[0]}", 'inicio')
            lance.update(coords_inicio)
        
        if len(latitudes) >= 2 and len(longitudes) >= 2:
            coords_fin = self._parsear_coordenadas_gms(f"{latitudes[1]} / {longitudes[1]}", 'fin')
            lance.update(coords_fin)
        
        # Extraer especies capturadas (buscar en página actual y siguiente si es necesario)
        lance['especies'] = self._extraer_especies_lance(contenido, page, num_lance, page_index)
        
        return lance
    
    def _parsear_coordenadas_gms(self, coord_texto: str, prefijo: str) -> Dict:
        """
        Parsea coordenadas en formato: 35° 2.15939' S / 72° 36.95262' W
        Convierte a decimal
        """
        coords = {}
        
        try:
            # Latitud (formato: grados° minutos' S/N)
            # IMPORTANTE: Aceptar tanto ° como º (ordinal masculino)
            lat_match = re.search(r'(\d+)[°º]\s*([\d.]+)[\'\']\s*([NS])', coord_texto, re.IGNORECASE)
            if lat_match:
                grados = float(lat_match.group(1))
                minutos = float(lat_match.group(2))
                direccion = lat_match.group(3).upper()
                
                lat_decimal = grados + (minutos / 60.0)
                if direccion == 'S':
                    lat_decimal = -lat_decimal
                
                if lat_decimal is not None:
                    coords[f'latitud_{prefijo}'] = round(lat_decimal, 6)
            
            # Longitud (formato: grados° minutos' E/W)
            # IMPORTANTE: Aceptar tanto ° como º (ordinal masculino)
            lon_match = re.search(r'(\d+)[°º]\s*([\d.]+)[\'\']\s*([EW])', coord_texto, re.IGNORECASE)
            if lon_match:
                grados = float(lon_match.group(1))
                minutos = float(lon_match.group(2))
                direccion = lon_match.group(3).upper()
                
                lon_decimal = grados + (minutos / 60.0)
                if direccion == 'W':
                    lon_decimal = -lon_decimal
                
                if lon_decimal is not None:
                    coords[f'longitud_{prefijo}'] = round(lon_decimal, 6)
        
        except Exception as e:
            print(f"⚠️  Error parseando coordenadas '{coord_texto}': {e}")
        
        return coords
    
    def _extraer_especies_lance(self, contenido: str, page, num_lance: int) -> List[Dict]:
        """
        Extrae especies de un lance usando la tabla estructurada del PDF
        
        Estructura real de la tabla (6 columnas):
        [0] # (número)
        [1] ESPECIE (nombre)
        [2] Retenida (TON) 
        [3] Descartada (TON) 
        [4] Descartada (N°) - UNIDADES, no toneladas
        [5] Incidental (N°) - UNIDADES, no toneladas
        
        Solo procesamos columnas [2] y [3] que son toneladas.
        Ignoramos [4] y [5] que son unidades.
        """
        especies = []
        
        if not page:
            return especies
        
        try:
            # Extraer tablas de la página
            tablas = page.extract_tables()
            
            if not tablas:
                return especies
            
            # ESTRATEGIA: Priorizar tabla dedicada de especies sobre tabla "DETALLE DE LANCE"
            # 1. Buscar primero tabla con "ESPECIE" + headers Retenida/Descartada
            # 2. Si no existe, buscar en tablas "DETALLE DE LANCE"
            # 3. Procesar SOLO UNA tabla por lance
            
            tabla_especies = None
            tabla_detalle_lance = None
            
            for tabla in tablas:
                if not tabla or len(tabla) < 2:
                    continue
                
                # Verificar si es tabla "DETALLE DE LANCE" (primera celda)
                primera_celda = str(tabla[0][0]) if tabla[0] and tabla[0][0] else ''
                es_tabla_detalle = 'DETALLE' in primera_celda.upper() and 'LANCE' in primera_celda.upper()
                
                # VERIFICACIÓN CRÍTICA: Si es tabla DETALLE, verificar que pertenece al lance correcto
                if es_tabla_detalle:
                    tabla_str = ' '.join([' '.join([str(c) for c in fila if c]) for fila in tabla[:5]])
                    # Buscar "LANCE # {num_lance}" en las primeras filas
                    import re
                    patron_lance = r'LANCE\s*#?\s*' + str(num_lance) + r'\b'
                    if not re.search(patron_lance, tabla_str, re.IGNORECASE):
                        # Esta tabla DETALLE NO pertenece a este lance, saltar
                        continue
                
                # Buscar headers en las primeras filas
                for i, fila in enumerate(tabla[:10]):  # Revisar primeras 10 filas (DETALLE puede tener headers más abajo)
                    if not fila:
                        continue
                    fila_str = ' '.join([str(c) for c in fila if c])
                    
                    if 'Retenida' in fila_str and 'Descartada' in fila_str and 'TON' in fila_str:
                        # Encontramos una tabla con headers válidos
                        if not es_tabla_detalle and ('ESPECIE' in fila_str.upper() or i == 0):
                            # Tabla dedicada de especies - PRIORIDAD
                            # NO verificamos número de lance aquí - asumimos que pertenece a la página
                            tabla_especies = (tabla, i)
                            break
                        elif es_tabla_detalle:
                            # Tabla "DETALLE DE LANCE" - FALLBACK (ya verificada que coincide el lance)
                            if not tabla_detalle_lance:
                                tabla_detalle_lance = (tabla, i)
                            break
                
                # Si ya encontramos tabla dedicada, no seguir buscando
                if tabla_especies:
                    break
            
            # Usar la tabla con prioridad: dedicada > detalle > ninguna
            tabla_a_procesar = tabla_especies if tabla_especies else tabla_detalle_lance
            
            if not tabla_a_procesar:
                return especies
            
            tabla, fila_header_idx = tabla_a_procesar
            
            # Procesar SOLO esta tabla
            header_encontrado = False
            inicio_datos = 0
            retenida_col = None
            descartada_col = None
            
            # Extraer columnas del header
            fila_header = tabla[fila_header_idx]
            fila_str = ' '.join([str(c) for c in fila_header if c])
            
            if 'Retenida' in fila_str and 'Descartada' in fila_str and 'TON' in fila_str:
                header_encontrado = True
                inicio_datos = fila_header_idx + 1
                
                # DETECCIÓN DINÁMICA: Buscar columnas de Retenida y Descartada
                for col_idx, celda in enumerate(fila_header):
                    celda_str = str(celda) if celda else ''
                    if 'Retenida' in celda_str and 'TON' in celda_str:
                        retenida_col = col_idx
                    elif 'Descartada' in celda_str and 'TON' in celda_str:
                        descartada_col = col_idx
                
                tipo_tabla = "ESPECIES" if tabla_especies else "DETALLE"
                print(f"  📋 Lance #{num_lance} - Tabla {tipo_tabla} - Headers: Retenida=[{retenida_col}], Descartada=[{descartada_col}]")
                tipo_tabla = "ESPECIES" if tabla_especies else "DETALLE"
                print(f"  📋 Lance #{num_lance} - Tabla {tipo_tabla} - Headers: Retenida=[{retenida_col}], Descartada=[{descartada_col}]")
            
            if not header_encontrado or retenida_col is None or descartada_col is None:
                return especies
            
            # Procesar filas de datos de la tabla seleccionada
            for fila in tabla[inicio_datos:]:
                if not fila or len(fila) < 3:
                    continue
                
                # Usar detección DINÁMICA de columnas basada en headers
                # Esto maneja diferentes estructuras de tabla correctamente
                
                numero = fila[0] if len(fila) > 0 else ''
                nombre = fila[1] if len(fila) > 1 else ''
                
                # Validar que es una fila de datos (tiene número y nombre)
                if not numero or not nombre:
                    continue
                
                # Saltar headers
                nombre_upper = str(nombre).upper()
                if 'ESPECIE' in nombre_upper or 'CAPTURA' in nombre_upper or 'TIPO' in nombre_upper or 'OBSERV' in nombre_upper:
                    continue
                
                # Limpiar nombre
                nombre = str(nombre).strip()
                if ';' in nombre:
                    nombre = nombre.replace(';', ' / ')
                
                # USAR COLUMNAS DETECTADAS DINÁMICAMENTE
                # Posición retenida_col = Retenida (TON)
                retenida_str = fila[retenida_col] if len(fila) > retenida_col else ''
                if retenida_str and str(retenida_str).strip() and str(retenida_str).strip() != '':
                    try:
                        retenida_ton = float(str(retenida_str).strip())
                        if retenida_ton >= 0.001:
                            especies.append({
                                'nombre': nombre,
                                'cantidad_ton': retenida_ton,
                                'tipo_captura': 'retenida',
                                'tipo_especie': obtener_tipo_especie(nombre)
                            })
                            print(f"  Lance #{num_lance} - {nombre}: {retenida_ton} TON retenida")
                    except (ValueError, TypeError):
                        pass
                
                # Posición descartada_col = Descartada (TON)
                descartada_str = fila[descartada_col] if len(fila) > descartada_col else ''
                if descartada_str and str(descartada_str).strip() and str(descartada_str).strip() != '':
                    try:
                        descartada_ton = float(str(descartada_str).strip())
                        if descartada_ton >= 0.001:
                            especies.append({
                                'nombre': nombre,
                                'cantidad_ton': descartada_ton,
                                'tipo_captura': 'descartada',
                                'tipo_especie': obtener_tipo_especie(nombre)
                            })
                            print(f"  Lance #{num_lance} - {nombre}: {descartada_ton} TON descartada")
                    except (ValueError, TypeError):
                        pass
        
        except Exception as e:
            print(f"⚠️  Error extrayendo especies del lance #{num_lance}: {e}")
        
        return especies
    
    def _validar_datos(self, viaje: Dict, lances: List[Dict]) -> Dict:
        """
        Valida y calcula métricas del viaje
        """
        # Calcular totales por especie
        totales_especies = {}
        total_camaron = 0
        total_merluza = 0
        
        # Preparar lista de capturas para cálculo de ratio
        todas_capturas = []
        
        # Separar lance de CAPTURA TOTAL de lances individuales
        lance_captura_total = None
        lances_individuales = []
        
        for lance in lances:
            if lance.get('numero_lance') == 0:
                lance_captura_total = lance
            else:
                lances_individuales.append(lance)
        
        # IMPORTANTE: Usar SOLO el lance de CAPTURA TOTAL si existe (fuente de verdad)
        # Si no existe, usar los lances individuales
        lances_para_calcular = [lance_captura_total] if lance_captura_total else lances_individuales
        
        for lance in lances_para_calcular:
            for especie in lance.get('especies', []):
                nombre = especie['nombre']
                cantidad = especie['cantidad_ton']
                tipo_captura = especie['tipo_captura']
                
                if nombre not in totales_especies:
                    totales_especies[nombre] = {
                        'retenida': 0,
                        'descartada': 0
                    }
                
                totales_especies[nombre][tipo_captura] += cantidad
                
                # Agregar a lista para ratio (solo retenida)
                if tipo_captura == 'retenida':
                    todas_capturas.append({
                        'especie': nombre,
                        'retenida_ton': cantidad
                    })
                
                # Sumar camarón y merluza para stats
                if 'camarón' in nombre.lower() or 'camaron' in nombre.lower():
                    total_camaron += cantidad
                if 'merluza' in nombre.lower():
                    total_merluza += cantidad
        
        # Calcular ratio merluza (pasa lista de capturas)
        ratio_merluza = calcular_ratio_merluza(todas_capturas)
        
        # Calcular alerta ecosistema
        alerta = calcular_alerta_ecosistema(ratio_merluza)
        
        validacion = {
            'total_lances_procesados': len(lances_individuales),  # Solo lances reales
            'total_lances_declarados': viaje.get('total_lances_declarados', 0),
            'coincide_numero_lances': len(lances_individuales) == viaje.get('total_lances_declarados', 0),
            'total_especies': len(totales_especies),
            'total_camaron_ton': round(total_camaron, 3) if total_camaron else 0,
            'total_merluza_ton': round(total_merluza, 3) if total_merluza else 0,
            'ratio_merluza_camaron': round(ratio_merluza, 4) if ratio_merluza is not None else 0,
            'alerta_ecosistema': alerta,
            'especies_totales': totales_especies
        }
        
        return validacion
    
    def _buscar_patron(self, texto: str, patron: str, default: Optional[str]) -> Optional[str]:
        """Busca un patrón regex y retorna el primer grupo"""
        match = re.search(patron, texto, re.IGNORECASE)
        return match.group(1) if match else default
    
    def _parsear_fecha(self, fecha_str: Optional[str]) -> Optional[str]:
        """
        Parsea fecha en formato: 02-01-2021 10:54:58
        Retorna ISO format
        """
        if not fecha_str:
            return None
        
        fecha_str = fecha_str.strip()
        
        # Formatos posibles
        formatos = [
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%d-%m-%Y',
            '%d/%m/%Y'
        ]
        
        for formato in formatos:
            try:
                dt = datetime.strptime(fecha_str, formato)
                return dt.isoformat()
            except ValueError:
                continue
        
        return None


# Mantener compatibilidad con código existente
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python pdf_parser_v2.py <ruta_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print(f"📄 Procesando: {pdf_path}")
    
    with BitacoraParser(pdf_path) as parser:
        resultado = parser.parsear_completo()
    
    print("\n✅ Viaje:")
    for key, value in resultado['viaje'].items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ Lances procesados: {len(resultado['lances'])}")
    
    print("\n✅ Validación:")
    for key, value in resultado['validacion'].items():
        if key != 'especies_totales':
            print(f"  {key}: {value}")
