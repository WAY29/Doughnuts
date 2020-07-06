from libs.config import alias, gget, color
from libs.debug import DEBUG



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
        DEBUG[switch] = not DEBUG[switch]
        print(f"\nSet DEBUG switch {switch}: {color.green('On') if DEBUG[switch] else color.red('Off')}\n")
    else:
        print(color.red("\nNo this switch\n"))
