from libs.config import alias, color
from libs.myapp import send


def get_php(web_file_path):
    return """if(unlink("%s")){echo 'success';}""" % web_file_path


@alias(True, func_alias="del")
def run(*web_file_paths):
    """
    delete

    Delete website file(s)
    """
    for each_file_path in web_file_paths:
        php = get_php(each_file_path)
        text = send(php).r_text.strip()
        if (text == 'success'):
            print("\n" + color.yellow(each_file_path))
            print("\n" + color.green(f"Delete {each_file_path} success") + "\n")
        else:
            print("\n" + color.yellow(each_file_path))
            print("\n" + color.red(f"Delete {each_file_path} failed") + "\n")
