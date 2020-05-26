from libs.config import alias, color, gget
from libs.myapp import open_editor


@alias(True, func_alias="m")
def run(web_file_path: str):
    """
    modify

    modify file(s) from target system (download->modify->upload) by notepad/vi.

    eg: modify {web_file_path}
    """
    webshell_pf = gget("webshell.pf")
    download_file_path = webshell_pf["download"].run(web_file_path)
    if (not download_file_path):
        return
    flag = open_editor(download_file_path)
    if (not flag):
        print("\n" + color.red("Call vi / notepad failed") + "\n")
        return
    webshell_pf["upload"].run(download_file_path, web_file_path, True)
