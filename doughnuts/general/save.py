from libs.config import alias, custom_gets, color
from os import path
from json import dumps


@alias(True)
def run():
    """
    save

    Save the configuration of the variable(s) to variables.config.
    """
    filepath = "variables.config"
    variable_dict = dumps(custom_gets())

    with open(filepath, "w") as f:
        f.write(variable_dict)

    if(path.exists(filepath)):
        print()
        for k, v in custom_gets().items():
            print(f"{color.green(f'{k} => {v} [{type(v).__name__}]')}")
        print(color.cyan(
            f"\nThe above variables have been written to {filepath}\n"))
    else:
        print(f"\n{color.red('Write failed')}\n")
