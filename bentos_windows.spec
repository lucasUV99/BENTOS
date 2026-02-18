# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para BENTOS — Windows
Genera un ejecutable único (.exe) con todos los recursos empaquetados.

Uso:
    pyinstaller bentos_windows.spec
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
datas += collect_data_files('tkinterdnd2')

# Agregar matplotlib con manejo de errores para tests
try:
    datas += collect_data_files('matplotlib')
except Exception as e:
    print(f"Warning: Could not collect all matplotlib data: {e}")

# Submódulos ocultos que PyInstaller no detecta automáticamente
hidden_imports = [
    'customtkinter',
    'CTkMessagebox',
    'tkcalendar',
    'tkinterdnd2',
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
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.patches',
]

# Agregar submódulos de firebase y google cloud
hidden_imports += collect_submodules('firebase_admin')
hidden_imports += collect_submodules('google.cloud.firestore')
hidden_imports += collect_submodules('google.cloud.firestore_v1')
hidden_imports += collect_submodules('google.api_core')
hidden_imports += collect_submodules('grpc')

# Agregar submódulos de matplotlib con manejo de errores para tests
try:
    matplotlib_modules = collect_submodules('matplotlib')
    # Filtrar módulos de tests que causan problemas
    matplotlib_modules = [m for m in matplotlib_modules if 'test' not in m.lower()]
    hidden_imports += matplotlib_modules
except Exception as e:
    print(f"Warning: Could not collect all matplotlib modules: {e}")
    # Agregar manualmente los más importantes
    hidden_imports += [
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.figure',
        'matplotlib.pyplot',
    ]

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
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BENTOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola — solo GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar: icon='assets/bentos.ico'
)
