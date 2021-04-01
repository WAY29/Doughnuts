from libs.config import alias, color
from libs.myapp import send


def get_php(web_file_path: str):
    return """if (!rmdir("%s")) {echo "fail";}""" % (web_file_path)


@alias(True, _type="FILE")
def run(web_file_path: str):
    """
    cat

    remove empty directory in target system.

    eg: rmdir {web_file_path}
    """
    res = send(get_php(web_file_path))
    if (not res):
        return
    text = res.r_text.strip()
    if "fail" in text:
        print(f"\n remove directory {web_file_path} {color.red('failed')}\n")
    else:
        print(f"\n remove directory {web_file_path} {color.green('success')}\n")
