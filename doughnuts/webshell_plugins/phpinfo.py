import webbrowser
from uuid import uuid4

from os import path
from libs.config import alias
from libs.myapp import send, newfile, gget, gset


@alias(True, _type="COMMON")
def run(force: bool = False):
    """
    phpinfo

    show phpinfo by web browser.

    eg: phpinfo {force=False}
    """
    phpinfo_filepath = gget("webshell.phpinfo_filepath", "webshell")

    if phpinfo_filepath and path.isfile(phpinfo_filepath) and not force:
        webbrowser.open(f"file://{phpinfo_filepath}", 0)
    else:
        res = send("phpinfo();")
        file_name = str(uuid4()) + ".html"
        real_file_path = newfile(file_name)
        with open(real_file_path, "wb") as f:
            f.write(res.r_content)
        webbrowser.open(f"file://{real_file_path}", 0)
        gset("webshell.phpinfo_filepath", real_file_path, namespace="webshell")
