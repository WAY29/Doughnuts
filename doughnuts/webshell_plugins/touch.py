from re import match

from libs.config import alias, color
from libs.myapp import send
from libs.functions.webshell_plugins.touch import get_php_touch


def get_php(filename):
    return get_php_touch() % (filename)


@alias(True, _type="FILE", func_alias="t", f="filename")
def run(filename: str = ""):
    """
    touch

    Create an empty file or Specify a file whose modification time stamp is the same as a random file in the current directory.

    eg: touch {filename=this_webshell}
    """
    res = send(get_php(filename))
    if (not res):
        return
    text = res.r_text.strip()
    if (match(r"\d+", text)):
        print(
            color.green(f"\nSuccessfully created an empty file {filename}\n"))
    elif (len(text) > 0):
        print(color.green(f"\nModify time stamp {text} success\n"))
