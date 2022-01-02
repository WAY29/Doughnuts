import json
import shlex
from os import _exit, chdir, getcwd
from re import compile as re_compile
from re import findall, match
from sys import exc_info, path
from traceback import print_exception

from libs.config import custom_get, gget, gset, order_alias, set_namespace, color
from libs.readline import LovelyReadline
from Myplugin import Platform

NUMBER_PATTERN = re_compile(r"^[-+]?\d*(\.?\d+|)$")
STDIN_STREAM = b''
HISTORY = None
HISTORY_POINTER = 0
FROM_HISTORY = False
readline = LovelyReadline()
readline.init({}, {})

"""
api ['main']
history_commands ['main']
leave_message ['main']
namespace ['main']
namespace_folders ['main']
folders_namespace ['main']
root_path ['main']
{platform}.pf ['main']
{platform}.prompt ['main']

{plugin_name}.reverse_alias [namespace]
order_alias [namespace]
special plugin platform:general   general commands
special plugin platform:encode    Encoders
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
        gset("namespace_folders", platforms)
        gset("folders_namespace", {v: k for k, v in platforms.items()})
        root_path = gget("root_path")
        cwd = getcwd()
        chdir(root_path)
        # {平台名称 -> 插件路径}
        for k, v in platforms.items():
            pf = import_platform(v, api)
            gset(k + ".pf", pf)
            # 平台 -> 命令列表
            gset(k + ".wordlist", {"command_wordlist": list(pf.names())})
            # 平台 -> {命令名称 -> [命令参数,]}
            gset(k + ".prefix_wordlist", {command: gget(command + ".arg_wordlist", k)
                                          for command in gget(k + ".wordlist")["command_wordlist"]})
        general_wordlist = gget("general.wordlist")["command_wordlist"]
        for k in platforms.keys():  # 往其他插件平台添加general平台的命令列表
            if (k == "general"):
                continue
            wordlist = gget(k + ".wordlist")
            wordlist["command_wordlist"] += general_wordlist
        # 设置输入提示符
        for k, v in self.set_prompts().items():
            gset(k + ".prompt", v)
        chdir(cwd)

    def set_platforms(self) -> dict:
        return {"main": "main_plugins"}

    def set_prompts(self) -> dict:
        return {"main": ":>"}


def import_platform(platform_path: str, api: str):
    return Platform(platform_path, api, message=True)


def is_numberic(string):
    global NUMBER_PATTERN
    return True if (len(string) and (isinstance(
        string, (int, float)) or NUMBER_PATTERN.match(string))) else False


def value_translation(arg):
    if is_numberic(arg):
        arg = float(arg) if "." in arg else int(arg)
    else:
        try:
            arg = json.loads(arg)
        except json.JSONDecodeError:
            pass
        if (isinstance(arg, str)):
            custom_vars = findall("#{(\\w+)}", arg)
            if (match("#{(\\w+)}", arg)):
                arg = custom_get(custom_vars[0], arg)
            else:
                if (not custom_vars):
                    return arg
                for var in custom_vars:
                    arg = arg.replace("#{%s}" % var, custom_get(var, ''))
    return arg


def args_parse(args: list) -> dict:
    arg_name = ""
    arg_dict = {"": []}
    for each in args:  # 解析参数
        if each.startswith("-"):
            if len(each) > 2 and each[1] == "-":
                arg_name = each[2:]
            elif (is_numberic(each)):
                arg_dict[""].append(value_translation(each))
            else:
                arg_name = each[1:]
            arg_dict[arg_name] = True
        else:
            if arg_name == "":
                arg_dict[""].append(value_translation(each))
            elif arg_name in arg_dict:
                if (arg_dict[arg_name] is True):
                    arg_dict[arg_name] = value_translation(each)
                else:
                    arg_dict[arg_name] = f"{arg_dict[arg_name]} {value_translation(each)}"
            else:
                arg_dict[arg_name] = value_translation(each)
    if (not len(arg_dict[""])):
        del arg_dict[""]
    return arg_dict


def sys_exit():
    print('\n' + gget("leave_message"))
    if (gget("log_filepath")):
        gget("log_stdout").log.close()
        gget("log_stderr").log.close()
    _exit(0)


def loop_main():
    """
    run_loop main function
    """
    gpf = gget("general.pf")
    api = gget("api")
    old_namespace = ''
    while gget("loop"):
        # 获取当前命名空间
        namespace = gget("namespace")
        tpf = None
        # 获取当前平台
        npf = gget(f"{namespace}.pf")
        # 获取自定义平台
        cpf = gget("custom.pf")
        # 如果跳出当前平台（进入其他平台时）
        if (namespace != old_namespace):
            # 初始化新平台命令列表
            wordlist = gget(namespace + ".wordlist")
            # 初始化新平台{命令名称 -> 命令参数}
            prefix_wordlist = gget(namespace + ".prefix_wordlist")
            # 合并general的参数部分
            prefix_wordlist = {
                **prefix_wordlist,
                **gget("general.prefix_wordlist")}
            # 初始化readline
            readline.set_wordlist(wordlist)
            readline.set_prefix_wordlist(prefix_wordlist)
            # 记录
            old_namespace = namespace
        # --------------------------------------
        # 判断是否有预载命令
        if (gget("preload_command")):
            cmd = gget("preload_command")
            gset("preload_command", None, True)
        else:
            print(gget(f"{namespace}.prompt"), end="", flush=True)
            if (gget("raw_input") is True):
                cmd = input().strip()
            else:
                cmd = readline().strip()
        # 存储输入的命令值
        gset("raw_command", cmd, True)
        # 若输入空值
        if (not cmd):
            continue
        try:
            args = shlex.split(cmd)  # 切割
        except ValueError:
            print(color.red("Invalid command"))
            continue
        # 判断输入的命令值有无参数，获取输入的命令
        if " " in cmd:  # 输入的命令
            order = args[0]
        else:
            order = cmd
        del args[0]
        # 存储输入的命令值的参数
        raw_command_args = " ".join(args)
        gset("raw_command_args", raw_command_args, True)
        order = order_alias(order)  # 解析别名
        # --------------------------------------
        # 判断命令是否存在于[当前平台]/[general]/[自定义平台]
        if order in npf:  # 命令存在
            tpf = npf
        elif order in gpf:
            tpf = gpf
        elif order in cpf:
            tpf = cpf
        elif cmd:
            print(f'\n{order}: {color.red("Command Not Found")}\n')

        if tpf:
            debug = gget("DEBUG.LOOP")
            try:
                arg_dict = args_parse(args)  # 解析参数
                tpf[order].run(**arg_dict)
            except TypeError as e:
                exc_type, exc_value, exc_tb = exc_info()
                print(
                    "[TypeError] %s" %
                    str(e).replace(
                        "%s()" %
                        api,
                        "%s()" %
                        order))
                if debug:
                    print_exception(exc_type, exc_value, exc_tb)
            except Exception as e:
                exc_type, exc_value, exc_tb = exc_info()
                print("[%s] %s" % (exc_type.__name__, e))
                if debug:
                    print_exception(exc_type, exc_value, exc_tb)


def run_loop(loop_init_object: Loop_init, leave_message: str = "Bye!"):
    """
    run_loop

    Args:
        loop_init_object (Loop_init): Loop Init class
        leave_message (str, optional): The message when you leave. Defaults to 'Bye!'.
    """
    from threading import Thread
    from time import sleep

    set_namespace("main", callback=False if gget("preload_command") else True)
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
