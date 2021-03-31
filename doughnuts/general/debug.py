from libs.config import alias, color
from libs.runtime_config import CONFIG


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
        CONFIG[switch] = not CONFIG[switch]
        print(
            f"\nSet DEBUG switch {switch}: {color.green('On') if CONFIG[switch] else color.red('Off')}\n")
    else:
        print(color.red("\nNo this switch\n"))
