from os import system, chdir, getcwd

from libs.config import alias, gget, color
from libs.app import value_translation


@alias(True,  func_alias="!")
def run(*coomands):
    """
    lsh

    Run a command on local machine.

    """
    command = str(value_translation(gget("raw_command_args")))
    if (command):
        if (command.startswith("cd ")):
            chdir(command[3:])
            print(color.green("\nResult:\n\n") + "current working directory:\n\n    " + getcwd() + "\n")
        else:
            print(color.green("\nResult:\n"))
            system(command)
            print()
