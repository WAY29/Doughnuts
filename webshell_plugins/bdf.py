from libs.config import alias, gset, color

mode_to_desc_dict = {0: color.red("closed"), 1: color.green("php7-backtrace")}


@alias(True, m="mode")
def run(mode: int = 0):
    """
    bdf

    Try to bypass disable_functions by php7-backtrace-bypass.

    Mode 0:

        close

    Mode 1 php7-backtrace(Only for php7.0-7.4) :

        Origin:
        - https://github.com/mm0r1/exploits/tree/master/php7-backtrace-bypass

        Targets:
        - 7.0 - all versions to date
        - 7.1 - all versions to date
        - 7.2 - all versions to date
        - 7.3 < 7.3.15 (released 20 Feb 2020)
        - 7.4 < 7.4.3 (released 20 Feb 2020)
    """
    if (mode in mode_to_desc_dict):
        print(
            f"\nbypass disable_functions: {mode_to_desc_dict}\n")
        gset("webshell.bypass_df", mode, True, "webshell")
    else:
        print(color.red("Mode error."))
        return
