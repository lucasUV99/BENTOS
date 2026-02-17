#!/bin/bash
# ================================================
#  BENTOS — Construir Instalador macOS
# ================================================
#
# Uso:
#   chmod +x construir_macos.sh
#   ./construir_macos.sh
#   ./construir_macos.sh /Volumes/USB/BENTOS    # Copiar a pendrive
#

set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
COPIAR_A="${1:-}"

echo ""
echo "================================================"
echo "  BENTOS — Construir Instalador macOS"
echo "================================================"
echo ""

# Verificar entorno virtual
VENV_PYTHON="$BASE_DIR/.venv/bin/python"
VENV_PYINSTALLER="$BASE_DIR/.venv/bin/pyinstaller"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: No se encontró el entorno virtual en .venv/"
    echo "Ejecuta: python3 -m venv .venv"
    exit 1
fi

if [ ! -f "$VENV_PYINSTALLER" ]; then
    echo "Instalando PyInstaller..."
    "$VENV_PYTHON" -m pip install pyinstaller --quiet
fi

# Instalar dependencias
echo "Verificando dependencias..."
"$VENV_PYTHON" -m pip install -r "$BASE_DIR/requirements.txt" --quiet 2>/dev/null || true

# Limpiar builds anteriores
echo "Limpiando builds anteriores..."
rm -rf "$BASE_DIR/dist" "$BASE_DIR/build"

# Construir
echo ""
echo "Construyendo BENTOS.app..."
echo "Esto puede tardar varios minutos..."
echo ""

cd "$BASE_DIR"
"$VENV_PYINSTALLER" bentos_macos.spec --noconfirm 2>&1 | grep -E "Building|Completed|ERROR|successfully" || true

# Verificar resultado
APP_PATH="$BASE_DIR/dist/BENTOS.app"

if [ -d "$APP_PATH" ]; then
    APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
    echo ""
    echo "================================================"
    echo "  CONSTRUCCIÓN EXITOSA"
    echo "================================================"
    echo "  Archivo: $APP_PATH"
    echo "  Tamaño:  $APP_SIZE"
    echo ""
    
    # Copiar a pendrive si se especificó
    if [ -n "$COPIAR_A" ]; then
        echo "Copiando a $COPIAR_A..."
        
        DESTINO_MACOS="$COPIAR_A/macOS"
        mkdir -p "$DESTINO_MACOS"
        
        # Copiar .app bundle
        cp -R "$APP_PATH" "$DESTINO_MACOS/"
        
        # Crear archivo de instrucciones
        cat > "$DESTINO_MACOS/INSTRUCCIONES.txt" << 'EOF'
BENTOS — Instalación macOS
==============================

1. Arrastra BENTOS.app a tu carpeta Aplicaciones
2. La primera vez que lo abras, macOS puede bloquearlo:
   → Ve a Preferencias del Sistema → Seguridad y Privacidad
   → Haz clic en "Abrir de todos modos"
   
   O bien: clic derecho en BENTOS.app → Abrir → Abrir

Requisitos:
- macOS 11 (Big Sur) o superior
- Conexión a internet (para sincronización con la nube)

Soporte: Contacta al administrador del sistema
EOF
        
        echo "✅ Copiado a: $DESTINO_MACOS/BENTOS.app"
    fi
    
    echo ""
else
    echo ""
    echo "ERROR: No se generó BENTOS.app"
    echo "Revisa los errores arriba."
    exit 1
fi
