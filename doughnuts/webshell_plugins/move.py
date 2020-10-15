from libs.config import alias, color
from libs.myapp import send, base64_encode
from os import path


@alias(True, func_alias="mv", _type="FILE")
def run(web_file_path: str, new_file_path: str):
    """
    move

    Rename file or move it to new_file_path like linux mv command.

    eg: move {web_file_path} {new_file_path}
    """
    if (new_file_path.endswith("/")):
        new_file_path += path.basename(web_file_path)
    res = send(f"print(rename(base64_decode('{base64_encode(web_file_path)}'), base64_decode('{base64_encode(new_file_path)}')));")
    if (not res):
        return
    text = res.r_text.strip()
    if len(text):
        print(f"\nmove {web_file_path} to {new_file_path} {color.green('success')}\n")
    else:
        print(f"\nmove {web_file_path} to {new_file_path} {color.red('failed')}\n")
