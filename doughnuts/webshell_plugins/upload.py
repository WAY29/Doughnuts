from os import path
from base64 import b64encode

from libs.config import alias, color
from libs.myapp import send


def get_php(filename: str, web_file_path: str, force: bool):
    return """if (isset($_FILES)){
    $upload_path="%s";
    if (file_exists($upload_path)) {$upload_path=realpath($upload_path);}
    $fname="%s";
    if (is_dir($upload_path)) {
        $upload_path .= DIRECTORY_SEPARATOR.$fname;
    }
    if (%s and file_exists($upload_path)){
        print("$upload_path exist");
    }
    else if (move_uploaded_file($_FILES["file"]["tmp_name"], $upload_path)){
        print("Upload $upload_path success");
    } else {
        print($_FILES["file"]["error"]);
    }
}""" % (web_file_path, filename, str(not force).lower())


def get_php_file_put_contents(filename: str, web_file_path: str, force: bool, content: str):
    return """
    $upload_path="%s";
    if (file_exists($upload_path)) {$upload_path=realpath($upload_path);}
    $fname="%s";
    if (is_dir($upload_path)) {
        $upload_path .= DIRECTORY_SEPARATOR.$fname;
    }
    if (%s and file_exists($upload_path)){
        print("$upload_path exist");
    }
    else if(file_put_contents($upload_path, base64_decode("%s"))) {
        print("Upload $upload_path success");
    } else {
        print("Upload $upload_path error");
    }
""" % (web_file_path, filename, str(not force).lower(), content)


@alias(True, func_alias="u", _type="FILE", t="upload_type")
def run(file_path: str, web_file_path: str = "", upload_type: int = 0, force: bool = False):
    """
    upload

    Upload file to target system.

    eg: upload {file_path} {web_file_path=file_name} {upload_type=0(FILES)/1(file_put_contents)} {force=False}
    """
    filename = path.basename(file_path)
    if (not web_file_path):
        web_file_path = filename
    try:
        fp = open(file_path, "rb")
    except FileNotFoundError:
        print("\n" + color.red("Local File not exist") + "\n")
        return
    if upload_type == 0:
        php = get_php(filename, web_file_path, force)
        res = send(php, files={"file": fp})
    else:
        php = get_php_file_put_contents(filename, web_file_path, force, b64encode(fp.read()).decode())
        res = send(php)
    if (not res):
        return
    text = res.r_text.strip()
    if "success" in text:
        print(color.green(f"\n{text}\n"))
        return True
    elif "exist" in text:
        print(color.yellow(f"\n{text}\n"))
        return True
    else:
        print("\n" + color.red(f"Upload error / Privileges not enough. Result: {text}") + "\n")
