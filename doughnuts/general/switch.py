from libs.config import alias, gget, gset, color


@alias(True,  func_alias="sw")
def run():
    """
    switch

    (for input Non-ascii) Switch input between raw input and better input.

    """
    switch = not gget("raw_input", default=False)
    print(
        f"\nRaw input: {color.green('On') if switch else color.red('Off')}\n")
    gset("raw_input", switch, True)
