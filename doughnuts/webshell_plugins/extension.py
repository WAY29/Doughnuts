from libs.config import alias, gget, color


@alias(func_alias="ext", _type="COMMON",)
def run():
    """
    extension

    Lists installed extensions.
    """
    loaded_ext = gget("webshell.loaded_ext", namespace="webshell")
    print()
    if isinstance(loaded_ext, list):
        print(color.magenta("Extension ---> \n"))
        for line in loaded_ext:
            print(color.cyan(" * " + line))
    else:
        print(color.red("Unknown..."))
    print()
