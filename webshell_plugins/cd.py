from libs.config import alias, color, gset, gget
from libs.myapp import send


@alias(True, d="dir")
def run(dir: str = ''):
    """
    cd

    Change the working directory.
    """
    pwd = send(f"chdir('{dir}');print(getcwd());").r_text.strip()
    gset("webshell.pwd", pwd, namespace="webshell")
    gset("webshell.prompt", f"doughnuts ({color.cyan(gget('webshell.netloc', 'webshell'))}) > ")
