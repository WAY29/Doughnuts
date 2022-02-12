from libs.config import alias
from libs.myapp import send, color
from libs.functions.webshell_plugins.outnetwork import get_php_outnetwork


def get_php():
    return get_php_outnetwork()


@alias(True, _type="DETECT")
def run():
    """
    outnetwork

    Quickly detect the situation of the target out of the Internet.
    - HTTP(TCP)
    - DNS
    - UDP

    Origin: https://github.com/AntSword-Store/AS_Out-of-Network

    """
    res = send(get_php())
    for line in res.r_text.split("\n"):
        if line.startswith("[+]"):
            print(color.green(line))
        elif line.startswith("[-]"):
            print(color.red(line))
        else:
            print(line)
