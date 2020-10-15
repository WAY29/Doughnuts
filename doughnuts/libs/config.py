import functools
from typing import Any
from inspect import getfullargspec

from colorama import Back, Fore, init

GLOBAL_DICT = {}
NAMESPACE_CALLBACK_LIST = []


def gget(key, namespace: str = "main", default=None) -> Any:
    if (namespace not in GLOBAL_DICT):
        return None
    return GLOBAL_DICT[namespace].get(key, default)


def gset(key, value, force=False, namespace: str = "main") -> bool:
    if namespace not in GLOBAL_DICT:
        GLOBAL_DICT[namespace] = {}
    if key not in GLOBAL_DICT or (key in GLOBAL_DICT and force):
        GLOBAL_DICT[namespace][key] = value
        return True
    return False


def custom_get(key, default=None) -> Any:
    return gget(key, "custom", default)


def custom_gets() -> Any:
    return GLOBAL_DICT.get("custom", {})


def custom_set(key, value) -> Any:
    return gset(key, value, True, "custom")


def conver_args(arg_dict: dict, arg_name_dict: dict) -> dict:  # 别名转换
    for k, v in arg_dict.items():
        if k in arg_name_dict:
            arg_dict[arg_name_dict[k]] = v
            del arg_dict[k]
    return arg_dict


def set_namespace(namespace: str = "main", callback: bool = True, clean_history: bool = True) -> None:  # 改变名称空间
    gset("namespace", namespace, True)
    if (clean_history):
        gset("history_commands", [], True)
        gset("history_pointer", 0, True)
    if (not callback):
        return
    for func in NAMESPACE_CALLBACK_LIST:
        func()


def set_prompt(prompt: str = ":>", namespace: str = "") -> None:  # 改变名称空间
    namespace = namespace if len(namespace) else gget("namespace")
    gset(f"{namespace}.prompt", prompt, True)


def add_namespace_callback(func):
    NAMESPACE_CALLBACK_LIST.append(func)

    @functools.wraps(func)
    def wrapper(*args, **kw):
        return func(*args, **kw)

    return wrapper


def order_alias(order):
    namespace = gget("namespace")
    func_alias_dict = gget("order_alias", namespace=namespace)
    general_func_alias_dict = gget("order_alias", namespace="general")
    if order in func_alias_dict:
        return func_alias_dict[order]
    elif order in general_func_alias_dict:
        return general_func_alias_dict[order]
    return order


def alias(none_named_arg: bool = False, func_alias: str = "", _type: str = "general", **alias):  # 别名装饰器
    def decorator(func):
        if (not gget("outside")):
            folders_namespace = gget("folders_namespace")
            reverse_alias = {v: k for k, v in alias.items()}
            func_folder, func_name = func.__module__.split(".")
            gset(
                func_name + ".reverse_alias",
                reverse_alias,
                namespace=folders_namespace[func_folder],
            )
            arg_wordlist = ["-" + name for name in alias.keys()] + \
                ["--" + name for name in getfullargspec(func)[0]]
            gset(func_name + ".arg_wordlist", arg_wordlist,
                 namespace=folders_namespace[func_folder])
            if len(func_alias):
                func_alias_dict = gget(
                    "order_alias", namespace=folders_namespace[func_folder])
                if not func_alias_dict:
                    func_alias_dict = {}
                    gset("order_alias", func_alias_dict,
                         namespace=folders_namespace[func_folder])
                func_alias_dict[func_alias] = func_name
            func_type_list = gget(
                "type_list", namespace=folders_namespace[func_folder])
            if not func_type_list:
                func_type_list = []
                gset("type_list", func_type_list,
                        namespace=folders_namespace[func_folder])
            type_func_dict = gget(
                "type_func_dict", namespace=folders_namespace[func_folder])
            if not type_func_dict:
                type_func_dict = {}
                gset("type_func_dict", type_func_dict,
                        namespace=folders_namespace[func_folder])
            if (_type not in func_type_list):
                func_type_list.append(_type)
            if (_type not in type_func_dict):
                type_func_dict[_type] = []
            type_func_dict[_type].append(func_name)
            try:
                short_doc = func.__doc__.split("\n")[3].strip().strip(".")
            except (AttributeError, IndexError):
                short_doc = ''
            command_doc = f"[{func_alias}|{func_name}]" if func_alias else f"[{func_name}]"
            gset(func_name + ".helpdoc", "%-30s%s" % (color.yellow(command_doc),
                                                        color.cyan(short_doc)), namespace=folders_namespace[func_folder])

        @functools.wraps(func)
        def wrapper(*args, **kw):   
            kw = conver_args(kw, alias)
            if "" in kw:
                if none_named_arg:
                    args = tuple(kw[""]) + args
                del kw[""]
            return func(*args, **kw)

        return wrapper

    return decorator


init(autoreset=True)


class Colored(object):

    #  前景色:红色  背景色:默认
    def red(self, s):
        return Fore.RED + s + Fore.RESET

    #  前景色:绿色  背景色:默认
    def green(self, s):
        return Fore.GREEN + s + Fore.RESET

    #  前景色:黄色  背景色:默认
    def yellow(self, s):
        return Fore.YELLOW + s + Fore.RESET

    #  前景色:蓝色  背景色:默认
    def blue(self, s):
        return Fore.BLUE + s + Fore.RESET

    #  前景色:洋红色  背景色:默认
    def magenta(self, s):
        return Fore.MAGENTA + s + Fore.RESET

    #  前景色:青色  背景色:默认
    def cyan(self, s):
        return Fore.CYAN + s + Fore.RESET

    #  前景色:白色  背景色:默认
    def white(self, s):
        return Fore.WHITE + s + Fore.RESET

    #  前景色:黑色  背景色:默认
    def black(self, s):
        return Fore.BLACK

    #  前景色:白色  背景色:绿色
    def white_green(self, s):
        return Fore.WHITE + Back.GREEN + s + Fore.RESET + Back.RESET


color = Colored()
