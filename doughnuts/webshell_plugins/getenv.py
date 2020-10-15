from libs.config import color, alias
from libs.myapp import gget, send


@alias(True, func_alias="env", _type="COMMON", v="varname")
def run(varname: str):
    """
    getenv

    print PHP environment variables by ini_get.
    """
    disable_func_list = gget("webshell.disable_functions", "webshell")
    if ("ini_get" in disable_func_list):
        print(color.red("ini_get is disabled"))
    else:
        res = send("print(ini_get('%s'));" % varname)
        result = "None" if not res.r_text else res.r_text
        if (not res):
            return
        print(f"\n{varname}:{result}\n")
