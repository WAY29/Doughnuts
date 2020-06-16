import json
from os import _exit
from re import compile as re_compile
from sys import exc_info, path
from traceback import print_exception

from libs.readline import LovelyReadline
from Myplugin import Platform

from .config import gget, gset, order_alias, set_namespace

NUMBER_PATTERN = re_compile(r"^[-+]?\d*(\.?\d+|)$")
STDIN_STREAM = b''
HISTORY = None
HISTORY_POINTER = 0
FROM_HISTORY = False
readline = LovelyReadline()
readline.init({}, {})

"""
api ['']
history_commands ['']
leave_message ['']
namespace ['']
namespace_folders ['']
folders_namespace ['']
root_path ['']
{platform}.pf ['']
{platform}.prompt ['']

{module_name}.reverse_alias [namespace]
order_alias [namespace]
speical plugin platform:general   general commands
speical plugin platform:encode    Encoders
"""


class Loop_init:
    def __init__(self, api: str = "run", init_namespace: str = "main"):
        """
        Initialize the loop

        Args:
            api (str, optional): The name of the entry function that is common to all plugins.. Defaults to "run".
            default_namespace (str, optional): Initial namespace. Defaults to "main".
        """
        platforms = self.set_platforms()
        gset("api", api)
        gset("loop", True)
        gset("blockexit", False)
        gset("namespace", init_namespace)
        gset("root_path", path[0])
        gset("namespace_folders",  platforms)
        gset("folders_namespace", {v: k for k, v in platforms.items()})
        for k, v in platforms.items():
            pf = import_platform(v, api)
            gset(k + ".pf", pf)
            gset(k + ".wordlist", {"command_wordlist": list(pf.names())})
            gset(k + ".prefix_wordlist", {command: gget(command + ".arg_wordlist", k)
                                          for command in gget(k + ".wordlist")["command_wordlist"]})
        general_wordlist = gget("general.wordlist")["command_wordlist"]
        for k in platforms.keys():  # 往其他插件平台添加general平台的命令列表
            if (k == "general"):
                continue
            wordlist = gget(k + ".wordlist")
            wordlist["command_wordlist"] += general_wordlist
        for k, v in self.set_prompts().items():
            gset(k + ".prompt", v)

    def set_platforms(self) -> dict:
        return {"main": "main_plugins"}

    def set_prompts(self) -> dict:
        return {"main": ":>"}


def import_platform(platform_name: str, api: str):
    return Platform(platform_name, api)


def value_translation(arg):
    def is_numberic(string):
        global NUMBER_PATTERN
        return True if (NUMBER_PATTERN.match(string)) else False

    if is_numberic(arg):
        arg = float(arg) if "." in arg else int(arg)
    else:
        try:
            arg = json.loads(arg.replace("'", '"'))
        except json.JSONDecodeError:
            pass
    return arg


def args_parse(args: list) -> dict:
    arg_name = ""
    arg_dict = {"": []}
    for each in args:  # 解析参数
        if each.startswith("-"):
            if len(each) > 2 and each[1] == "-":
                arg_name = each[2:]
            else:
                arg_name = each[1:]
        else:
            if arg_name == "":
                arg_dict[""].append(value_translation(each))
            elif arg_name in arg_dict:
                arg_dict[arg_name] = "%s %s" % (arg_dict[arg_name], each)
            else:
                arg_dict[arg_name] = value_translation(each)
    if (not len(arg_dict[""])):
        del arg_dict[""]
    return arg_dict


def sys_exit():
    print('\n' + gget("leave_message"))
    _exit(0)


def loop_main():
    """
    run_loop main function
    """
    gpf = gget("general.pf")
    api = gget("api")
    old_namespace = ''
    while gget("loop"):
        namespace = gget("namespace")
        tpf = None
        npf = gget(f"{namespace}.pf")
        if (namespace != old_namespace):
            wordlist = gget(namespace + ".wordlist")
            prefix_wordlist = gget(namespace + ".prefix_wordlist")
            readline.set_wordlist(wordlist)
            readline.set_prefix_wordlist(prefix_wordlist)
        # --------------------------------------
        print(gget(f"{namespace}.prompt"), end="")
        cmd = readline()
        if (not cmd):
            continue
        args = cmd.split(" ")  # 切割
        if " " in cmd:  # 输入的命令
            order = args[0]
        else:
            order = cmd
        del args[0]
        order = order_alias(order)  # 解析别名
        # --------------------------------------
        if order in npf:  # 命令存在
            tpf = npf
        elif order in gpf:
            tpf = gpf
        elif cmd:
            print("[Error] %s: Command Not Found" % order)
        if tpf:
            try:
                arg_dict = args_parse(args)  # 解析参数
                tpf[order].run(**arg_dict)
            except TypeError as e:
                print("[TypeError] %s" % str(e).replace(
                    "%s()" % api, "%s()" % order))
            except Exception as e:
                exc_type, exc_value, exc_tb = exc_info()
                if 0:
                    print_exception(exc_type, exc_value, exc_tb)
                print("[%s] %s" % (exc_type.__name__, e))


def run_loop(loop_init_object: Loop_init, leave_message: str = "Bye!"):
    """
    run_loop

    Args:
        loop_init_object (Loop_init): Loop Init class
        leave_message (str, optional): The message when you leave. Defaults to 'Bye!'.
    """
    from threading import Thread
    from time import sleep

    set_namespace("main")
    gset("leave_message", leave_message)
    t = Thread(target=loop_main)
    t.setDaemon(True)
    t.start()
    while gget("loop"):
        try:
            sleep(10)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
    sys_exit()
