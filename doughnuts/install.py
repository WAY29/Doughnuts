from os import path, chmod, system

cpath = path.split(path.realpath(__file__))[0]

from sys import path as pyfpath, executable, argv
pyfpath.append(cpath)

from libs.config import color
from libs.myapp import is_windows
from os import environ

pypath = executable
filename = "doughnuts"


if (len(argv) == 2 and argv[1] != ""):
    filename = argv[1]

if (not is_windows(False)):
    if ("/usr/local/bin" not in environ["PATH"]):
        print(color.red(f"please add /usr/local/bin to $PATH"))
        exit(1)
    fpath = "/usr/local/bin/" + filename
    print(color.green(f"Try to generate {fpath}"))
    with open(fpath, "w+") as f:
        f.write(f"#!/bin/sh\n{pypath} {cpath}/doughnuts.py $*")
    chmod(fpath, 0o755)
    if (path.exists(fpath)):
        print(color.green("generate success!"))
    else:
        print(color.red("generate error!"))
else:
    fpath = path.dirname(pypath)+"\\" + filename + ".bat"
    print(color.green(f"Try to generate {fpath}"))
    text = f"""@echo off
:param
set str=%1
if "%str%"=="" (
    goto end
)
set allparam=%allparam% %str%
shift /0
goto param
:end
{pypath} {cpath}\\doughnuts.py %allparam%
"""
    with open(fpath, "w+") as f:
        f.write(text)
    if (path.exists(fpath)):
        print(color.green("generate success!"))
    else:
        print(color.red("generate error!"))
