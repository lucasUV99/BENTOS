"""
Módulo mejorado de extracción de datos desde PDF de Bitácora Electrónica
Parsea el formato real de PDFs de Sernapesca usando enfoque table-sequential.

Resuelve problemas conocidos:
- Lances que se extienden entre múltiples páginas
- Tablas de continuación de especies (6 cols) al inicio de páginas
- Tablas DETALLE DE LANCE con número variable de columnas (4, 8, 9 cols)
- CAPTURA TOTAL que continúa en la página 2
- Observaciones multilínea
"""

import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
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
        Parsea todo el PDF y retorna estructura completa.
        Usa enfoque table-sequential: recorre TODAS las tablas de TODAS las páginas
        en orden para manejar correctamente lances que cruzan páginas.
        """
        # Paso 1: Recopilar TODAS las tablas de TODAS las páginas en orden
        todas_tablas = self._recopilar_todas_tablas()
        
        # Paso 2: Extraer cabecera desde la primera página (tabla INFORMACION GENERAL)
        texto_completo = self._extraer_texto_completo()
        viaje = self._extraer_cabecera(texto_completo, todas_tablas)
        
        # Paso 3: Clasificar y procesar tablas secuencialmente
        especies_totales, lances_individuales = self._procesar_tablas_secuencial(todas_tablas)
        
        # Paso 4: Construir lista de lances
        lances = []
        
        if especies_totales:
            print(f"  CAPTURA TOTAL encontrada: {len(especies_totales)} especies")
            lances.append({
                'numero_lance': 0,
                'arte_pesca': 'CAPTURA TOTAL',
                'especies': especies_totales,
                'fecha_inicio': viaje.get('fecha_zarpe'),
                'fecha_fin': viaje.get('fecha_recalada'),
                'es_captura_total': True
            })
        
        if lances_individuales:
            print(f"  Lances individuales encontrados: {len(lances_individuales)}")
            lances.extend(lances_individuales)
        else:
            print(f"  No se encontraron lances individuales en el PDF")
        
        # Paso 5: Validaciones
        validacion = self._validar_datos(viaje, lances)
        
        return {
            'viaje': viaje,
            'lances': lances,
            'validacion': validacion
        }
    
    # =========================================================================
    # RECOPILACIÓN DE TABLAS
    # =========================================================================
    
    def _recopilar_todas_tablas(self) -> List[Tuple[int, list]]:
        """
        Recopila TODAS las tablas de TODAS las páginas en orden secuencial.
        Retorna lista de tuplas (num_pagina, tabla).
        """
        todas = []
        for page_idx, page in enumerate(self.pdf.pages):
            tablas = page.extract_tables()
            if tablas:
                for tabla in tablas:
                    if tabla and len(tabla) > 0:
                        todas.append((page_idx, tabla))
        return todas
    
    def _extraer_texto_completo(self) -> str:
        """Extrae todo el texto del PDF"""
        texto = ""
        for pagina in self.pdf.pages:
            texto += (pagina.extract_text() or "") + "\n"
        return texto
    
    # =========================================================================
    # CLASIFICACIÓN DE TABLAS
    # =========================================================================
    
    def _clasificar_tabla(self, tabla: list) -> str:
        """
        Clasifica una tabla según su contenido.
        Retorna uno de:
          'info_general', 'captura_total_header', 'detalle_lance',
          'lance_continuation', 'species_data_6col', 'species_standalone',
          'observaciones', 'unknown'
        """
        if not tabla or len(tabla) == 0:
            return 'unknown'
        
        primera_fila = tabla[0]
        primera_celda = str(primera_fila[0] or '').strip().upper() if primera_fila and primera_fila[0] else ''
        num_cols = len(primera_fila) if primera_fila else 0
        
        # INFORMACIÓN GENERAL (4 cols, primera celda = "INFORMACIÓN GENERAL")
        if 'INFORMACI' in primera_celda and 'GENERAL' in primera_celda:
            return 'info_general'
        
        # CAPTURA TOTAL (6 cols, primera celda = "CAPTURA TOTAL")
        if 'CAPTURA TOTAL' in primera_celda:
            return 'captura_total_header'
        
        # DETALLE DE LANCE (primera celda contiene "DETALLE" y "LANCE")
        if 'DETALLE' in primera_celda and 'LANCE' in primera_celda:
            return 'detalle_lance'
        
        # Lance continuation: tabla 8-9 cols que empieza con INICIO, Latitud, Longitud, o LANCE #
        if num_cols >= 8:
            if primera_celda in ('INICIO',):
                return 'lance_continuation'
            if 'LATITUD' in primera_celda:
                return 'lance_continuation'
            if 'LONGITUD' in primera_celda:
                return 'lance_continuation'
            if 'LANCE' in primera_celda and '#' in primera_celda:
                return 'lance_continuation'
        
        # Tabla de solo observaciones
        if primera_celda == 'OBSERVACIONES' and len(tabla) <= 3:
            return 'observaciones'
        
        # Tabla 5-6 cols con primera fila que tiene ESPECIE → standalone species header
        if 'ESPECIE' in primera_celda and num_cols <= 6:
            return 'species_standalone'
        
        # Tabla 6 cols con datos numéricos en col 0 → continuation species data
        if num_cols == 6:
            tiene_datos_especie = False
            for fila in tabla:
                if fila and fila[0] and str(fila[0]).strip().isdigit():
                    tiene_datos_especie = True
                    break
            if tiene_datos_especie:
                return 'species_data_6col'
        
        return 'unknown'
    
    # =========================================================================
    # PROCESAMIENTO SECUENCIAL DE TABLAS
    # =========================================================================
    
    def _procesar_tablas_secuencial(self, todas_tablas: List[Tuple[int, list]]) -> Tuple[List[Dict], List[Dict]]:
        """
        Procesa todas las tablas secuencialmente.
        Mantiene estado para manejar lances que cruzan páginas.
        
        Returns:
            (especies_captura_total, lances_individuales)
        """
        especies_captura_total = []
        lances = []
        lance_actual = None
        captura_total_encontrada = False
        lances_iniciados = False
        
        for page_idx, tabla in todas_tablas:
            tipo = self._clasificar_tabla(tabla)
            
            # ---- INFORMACIÓN GENERAL (ya procesada en cabecera, saltar) ----
            if tipo == 'info_general':
                continue
            
            # ---- CAPTURA TOTAL ----
            if tipo == 'captura_total_header':
                captura_total_encontrada = True
                especies_captura_total.extend(
                    self._procesar_tabla_captura_total(tabla)
                )
                continue
            
            # ---- Continuación de CAPTURA TOTAL (6 cols con datos, antes de cualquier lance) ----
            if tipo == 'species_data_6col' and captura_total_encontrada and not lances_iniciados:
                especies_captura_total.extend(
                    self._procesar_tabla_especies_6col(tabla)
                )
                continue
            
            # ---- DETALLE DE LANCE (inicio de un nuevo lance) ----
            if tipo == 'detalle_lance':
                # Guardar lance anterior si existe
                if lance_actual:
                    lances.append(lance_actual)
                
                lances_iniciados = True
                lance_actual = self._iniciar_lance_desde_detalle(tabla)
                continue
            
            # ---- Lance continuation (9 cols, inicio con datos de coords/fechas) ----
            if tipo == 'lance_continuation':
                lances_iniciados = True
                
                # Verificar si es realmente un NUEVO lance (LANCE # con número diferente)
                nuevo_num = self._detectar_numero_lance_en_tabla(tabla)
                if nuevo_num and lance_actual and nuevo_num != lance_actual.get('numero_lance', 0):
                    # Es un nuevo lance sin header "DETALLE DE LANCE"
                    lances.append(lance_actual)
                    lance_actual = self._iniciar_lance_desde_detalle(tabla)
                elif lance_actual:
                    self._completar_lance_desde_continuacion(lance_actual, tabla)
                else:
                    # No hay lance actual, iniciar uno nuevo
                    lance_actual = self._iniciar_lance_desde_detalle(tabla)
                continue
            
            # ---- Species standalone (5-6 cols con header ESPECIE) ----
            if tipo == 'species_standalone':
                if lance_actual:
                    nuevas_especies, obs = self._procesar_tabla_especies_standalone(tabla)
                    lance_actual.setdefault('especies', []).extend(nuevas_especies)
                    if obs:
                        lance_actual['observaciones'] = obs
                continue
            
            # ---- Species data 6 cols (continuación de especies del lance actual) ----
            if tipo == 'species_data_6col' and lances_iniciados:
                if lance_actual:
                    nuevas_especies = self._procesar_tabla_especies_6col(tabla)
                    lance_actual.setdefault('especies', []).extend(nuevas_especies)
                    # También verificar si hay observaciones en esta tabla
                    obs = self._extraer_observaciones_de_continuation(tabla)
                    if obs:
                        lance_actual['observaciones'] = obs
                continue
            
            # ---- Observaciones sueltas ----
            if tipo == 'observaciones':
                if lance_actual:
                    obs = self._extraer_observaciones_tabla(tabla)
                    if obs:
                        lance_actual['observaciones'] = obs
                continue
        
        # Guardar último lance
        if lance_actual:
            lances.append(lance_actual)
        
        return especies_captura_total, lances
    
    # =========================================================================
    # CAPTURA TOTAL
    # =========================================================================
    
    def _procesar_tabla_captura_total(self, tabla: list) -> List[Dict]:
        """
        Procesa la tabla CAPTURA TOTAL (6 columnas).
        Estructura:
          Fila 0: ['CAPTURA TOTAL', None, None, None, None, None]
          Fila 1: ['ESPECIE', None, 'TIPO DE CAPTURA', None, None, None]
          Fila 2: [None, None, 'Retenida (TON)', 'Descartada (TON)', 'Descartada (N°)', 'Incidental (N°)']
          Fila 3+: datos
        """
        especies = []
        
        # Encontrar fila de inicio de datos (después de headers)
        inicio_datos = 0
        for i, fila in enumerate(tabla):
            if not fila:
                continue
            fila_str = ' '.join([str(c) for c in fila if c])
            if 'Retenida' in fila_str and 'TON' in fila_str:
                inicio_datos = i + 1
                break
        
        for fila in tabla[inicio_datos:]:
            especies.extend(self._parsear_fila_especie_6col(fila))
        
        return especies
    
    def _procesar_tabla_especies_6col(self, tabla: list) -> List[Dict]:
        """
        Procesa tabla de continuación con 6 columnas (sin headers).
        Estructura: [numero, nombre, retenida, descartada_ton, descartada_n, incidental_n]
        También puede tener filas de OBSERVACIONES al final.
        """
        especies = []
        for fila in tabla:
            if not fila:
                continue
            primera_celda = str(fila[0] or '').strip().upper()
            if primera_celda == 'OBSERVACIONES':
                break
            especies.extend(self._parsear_fila_especie_6col(fila))
        return especies
    
    def _procesar_tabla_especies_standalone(self, tabla: list) -> Tuple[List[Dict], Optional[str]]:
        """
        Procesa tabla standalone de especies (5-6 cols con header ESPECIE).
        Similar a CAPTURA TOTAL pero sin el título.
        Returns:
            (lista_especies, observaciones_o_None)
        """
        especies = []
        observaciones = None
        inicio_datos = 0
        
        for i, fila in enumerate(tabla):
            if not fila:
                continue
            fila_str = ' '.join([str(c) for c in fila if c])
            if 'Retenida' in fila_str and 'TON' in fila_str:
                inicio_datos = i + 1
                break
        
        encontro_obs = False
        for fila in tabla[inicio_datos:]:
            if not fila:
                continue
            primera_celda = str(fila[0] or '').strip().upper()
            if primera_celda == 'OBSERVACIONES':
                encontro_obs = True
                continue
            if encontro_obs:
                texto = str(fila[0] or '').strip()
                if texto and texto.upper() not in ('', 'NONE'):
                    observaciones = texto
                continue
            if 'LANCE DECLARADO SIN CAPTURAS' in primera_celda:
                continue
            especies.extend(self._parsear_fila_especie_6col(fila))
        
        return especies, observaciones
    
    def _parsear_fila_especie_6col(self, fila: list) -> List[Dict]:
        """
        Parsea una fila de especie en formato 6 columnas:
        [numero, nombre, retenida_ton, descartada_ton, descartada_n, incidental_n]
        
        Puede generar múltiples registros si tiene datos en varias columnas.
        """
        resultados = []
        
        if not fila or len(fila) < 3:
            return resultados
        
        numero = str(fila[0] or '').strip()
        nombre = str(fila[1] or '').strip()
        
        if not numero or not nombre:
            return resultados
        
        if not numero.isdigit():
            return resultados
        
        nombre_upper = nombre.upper()
        if any(kw in nombre_upper for kw in ('ESPECIE', 'CAPTURA', 'TIPO', 'LANCE', 'OBSERVACIONES')):
            return resultados
        
        # Limpiar nombre: reemplazar "; " y ";" con " / "
        nombre_limpio = re.sub(r'\s*;\s*', ' / ', nombre) if ';' in nombre else nombre
        nombre_original = nombre  # Para buscar en config
        
        tipo_especie = obtener_tipo_especie(nombre_original)
        
        # Columna 2: Retenida (TON)
        retenida_str = str(fila[2] or '').strip() if len(fila) > 2 else ''
        if retenida_str:
            try:
                retenida_ton = float(retenida_str)
                if retenida_ton >= 0.001:
                    resultados.append({
                        'nombre': nombre_limpio,
                        'cantidad_ton': retenida_ton,
                        'cantidad_unidades': 0,
                        'tipo_captura': 'retenida',
                        'tipo_especie': tipo_especie
                    })
            except (ValueError, TypeError):
                pass
        
        # Columna 3: Descartada (TON)
        descartada_str = str(fila[3] or '').strip() if len(fila) > 3 else ''
        if descartada_str:
            try:
                descartada_ton = float(descartada_str)
                if descartada_ton >= 0.001:
                    resultados.append({
                        'nombre': nombre_limpio,
                        'cantidad_ton': descartada_ton,
                        'cantidad_unidades': 0,
                        'tipo_captura': 'descartada',
                        'tipo_especie': tipo_especie
                    })
            except (ValueError, TypeError):
                pass
        
        # Columna 4: Descartada (N° unidades)
        desc_unidades_str = str(fila[4] or '').strip() if len(fila) > 4 else ''
        if desc_unidades_str:
            try:
                desc_unidades = int(float(desc_unidades_str))
                if desc_unidades > 0:
                    resultados.append({
                        'nombre': nombre_limpio,
                        'cantidad_ton': 0,
                        'cantidad_unidades': desc_unidades,
                        'tipo_captura': 'descartada',
                        'tipo_especie': tipo_especie
                    })
            except (ValueError, TypeError):
                pass
        
        # Columna 5: Incidental (N° unidades)
        incidental_str = str(fila[5] or '').strip() if len(fila) > 5 else ''
        if incidental_str:
            try:
                incidental = int(float(incidental_str))
                if incidental > 0:
                    resultados.append({
                        'nombre': nombre_limpio,
                        'cantidad_ton': 0,
                        'cantidad_unidades': incidental,
                        'tipo_captura': 'incidental',
                        'tipo_especie': tipo_especie
                    })
            except (ValueError, TypeError):
                pass
        
        return resultados
    
    # =========================================================================
    # LANCES - DETALLE DE LANCE
    # =========================================================================
    
    def _iniciar_lance_desde_detalle(self, tabla: list) -> Dict:
        """
        Inicia un lance desde una tabla DETALLE DE LANCE.
        Puede ser completa (9 cols) o parcial (4-5 cols) cuando se divide entre páginas.
        """
        lance = {
            'numero_lance': 0,
            'arte_pesca': 'ARRASTRE FONDO',
            'fecha_inicio': None,
            'fecha_fin': None,
            'observaciones': None,
            'especies': []
        }
        
        num_cols = len(tabla[0]) if tabla and tabla[0] else 0
        
        if num_cols >= 8:
            self._parsear_lance_multicol(lance, tabla)
        elif num_cols >= 4:
            self._parsear_lance_4col(lance, tabla)
        
        return lance
    
    def _parsear_lance_multicol(self, lance: Dict, tabla: list):
        """
        Parsea tabla DETALLE DE LANCE con 8-9 columnas.
        """
        for fila in tabla:
            if not fila:
                continue
            
            primera_celda = str(fila[0] or '').strip().upper()
            
            if 'LANCE' in primera_celda and '#' in primera_celda:
                lance['numero_lance'] = self._extraer_numero_lance(fila)
                lance['arte_pesca'] = self._extraer_arte_pesca(fila)
            
            elif primera_celda == 'INICIO':
                self._extraer_fechas_lance(lance, fila)
            
            elif 'LATITUD' in primera_celda:
                self._extraer_latitudes(lance, fila)
            
            elif 'LONGITUD' in primera_celda:
                self._extraer_longitudes(lance, fila)
        
        # Extraer especies de esta tabla
        especies = self._extraer_especies_de_tabla_9col(tabla)
        lance['especies'].extend(especies)
        
        # Extraer observaciones
        obs = self._extraer_observaciones_de_tabla(tabla)
        if obs:
            lance['observaciones'] = obs
    
    def _parsear_lance_4col(self, lance: Dict, tabla: list):
        """
        Parsea tabla DETALLE DE LANCE reducida (4-5 columnas).
        """
        for fila in tabla:
            if not fila:
                continue
            
            primera_celda = str(fila[0] or '').strip().upper()
            num_cols = len(fila)
            
            if 'LANCE' in primera_celda and '#' in primera_celda:
                for celda in fila[1:]:
                    val = str(celda or '').strip()
                    if val.isdigit():
                        lance['numero_lance'] = int(val)
                        break
                for i, celda in enumerate(fila):
                    celda_upper = str(celda or '').upper()
                    if 'ARTE' in celda_upper and 'PESCA' in celda_upper:
                        if i + 1 < num_cols and fila[i + 1]:
                            lance['arte_pesca'] = str(fila[i + 1]).strip()
                        break
            
            elif primera_celda == 'INICIO':
                if num_cols >= 2 and fila[1]:
                    lance['fecha_inicio'] = self._parsear_fecha(str(fila[1]).strip())
                # Buscar FIN
                for i in range(2, num_cols):
                    if str(fila[i] or '').strip().upper() == 'FIN':
                        if i + 1 < num_cols and fila[i + 1]:
                            lance['fecha_fin'] = self._parsear_fecha(str(fila[i + 1]).strip())
                        break
            
            elif 'LATITUD' in primera_celda:
                if num_cols >= 2 and fila[1]:
                    coords = self._parsear_coordenada_gms(str(fila[1]))
                    if coords:
                        lance['latitud_inicio'] = coords[0]
                # Buscar segunda latitud
                for i in range(2, num_cols):
                    celda_val = str(fila[i] or '').strip().upper()
                    if 'LATITUD' in celda_val:
                        if i + 1 < num_cols and fila[i + 1]:
                            coords = self._parsear_coordenada_gms(str(fila[i + 1]))
                            if coords:
                                lance['latitud_fin'] = coords[0]
                        break
            
            elif 'LONGITUD' in primera_celda:
                if num_cols >= 2 and fila[1]:
                    coords = self._parsear_coordenada_gms(str(fila[1]))
                    if coords:
                        lance['longitud_inicio'] = coords[0]
                for i in range(2, num_cols):
                    celda_val = str(fila[i] or '').strip().upper()
                    if 'LONGITUD' in celda_val:
                        if i + 1 < num_cols and fila[i + 1]:
                            coords = self._parsear_coordenada_gms(str(fila[i + 1]))
                            if coords:
                                lance['longitud_fin'] = coords[0]
                        break
    
    def _completar_lance_desde_continuacion(self, lance: Dict, tabla: list):
        """
        Completa un lance con datos de una tabla de continuación (8-9 cols).
        """
        for fila in tabla:
            if not fila:
                continue
            primera_celda = str(fila[0] or '').strip().upper()
            
            if 'LANCE' in primera_celda and '#' in primera_celda:
                lance['numero_lance'] = self._extraer_numero_lance(fila)
                lance['arte_pesca'] = self._extraer_arte_pesca(fila)
            
            elif primera_celda == 'INICIO':
                self._extraer_fechas_lance(lance, fila)
            
            elif 'LATITUD' in primera_celda:
                self._extraer_latitudes(lance, fila)
            
            elif 'LONGITUD' in primera_celda:
                self._extraer_longitudes(lance, fila)
        
        especies = self._extraer_especies_de_tabla_9col(tabla)
        lance['especies'].extend(especies)
        
        obs = self._extraer_observaciones_de_tabla(tabla)
        if obs:
            lance['observaciones'] = obs
    
    # =========================================================================
    # HELPERS: EXTRAER DATOS DE FILAS
    # =========================================================================
    
    def _extraer_numero_lance(self, fila: list) -> int:
        """Extrae el número de lance de una fila LANCE #"""
        for celda in fila[1:]:
            val = str(celda or '').strip()
            if val.isdigit():
                return int(val)
        return 0
    
    def _detectar_numero_lance_en_tabla(self, tabla: list) -> Optional[int]:
        """Detecta si una tabla contiene un LANCE # y retorna su número"""
        for fila in tabla[:3]:  # Solo buscar en las primeras 3 filas
            if not fila:
                continue
            primera_celda = str(fila[0] or '').strip().upper()
            if 'LANCE' in primera_celda and '#' in primera_celda:
                for celda in fila[1:]:
                    val = str(celda or '').strip()
                    if val.isdigit():
                        return int(val)
        return None
    
    def _extraer_arte_pesca(self, fila: list) -> str:
        """Extrae el arte de pesca de una fila LANCE #"""
        for i, celda in enumerate(fila):
            celda_str = str(celda or '').upper()
            if 'ARTE' in celda_str and 'PESCA' in celda_str:
                for j in range(i + 1, len(fila)):
                    val = str(fila[j] or '').strip()
                    if val and not val.isdigit() and val.upper() != 'NONE':
                        return val
        return 'ARRASTRE FONDO'
    
    def _extraer_fechas_lance(self, lance: Dict, fila: list):
        """Extrae fechas de INICIO y FIN de una fila"""
        num_cols = len(fila)
        
        for i in range(1, min(4, num_cols)):
            val = str(fila[i] or '').strip()
            if re.match(r'\d{2}-\d{2}-\d{4}', val):
                lance['fecha_inicio'] = self._parsear_fecha(val)
                break
        
        for i in range(1, num_cols):
            celda_str = str(fila[i] or '').strip().upper()
            if celda_str == 'FIN':
                for j in range(i + 1, min(i + 3, num_cols)):
                    val = str(fila[j] or '').strip()
                    if re.match(r'\d{2}-\d{2}-\d{4}', val):
                        lance['fecha_fin'] = self._parsear_fecha(val)
                        break
                break
    
    def _extraer_latitudes(self, lance: Dict, fila: list):
        """Extrae latitudes inicio y fin de una fila"""
        coords_encontradas = []
        for celda in fila:
            val = str(celda or '').strip()
            if val and 'º' in val and ("'" in val or "'" in val or "'" in val):
                coord = self._parsear_coordenada_gms(val)
                if coord:
                    coords_encontradas.append(coord[0])
        
        if len(coords_encontradas) >= 1 and 'latitud_inicio' not in lance:
            lance['latitud_inicio'] = coords_encontradas[0]
        if len(coords_encontradas) >= 2:
            lance['latitud_fin'] = coords_encontradas[1]
    
    def _extraer_longitudes(self, lance: Dict, fila: list):
        """Extrae longitudes inicio y fin de una fila"""
        coords_encontradas = []
        for celda in fila:
            val = str(celda or '').strip()
            if val and 'º' in val and ("'" in val or "'" in val or "'" in val):
                coord = self._parsear_coordenada_gms(val)
                if coord:
                    coords_encontradas.append(coord[0])
        
        if len(coords_encontradas) >= 1 and 'longitud_inicio' not in lance:
            lance['longitud_inicio'] = coords_encontradas[0]
        if len(coords_encontradas) >= 2:
            lance['longitud_fin'] = coords_encontradas[1]
    
    def _extraer_especies_de_tabla_9col(self, tabla: list) -> List[Dict]:
        """
        Extrae especies de una tabla DETALLE DE LANCE (8-9 cols).
        Detecta dinámicamente las columnas de captura.
        """
        especies = []
        
        retenida_col = None
        descartada_col = None
        descartada_n_col = None
        incidental_n_col = None
        inicio_datos = None
        
        for i, fila in enumerate(tabla):
            if not fila:
                continue
            fila_str = ' '.join([str(c) for c in fila if c])
            
            if 'Retenida' in fila_str and 'TON' in fila_str:
                for col_idx, celda in enumerate(fila):
                    celda_str = str(celda or '').strip()
                    if 'Retenida' in celda_str and 'TON' in celda_str:
                        retenida_col = col_idx
                    elif 'Descartada' in celda_str and 'TON' in celda_str:
                        descartada_col = col_idx
                    elif 'Descartada' in celda_str and 'N°' in celda_str:
                        descartada_n_col = col_idx
                    elif 'Incidental' in celda_str:
                        incidental_n_col = col_idx
                
                inicio_datos = i + 1
                break
        
        if inicio_datos is None or retenida_col is None:
            return especies
        
        nombre_col = 1
        
        for fila in tabla[inicio_datos:]:
            if not fila or len(fila) <= nombre_col:
                continue
            
            primera_celda = str(fila[0] or '').strip().upper()
            
            if primera_celda == 'OBSERVACIONES':
                break
            
            if 'LANCE DECLARADO SIN CAPTURAS' in primera_celda:
                continue
            
            numero = str(fila[0] or '').strip()
            nombre = str(fila[nombre_col] or '').strip()
            
            if not numero or not numero.isdigit() or not nombre:
                continue
            
            nombre_upper = nombre.upper()
            if any(kw in nombre_upper for kw in ('ESPECIE', 'CAPTURA', 'TIPO')):
                continue
            
            nombre_original = nombre
            nombre_limpio = re.sub(r'\s*;\s*', ' / ', nombre) if ';' in nombre else nombre
            tipo_especie = obtener_tipo_especie(nombre_original)
            
            # Retenida (TON)
            if retenida_col is not None and len(fila) > retenida_col:
                val = str(fila[retenida_col] or '').strip()
                if val:
                    try:
                        ton = float(val)
                        if ton >= 0.001:
                            especies.append({
                                'nombre': nombre_limpio,
                                'cantidad_ton': ton,
                                'cantidad_unidades': 0,
                                'tipo_captura': 'retenida',
                                'tipo_especie': tipo_especie
                            })
                    except (ValueError, TypeError):
                        pass
            
            # Descartada (TON)
            if descartada_col is not None and len(fila) > descartada_col:
                val = str(fila[descartada_col] or '').strip()
                if val:
                    try:
                        ton = float(val)
                        if ton >= 0.001:
                            especies.append({
                                'nombre': nombre_limpio,
                                'cantidad_ton': ton,
                                'cantidad_unidades': 0,
                                'tipo_captura': 'descartada',
                                'tipo_especie': tipo_especie
                            })
                    except (ValueError, TypeError):
                        pass
            
            # Descartada (N° unidades)
            if descartada_n_col is not None and len(fila) > descartada_n_col:
                val = str(fila[descartada_n_col] or '').strip()
                if val:
                    try:
                        unidades = int(float(val))
                        if unidades > 0:
                            especies.append({
                                'nombre': nombre_limpio,
                                'cantidad_ton': 0,
                                'cantidad_unidades': unidades,
                                'tipo_captura': 'descartada',
                                'tipo_especie': tipo_especie
                            })
                    except (ValueError, TypeError):
                        pass
            
            # Incidental (N° unidades)
            if incidental_n_col is not None and len(fila) > incidental_n_col:
                val = str(fila[incidental_n_col] or '').strip()
                if val:
                    try:
                        unidades = int(float(val))
                        if unidades > 0:
                            especies.append({
                                'nombre': nombre_limpio,
                                'cantidad_ton': 0,
                                'cantidad_unidades': unidades,
                                'tipo_captura': 'incidental',
                                'tipo_especie': tipo_especie
                            })
                    except (ValueError, TypeError):
                        pass
        
        return especies
    
    def _extraer_observaciones_de_tabla(self, tabla: list) -> Optional[str]:
        """Extrae observaciones de una tabla DETALLE DE LANCE o continuación"""
        encontro_obs = False
        observaciones_partes = []
        
        for fila in tabla:
            if not fila:
                continue
            primera_celda = str(fila[0] or '').strip().upper()
            
            if primera_celda == 'OBSERVACIONES':
                encontro_obs = True
                continue
            
            if encontro_obs:
                texto = str(fila[0] or '').strip()
                if texto and texto.upper() not in ('', 'NONE', 'DETALLE DE LANCE'):
                    observaciones_partes.append(texto)
        
        if observaciones_partes:
            return ' '.join(observaciones_partes)
        return None
    
    def _extraer_observaciones_de_continuation(self, tabla: list) -> Optional[str]:
        """Extrae observaciones de una tabla de continuación 6 cols"""
        encontro_obs = False
        partes = []
        
        for fila in tabla:
            if not fila:
                continue
            primera_celda = str(fila[0] or '').strip().upper()
            
            if primera_celda == 'OBSERVACIONES':
                encontro_obs = True
                continue
            
            if encontro_obs:
                texto = str(fila[0] or '').strip()
                if texto and texto.upper() not in ('', 'NONE'):
                    partes.append(texto)
        
        return ' '.join(partes) if partes else None
    
    def _extraer_observaciones_tabla(self, tabla: list) -> Optional[str]:
        """Extrae observaciones de una tabla de solo observaciones (2-3 filas)"""
        partes = []
        skip_first = True
        for fila in tabla:
            if not fila:
                continue
            if skip_first:
                skip_first = False
                continue
            texto = str(fila[0] or '').strip()
            if texto and texto.upper() not in ('', 'NONE'):
                partes.append(texto)
        
        return ' '.join(partes) if partes else None
    
    # =========================================================================
    # COORDENADAS
    # =========================================================================
    
    def _parsear_coordenada_gms(self, texto: str) -> Optional[Tuple[float]]:
        """
        Parsea coordenada: "33º 51.21588' S" o "72º 2.6990999999998' W"
        Acepta º, °, ' y variantes.
        Returns: Tupla (valor_decimal,) o None
        """
        try:
            match = re.search(r'(\d+)[°º]\s*([\d.]+)[\'\'´`]\s*([NSEW])', texto, re.IGNORECASE)
            if match:
                grados = float(match.group(1))
                minutos = float(match.group(2))
                direccion = match.group(3).upper()
                
                decimal = grados + (minutos / 60.0)
                if direccion in ('S', 'W'):
                    decimal = -decimal
                
                return (round(decimal, 6),)
        except Exception:
            pass
        return None
    
    # =========================================================================
    # CABECERA
    # =========================================================================
    
    def _extraer_cabecera(self, texto: str, todas_tablas: List[Tuple[int, list]]) -> Dict:
        """
        Extrae información de la cabecera del viaje.
        Usa las tablas (más confiable) y texto como fallback.
        """
        cabecera = {}
        
        for page_idx, tabla in todas_tablas:
            if not tabla or len(tabla) == 0:
                continue
            primera_celda = str(tabla[0][0] or '').strip().upper()
            
            if 'INFORMACI' in primera_celda and 'GENERAL' in primera_celda:
                cabecera = self._parsear_tabla_info_general(tabla)
                break
        
        self._completar_cabecera_desde_texto(cabecera, texto)
        
        return cabecera
    
    def _parsear_tabla_info_general(self, tabla: list) -> Dict:
        """
        Parsea la tabla INFORMACION GENERAL (4 columnas).
        """
        cabecera = {}
        
        for fila in tabla:
            if not fila or len(fila) < 2:
                continue
            
            clave = str(fila[0] or '').strip().upper()
            valor = str(fila[1] or '').strip() if fila[1] else ''
            
            if clave == 'ARMADOR':
                cabecera['armador'] = valor
            elif clave in ('EMBARCACIÓN', 'EMBARCACION'):
                cabecera['nave_nombre'] = valor
                if len(fila) >= 4 and fila[3]:
                    cabecera['pais_abanderamiento'] = str(fila[3]).strip()
            elif clave in ('MATRÍCULA', 'MATRICULA'):
                cabecera['nave_matricula'] = valor
                if len(fila) >= 4 and fila[3]:
                    cabecera['señal_llamada'] = str(fila[3]).strip()
            elif clave in ('CAPITÁN', 'CAPITAN'):
                cabecera['capitan'] = valor
            elif clave == 'TIPO REGISTRO':
                cabecera['tipo_registro'] = valor
                if len(fila) >= 4 and fila[3]:
                    cabecera['n_registro'] = str(fila[3]).strip()
            elif clave == 'ZARPE':
                cabecera['fecha_zarpe'] = self._parsear_fecha(valor)
                # Puerto puede estar en col 2 o col 3
                if len(fila) >= 4 and fila[3]:
                    cabecera['puerto_zarpe'] = str(fila[3]).strip()
                elif len(fila) >= 3 and fila[2] and str(fila[2]).strip().upper() == 'ZARPE':
                    # La col 2 dice "ZARPE" (label), el puerto real está en col 3
                    pass
            elif clave == 'RECALADA':
                cabecera['fecha_recalada'] = self._parsear_fecha(valor)
                if len(fila) >= 4 and fila[3]:
                    cabecera['puerto_recalada'] = str(fila[3]).strip()
        
        return cabecera
    
    def _completar_cabecera_desde_texto(self, cabecera: Dict, texto: str):
        """Completa datos faltantes usando regex sobre el texto"""
        
        # Folio / N° Bitácora
        if 'id_viaje' not in cabecera:
            folio = self._buscar_patron(texto, r'(SERNAPESCA-BE\d{4}-\d+-\d+)', None)
            if not folio:
                num_bitacora = self._buscar_patron(texto, r'N°\s+BIT[ÁA]CORA\s+(\d+)', None)
                if num_bitacora:
                    folio = f'SERNAPESCA-BE-{num_bitacora}'
            
            if not folio:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                folio = f'SERNAPESCA-BE-TEMP-{timestamp}'
            
            cabecera['id_viaje'] = folio
            cabecera['folio_interno'] = folio
        
        # Total de lances declarados
        if 'total_lances_declarados' not in cabecera:
            total = self._buscar_patron(texto, r'TOTAL\s+DE\s+LANCES\s+(\d+)', '0')
            cabecera['total_lances_declarados'] = int(total)
        
        # Aviso de recalada
        if 'aviso_recalada' not in cabecera:
            cabecera['aviso_recalada'] = self._buscar_patron(
                texto, r'AVISO\s+(?:DE\s+)?RECALADA\s+(\d+)', None
            )
        
        # RPA
        if 'rpa' not in cabecera:
            cabecera['rpa'] = self._buscar_patron(texto, r'RPA\s+([^\n]+)', None)
        
        # Valores por defecto
        cabecera.setdefault('armador', 'DESCONOCIDO')
        cabecera.setdefault('nave_nombre', 'DESCONOCIDA')
        cabecera.setdefault('capitan', 'DESCONOCIDO')
        cabecera.setdefault('puerto_zarpe', 'QUINTERO')
        cabecera.setdefault('puerto_recalada', 'QUINTERO')
        cabecera.setdefault('pais_abanderamiento', 'CL')
    
    # =========================================================================
    # VALIDACIÓN
    # =========================================================================
    
    def _validar_datos(self, viaje: Dict, lances: List[Dict]) -> Dict:
        """Valida y calcula métricas del viaje"""
        totales_especies = {}
        total_camaron = 0
        total_merluza = 0
        todas_capturas = []
        
        lance_captura_total = None
        lances_individuales = []
        
        for lance in lances:
            if lance.get('numero_lance') == 0:
                lance_captura_total = lance
            else:
                lances_individuales.append(lance)
        
        lances_para_calcular = [lance_captura_total] if lance_captura_total else lances_individuales
        
        for lance in lances_para_calcular:
            for especie in lance.get('especies', []):
                nombre = especie.get('nombre', '')
                cantidad = especie.get('cantidad_ton', 0)
                tipo_captura = especie.get('tipo_captura', 'retenida')
                
                if nombre not in totales_especies:
                    totales_especies[nombre] = {'retenida': 0, 'descartada': 0}
                
                if tipo_captura == 'retenida':
                    totales_especies[nombre]['retenida'] += cantidad
                elif tipo_captura in ('descartada', 'incidental'):
                    totales_especies[nombre]['descartada'] += cantidad
                
                if tipo_captura == 'retenida' and cantidad > 0:
                    todas_capturas.append({
                        'especie': nombre.replace(' / ', '; '),
                        'retenida_ton': cantidad
                    })
                
                nombre_lower = nombre.lower()
                if ('camarón' in nombre_lower or 'camaron' in nombre_lower) and tipo_captura == 'retenida':
                    total_camaron += cantidad
                if 'merluza' in nombre_lower and tipo_captura == 'retenida':
                    total_merluza += cantidad
        
        ratio_merluza = calcular_ratio_merluza(todas_capturas)
        alerta = calcular_alerta_ecosistema(ratio_merluza)
        
        validacion = {
            'total_lances_procesados': len(lances_individuales),
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
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    
    def _buscar_patron(self, texto: str, patron: str, default: Optional[str]) -> Optional[str]:
        """Busca un patrón regex y retorna el primer grupo"""
        match = re.search(patron, texto, re.IGNORECASE)
        return match.group(1) if match else default
    
    def _parsear_fecha(self, fecha_str: Optional[str]) -> Optional[str]:
        """Parsea fecha en varios formatos. Retorna ISO format."""
        if not fecha_str:
            return None
        
        fecha_str = fecha_str.strip()
        
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
    
    print(f"Procesando: {pdf_path}")
    
    with BitacoraParser(pdf_path) as parser:
        resultado = parser.parsear_completo()
    
    print("\nViaje:")
    for key, value in resultado['viaje'].items():
        print(f"  {key}: {value}")
    
    print(f"\nLances procesados: {len(resultado['lances'])}")
    for lance in resultado['lances']:
        num = lance.get('numero_lance', '?')
        n_especies = len(lance.get('especies', []))
        arte = lance.get('arte_pesca', '?')
        lat = lance.get('latitud_inicio', 'N/A')
        lon = lance.get('longitud_inicio', 'N/A')
        obs = lance.get('observaciones', '')
        print(f"  Lance #{num}: {n_especies} especies, {arte}, lat={lat}, lon={lon}")
        if obs:
            print(f"    Obs: {obs[:80]}...")
    
    print("\nValidacion:")
    for key, value in resultado['validacion'].items():
        if key != 'especies_totales':
            print(f"  {key}: {value}")
