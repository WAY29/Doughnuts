from os import path
from libs.config import color, alias
from json import loads
from libs.myapp import gget, send, get_system_code, is_windows


@alias(True, _type="DETECT", p="find_path")
def run(find_path: str = "/usr&/bin"):
    """
    priv

    (Only for *unix) Find all files with suid belonging to root and try to get privilege escalation tips.
    ps:use & to split find_path

    eg: priv {find_path="/usr&/bin"}
    """
    if (is_windows()):
        print(color.red("\nTarget system isn't *unix\n"))
        return
    print(color.yellow(f"\nFinding all files with suid belonging to root in {find_path}...\n"))
    phpcode = ""
    priv_tips = {}
    if ("&" in find_path):
        find_paths = find_path.split("&")
    else:
        find_paths = (find_path, )
    for each in find_paths:
        phpcode += get_system_code(f"find {each} -user root -perm -4000 -type f 2>/dev/null")
    res = send(phpcode)
    if (not res):
        return
    suid_commands = res.r_text.strip().split("\n")
    if (not suid_commands or "No system execute function" in suid_commands[0]):
        print(color.red("\nFind error\n"))
        return
    with open(path.join(gget("root_path"), "auxiliary", "priv", "gtfo.json"), "r") as f:
        priv_tips = loads(f.read())
    for cmd_path in suid_commands:
        cmd = cmd_path.split("/")[-1]
        if (cmd in priv_tips):
            print(color.yellow(cmd_path) + f" ( https://gtfobins.github.io/gtfobins/{cmd}/ )\n")
            for k, v in priv_tips[cmd].items():
                info = '\n'.join(v)
                print(f"""{color.cyan(k)}\n{color.green(info)}\n""")
