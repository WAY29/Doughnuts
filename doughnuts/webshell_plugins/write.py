from re import match
from os import remove
from uuid import uuid4

from libs.config import alias, color
from libs.myapp import send, open_editor, newfile, gget
from libs.functions.webshell_plugins.write import *


@alias(True, func_alias="w", _type="FILE")
def run(web_file_path: str, editor: str = "", edit_args: str = ""):
    """
    write

    Write files directly to the target system by notepad / vi as default or your own editor,edit_args split by space.

    eg: write {web_file_path} {editor=""} {edit_args=""} write a.php code '"--wait"'
    """
    disable_func_list = gget("webshell.disable_functions", "webshell")
    disable_classes_list = gget("webshell.disable_classes", "webshell")
    loaded_ext_list = gget("webshell.loaded_ext", "webshell")
    write_method = 0
    if "file_put_contents" not in disable_func_list:
        write_method = 1
    elif not any((bool(each in disable_func_list) for each in ["fopen", "fwrite"])):
        write_method = 2
    elif "DOMDocument" not in disable_classes_list and "dom" in loaded_ext_list:
        write_method = 3
    elif "SplFileObject" not in disable_classes_list and "SPL" in loaded_ext_list:
        write_method = 4

    file_name = str(uuid4()) + ".php"
    real_file_path = newfile(file_name)

    open_editor(real_file_path, editor, edit_args)

    with open(real_file_path, "r") as f:
        result = base64_encode(f.read())
        res = send(get_php_write(web_file_path,result,write_method))
        if (not res):
            return
        text = res.r_text.strip()
        if (match(r"\d+", text)):
            print(color.green(f"\nWrite {web_file_path} success\n"))
        else:
            print(color.red(f"\nWrite {web_file_path} failed\n"))
    remove(real_file_path)
