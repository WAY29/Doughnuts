from libs.config import alias, color, gget
from libs.myapp import open_editor


@alias(True, func_alias="e", _type="FILE")
def run(web_file_path: str, editor: str = "", edit_args: str = ""):
    """
    edit

    edit file from target system (download->edit->upload) by notepad / vi as default or your own editor,edit_args split by space.

    eg: edit {web_file_path} {editor=""} {edit_args=""} edit a.php code '"--wait"'
    """
    webshell_pf = gget("webshell.pf")
    download_file_path = webshell_pf["download"].run(web_file_path)
    if (not download_file_path):
        return

    flag = open_editor(download_file_path, editor, edit_args)
    if (not flag):
        print("\n" + color.red(f"Call {editor} failed") + "\n")
        return
    webshell_pf["upload"].run(download_file_path, web_file_path, force=True)
