from libs.config import alias, color, gset, gget
from libs.myapp import send, base64_encode


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
    gset("webshell.prompt", f"doughnuts ({color.cyan(gget('webshell.netloc', 'webshell'))}) > ")
