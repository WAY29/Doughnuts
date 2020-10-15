from libs.config import color, alias
from libs.myapp import gget


@alias(_type="COMMON")
def run():
    """
    pdf

    print disable_functions of website.
    """
    disable_func_list = gget("webshell.disable_functions", "webshell")
    if len(disable_func_list):
        print(color.green("\ndisable_functions:\n"))
        print("    " + "\n    ".join(disable_func_list) + "\n")
    else:
        print(f"{color.green('No disable_functions')} / {color.red('Read error')}")
