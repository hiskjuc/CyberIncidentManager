"""Point Tkinter to the bundled Tcl/Tk runtime when frozen."""

from __future__ import annotations

import os
import sys
from pathlib import Path


_dll_directory = None
_tcl_probe = None


def configure_tkinter_runtime() -> None:
    global _dll_directory, _tcl_probe

    runtime_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    tcl_data = runtime_root / "_tcl_data"
    tk_data = runtime_root / "_tk_data"

    tcl_runtime_path = str(tcl_data)
    tk_runtime_path = str(tk_data)

    if tcl_data.exists():
        os.environ["TCL_LIBRARY"] = tcl_runtime_path.replace("\\", "/")
    if tk_data.exists():
        os.environ["TK_LIBRARY"] = tk_runtime_path.replace("\\", "/")

    if sys.platform != "win32":
        return

    try:
        import ctypes

        if hasattr(os, "add_dll_directory") and _dll_directory is None:
            _dll_directory = os.add_dll_directory(str(runtime_root))

        tcl_dll = runtime_root / "tcl86t.dll"
        if tcl_dll.exists():
            tcl_runtime = ctypes.CDLL(str(tcl_dll))
            tcl_runtime.Tcl_FindExecutable.argtypes = [ctypes.c_char_p]
            executable_path = str(sys.executable).replace("\\", "/").encode("utf-8")
            tcl_runtime.Tcl_FindExecutable(executable_path)
            tcl_runtime.Tcl_CreateInterp.restype = ctypes.c_void_p
            tcl_runtime.Tcl_Eval.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            tcl_runtime.Tcl_Init.argtypes = [ctypes.c_void_p]
            tcl_runtime.Tcl_Init.restype = ctypes.c_int

            interp = tcl_runtime.Tcl_CreateInterp()
            tcl_data_path = tcl_runtime_path.replace("\\", "/").encode("utf-8")
            init_path = (tcl_runtime_path.replace("\\", "/") + "/init.tcl").encode("utf-8")
            runtime_root_path = str(runtime_root).replace("\\", "/").encode("utf-8")
            # Prime Tcl's filesystem layer before Tkinter asks it to source init.tcl.
            tcl_runtime.Tcl_Eval(interp, b"pwd")
            tcl_runtime.Tcl_Eval(interp, b"file exists {C:/Windows/win.ini}")
            tcl_runtime.Tcl_Eval(interp, b"file exists {" + runtime_root_path + b"}")
            tcl_runtime.Tcl_Eval(interp, b"glob -nocomplain {" + tcl_data_path + b"/*}")
            tcl_runtime.Tcl_Eval(interp, b"set __cim_init_file [open {" + init_path + b"} r]; close $__cim_init_file")
            tcl_runtime.Tcl_Init(interp)

        if tcl_data.exists() and _tcl_probe is None:
            import _tkinter

            _tcl_probe = _tkinter.create(None, "py", "Tk", False, True, False, False, None)
    except Exception:
        pass


configure_tkinter_runtime()
