# fkb-remote.spec
# Gerado para PyInstaller 5.x+
#
# ANTES DE COMPILAR:
#   1. Baixe o fkb.exe em:
#      https://github.com/finjackin/FKB-Remote/releases/download/v2.0.0/fkb.exe
#   2. Coloque o fkb.exe na mesma pasta deste .spec (raiz do projeto)
#   3. Execute na raiz do projeto:
#      pyinstaller fkb-remote.spec

import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['fkb_remote.py'],
    pathex=['.'],
    binaries=[
        # fkb.exe embutido — será extraído para sys._MEIPASS em runtime
        ('fkb.exe', '.'),
    ],
    datas=[],
    hiddenimports=[
        # requests e dependências internas que o PyInstaller às vezes não detecta
        'requests',
        'requests.adapters',
        'requests.auth',
        'requests.cookies',
        'requests.exceptions',
        'requests.models',
        'requests.sessions',
        'urllib3',
        'urllib3.util',
        'urllib3.util.retry',
        'certifi',
        'charset_normalizer',
        'idna',
        # Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.PngImagePlugin',
        'PIL.JpegImagePlugin',
        'PIL.BmpImagePlugin',
        'PIL.WebPImagePlugin',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # excluir módulos pesados desnecessários
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PyQt5',
        'PyQt6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fkb-remote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # comprime o exe com UPX se disponível (reduz tamanho)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # terminal visível — obrigatório para programa de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # descomente e aponte para um .ico quando tiver o ícone
)
