from base64 import b64encode
from codecs import getencoder
from hashlib import md5

from libs.config import alias


@alias(True)
def run(data: str, salt: str):
    change = 0x80
    # that = ""
    key = md5(salt.encode()).hexdigest()
    data = (getencoder("rot-13")(data)[0][::-1] + key)[::-1].encode()
    key = key.encode()
    cipher = bytes(data[i] ^ change ^ key[i % 32] for i in range(len(data)))
    return b64encode(cipher).decode()
