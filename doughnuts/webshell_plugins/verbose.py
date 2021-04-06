from libs.myapp import update_prompt
from libs.config import gset, gget, alias, color
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
        switch_name = "PROMPT.VERBOSE"
        if switch == "":
            gset(switch_name, not gget(switch_name, default=False))
        elif switch == "ON":
            gset(switch_name, True)
        elif switch == "OFF":
            gset(switch_name, False)
        update_prompt()
        print(
            f"\nSet verbose info: {color.green('On') if gget(switch_name) else color.red('Off')}\n")
    else:
        print(color.red("\nNo this switch\n"))
