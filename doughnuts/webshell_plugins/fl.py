from libs.config import alias
from libs.myapp import send, color, print_tree
from libs.functions.webshell_plugins.fl import *
from json import JSONDecodeError


def get_php(file_path: str):
    return get_php_fl() % file_path


@alias(True, _type="DETECT", fp="web_file_path")
def run(web_file_path: str = "/var"):
    """
    fl

    Search log file (access.log,error.log) from target system.

    eg: fl {web_file_path="/var"}
    """
    php = get_php(web_file_path)
    try:
        res = send(php)
        if (not res):
            return
        file_tree = res.r_json()
    except JSONDecodeError:
        print(color.red("Parse Error"))
        return
    print_tree(web_file_path, file_tree)
