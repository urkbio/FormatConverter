# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['file_converter.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/joomaen/Documents/Code/FormatConverter/icons', 'icons')],
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
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
    name='file_converter',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='file_converter',
)
app = BUNDLE(
    coll,
    name='file_converter.app',
    icon=None,
    bundle_identifier=None,
)
