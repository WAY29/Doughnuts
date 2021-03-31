from libs.myapp import set_prompt
from libs.config import alias, color
from libs.runtime_config import CONFIG


@alias(True)
def run(switch: str = ""):
    """
    verbose

    Open / Close verbose info for prompt.

    switch:
        - ON
        - OFF
    """
    switch = switch.upper()
    if (switch in ["ON", "OFF", ""]):
        if switch == "":
            CONFIG["VERBOSE"] = not CONFIG["VERBOSE"]
        elif switch == "ON":
            CONFIG["VERBOSE"] = True
        elif switch == "OFF":
            CONFIG["VERBOSE"] = False
        set_prompt()
        print(
            f"\nSet verbose info: {color.green('On') if CONFIG['VERBOSE'] else color.red('Off')}\n")
    else:
        print(color.red("\nNo this switch\n"))
