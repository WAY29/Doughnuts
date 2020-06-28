from libs.config import alias, gget, gset, color

needle_functions = {"ini_set", "chdir"}


@alias()
def run():
    """
    bdf

    (Only for php7.0-7.4) Try to bypass disable_functions by php7-backtrace-bypass.

    Origin:
    - https://github.com/mm0r1/exploits/tree/master/php7-backtrace-bypass

    Targets:
    - 7.0 - all versions to date
    - 7.1 - all versions to date
    - 7.2 - all versions to date
    - 7.3 < 7.3.15 (released 20 Feb 2020)
    - 7.4 < 7.4.3 (released 20 Feb 2020)
    """
    switch = not gget("webshell.bypass_df", "webshell", default=False)
    print(
        f"\nbypass disable_functions: {color.green('On') if switch else color.red('Off')}\n")
    gset("webshell.bypass_df", switch, True, "webshell")
