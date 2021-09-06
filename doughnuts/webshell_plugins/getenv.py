from libs.config import alias
from libs.myapp import send, get_ini_value_code


def get_php(varname: str):
    return """
%s
print(@get_ini_value('%s'));
""" % (get_ini_value_code(), varname)


@alias(True, func_alias="env", _type="COMMON", v="varname")
def run(varname: str):
    """
    getenv

    print PHP environment variables.
    """
    res = send(get_php(varname))
    result = "None" if not res.r_text else res.r_text
    if (not res):
        return
    print(f"\n{varname}:{result}\n")
