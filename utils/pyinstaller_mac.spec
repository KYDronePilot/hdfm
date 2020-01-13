import os
from pathlib import Path

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.osx import BUNDLE

block_cipher = None

PROJECT_ROOT = Path(os.getenv('PROJECT_PATH'))

a = Analysis(
    [str(PROJECT_ROOT / Path('src') / Path('new_gui.py'))],
    # TODO: Make this better...
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
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='hdfm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hdfm',
)

app = BUNDLE(
    coll,
    name='HDFM.app',
    icon=None,
    bundle_identifier=None,
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [],
    },
)
