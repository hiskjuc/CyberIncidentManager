# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe for the portable Windows build."""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


customtkinter_data = collect_data_files("customtkinter")
python_root = Path(sys.executable).resolve().parent
tk_binaries = [
    (str(python_root / "DLLs" / file_name), ".")
    for file_name in ("_tkinter.pyd", "tcl86t.dll", "tk86t.dll")
    if (python_root / "DLLs" / file_name).exists()
]
tk_data = []
tkinter_package = python_root / "Lib" / "tkinter"
if tkinter_package.exists():
    tk_data.append((str(tkinter_package), "tkinter"))
tcl_data_dir = python_root / "tcl" / "tcl8.6"
tk_data_dir = python_root / "tcl" / "tk8.6"
if tcl_data_dir.exists():
    tk_data.append((str(tcl_data_dir), "_tcl_data"))
if tk_data_dir.exists():
    tk_data.append((str(tk_data_dir), "_tk_data"))

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=tk_binaries,
    datas=[*customtkinter_data, *tk_data],
    hiddenimports=["_tkinter", "tkinter"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["runtime_tkinter.py"],
    excludes=[],
    noarchive=False,
    optimize=0,
)
runtime_tkinter_hooks = [script for script in a.scripts if script[0] == "runtime_tkinter"]
other_runtime_hooks = [script for script in a.scripts if script[0] != "runtime_tkinter"]
a.scripts = other_runtime_hooks + runtime_tkinter_hooks
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Cyber Incident Manager",
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
    name="Cyber Incident Manager",
)
