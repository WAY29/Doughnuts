from libs.config import gset, gget, alias, color


@alias(True)
def run(switch: str = "SEND"):
    """
    debug

    Open / Close Debug switch.

    switch:
        - SEND
        - LOOP
    """
    switch = switch.upper()
    if (switch in ["LOOP", "SEND"]):
        switch_name = "DEBUG." + switch
        button = not gget(switch_name, default=False)
        gset(switch_name, button)
        print(
            f"\nSet DEBUG switch {switch}: {color.green('On') if button else color.red('Off')}\n")
    else:
        print(color.red("\nNo this switch\n"))
