from libs.config import alias
from libs.myapp import print_webshell_info


@alias(func_alias="i", _type="COMMON")
def run():
    """
    info

    Show website information.
    """
    print_webshell_info()
