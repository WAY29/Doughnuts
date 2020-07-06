from base64 import b64encode
from codecs import getencoder
from hashlib import md5

from libs.config import alias


@alias(True)
def run(data: str, salt: str):
    change = 0x80
    that = ""
    saltm = md5(salt.encode()).hexdigest()
    pas = (getencoder("rot-13")(data)[0][::-1] + saltm)[::-1]
    for i in range(len(pas)):
        that += chr(ord(pas[i]) ^ change ^ ord(saltm[i % 32]))
    return b64encode(that.encode('latin1')).decode()
