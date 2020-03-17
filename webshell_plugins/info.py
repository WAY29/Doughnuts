'''
@Description: command-function: whoami
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
'''
from libs.config import alias, set_namespace
from libs.myapp import print_webshell_info


@alias(func_alias="i")
def run():
    """
    info

    Show website information
    """
    print_webshell_info()
    set_namespace("webshell")
