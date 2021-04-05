from libs.config import alias, gget, gset, color


@alias(True)
def run():
    """
    enrecv

    Open / Close encode recv data switch.

    """
    switch = not gget("encode_recv", default=False)
    print(
        f"\nEncode_recv: {color.green('On') if switch else color.red('Off')}\n")
    gset("encode_recv", switch, True)
