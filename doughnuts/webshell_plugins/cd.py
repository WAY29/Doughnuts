from libs.config import alias, gset
from libs.myapp import send, base64_encode, update_prompt


@alias(True, _type="COMMON", d="dir")
def run(directory: str = ''):
    """
    cd

    Change the working directory.

    eg: cd {directory=""}
    """
    res = send(f"chdir(base64_decode('{base64_encode(str(directory))}'));print(getcwd());")
    if (not res):
        return
    pwd = res.r_text.strip()
    gset("webshell.pwd", pwd, namespace="webshell")
    update_prompt()
