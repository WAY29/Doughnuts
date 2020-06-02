import json
from os import _exit
from re import compile as re_compile
from sys import exc_info, path, stdout
from traceback import print_exception

from Myplugin import Platform

from .config import gget, gset, order_alias, set_namespace, color

NUMBER_PATTERN = re_compile(r"^[-+]?\d*(\.?\d+|)$")
STDIN_STREAM = b''
HISTORY = None
HISTORY_POINTER = 0
FROM_HISTORY = False

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
            commands = [s.encode() for s in pf.names()]
            gset(k + ".pf", pf)
            gset(k + ".commands", commands)
            gset(k + ".command_number", len(commands))
        for k in platforms.keys():
            gset(k + ".command_number", gget(k + ".command_number") + gget("general.command_number"), True)
        gset("history_commands", gget("general.commands") + gget(f"{init_namespace}.commands"))
        gset("history_pointer", gget(init_namespace + ".command_number"))
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


try:
    # POSIX system: Create and return a getch that manipulates the tty
    import termios
    import sys, tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    #  Read arrow keys correctly
    def getchar():
        firstChar = getch()
        if firstChar == '\x1b':
            return {"[A": "up", "[B": "down", "[C": "right", "[D": "left"}[getch() + getch()]
        else:
            return firstChar.encode()

except ImportError:
    # Non-POSIX: Return msvcrt's (Windows') getch
    from msvcrt import getch

    # Read arrow keys correctly
    def getchar():
        firstChar = getch()
        if firstChar == b'\xe0':
            return {b"H": "up", b"P": "down", b"M": "right", b"K": "left"}[getch()]
        else:
            return firstChar


def getline():
    global STDIN_STREAM, HISTORY, HISTORY_POINTER, FROM_HISTORY
    cmd = ''
    pointer = 0
    history_line = b''
    HISTORY = gget("history_commands")
    HISTORY_POINTER = gget("history_pointer")
    while 1:
        if (history_line):
            old_stream_len = len(history_line)
        else:
            old_stream_len = len(STDIN_STREAM)
        old_pointer = pointer
        try:
            ch = getchar()
        except Exception:
            print(f"\nGetchar error\n")
            cmd = ''
            break
        if (isinstance(ch, bytes)):
            try:
                dch = ch.decode()
            except UnicodeDecodeError:
                continue
        if (isinstance(ch, str)):
            read_history = False
            if (ch == "up" and HISTORY_POINTER > gget(f"{gget('namespace')}.command_number")):  # up
                HISTORY_POINTER -= 1
                read_history = True
            elif (ch == "down" and HISTORY_POINTER < len(HISTORY) - 1):  # down
                HISTORY_POINTER += 1
                read_history = True
            elif (ch == "left" and pointer > 0):  # left
                pointer -= 1
            elif (ch == "right"):  # right
                if (pointer < len(STDIN_STREAM)):
                    pointer += 1
                elif (history_line):
                    STDIN_STREAM = history_line
                    pointer = len(history_line)
            if ((ch == "up" or ch == "down") and read_history):
                STDIN_STREAM = HISTORY[HISTORY_POINTER]
                pointer = len(STDIN_STREAM)
                FROM_HISTORY = True
        elif (32 <= ord(dch) <= 127):
            if (pointer == len(STDIN_STREAM)):
                STDIN_STREAM += ch
            else:
                STDIN_STREAM = STDIN_STREAM[:pointer] + ch + STDIN_STREAM[pointer:]
            if (FROM_HISTORY):
                FROM_HISTORY = False
            pointer += 1
        elif(ch == b'\r' or ch == b'\n'):  # enter
            stdout.write('\n')
            stdout.flush()
            cmd = STDIN_STREAM.decode()
            STDIN_STREAM = b''
            break
        elif(ord(dch) == 8 and pointer > 0):  # \b
            if (pointer == len(STDIN_STREAM)):
                STDIN_STREAM = STDIN_STREAM[:-1]
            else:
                STDIN_STREAM = STDIN_STREAM[:pointer] + STDIN_STREAM[pointer+1:]
            pointer -= 1
        elif(ch == b'\t' and history_line):  # \t
            STDIN_STREAM = history_line
            pointer = len(history_line)
        elif(ord(dch) == 4):  # ctrl+d
            STDIN_STREAM = b''
            print(color.cyan("quit\n"), end="")
            cmd = 'quit'
            break
        elif(ord(dch) == 3):  # ctrl+c
            print(color.cyan('^C'))
            stdout.flush()
            STDIN_STREAM = b''
            break
        stdout.write("\b" * old_pointer + " " * old_stream_len + "\b" * old_stream_len)
        print(color.cyan(STDIN_STREAM.decode()), end="")
        if (history_line):
            history_line = b''
        if (STDIN_STREAM):
            temp_history_lines = [line for line in reversed(HISTORY) if (line.startswith(STDIN_STREAM) and STDIN_STREAM != line)]
            if (len(temp_history_lines)):
                history_line = min(temp_history_lines)
                stdout.write(history_line[len(STDIN_STREAM):].decode() + "\b" * (len(history_line) - len(STDIN_STREAM)))
            stdout.write("\b" * (len(STDIN_STREAM) - pointer))
            stdout.flush()
    if (cmd and not FROM_HISTORY and (not len(HISTORY) or (len(HISTORY) and HISTORY[-1] != cmd.encode()))):
        HISTORY.append(cmd.encode())
    HISTORY_POINTER = len(HISTORY)
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
    api = gget("api")
    while gget("loop"):
        namespace = gget("namespace")
        tpf = None
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
