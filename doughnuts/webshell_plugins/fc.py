from libs.config import alias, gget
from libs.myapp import send, color, print_tree
from libs.functions.webshell_plugins.fc import get_php_fc
from json import JSONDecodeError


def get_php(file_path: str):
    return get_php_fc() % file_path


@alias(True, _type="DETECT", fp="web_file_path")
def run(web_file_path: str = ""):
    """
    fc

    Search config file from target system.

    eg: fc {web_file_path=webroot}
    """
    web_file_path = web_file_path if (
        len(web_file_path)) else gget(
        "webshell.root",
        "webshell")
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
