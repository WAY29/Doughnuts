from os import path
from libs.config import color, alias
from json import loads
from libs.myapp import gget, send, get_system_code, is_windows


@alias(True, _type="DETECT", p="find_path")
def run(find_path: str = "/usr&/bin"):
    """
    av

    (Only for windows) Detect anti-virus software running on the target system.
    ps: Need to run system commands

    Origin: https://github.com/BrownFly/findAV, https://github.com/gh0stkey/avList
    """
    if (not is_windows()):
        print(color.red("\nTarget system isn't windows\n"))
        return
    res = send(get_system_code("tasklist /svc"))
    if (not res or not res.r_text or "No system execute function" in res.r_text):
        print(color.red("\nDetect error\n"))
        return
    with open(path.join(gget("root_path"), "auxiliary", "av", "av.json"), "r", encoding="utf-8") as f:
        av_processes = loads(f.read())
    flag = 0
    print("\n" + color.green(" " * 37 + "Result"))
    for line in res.r_text.split("\n"):
        process = line.split(' ')[0]
        if process in av_processes:
            flag = 1
            print("    %40s     -     %-30s" % (color.cyan(process), color.yellow(av_processes[process])))
    if (not flag):
        print("    %40s     /      %-30s" % (color.green('No anti-virus'), color.red('Not found')))
    print()
