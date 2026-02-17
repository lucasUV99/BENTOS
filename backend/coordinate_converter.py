"""
Módulo de conversión de coordenadas
Convierte coordenadas de formato grados/minutos (usado en bitácoras)
a formato decimal (para mapas y Firebase)
"""

import re
from typing import Tuple, Optional


def parse_coordinate_string(coord_str: str) -> Tuple[float, str]:
    """
    Parsea una coordenada en formato: "33° 51.21588' S"
    
    Args:
        coord_str: String con coordenada en formato grados/minutos
        
    Returns:
        Tupla (valor_en_minutos, dirección)
        
    Example:
        >>> parse_coordinate_string("33° 51.21588' S")
        (33.853598, 'S')
    """
    # Patrón: captura grados, minutos y dirección (N/S/E/W)
    pattern = r"(\d+)°\s*(\d+\.?\d*)'?\s*([NSEW])"
    match = re.search(pattern, coord_str.upper())
    
    if not match:
        raise ValueError(f"Formato de coordenada inválido: {coord_str}")
    
    degrees = float(match.group(1))
    minutes = float(match.group(2))
    direction = match.group(3)
    
    return degrees, minutes, direction


def dms_to_decimal(degrees: float, minutes: float, direction: str) -> float:
    """
    Convierte grados y minutos a decimal.
    
    Args:
        degrees: Grados
        minutes: Minutos (con decimales)
        direction: 'N', 'S', 'E', 'W'
        
    Returns:
        Coordenada en decimal
        
    Example:
        >>> dms_to_decimal(33, 51.21588, 'S')
        -33.853598
    """
    decimal = degrees + (minutes / 60.0)
    
    # Sur y Oeste son negativos
    if direction in ['S', 'W']:
        decimal *= -1
    
    return round(decimal, 6)


def convert_coordinate(coord_str: str) -> float:
    """
    Función principal: convierte una coordenada completa de string a decimal.
    
    Args:
        coord_str: Coordenada en formato "33° 51.21588' S"
        
    Returns:
        Coordenada en decimal
        
    Example:
        >>> convert_coordinate("33° 51.21588' S")
        -33.853598
    """
    degrees, minutes, direction = parse_coordinate_string(coord_str)
    return dms_to_decimal(degrees, minutes, direction)


def convert_position(lat_str: str, lng_str: str) -> dict:
    """
    Convierte un par de coordenadas y devuelve un objeto con formato raw y convertido.
    
    Args:
        lat_str: Latitud en formato "33° 51.21588' S"
        lng_str: Longitud en formato "72° 8.14188' W"
        
    Returns:
        Diccionario con raw y conversión decimal
    """
    return {
        "raw_lat": lat_str,
        "raw_lng": lng_str,
        "lat": convert_coordinate(lat_str),
        "lng": convert_coordinate(lng_str)
    }


if __name__ == "__main__":
    # Pruebas con las coordenadas del PDF ejemplo
    print("=== Prueba de Conversión de Coordenadas ===")
    
    # Lance 12 - Posición inicial
    lat1 = "33° 51.21588' S"
    lng1 = "72° 8.14188' W"
    
    pos1 = convert_position(lat1, lng1)
    print(f"\nPosición Inicial Lance 12:")
    print(f"  Original: {lat1}, {lng1}")
    print(f"  Decimal: {pos1['lat']}, {pos1['lng']}")
    
    # Lance 12 - Posición final
    lat2 = "33° 46.31808' S"
    lng2 = "72° 4.62120' W"
    
    pos2 = convert_position(lat2, lng2)
    print(f"\nPosición Final Lance 12:")
    print(f"  Original: {lat2}, {lng2}")
    print(f"  Decimal: {pos2['lat']}, {pos2['lng']}")
