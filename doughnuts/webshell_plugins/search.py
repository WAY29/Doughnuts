from libs.config import alias, color
from libs.myapp import send
from libs.functions.webshell_plugins.search import get_php_search


def get_php(web_file_path: str, pattern: str):
    return get_php_search() % (web_file_path, pattern)


@alias(True, func_alias="find", _type="DETECT", w="web_file_path", p="pattern")
def run(pattern: str, web_file_path: str = "."):
    """
    search

    Search file(s) from target system (Support regex expression).

    eg: search {pattern} {web_file_path="."}
    """
    web_file_path = str(web_file_path)
    res = send(get_php(web_file_path, pattern))
    if (not res):
        return
    files = res.r_text.strip()
    if (len(files)):
        print(f"\n{color.green('Search Result:')}")
        if (web_file_path == "./"):
            web_file_path = ""
        for f in files.split("\n"):
            print("    " + f)
        print()
    else:
        print(f"\n{color.red('File not exist / Search error')}\n")
