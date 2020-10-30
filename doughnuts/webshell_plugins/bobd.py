from libs.config import alias, gget, gset, color
from libs.myapp import is_windows

needle_functions = {"ini_set", "chdir"}


@alias(_type="OTHER")
def run():
    """
    bobd

    (Only for *unix) Try to bypass open_basedir by ini_set and chdir.
    """
    disable_func_list = gget("webshell.disable_functions", "webshell")
    if (is_windows()):
        print(color.red("Target system isn't *unix"))
        return
    if ("chdir" in disable_func_list or ("ini_set" in disable_func_list and "ini_alter" in disable_func_list)):
        print("\n" + color.red("ini_set/ini_alter or chdir function is disabled") + "\n")
        return
    switch = not gget("webshell.bypass_obd", "webshell", default=False)
    print(
        f"\nbypass open_basedir: {color.green('On') if switch else color.red('Off')}\n")
    gset("webshell.bypass_obd", switch, True, "webshell")
