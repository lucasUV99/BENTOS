"""
Script para crear un PDF de prueba con el formato real de Sernapesca
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def crear_pdf_prueba(filename="data/pdfs_ejemplo/SERNAPESCA-BE2021-3088-1.pdf"):
    """Crea un PDF de prueba con el formato real de Sernapesca"""
    
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    y = height - 50  # Posición inicial
    
    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "REPRESENTACIÓN IMPRESA DE BITÁCORA ELECTRÓNICA DE PESCA")
    y -= 30
    
    c.setFont("Helvetica", 10)
    c.drawString(400, y, "Folio: SERNAPESCA-BE2021-3088-1")
    y -= 30
    
    # Información General
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "INFORMACIÓN GENERAL")
    y -= 20
    
    info_general = [
        ("Armador", "QUINTERO S.A., PESQ."),
        ("Embarcación", "RAUTEN"),
        ("Matrícula", "3088"),
        ("Capitán", "JUAN MANUEL CASTRO GALDAMES"),
        ("País Abanderamiento", "CL"),
        ("Señal de Llamada", "CB-7395"),
        ("Puerto Zarpe", "QUINTERO"),
        ("Puerto Desembarque", "QUINTERO"),
        ("Fecha Zarpe", "02-01-2021 10:54:58"),
        ("Fecha Recalada", "06-01-2021 07:19:11"),
        ("Total Lances", "14"),
    ]
    
    c.setFont("Helvetica", 10)
    for campo, detalle in info_general:
        c.drawString(70, y, f"{campo}")
        c.drawString(200, y, detalle)
        y -= 15
    
    y -= 20
    
    # Captura Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "CAPTURA TOTAL (Resumen del Viaje)")
    y -= 20
    
    especies_resumen = [
        ("Congrio negro", "0.08", "", ""),
        ("Merluza común", "0.257", "", ""),
        ("Lenguado de ojo grande", "1.173", "", ""),
        ("Langostino colorado", "1.53", "", ""),
        ("Camarón nailon", "17.703", "", ""),
    ]
    
    c.setFont("Helvetica", 9)
    for especie, retenida, descartada, num in especies_resumen:
        c.drawString(70, y, especie)
        c.drawString(250, y, retenida)
        y -= 12
    
    y -= 20
    
    # DETALLE DE LANCES
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "DETALLE DE LANCES")
    y -= 20
    
    # Lance 1
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "LANCE # 1")
    y -= 15
    
    c.setFont("Helvetica", 9)
    lances_info = [
        "Arte Pesca: ARRASTRE FONDO",
        "Inicio: 03-01-2021 06:43:15",
        "Fin: 03-01-2021 08:43:45",
        "Lat/Long Inicio: 35° 2.15939' S / 72° 36.95262' W",
        "Lat/Long Fin: 35° 5.46209' S / 72° 38.7495' W",
    ]
    
    for info in lances_info:
        c.drawString(70, y, info)
        y -= 12
    
    y -= 5
    c.drawString(70, y, "Captura Lance 1:")
    y -= 12
    
    capturas_l1 = [
        ("Camarón nailon", "1.596"),
        ("Lenguado de ojo grande", "0.24"),
        ("Merluza común", "0.001"),
    ]
    
    for especie, cantidad in capturas_l1:
        c.drawString(90, y, f"{especie}{cantidad}")
        y -= 12
    
    # Nueva página para más lances
    c.showPage()
    y = height - 50
    
    # Lance 2
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "LANCE # 2")
    y -= 15
    
    c.setFont("Helvetica", 9)
    lances_info2 = [
        "Arte Pesca: ARRASTRE FONDO",
        "Inicio: 03-01-2021 09:36:29",
        "Fin: 03-01-2021 11:23:09",
        "Lat/Long Inicio: 35° 5.42447' S / 72° 38.99418' W",
        "Lat/Long Fin: 35° 24.14748' S / 72° 21.8535' W",
    ]
    
    for info in lances_info2:
        c.drawString(70, y, info)
        y -= 12
    
    y -= 5
    c.drawString(70, y, "Captura Lance 2:")
    y -= 12
    
    capturas_l2 = [
        ("Camarón nailon", "2.898"),
        ("Lenguado de ojo grande", "0.24"),
        ("Merluza común", "0.001"),
    ]
    
    for especie, cantidad in capturas_l2:
        c.drawString(90, y, f"{especie}{cantidad}")
        y -= 12
    
    y -= 20
    
    # Lance 3
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "LANCE # 3")
    y -= 15
    
    c.setFont("Helvetica", 9)
    lances_info3 = [
        "Arte Pesca: ARRASTRE FONDO",
        "Inicio: 03-01-2021 13:05:13",
        "Fin: 03-01-2021 14:51:17",
        "Lat/Long Inicio: 35° 26.55456' S / 72° 19.05648' W",
        "Lat/Long Fin: 35° 26.571' S / 72° 18.90108' W",
        "Observaciones: Red con piedras",
    ]
    
    for info in lances_info3:
        c.drawString(70, y, info)
        y -= 12
    
    y -= 5
    c.drawString(70, y, "Captura Lance 3:")
    y -= 12
    
    capturas_l3 = [
        ("Langostino colorado", "0.374"),
        ("Lenguado de ojo grande", "0.03"),
        ("Merluza común", "0.001"),
    ]
    
    for especie, cantidad in capturas_l3:
        c.drawString(90, y, f"{especie}{cantidad}")
        y -= 12
    
    # Guardar PDF
    c.save()
    print(f"✅ PDF creado: {filename}")

if __name__ == "__main__":
    crear_pdf_prueba()
