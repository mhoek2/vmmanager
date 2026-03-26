# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from PyInstaller.utils.hooks import collect_data_files


# ------------------------------------------------------
# Copy asset folders
# ------------------------------------------------------
files_to_copy = {
    os.path.join("config.json"):    "dist/config.json",
    os.path.join("vms.json"):       "dist/vms.json",
}

folders_to_copy = { 
}

for src, dst in folders_to_copy.items():
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

for src, dst in files_to_copy.items():
    if os.path.isfile(src):
        shutil.copy2(src, dst)

# ------------------------------------------------------
# Configuration
# ------------------------------------------------------
datas = [
    ('modules',        'modules'),
    ('templates',        'templates'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=['./hooks'],
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
    a.binaries,
    a.datas,
    [],
    name='VM Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
	icon='icon.ico',
)