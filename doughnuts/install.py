from os import path, chmod, system

cpath = path.split(path.realpath(__file__))[0]

from sys import path as pyfpath, executable, argv
pyfpath.append(cpath)

from libs.config import color
from libs.myapp import is_windows

pypath = executable
filename = "doughnuts"


if (len(argv) == 2 and argv[1] != ""):
    filename = argv[1]

if (not is_windows(False)):
    fpath = "/usr/local/bin/" + filename
    print(color.green(f"Try to generate {fpath}"))
    with open(fpath, "w+") as f:
        f.write(f"#!/bin/sh\n{pypath} {cpath}/doughnuts.py")
    chmod(fpath, 0o755)
    if (path.exists(fpath)):
        print(color.green("generate success!"))
    else:
        print(color.red("generate error!"))
else:
    fpath = path.dirname(pypath)+"\\" + filename + ".bat"
    print(color.green(f"Try to generate {fpath}"))
    with open(fpath, "w+") as f:
        f.write(f"@echo off\n{pypath} {cpath}\\doughnuts.py")
    if (path.exists(fpath)):
        print(color.green("generate success!"))
    else:
        print(color.red("generate error!"))