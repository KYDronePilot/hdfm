import os
from pathlib import Path

block_cipher = None

PROJECT_ROOT = Path(os.getenv('PROJECT_PATH'))

a = Analysis(
    [str(PROJECT_ROOT / Path('src') / Path('new_gui.py'))],
    pathex=[str(PROJECT_ROOT / 'src')],
    binaries=[],
    datas=[
        (
            str(PROJECT_ROOT / Path('font') / Path('GlacialIndifference-Regular.otf')),
            '.',
        ),
        (str(PROJECT_ROOT / Path('maps') / Path('us_map.png')), '.'),
        (str(PROJECT_ROOT / Path('icons') / Path('*')), 'icons'),
    ],
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name='hdfm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
