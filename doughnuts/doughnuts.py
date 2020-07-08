import builtins
from os import path
from sys import argv

from helpmenu import register_helpmenu
from libs.app import Loop_init, run_loop
from libs.config import color, gset, gget
from libs.debug import DEBUG
from libs.myapp import banner


if (DEBUG["DEV"]):
    print(color.yellow("\nDEV MODE"))
    try:
        from icecream import ic
        print(color.yellow("builtin ic functions\nuse it to inspect objects\n"))
        builtins.ic = ic
    except ImportError:
        print(color.red("iceream module is not install\n"))


def main(print_banner: bool = True):
    if (print_banner):
        banner()
    gset("root_path", path.split(path.realpath(__file__))[0])
    with open(path.join(gget("root_path"), "auxiliary", "user_agents", "ua.txt"), "r") as f:
        gset("user_agents", f.readlines())
    register_helpmenu()
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
