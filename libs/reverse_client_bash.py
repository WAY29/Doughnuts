import socket
import sys
import tty
import termios
from os import popen
from sys import stdout
import _thread as thread
from libs.config import is_windows


class _GetchUnix:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


getch = _GetchUnix()
FD = None
OLD_SETTINGS = None
CONN = None
CONNECTED = 0
CONN_ONLINE = 1
CLOSED = 0
STDOUT = stdout.buffer


def stdprint(message):
    stdout.write(message)
    stdout.flush()


def close_socket():
    import os
    global FD, OLD_SETTINGS, CONN_ONLINE, CLOSED, CONN
    if (CLOSED):
        return
    CLOSED = 1
    CONN_ONLINE = 0
    CONN.close()
    try:
        if (CONNECTED):
            termios.tcsetattr(FD, termios.TCSADRAIN, OLD_SETTINGS)
    except Exception:
        pass
    os.system("clear")
    os.system("reset")


def recv_daemon(conn):
    global CONN_ONLINE
    while CONN_ONLINE:
        try:
            tmp = conn.recv(16)
            if (tmp):
                STDOUT.write(tmp)
                stdout.flush()
            else:
                raise socket.error
        except socket.error:
            stdprint("Connection close by socket.\n")
            conn.close()
            CONN_ONLINE = 0
            close_socket()


def main(port):
    global CONN, CONNECTED
    CONN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CONN.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    CONN.settimeout(30.0)
    reset = True
    try:
        CONN.bind(('0.0.0.0', port))
        CONN.listen(1)
    except socket.error:
        return False
    try:
        rows, columns = popen('stty size', 'r').read().strip().split(" ")
        term = popen('printf $TERM').read()
    except Exception:
        reset = False
    try:
        talk, addr = CONN.accept()
        CONNECTED = 1
        stdprint("Connect from %s.\n" % addr[0])
        thread.start_new_thread(recv_daemon, (talk,))
        # talk.send(bytes("""python -c "__import__('pty').spawn('/bin/sh')" && exit\n""", encoding='utf-8'))
        if (reset):
            talk.send(bytes("""stty rows %s columns %s\n""" %
                            (rows, columns), encoding='utf-8'))
            talk.send(bytes("""reset -s %s\n""" % term, encoding='utf-8'))
            talk.send(bytes("""PS1='[\\u@\\h \\W]\\$ '\n""", encoding='utf-8'))
            # talk.send(bytes(r"""PS1="[\u@\h \W]\$"\n""" % term, encoding='utf-8'))
        while CONN_ONLINE:
            c = getch()
            if c:
                try:
                    talk.send(bytes(c, encoding='utf-8'))
                except socket.error:
                    break
    except KeyboardInterrupt:
        pass
    except socket.timeout:
        stdprint("Connection timeout...\n")
    finally:
        stdprint("Connection close...\n")
        close_socket()
        return True
