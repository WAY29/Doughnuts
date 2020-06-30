from os import path
from sys import path as fpath
cpath = path.split(path.realpath(__file__))[0]
fpath.append(cpath)

from .doughnuts import main
main()
