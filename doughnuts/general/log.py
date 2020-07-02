import sys
from itertools import chain
from os import W_OK, access, path
from re import findall, split, sub

from libs.config import alias, color, gset
from libs.myapp import is_windows

pattern = "\033\[.*m"


class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(sub(pattern, "", message))
        self.log.flush()

    def flush(self):
        pass


@alias(True)
def run(filepath="./log/log.txt"):
    """
    log

    (Only for *unix) Write input and output to the log.

    eg: log {filepath="./log/log.txt"}
    """
    if (is_windows(False)):
        print(color.red("\nYour system isn't *unix\n"))
        return
    if access(path.dirname(filepath), W_OK):
        print(color.green(f"\nset log in {filepath}\n"))
        sys.stdout = Logger(filepath, sys.__stdout__)
        sys.stderr = Logger(filepath, sys.__stderr__)
        gset("log_filepath", filepath, True)
        gset("log_stdout", sys.stdout, True)
        gset("log_stderr", sys.stderr, True)
    else:
        print(color.red("\nfile path is invalid\n"))
