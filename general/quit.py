from libs.config import alias, gset
from libs.app import sys_exit


# ? alias装饰器第一个参数为none_named_arg(true/FALSE),True即把没有参数名时传入的参数值顺序传入
# ? alias装饰器第e二个参数为该命令的别名,如设置"w"为whoami的别名
@alias(True, func_alias="q")
def run():
    """
    exit

    Quit this program.
    """
    gset("loop", False, True)
    sys_exit()
