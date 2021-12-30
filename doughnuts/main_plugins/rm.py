from libs.config import alias, color, gget
from libs.app import readline
from os import path


@alias(True, "rm")
def run(id: int = 0):
    """
    remove

    Remove a webshell log.

    eg: remove {_id}
    """
    pf = gget("main.pf")
    root_path = gget("root_path")
    webshell_log_path = path.join(root_path, "webshell.log")
    if (not path.exists(webshell_log_path)):
        print(color.red("No webshell.log"))
        return
    f = open(webshell_log_path, "r+")
    lines = f.readlines()
    line_num = len(lines)
    f.seek(0)
    f.truncate()
    try:
        if (id <= 0):
            pf["show"].run()
            print("choose:>", end="")
            load_id = readline()
            if (load_id.isdigit()):
                load_id = int(load_id)
            else:
                print(color.red("\nInput Error\n"))
                return
        else:
            load_id = id
        if load_id <= line_num:
            del lines[load_id - 1]
            f.write("".join(lines))
            print(color.green("\nRemove success\n"))
        else:
            print(color.red("ID error"))
    finally:
        f.close()
