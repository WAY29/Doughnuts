from binascii import b2a_hex
from libs.config import alias


@alias(True)
def run(data: str):
    return b2a_hex(data.encode()).decode()
