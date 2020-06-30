from libs.config import alias, gget


@alias()
def run():
    """
    pwd

    Print the name of the current working directory.
    """
    pwd = gget("webshell.pwd", namespace="webshell")
    print(f"\nCurrent working directory:\n  {pwd}\n")
