from libs.config import alias, color
from libs.myapp import send
from libs.app import readline
from libs.functions.webshell_plugins.ls import *

PREFIX_LIST = ["c", "cat", "w", "write", "e", "edit", "u", "upload", "mupload", "cp", "copy",
               "d", "download", "mdownload", "dump", "mv", "rm", "cd", "ls", "chmod", "touch"]

def get_php(path, mode):
    scan_code = f'$files=scandir("{path}");sort($files);'
    if (mode == 2):
        scan_code = f'$files=glob("{path}/*");$pfiles=glob("{path}/.*");$files=array_merge($files,$pfiles);sort($files);'
    return get_php_ls() % (scan_code, path)


@alias(True, func_alias="dir", _type="COMMON", p="path", m="mode")
def run(path: str = ".", mode: int = 1):
    """
    ls

    List information about the files.

    eg: ls {path=.} {mode=1}

    mode:
      - 1 : scandir
      - 2 : glob
    """
    res = send(get_php(path, mode))
    if (not res):
        return
    info_list = res.r_text.strip().split('\n')
    print('\n'.join(info_list[:3]))
    ls_wordlist = []
    for line in info_list[3:]:
        info = line.split(" ")
        if (len(info) < 7):
            continue
        prems, name = info[0], " ".join(info[6:])
        ls_wordlist.append(name)
        if (prems[0] == 'd'):
            name = color.cyan(name)
            info[3] = ''
        elif ('x' in prems):
            name = color.green(name)
        print("%s  %-8s  %-8s  %6s  %s  %s  %s" %
              (info[0], info[1], info[2], info[3], info[4], info[5], name))
    for prefix in PREFIX_LIST:
        readline.add_prefix_wordlist(prefix, ls_wordlist)
