import builtins
from os import path
from sys import argv
from helpmenu import register_helpmenu
from libs.app import Loop_init, run_loop
from libs.config import gset, gget, load_custom_config, load_var_config
from libs.myapp import banner


builtins.ic = lambda *a, **kw: None


def load_config():
    # load variables.config
    load_var_config()
    # load config.ini
    load_custom_config()

    # DEBUG
    if (gget("DEBUG.DEV")):
        try:
            from icecream import ic
            builtins.ic = ic
        except ImportError:
            pass


def main(print_banner: bool = True):
    # 标语
    if (print_banner):
        banner()
    # 初始化根路径
    gset("root_path", path.split(path.realpath(__file__))[0])
    # 载入 user_agents
    with open(path.join(gget("root_path"), "auxiliary", "user_agents", "ua.txt"), "r") as f:
        gset("user_agents", f.readlines())
    # 初始化帮助菜单
    register_helpmenu()
    # 加载配置
    load_config()
    # 主循环
    run_loop(My_Loop_init(), leave_message="Bye! Remember to eat doughnuts :)")


class My_Loop_init(Loop_init):
    def __init__(self, api: str = "run", init_namespace: str = "main"):
        super().__init__(api=api, init_namespace=init_namespace)
        # 为webshell平台添加custom的命令列表
        wordlist = gget("webshell.wordlist")
        wordlist["command_wordlist"] += gget("custom.wordlist")[
            "command_wordlist"]

    def set_platforms(self) -> dict:
        platforms = {
                    "main": "main_plugins",
                     "webshell": "webshell_plugins",
                     "general": "general",
                     "encode": "encode",
                     "custom": "custom_plugins"
        }
        return platforms

    def set_prompts(self) -> dict:
        return {
                "main": "doughnuts > ",
                "webshell": "> ",
                "custom": "> "
        }


if __name__ == "__main__":
    argc = len(argv)
    if (argc > 1):
        if (argv[1].lower() in ["generate", "gen"] and 1 < argc < 8):
            gset("outside", True)
            from main_plugins.generate import outside_generate as generate
            generate(*argv[2:])
    else:
        main()
