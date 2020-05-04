from libs.config import color
from libs.myapp import gget


def run():
    """
    pdf

    print disable_functions of website
    """
    disable_func_list = gget("webshell.disable_functions", "webshell")
    print(len(disable_func_list), disable_func_list)
    if len(disable_func_list):
        print(color.green("\ndisable_functions:\n"))
        print("    " + "\n    ".join(disable_func_list) + "\n")
    else:
        print(f"{color.green('No disable_functions')} / {color.red('Read error')}")
