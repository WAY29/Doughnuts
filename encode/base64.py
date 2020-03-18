from base64 import b64encode

from libs.config import alias


@alias(True)
def run(data: str):
    return b64encode(data.encode()).decode()
