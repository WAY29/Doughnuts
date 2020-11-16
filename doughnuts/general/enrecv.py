from libs.config import alias, gget, gset, color


@alias(True,  func_alias="enre")
def run():
    """
    enrecv
    
    Turn on / off response result encoding.
    
    """
    switch = not gget("encode_recv", default=False)
    print(
        f"\nEncode recv: {color.green('On') if switch else color.red('Off')}\n")
    gset("encode_recv", switch, True)