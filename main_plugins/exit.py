"""
@Description: command-function: exit
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from libs.config import alias, gset
import os


# ? alias装饰器第一个参数为none_named_arg(true/FALSE),True即把没有参数名时传入的参数值顺序传入
# ? alias装饰器第e二个参数为该命令的别名,如设置"w"为whoami的别名
@alias(True, "quit")
def run():
    """
    exit

    Quit this program
    """
    gset("loop", False, True)
    os.kill(os.getpid(), 0)
