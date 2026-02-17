"""
Módulo de extracción de datos desde PDF de Bitácora Electrónica
Parsea el PDF generado por Sernapesca y extrae:
- Cabecera del viaje
- Detalle de lances (con coordenadas y capturas)
- Validaciones
"""

import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from coordinate_converter import convert_position
from especies_config import (
    obtener_tipo_especie, 
    calcular_ratio_merluza, 
    calcular_alerta_ecosistema
)


class BitacoraParser:
    """Parser para PDFs de Bitácora Electrónica de Sernapesca"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf = None
        self.viaje_data = {}
        self.lances_data = []
        
    def __enter__(self):
        self.pdf = pdfplumber.open(self.pdf_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pdf:
            self.pdf.close()
    
    def extraer_cabecera(self, primera_pagina) -> Dict:
        """
        Extrae información de la cabecera del viaje desde la primera página.
        
        Returns:
            Diccionario con datos del viaje
        """
        texto = primera_pagina.extract_text()
        
        # Extraer datos usando regex
        cabecera = {}
        
        # Folio/ID
        folio_match = re.search(r'N° BITACORA[:\s]+(\d+)', texto)
        if folio_match:
            cabecera['folio_interno'] = folio_match.group(1)
            cabecera['id_viaje'] = f"SERNAPESCA-BE2021-{folio_match.group(1)}-1"
        
        # Nombre de nave
        nave_match = re.search(r'NOMBRE NAVE[:\s]+([A-ZÁÉÍÓÚÑ\s]+)', texto)
        if nave_match:
            cabecera['nave_nombre'] = nave_match.group(1).strip()
        
        # Armador
        armador_match = re.search(r'ARMADOR[:\s]+([A-ZÁÉÍÓÚÑ.,\s]+?)(?=CAPITAN|$)', texto, re.DOTALL)
        if armador_match:
            cabecera['armador'] = armador_match.group(1).strip()
        
        # Capitán
        capitan_match = re.search(r'CAPITAN[:\s]+([A-ZÁÉÍÓÚÑ\s]+)', texto)
        if capitan_match:
            cabecera['capitan'] = capitan_match.group(1).strip()
        
        # Puerto de zarpe
        zarpe_match = re.search(r'PUERTO ZARPE[:\s]+([A-ZÁÉÍÓÚÑ\s]+)', texto)
        if zarpe_match:
            cabecera['puerto_zarpe'] = zarpe_match.group(1).strip()
        
        # Puerto de desembarque
        desembarque_match = re.search(r'PUERTO DESEMBARQUE[:\s]+([A-ZÁÉÍÓÚÑ\s]+)', texto)
        if desembarque_match:
            cabecera['puerto_desembarque'] = desembarque_match.group(1).strip()
        
        # Fechas (formato aproximado, ajustar según PDF real)
        fecha_zarpe_match = re.search(r'FECHA Y HORA ZARPE[:\s]+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', texto)
        if fecha_zarpe_match:
            cabecera['fecha_zarpe'] = self._parse_fecha(fecha_zarpe_match.group(1))
        
        fecha_recalada_match = re.search(r'FECHA Y HORA RECALADA[:\s]+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', texto)
        if fecha_recalada_match:
            cabecera['fecha_recalada'] = self._parse_fecha(fecha_recalada_match.group(1))
        
        cabecera['estado_procesamiento'] = "PROCESANDO"
        
        return cabecera
    
    def _parse_fecha(self, fecha_str: str) -> str:
        """
        Convierte fecha de formato DD/MM/YYYY HH:MM:SS a ISO 8601
        
        Args:
            fecha_str: Fecha en formato "02/01/2021 10:54:58"
            
        Returns:
            Fecha en formato ISO "2021-01-02T10:54:58"
        """
        try:
            dt = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")
            return dt.isoformat()
        except:
            return fecha_str
    
    def extraer_lances(self) -> List[Dict]:
        """
        Extrae todos los lances del PDF.
        La tabla de lances puede estar en múltiples páginas.
        
        Returns:
            Lista de diccionarios, cada uno representa un lance
        """
        lances = []
        
        for i, pagina in enumerate(self.pdf.pages):
            print(f"Procesando página {i+1}...")
            
            # Extraer tablas de la página
            tablas = pagina.extract_tables()
            
            for tabla in tablas:
                if not tabla:
                    continue
                
                # Identificar si es la tabla de lances
                # Buscar headers que contengan "LANCE", "ESPECIE", "CAPTURA", etc.
                headers = tabla[0] if tabla else []
                
                if self._es_tabla_lances(headers):
                    lances_pagina = self._parsear_tabla_lances(tabla)
                    lances.extend(lances_pagina)
        
        return lances
    
    def _es_tabla_lances(self, headers: List) -> bool:
        """
        Verifica si una tabla es la tabla de detalle de lances.
        
        Args:
            headers: Primera fila de la tabla
            
        Returns:
            True si es tabla de lances
        """
        if not headers:
            return False
        
        headers_str = ' '.join([str(h).upper() for h in headers if h])
        
        # Buscar palabras clave
        keywords = ['LANCE', 'ESPECIE', 'CAPTURA', 'POSICION', 'COORDENADA']
        return any(keyword in headers_str for keyword in keywords)
    
    def _parsear_tabla_lances(self, tabla: List[List]) -> List[Dict]:
        """
        Parsea la tabla de lances y extrae los datos.
        NOTA: Esta función debe adaptarse al formato exacto del PDF.
        
        Args:
            tabla: Tabla extraída por pdfplumber
            
        Returns:
            Lista de lances parseados
        """
        lances = []
        
        # Saltar header
        for fila in tabla[1:]:
            if not fila or len(fila) < 3:
                continue
            
            # Intentar extraer número de lance
            try:
                num_lance = int(fila[0]) if fila[0] and str(fila[0]).strip().isdigit() else None
                if num_lance is None:
                    continue
                
                lance = self._parsear_fila_lance(fila, num_lance)
                if lance:
                    lances.append(lance)
                    
            except (ValueError, IndexError) as e:
                print(f"Error parseando fila: {e}")
                continue
        
        return lances
    
    def _parsear_fila_lance(self, fila: List, num_lance: int) -> Optional[Dict]:
        """
        Parsea una fila individual de la tabla de lances.
        ESTRUCTURA ESPERADA (ajustar según PDF real):
        [N° Lance, Arte, Fecha/Hora Inicio, Fecha/Hora Fin, Lat Ini, Lon Ini, Lat Fin, Lon Fin, ...]
        
        Args:
            fila: Fila de la tabla
            num_lance: Número de lance
            
        Returns:
            Diccionario con datos del lance o None si no se puede parsear
        """
        try:
            lance = {
                "numero_lance": num_lance,
                "arte_pesca": str(fila[1]).strip() if len(fila) > 1 else "ARRASTRE FONDO",
            }
            
            # Fechas (índices aproximados, ajustar según PDF)
            if len(fila) > 2 and fila[2]:
                lance["inicio_lance"] = self._parse_fecha(str(fila[2]))
            if len(fila) > 3 and fila[3]:
                lance["fin_lance"] = self._parse_fecha(str(fila[3]))
            
            # Coordenadas
            if len(fila) > 6:
                # Posición inicial
                lat_ini = str(fila[4]) if fila[4] else ""
                lon_ini = str(fila[5]) if fila[5] else ""
                
                if lat_ini and lon_ini:
                    try:
                        lance["posicion_inicial"] = convert_position(lat_ini, lon_ini)
                    except Exception as e:
                        print(f"Error convirtiendo posición inicial lance {num_lance}: {e}")
                
                # Posición final
                lat_fin = str(fila[6]) if fila[6] else ""
                lon_fin = str(fila[7]) if len(fila) > 7 and fila[7] else ""
                
                if lat_fin and lon_fin:
                    try:
                        lance["posicion_final"] = convert_position(lat_fin, lon_fin)
                    except Exception as e:
                        print(f"Error convirtiendo posición final lance {num_lance}: {e}")
            
            # Observaciones (buscar en columnas finales)
            observaciones = ""
            for col in fila[-3:]:  # Últimas 3 columnas
                if col and isinstance(col, str) and len(col) > 5:
                    observaciones = col.strip()
                    break
            
            if observaciones:
                lance["observaciones"] = observaciones
            
            # Capturas (esto requiere parsing adicional o tabla separada)
            lance["capturas"] = []
            
            return lance
            
        except Exception as e:
            print(f"Error en _parsear_fila_lance: {e}")
            return None
    
    def extraer_capturas_por_lance(self, num_lance: int, pagina) -> List[Dict]:
        """
        Extrae las capturas de un lance específico.
        Las capturas pueden estar en una tabla aparte o anidada.
        
        Args:
            num_lance: Número del lance
            pagina: Página del PDF
            
        Returns:
            Lista de capturas
        """
        capturas = []
        texto = pagina.extract_text()
        
        # Buscar patrón de especies y toneladas
        # Ejemplo: "Camarón nailon    3.234   TON"
        patron_captura = r'([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)\s+([\d.]+)\s+(TON|N°)'
        
        matches = re.finditer(patron_captura, texto)
        
        for match in matches:
            especie = match.group(1).strip()
            cantidad = float(match.group(2))
            unidad = match.group(3)
            
            captura = {
                "especie": especie,
                "tipo_calculado": obtener_tipo_especie(especie)
            }
            
            if unidad == "TON":
                captura["retenida_ton"] = cantidad
                captura["descartada_ton"] = 0.0
            else:  # N° (unidades)
                captura["descartada_unidades"] = int(cantidad)
            
            capturas.append(captura)
        
        return capturas
    
    def calcular_indicadores_lance(self, lance: Dict) -> Dict:
        """
        Calcula indicadores MSC para un lance.
        
        Args:
            lance: Diccionario con datos del lance
            
        Returns:
            Lance con indicadores agregados
        """
        capturas = lance.get("capturas", [])
        
        # Ratio de merluza
        ratio = calcular_ratio_merluza(capturas)
        if ratio is not None:
            lance["ratio_merluza_vs_objetivo"] = ratio
            lance["alerta_ecosistema"] = calcular_alerta_ecosistema(ratio)
        else:
            lance["alerta_ecosistema"] = "VERDE"
        
        return lance
    
    def validar_suma_camarones(self, lances: List[Dict]) -> Tuple[float, bool]:
        """
        Suma todas las capturas de camarón nailon para validar contra el total del PDF.
        
        Args:
            lances: Lista de lances parseados
            
        Returns:
            Tupla (total_calculado, es_valido)
        """
        total_camaron = 0.0
        
        for lance in lances:
            for captura in lance.get("capturas", []):
                if captura.get("especie") == "Camarón nailon":
                    total_camaron += captura.get("retenida_ton", 0.0)
        
        # El PDF de ejemplo dice 17.703 TON
        TOTAL_ESPERADO = 17.703
        diferencia = abs(total_camaron - TOTAL_ESPERADO)
        
        # Tolerancia de 0.01 TON por redondeo
        es_valido = diferencia < 0.01
        
        return round(total_camaron, 3), es_valido
    
    def parsear_completo(self) -> Dict:
        """
        Ejecuta el parsing completo del PDF.
        
        Returns:
            Diccionario con toda la información estructurada
        """
        print(f"Iniciando parsing de: {self.pdf_path}")
        
        # 1. Extraer cabecera
        print("Extrayendo cabecera...")
        if len(self.pdf.pages) > 0:
            self.viaje_data = self.extraer_cabecera(self.pdf.pages[0])
        
        # 2. Extraer lances
        print("Extrayendo lances...")
        self.lances_data = self.extraer_lances()
        
        # 3. Para cada lance, calcular indicadores
        print("Calculando indicadores MSC...")
        for lance in self.lances_data:
            self.calcular_indicadores_lance(lance)
        
        # 4. Validación
        print("Validando totales...")
        total_camaron, es_valido = self.validar_suma_camarones(self.lances_data)
        
        print(f"\n{'='*50}")
        print(f"Total Camarón nailon: {total_camaron} TON")
        print(f"Validación: {'✓ CORRECTO' if es_valido else '✗ ERROR'}")
        print(f"{'='*50}\n")
        
        # 5. Actualizar estado
        self.viaje_data['total_lances_declarados'] = len(self.lances_data)
        self.viaje_data['estado_procesamiento'] = "COMPLETADO" if es_valido else "ERROR_VALIDACION"
        
        return {
            "viaje": self.viaje_data,
            "lances": self.lances_data,
            "validacion": {
                "total_camaron_ton": total_camaron,
                "es_valido": es_valido
            }
        }


def main():
    """Función de prueba"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python pdf_parser.py <ruta_al_pdf>")
        print("\nEjemplo:")
        print("  python pdf_parser.py ../data/pdfs/Rauten_3088.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    with BitacoraParser(pdf_path) as parser:
        resultado = parser.parsear_completo()
        
        print("\n=== RESUMEN DEL PARSING ===")
        print(f"Nave: {resultado['viaje'].get('nave_nombre', 'N/A')}")
        print(f"Folio: {resultado['viaje'].get('folio_interno', 'N/A')}")
        print(f"Lances extraídos: {len(resultado['lances'])}")
        print(f"Estado: {resultado['viaje'].get('estado_procesamiento', 'N/A')}")


if __name__ == "__main__":
    main()
