from os import path, chmod, system

cpath = path.split(path.realpath(__file__))[0]

from sys import path as pyfpath, executable
pyfpath.append(cpath)

from libs.config import color
from libs.myapp import is_windows


pypath = executable

if (not is_windows(False)):
    fpath = "/usr/local/bin/doughnuts"
    print(color.green(f"Try to generate {fpath}"))
    with open(fpath, "w+") as f:
        f.write(f"#!/bin/sh\n{pypath} {cpath}/doughnuts.py")
    chmod(fpath, 0o755)
    if (path.exists(fpath)):
        print(color.green("generate success!"))
    else:
        print(color.red("generate error!"))
else:
    import ctypes

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    if is_admin():
        fpath = "C:\\windows\\System32\\doughnuts.bat"
        print(color.green(f"Try to generate {fpath}"))
        with open(fpath, "w+") as f:
            f.write(f"@echo off\n{pypath} {cpath}\\doughnuts.py")
        if (path.exists(fpath)):
            print(color.green("generate success!"))
        else:
            print(color.red("generate error!"))
        system("pause")
        # 将要运行的代码加到这里
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", executable, __file__, None, 1)