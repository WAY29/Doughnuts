from libs.config import alias, gget, gset, color


@alias()
def run():
    """
    bobd

    Try to bypass open_basedir by ini_set and chdir.
    """
    switch = not gget("webshell.bypass_obd", default=False)
    print(f"\nbypass open_basedir: {color.green('On') if switch else color.red('Off')}\n")
    gset("webshell.bypass_obd", switch, True)
