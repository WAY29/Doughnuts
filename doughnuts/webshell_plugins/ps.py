from libs.config import alias, color
from libs.myapp import send, randstr, is_windows
from libs.functions.webshell_plugins.ps import *

PREFIX_LIST = ["c", "cat", "w", "write", "e", "edit", "u", "upload", "mupload", "cp", "copy",
               "d", "download", "mdownload", "dump", "mv", "rm", "cd", "ls", "chmod", "touch"]


def get_php(splitchars):
    return get_php_ps() % splitchars


@alias(True, _type="COMMON")
def run():
    """
    ps

    (Only for *unix) Report a snapshot of the current processes.

    eg: ps

    """
    if (is_windows()):
        print(color.red("Only for target system is linux."))
        return False
    splitchars = randstr("!@#$%^&*()1234567890")
    res = send(get_php(splitchars))
    text = res.r_text.strip()
    if (not res):
        return
    if ("[-]" in text):
        print(color.red(text))
        return
    info_list = text.split('\n')
    for line in info_list:
        info = line.split(splitchars)
        if (len(info) < 4):
            continue
        if (info[-1] != "CMDLINE"):
            info[-1] = color.cyan(info[-1])
        print("%-4s  %-8s  %-12s  %s" %
              (info[0], info[1], info[2], info[3]))
