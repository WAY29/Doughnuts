import json
from re import compile as re_compile
from sys import exc_info, path
from traceback import print_exception

from Myplugin import Platform
from .config import gset, gget, order_alias, set_namespace

NUMBER_PATTERN = re_compile(r"^[-+]?\d*(\.?\d+|)$")

"""
namespace ['']
api ['']
{platform}.pf ['']
{platform}.prompt ['']
{module_name}.reverse_alias [namespace]
order_alias [namespace]
特殊插件平台:general 存放通用命令
特殊插件平台:encode 存放传输数据的编码命令
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
        gset("namespace", init_namespace)
        gset("root_path", path[0])
        gset("namespace_folders",  platforms)
        gset("folders_namespace", {v: k for k, v in platforms.items()})
        for k, v in platforms.items():
            gset(k + ".pf", import_platform(v, api))
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


def multi_input(prompt: str = "Multi:>"):
    result = ""
    data = input(prompt)
    stop = 0
    while gget("loop"):
        if data != "":
            result += data + "\n"
            stop = 0
        else:
            stop += 1
            result += "\n"
            if stop == 2:
                break
        data = input(" %s " % ("·" * (len(prompt) - 2)))
    return result.strip()


def loop_main():
    """
    run_loop main function

    Args:
        api (str, optional): The name of the entry function that is common to all plugins. Defaults to 'run'.
        prompt (str, optional): Command Prompt. Defaults to ':>'.
    """
    while gget("loop"):
        namespace = gget("namespace")
        npf = gget(f"{namespace}.pf")
        gpf = gget("general.pf")
        tpf = None
        api = gget("api")
        # --------------------------------------
        try:
            cmd = input(gget(f"{namespace}.prompt"))
        except (KeyboardInterrupt, EOFError):
            break
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
                print("[TypeError] %s" % str(e).replace("%s()" % api, "%s()" % order))
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
    t = Thread(target=loop_main)
    t.setDaemon(True)
    t.start()
    while gget("loop"):
        try:
            sleep(10)
        except (KeyboardInterrupt, EOFError):
            break
    print("\n%s" % leave_message)
