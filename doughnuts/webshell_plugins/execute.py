from os import remove
from uuid import uuid4
from libs.config import alias, color
from libs.myapp import send, open_editor, newfile


@alias(True, func_alias="exec", _type="SHELL")
def run(editor: str = "", edit_args: str = ""):
    """
    execute

    execute Custom PHP code by notepad / vi as default or your own editor, edit_args split by space.


    eg: execute {editor=""} {edit_args=""} execute code '"--wait"'
    """
    file_name = str(uuid4()) + ".php"
    real_file_path = newfile(file_name)

    open_editor(real_file_path, editor, edit_args)
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
