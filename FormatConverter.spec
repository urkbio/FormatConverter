# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['file_converter.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Cursor\\FormatConverter\\ffmpeg', 'ffmpeg'), ('C:\\Cursor\\FormatConverter\\icons', 'icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FormatConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Cursor\\FormatConverter\\version.txt',
    icon=['C:\\Cursor\\FormatConverter\\icons\\converter.ico'],
    manifest='C:\\Cursor\\FormatConverter\\app.manifest',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FormatConverter',
)
