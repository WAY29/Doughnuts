"""
@Description: alias config
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-03-02 18:33:01
@LastEditTime: 2020-03-03 10:05:29
"""

import functools
from typing import Any

from colorama import Back, Fore, init

GLOBAL_DICT = {}
NAMESPACE_CALLBACK_LIST = []


def gget(key, namespace: str = "") -> Any:
    if (namespace not in GLOBAL_DICT):
        return None
    return GLOBAL_DICT[namespace].get(key, None)


def gset(key, value, force=False, namespace: str = "") -> bool:
    if namespace not in GLOBAL_DICT:
        GLOBAL_DICT[namespace] = {}
    if key not in GLOBAL_DICT or (key in GLOBAL_DICT and force):
        GLOBAL_DICT[namespace][key] = value
        return True
    return False


def is_windows():
    return gget("webshell.os", "webshell")


def conver_args(arg_dict: dict, arg_name_dict: dict) -> dict:  # 别名转换
    for k, v in arg_dict.items():
        if k in arg_name_dict:
            arg_dict[arg_name_dict[k]] = v
            del arg_dict[k]
    return arg_dict


def set_namespace(namespace: str = "main") -> None:  # 改变名称空间
    gset("namespace", namespace, True)
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
    if order in func_alias_dict:
        return func_alias_dict[order]
    return order


def alias(none_named_arg: bool = False, func_alias: str = "", **alias):  # 别名装饰器
    def decorator(func):
        folders_namespace = gget("folders_namespace")
        reverse_alias = {v: k for k, v in alias.items()}
        func_folder, func_name = func.__module__.split(".")
        gset(
            "%s.reverse_alias" % func_name,
            reverse_alias,
            namespace=folders_namespace[func_folder],
        )
        if len(func_alias):
            func_alias_dict = gget("order_alias", namespace=folders_namespace[func_folder])
            if not func_alias_dict:
                func_alias_dict = {}
                gset("order_alias", func_alias_dict, namespace=folders_namespace[func_folder])
            func_alias_dict[func_alias] = func_name

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
