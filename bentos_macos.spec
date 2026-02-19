# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para BENTOS — macOS
Genera un .app bundle para macOS.

Uso (desde un Mac):
    pyinstaller bentos_macos.spec
    
NOTA: Este archivo .spec debe ejecutarse en un equipo macOS.
      No se puede compilar un .app desde Windows.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

# Recoger datos de paquetes que incluyen archivos no-Python
datas = [
    # Credenciales de Firebase
    (os.path.join(BASE_DIR, 'config', 'firebase-credentials.json'), 'config'),
    # Backend modules
    (os.path.join(BASE_DIR, 'backend', 'firebase_manager.py'), 'backend'),
    (os.path.join(BASE_DIR, 'backend', 'pdf_parser_v2.py'), 'backend'),
    (os.path.join(BASE_DIR, 'backend', 'pdf_parser.py'), 'backend'),
    (os.path.join(BASE_DIR, 'backend', 'coordinate_converter.py'), 'backend'),
    (os.path.join(BASE_DIR, 'backend', 'especies_config.py'), 'backend'),
    (os.path.join(BASE_DIR, 'backend', 'updater.py'), 'backend'),
    (os.path.join(BASE_DIR, 'backend', '__init__.py'), 'backend'),
]

# Agregar archivos de datos de customtkinter (temas, assets)
datas += collect_data_files('customtkinter')
datas += collect_data_files('CTkMessagebox')
datas += collect_data_files('tkcalendar')

# tkinterdnd2 puede no estar disponible en macOS
try:
    datas += collect_data_files('tkinterdnd2')
except Exception:
    pass

# Submódulos ocultos
hidden_imports = [
    'customtkinter',
    'CTkMessagebox',
    'tkcalendar',
    'babel.numbers',
    'firebase_admin',
    'firebase_admin.credentials',
    'firebase_admin.firestore',
    'google.cloud.firestore',
    'google.cloud.firestore_v1',
    'google.auth',
    'google.auth.transport',
    'google.auth.transport.requests',
    'google.api_core',
    'grpc',
    'pdfplumber',
    'pdfplumber.page',
    'pdfminer',
    'pdfminer.high_level',
    'pandas',
    'numpy',
    'openpyxl',
    'pyproj',
    'pydantic',
    'dotenv',
    'packaging',
    'packaging.version',
]

# tkinterdnd2 opcional en macOS
try:
    import tkinterdnd2
    hidden_imports.append('tkinterdnd2')
except ImportError:
    pass

hidden_imports += collect_submodules('firebase_admin')
hidden_imports += collect_submodules('google.cloud.firestore')
hidden_imports += collect_submodules('google.cloud.firestore_v1')
hidden_imports += collect_submodules('google.api_core')
hidden_imports += collect_submodules('grpc')

a = Analysis(
    [os.path.join(BASE_DIR, 'app.py')],
    pathex=[BASE_DIR, os.path.join(BASE_DIR, 'backend')],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'unittest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BENTOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Necesario en macOS para GUI apps
    target_arch='universal2',  # Compatible con Intel y Apple Silicon
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BENTOS',
)

app = BUNDLE(
    coll,
    name='BENTOS.app',
    icon=None,  # Puedes agregar: icon='assets/bentos.icns'
    bundle_identifier='com.pesqueraquintero.bentos',
    info_plist={
        'CFBundleName': 'BENTOS',
        'CFBundleDisplayName': 'BENTOS - Bitácoras MSC',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '11.0',  # macOS Big Sur en adelante
    },
)
