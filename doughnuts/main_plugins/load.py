from libs.config import alias, color, gset, gget
from libs.app import readline
from os import path


@alias(True, "l")
def run(id: int = 0):
    """
    load

    Load a webshell from log.

    eg: load {_id}
    """
    pf = gget("main.pf")
    root_path = gget("root_path")
    webshell_log_path = path.join(root_path, "webshell.log")
    if (not path.exists(webshell_log_path)):
        print(color.red("No webshell.log"))
        return
    f = open(webshell_log_path, "r+")
    lines = f.readlines()
    try:
        if (id <= 0):
            line_num = pf["show"].run()
            print("choose:>", end="")
            load_id = readline()
            if (load_id.isdigit()):
                load_id = int(load_id)
            else:
                print(color.red("\nInput Error\n"))
                return
        else:
            load_id = id
            line_num = len(lines)
        if load_id <= line_num:
            data = lines[load_id - 1].strip().split("|")
            gset("webshell.from_log", True, namespace="webshell")
            connect = pf["connect"].run(*data)
            if (not connect):
                print("\nThis webshell seems to no longer working, do you want to delete it?")
                flag = input("(YES/no) >")
                if (flag.lower() in ['n', 'no']):
                    return
                del lines[load_id - 1]
                f.seek(0)
                f.truncate()
                f.write("".join(lines))
        else:
            print(color.red("ID error"))
    finally:
        f.close()
