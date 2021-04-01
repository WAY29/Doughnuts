from libs.config import alias, color
from libs.myapp import send


def get_php(web_file_path: str, mode: str = "0777", recursive: bool = True):
    return """if (!mkdir("%s", %s, %s)) {echo "fail";}""" % (web_file_path, mode, str(recursive).lower())


@alias(True, _type="FILE")
def run(web_file_path: str, mode: str = "0777", recursive: bool = True):
    """
    cat

    make directory in target system.

    eg: mkdir {web_file_path}
    """
    res = send(get_php(web_file_path, mode, recursive))
    if (not res):
        return
    text = res.r_text.strip()
    if "fail" in text:
        print(f"\n make directory {web_file_path} {color.red('failed')}\n")
    else:
        print(f"\n make directory {web_file_path} {color.green('success')}\n")
