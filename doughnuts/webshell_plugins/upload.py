from os import path
from base64 import b64encode

from libs.config import alias, color
from libs.myapp import send
from libs.functions.webshell_plugins.upload import *


def get_php(filename: str, web_file_path: str, force: bool):
    return get_php_upload() % (web_file_path, filename, str(not force).lower())


def get_php_file_put_contents(
        filename: str, web_file_path: str, force: bool, content: str):
    return get_php_file_put_contents() % (
        web_file_path, filename, str(not force).lower(), content)


@alias(True, func_alias="u", _type="FILE", t="upload_type")
def run(file_path: str, web_file_path: str = "",
        upload_type: int = 0, force: bool = False):
    """
    upload

    Upload file to target system.

    eg: upload {file_path} {web_file_path=file_name} {upload_type=0(FILES)/1(file_put_contents)} {force=False}
    """
    try:
        upload_type = int(upload_type)
    except ValueError:
        upload_type = 0

    filename = path.basename(file_path)
    if (not web_file_path):
        web_file_path = filename
    try:
        fp = open(file_path, "rb")
    except FileNotFoundError:
        print("\n" + color.red("Local File not exist") + "\n")
        return
    if upload_type == 0:
        php = get_php(filename, web_file_path, force)
        res = send(php, files={"file": fp})
    else:
        php = get_php_file_put_contents(
            filename, web_file_path, force, b64encode(
                fp.read()).decode())
        res = send(php)
    if (not res):
        return
    text = res.r_text.strip()
    if "success" in text:
        print(color.green(f"\n{text}\n"))
        return True
    elif "exist" in text:
        print(color.yellow(f"\n{text}\n"))
        return True
    else:
        print(
            "\n" +
            color.red(f"Upload error / Privileges not enough. Error: {text}") +
            "\n")
