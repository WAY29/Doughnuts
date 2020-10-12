import builtins
from os import path
from sys import argv
from json import loads, JSONDecodeError

from helpmenu import register_helpmenu
from libs.app import Loop_init, run_loop
from libs.config import gset, gget, custom_set, color
from libs.debug import DEBUG
from libs.myapp import banner


builtins.ic = lambda *a, **kw: None

if (DEBUG["DEV"]):
    try:
        from icecream import ic
        builtins.ic = ic
    except ImportError:
        pass


def main(print_banner: bool = True):
    if (print_banner):
        banner()
    gset("root_path", path.split(path.realpath(__file__))[0])
    with open(path.join(gget("root_path"), "auxiliary", "user_agents", "ua.txt"), "r") as f:
        gset("user_agents", f.readlines())
    register_helpmenu()

    try:
        with open(path.join(gget("root_path"), "variables.config"), "r") as f:
            try:
                for key, value in loads(f.read()).items():
                    custom_set(key=key, value=value)
                print(
                    f"\n{color.green('Variable(s) loaded successfully from file variables.config')}\n")
            except JSONDecodeError:
                print(
                    f"\n{color.yellow('Variable(s) could not be read correctly')}\n")
    except FileNotFoundError:
        pass
    except IOError:
        print(f"\n{color.red('Permission denied to read variables.config')}\n")

    run_loop(My_Loop_init(), leave_message="Bye! Doughnuts:)")


class My_Loop_init(Loop_init):
    def set_platforms(self) -> dict:
        return {"main": "main_plugins", "webshell": "webshell_plugins", "general": "general", "encode": "encode"}

    def set_prompts(self) -> dict:
        return {"main": "doughnuts > ", "webshell": "> "}


if __name__ == "__main__":
    argc = len(argv)
    if (argc > 1):
        if (argv[1].lower() in ["generate", "gen"] and 1 < argc < 8):
            gset("outside", True)
            from main_plugins.generate import outside_generate as generate
            generate(*argv[2:])
        elif (argv[1] in ["connect", "c"]):
            gset("preload_command", " ".join(argv[1:]))
            main(False)
    else:
        main()
