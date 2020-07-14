from libs.config import alias, custom_get, custom_gets, color


@alias(True, k="key", a="show_all")
def run(key: str = "", show_all: bool = False):
    """
    get

    Get variable(s) use #{varname} to use it.
    """
    if (show_all):
        print()
        for k, v in custom_gets().items():
            print(f"{color.green(f'{k} => {v} [{type(v).__name__}]')}")
        print()
    elif (key):
        value = custom_get(str(key))
        if (value):
            print(f"\n{color.green(f'{key} => {value} [{type(value).__name__}]')}\n")
        else:
            print(f"\n{color.red(f'unset {key}')}\n")
