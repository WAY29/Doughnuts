from os import environ, path, chmod

cpath = path.split(path.realpath(__file__))[0]

from sys import path as pyfpath
pyfpath.append(cpath)

from libs.config import color
from libs.myapp import is_windows


if (not is_windows(False)):
    pypath = environ['_']
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
    print(color.red("doughnuts.install could not support windows!"))