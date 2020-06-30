from codecs import getencoder
from libs.config import alias


@alias(True)
def run(data: str):
    return getencoder("rot-13")(data)[0]
