from os import path, makedirs, remove
from uuid import uuid4
from libs.config import alias, color, gget
from libs.myapp import send, open_editor


@alias(True, func_alias="exec", _type="SHELL")
def run(editor: str = ""):
    """
    execute

    execute Custom PHP code by notepad / vi as default or your own editor.

    eg: execute {editor=""}
    """
    file_name = str(uuid4())
    file_path = gget("webshell.download_path", "webshell")
    if not path.exists(file_path):
        makedirs(file_path)
    real_file_path = path.join(file_path, file_name).replace("\\", "/")
    open(real_file_path, "a").close()
    open_editor(real_file_path, editor)
    with open(real_file_path, "r") as f:
        code = f.read()
        if (code.startswith("<?php")):
            code = code[5:]
        if (code.endswith("?>")):
            code = code[:-2]
        print(color.yellow("Execute php code..."))
        res = send(code)
        if (not res):
            return
        text = res.r_text.strip()
        status_code = color.green(str(res.status_code)) if res.status_code == 200 else color.yellow(str(res.status_code))
        print(f"\n{color.green('Result:')}\n[{status_code}] {color.cyan('length')}: {len(text)} \n{text}\n")
    remove(real_file_path)
