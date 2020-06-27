from libs.config import alias, gget, gset, color
from libs.myapp import is_windows


@alias()
def run():
    """
    bobd

    (Only for *unix) Try to bypass open_basedir by ini_set and chdir.
    """
    if (is_windows()):
        print(color.red("Target system is windows."))
        return
    switch = not gget("webshell.bypass_obd", default=False)
    print(f"\nbypass open_basedir: {color.green('On') if switch else color.red('Off')}\n")
    gset("webshell.bypass_obd", switch, True)
