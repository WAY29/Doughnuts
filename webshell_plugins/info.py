from libs.config import alias, set_namespace
from libs.myapp import print_webshell_info


@alias(func_alias="i")
def run():
    """
    info

    Show website information and command information.
    """
    print_webshell_info()
    set_namespace("webshell")
