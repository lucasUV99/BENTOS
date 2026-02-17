"""
Configuración de especies y categorías MSC
Mapea las especies que aparecen en las bitácoras a categorías de sostenibilidad
"""

from enum import Enum
from typing import Dict, Optional


class TipoEspecie(Enum):
    """Categorías de especies según MSC"""
    OBJETIVO = "OBJETIVO"  # Especie que se busca capturar
    DEPREDADOR_INCIDENTAL = "DEPREDADOR_INCIDENTAL"  # Peces grandes que afectan ecosistema
    FAUNA_ACOMPANANTE = "FAUNA_ACOMPANANTE"  # Otras especies capturadas
    DESCARTE = "DESCARTE"  # Especies que se devuelven al mar


class UnidadMedida(Enum):
    """Unidades en que se mide cada especie"""
    TONELADAS = "TON"
    UNIDADES = "N°"


# Configuración de especies basada en el PDF real
ESPECIES_CONFIG: Dict[str, dict] = {
    # === ESPECIES OBJETIVO ===
    "Camarón nailon": {
        "tipo": TipoEspecie.OBJETIVO,
        "unidad_principal": UnidadMedida.TONELADAS,
        "nombre_cientifico": "Heterocarpus reedi",
        "umbral_descarte_aceptable": 0.05  # 5% máximo de descarte
    },
    
    "Langostino colorado": {
        "tipo": TipoEspecie.OBJETIVO,
        "unidad_principal": UnidadMedida.TONELADAS,
        "nombre_cientifico": "Pleuroncodes monodon",
        "umbral_descarte_aceptable": 0.05
    },
    
    # === DEPREDADORES / INCIDENTALES (Crítico para MSC) ===
    "Merluza común": {
        "tipo": TipoEspecie.DEPREDADOR_INCIDENTAL,
        "unidad_principal": UnidadMedida.TONELADAS,
        "nombre_cientifico": "Merluccius gayi",
        "es_especie_critica": True,  # Regulada por cuotas
        "ratio_maximo_vs_objetivo": 0.10  # No más de 10% vs captura objetivo
    },
    
    # === FAUNA ACOMPAÑANTE ===
    "Congrio negro": {
        "tipo": TipoEspecie.FAUNA_ACOMPANANTE,
        "unidad_principal": UnidadMedida.TONELADAS,
        "nombre_cientifico": "Genypterus maculatus"
    },
    
    "Lenguado de ojo grande": {
        "tipo": TipoEspecie.FAUNA_ACOMPANANTE,
        "unidad_principal": UnidadMedida.TONELADAS,
        "nombre_cientifico": "Hippoglossina macrops"
    },
    
    "Granadero pichirata": {
        "tipo": TipoEspecie.FAUNA_ACOMPANANTE,
        "unidad_principal": UnidadMedida.TONELADAS,
        "nombre_cientifico": "Coelorinchus aconcagua",
        "descarte_habitual": True
    },
    
    # === CRUSTÁCEOS (medidos en unidades) ===
    "Jaiba paco": {
        "tipo": TipoEspecie.FAUNA_ACOMPANANTE,
        "unidad_principal": UnidadMedida.UNIDADES,
        "nombre_cientifico": "Mursia gaudichaudi",
        "descarte_habitual": True
    },
    
    "Jaiba limón": {
        "tipo": TipoEspecie.FAUNA_ACOMPANANTE,
        "unidad_principal": UnidadMedida.UNIDADES,
        "nombre_cientifico": "Hepatus chilensis",
        "descarte_habitual": True
    },
    
    # === TIBURONES Y RAYAS (Sensibles MSC) ===
    "Tollo negro raspa": {
        "tipo": TipoEspecie.FAUNA_ACOMPANANTE,
        "unidad_principal": UnidadMedida.UNIDADES,
        "nombre_cientifico": "Centroscyllium nigrum",
        "es_especie_sensible": True,  # Tiburón de profundidad
        "requiere_reporte_especial": True
    },
    
    "Raya volantín": {
        "tipo": TipoEspecie.FAUNA_ACOMPANANTE,
        "unidad_principal": UnidadMedida.UNIDADES,
        "nombre_cientifico": "Dipturus trachyderma",
        "es_especie_sensible": True,
        "requiere_reporte_especial": True
    }
}


