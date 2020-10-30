from libs.config import alias, color
from libs.myapp import send, base64_encode
from os import path


@alias(True, func_alias="cp", _type="FILE")
def run(web_file_path: str, new_file_path: str):
    """
    copy

    Copy file to a new destination.

    eg: copy {web_file_path} {new_file_path}
    """
    if (new_file_path.endswith("/")):
        new_file_path += path.basename(web_file_path)
    res = send(f"print(copy(base64_decode('{base64_encode(web_file_path)}'), base64_decode('{base64_encode(new_file_path)}')));")
    if (not res):
        return
    text = res.r_text.strip()
    if len(text):
        print(color.green(f"\n[Success] copy {web_file_path} to {new_file_path}\n"))
    else:
        print(color.red(f"\n[Failed] copy {web_file_path} to {new_file_path}\n"))
