'''
@Description: command-function: whoami
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
'''
from libs.config import alias, set_namespace


# ? alias装饰器第一个参数为none_named_arg(true/FALSE),True即把没有参数名时传入的参数值顺序传入
@alias(func_alias="b")
def run():
    """
    back

    Back to main menu
    """
    set_namespace("main")