def obtener_tipo_especie(nombre_especie: str) -> str:
    """
    Obtiene la categoría MSC de una especie.
    
    Args:
        nombre_especie: Nombre de la especie como aparece en la bitácora
        
    Returns:
        Tipo de especie (OBJETIVO, DEPREDADOR_INCIDENTAL, etc.)
    """
    config = ESPECIES_CONFIG.get(nombre_especie)
    if config:
        return config["tipo"].value
    return TipoEspecie.FAUNA_ACOMPANANTE.value  # Default


def es_especie_critica(nombre_especie: str) -> bool:
    """
    Verifica si una especie requiere monitoreo especial para MSC.
    
    Args:
        nombre_especie: Nombre de la especie
        
    Returns:
        True si es crítica para certificación
    """
    config = ESPECIES_CONFIG.get(nombre_especie, {})
    return config.get("es_especie_critica", False) or \
           config.get("es_especie_sensible", False)


def calcular_ratio_merluza(capturas: list) -> Optional[float]:
    """
    Calcula el ratio de merluza vs especies objetivo.
    Este es un indicador clave para MSC.
    
    Args:
        capturas: Lista de diccionarios con capturas del lance
        
    Returns:
        Ratio (0.0 a 1.0) o None si no hay datos suficientes
    """
    total_objetivo = 0.0
    total_merluza = 0.0
    
    for captura in capturas:
        especie = captura.get("especie", "")
        retenida = captura.get("retenida_ton", 0.0)
        
        config = ESPECIES_CONFIG.get(especie, {})
        tipo = config.get("tipo")
        
        if tipo == TipoEspecie.OBJETIVO:
            total_objetivo += retenida
        elif especie == "Merluza común":
            total_merluza += retenida
    
    if total_objetivo > 0:
        return round(total_merluza / total_objetivo, 3)
    return None


def calcular_alerta_ecosistema(ratio_merluza: Optional[float]) -> str:
    """
    Calcula el nivel de alerta basado en el ratio de merluza.
    
    Args:
        ratio_merluza: Ratio calculado
        
    Returns:
        "VERDE", "AMARILLO" o "ROJO"
    """
    if ratio_merluza is None:
        return "VERDE"
    
    if ratio_merluza <= 0.10:  # <= 10%
        return "VERDE"
    elif ratio_merluza <= 0.20:  # 10-20%
        return "AMARILLO"
    else:
        return "ROJO"


if __name__ == "__main__":
    print("=== Configuración de Especies MSC ===\n")
    
    print("Especies Objetivo:")
    for especie, config in ESPECIES_CONFIG.items():
        if config["tipo"] == TipoEspecie.OBJETIVO:
            print(f"  - {especie} ({config['nombre_cientifico']})")
    
    print("\nEspecies Críticas para MSC:")
    for especie, config in ESPECIES_CONFIG.items():
        if config.get("es_especie_critica") or config.get("es_especie_sensible"):
            print(f"  - {especie} ({config['nombre_cientifico']})")
    
    # Prueba del cálculo de ratio (Lance 12 del PDF)
    print("\n=== Prueba de Ratio (Lance 12) ===")
    capturas_lance_12 = [
        {"especie": "Camarón nailon", "retenida_ton": 3.234},
        {"especie": "Merluza común", "retenida_ton": 0.15},
        {"especie": "Jaiba paco", "descartada_unidades": 1000}
    ]
    
    ratio = calcular_ratio_merluza(capturas_lance_12)
    alerta = calcular_alerta_ecosistema(ratio)
    
    print(f"Ratio Merluza/Objetivo: {ratio} ({ratio*100:.1f}%)")
    print(f"Alerta: {alerta}")
