from libs.config import alias, set_namespace
from libs.myapp import clean_trace


# ? alias装饰器第一个参数为none_named_arg(true/FALSE),True即把没有参数名时传入的参数值顺序传入
@alias(func_alias="b", _type="COMMON")
def run():
    """
    back

    Back to main menu.
    """
    clean_trace()
    set_namespace("main")
