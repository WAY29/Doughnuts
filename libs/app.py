import json
from os import _exit
from re import compile as re_compile
from sys import exc_info, path, stdout
from traceback import print_exception

from Myplugin import Platform

from .config import gget, gset, order_alias, set_namespace

NUMBER_PATTERN = re_compile(r"^[-+]?\d*(\.?\d+|)$")
STDIN_STREAM = b''

"""
api ['']
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


def _find_getch():
    try:
        import termios
    except ImportError:
        import msvcrt
        return msvcrt.getch

    import sys, tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch


def getline():
    global STDIN_STREAM
    cmd = ''
    while 1:
        ch = _find_getch()()
        try:
            dch = ch.decode()
        except UnicodeDecodeError:
            continue
        if (32 <= ord(dch) <= 127):
            stdout.write(dch)
            stdout.flush()
            STDIN_STREAM += ch
        elif(ch == b'\r' or ch == b'\n'):
            stdout.write('\n')
            stdout.flush()
            cmd = STDIN_STREAM.decode()
            STDIN_STREAM = b''
            break
        elif(ord(dch) == 8 and len(STDIN_STREAM) > 0):
            stdout.write('\b \b')
            stdout.flush()
            STDIN_STREAM = STDIN_STREAM[:-1]
        elif(ord(dch) == 4):
            STDIN_STREAM = b''
            print("quit\n", end="")
            cmd = 'quit'
            break
        elif(ord(dch) == 3):
            stdout.write('^C\n')
            stdout.flush()
            STDIN_STREAM = b''
            break
    return cmd


def sys_exit():
    print('\n' + gget("leave_message"))
    _exit(0)


def loop_main():
    """
    run_loop main function

    Args:
        api (str, optional): The name of the entry function that is common to all plugins. Defaults to 'run'.
        prompt (str, optional): Command Prompt. Defaults to ':>'.
    """
    gpf = gget("general.pf")
    tpf = None
    api = gget("api")
    while gget("loop"):
        namespace = gget("namespace")
        npf = gget(f"{namespace}.pf")
        # --------------------------------------
        print(gget(f"{namespace}.prompt"), end="")
        cmd = getline()
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
    gset("leave_message", leave_message)
    t = Thread(target=loop_main)
    t.setDaemon(True)
    t.start()
    while gget("loop"):
        try:
            sleep(10)
        except (KeyboardInterrupt, EOFError):
            break
    sys_exit()
