from libs.config import alias
from libs.myapp import is_windows
from os import system


@alias(func_alias="cls")
def run():
    """
    clear

    Clear screen.
    """
    if (is_windows(False)):
        system("cls")
    else:
        system("clear")
