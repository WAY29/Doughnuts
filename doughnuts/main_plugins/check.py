from libs.config import gget, alias, color
from os.path import exists
from requests import post, exceptions


@alias(True)
def run(timeout: float = 2.0):
    """
    check

    Check if each webshell is alive.

     eg: check {timeout=2.0}
    """
    if not exists("webshell.log"):
        print(color.red("No webshell.Log"))
        return 0
    with open("webshell.log", "r") as f:
        for index, line in enumerate(f, 1):
            url, method, pwd, *encode_functions = line.split("|")
            if method == "GET":
                raw_key = "params"
            elif method == "POST":
                raw_key = "data"
            elif method == "COOKIE":
                raw_key = "cookies"
            elif method == "HEADER":
                raw_key = "headers"
            else:
                print(f"[{color.blue(str(index))}] {color.red('Method error')}")
                continue
            check_command = "print(md5(1));"
            encode_pf = gget("encode.pf")
            for func in encode_functions:
                if func in encode_pf:
                    check_command = encode_pf[func].run(check_command)
            params_dict = {"data": {}, "timeout": timeout}
            params_dict[raw_key] = {}
            params_dict[raw_key][pwd] = check_command
            common_text, status_code_text = "", "000"
            try:
                res = post(url, verify=False, **params_dict)
                status_code_text = str(res.status_code)
                if ("c4ca4238a0b923820dcc509a6f75849b" in res.text):
                    common_text = color.green("Alive")
                else:
                    common_text = color.red("Not Alive")
            except exceptions.Timeout:
                common_text = color.yellow("Timeout")
            except exceptions.RequestException:
                common_text = color.red("Request error")
            print(f"[{color.blue(str(index))}] [{color.yellow(status_code_text)}] {common_text} {url}")
