# LICENSE https://github.com/L-codes/Neo-reGeorg/blob/master/LICENSE
from threading import Thread
from itertools import chain
from socket import *
from datetime import datetime
from time import sleep, time, mktime
import codecs
import uuid
import requests
import hashlib
import random
import struct
import base64
import re
import os
import sys

requests.packages.urllib3.disable_warnings()

ROOT = os.path.dirname(os.path.realpath(__file__))

# Constants
SOCKTIMEOUT = 5
VER = b"\x05"
METHOD = b"\x00"
SUCCESS = b"\x00"
REFUSED = b"\x05"

# Globals
READBUFSIZE = 7
MAXTHERADS = 1000
READINTERVAL = 300
WRITEINTERVAL = 200
READBUF = 513
MAXREADSIZE = 512
LOCALDNS = False
BASE64CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
M_BASE64CHARS = ""
HEADERS = {}
K = {}
V = {}
rV = {}
EncodeMap = {}
DecodeMap = {}
PROXY = {}
INIT_COOKIE = ""
BASICCHECKSTRING = b""
CPATH = os.path.split(os.path.realpath(__file__))[0]


class SocksCmdNotImplemented(Exception):
    pass


class Rand:
    def __init__(self, key):
        n = int(hashlib.sha512(key.encode()).hexdigest(), 16)
        self.k_clist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.v_clist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
        self.k_clen = len(self.k_clist)
        self.v_clen = len(self.v_clist)
        random.seed(n)

    def header_key(self):
        str_len = random.getrandbits(4) + 2  # len 2 to 17
        return ''.join([self.k_clist[random.getrandbits(10) % self.k_clen]
                       for _ in range(str_len)]).capitalize()

    def header_value(self):
        str_len = random.getrandbits(6) + 2  # len 2 to 65
        return ''.join([self.v_clist[random.getrandbits(10) %
                       self.v_clen] for _ in range(str_len)])

    def base64_chars(self, charslist):
        newshuffle = random.shuffle
        newshuffle(charslist)


class session(Thread):
    def __init__(self, conn, pSocket, connectURLs, redirectURLs, FwdTarget):
        Thread.__init__(self)
        self.pSocket = pSocket
        self.connectURLs = connectURLs
        self.redirectURLs = redirectURLs
        self.conn = conn
        self.connect_closed = False
        self.session_connected = False
        self.fwd_target = FwdTarget

    def url_sample(self):
        return random.choice(self.connectURLs)

    def redirect_url_sample(self):
        return random.choice(self.redirectURLs)

    def headerupdate(self, headers):
        headers.update(HEADERS)
        if self.redirectURLs:
            headers[K['X-REDIRECTURL']] = self.redirect_url_sample()

    def session_mark(self):
        mark = base64.b64encode(uuid.uuid4().bytes)[0:-2]
        mark = mark.decode()
        mark = mark.replace('+', ' ').replace('/', '_')
        mark = re.sub('^[ _]| $', 'L', mark)
        return mark

    def parseSocks5(self, sock):
        nmethods = sock.recv(1)
        methods = sock.recv(ord(nmethods))
        sock.sendall(VER + METHOD)
        ver = sock.recv(1)
        if ver == b"\x02":                # this is a hack for proxychains
            ver, cmd, rsv, atyp = (sock.recv(1), sock.recv(
                1), sock.recv(1), sock.recv(1))
        else:
            cmd, rsv, atyp = (sock.recv(1), sock.recv(1), sock.recv(1))
        target = None
        targetPort = None
        if atyp == b"\x01":      # IPv4
            target = sock.recv(4)
            targetPort = sock.recv(2)
            target = inet_ntoa(target)
        elif atyp == b"\x03":             # Hostname
            targetLen = ord(sock.recv(1))  # hostname length (1 byte)
            target = sock.recv(targetLen)
            targetPort = sock.recv(2)
            if LOCALDNS:
                try:
                    target = gethostbyname(target)
                except Exception:
                    return False
            else:
                target = target.decode()
        elif atyp == b"\x04":    # IPv6
            target = sock.recv(16)
            targetPort = sock.recv(2)
            target = inet_ntop(AF_INET6, target)

        if targetPort is None:
            return False

        targetPortNum = struct.unpack('>H', targetPort)[0]

        if cmd == b"\x02":   # BIND
            raise SocksCmdNotImplemented("Socks5 - BIND not implemented")
        elif cmd == b"\x03":  # UDP
            raise SocksCmdNotImplemented("Socks5 - UDP not implemented")
        elif cmd == b"\x01":  # CONNECT
            try:
                serverIp = inet_aton(target)
            except Exception:
                # Forged temporary address 127.0.0.1
                serverIp = inet_aton('127.0.0.1')
            mark = self.setupRemoteSession(target, targetPortNum)
            if mark:
                sock.sendall(VER + SUCCESS + b"\x00" +
                             b"\x01" + serverIp + targetPort)
                return True
            else:
                sock.sendall(VER + REFUSED + b"\x00" +
                             b"\x01" + serverIp + targetPort)
                return False

        raise SocksCmdNotImplemented("Socks5 - Unknown CMD")

    def handleSocks(self, sock):
        try:
            ver = sock.recv(1)
            if ver == b"\x05":
                res = self.parseSocks5(sock)
                if not res:
                    sock.close()
                return res
            elif ver == b'':
                ...
            else:
                return False
        except OSError:
            return False
        except timeout:
            return False

    def handleFwd(self, sock):
        host, port = self.fwd_target.split(':', 1)
        mark = self.setupRemoteSession(host, int(port))
        return bool(mark)

    def error_log(self, str_format, headers):
        if K['X-ERROR'] in headers:
            message = headers[K["X-ERROR"]]
            if message in rV:
                message = rV[message]
            # log.error(str_format.format(repr(message)))

    def encode_target(self, data):
        data = base64.b64encode(data)
        data = data.decode()
        return data.translate(EncodeMap)

    def encode_body(self, data):
        data = base64.b64encode(data)
        data = data.decode()
        return data.translate(EncodeMap)

    def decode_body(self, data):
        data = data.decode()
        return base64.b64decode(data.translate(DecodeMap))

    def setupRemoteSession(self, target, port):
        self.mark = self.session_mark()
        target_data = ("%s|%d" % (target, port)).encode()
        headers = {K["X-CMD"]: self.mark + V["CONNECT"],
                   K["X-TARGET"]: self.encode_target(target_data)}
        self.headerupdate(headers)
        self.target = target
        self.port = port

        if '.php' in self.connectURLs[0]:
            try:
                response = self.conn.get(
                    self.url_sample(), headers=headers, timeout=0.5)
            except Exception:
                return self.mark
        else:
            response = self.conn.get(self.url_sample(), headers=headers)

        rep_headers = response.headers
        if K['X-STATUS'] in rep_headers:
            status = rep_headers[K["X-STATUS"]]
            if status == V["OK"]:
                return self.mark
            else:
                self.error_log('[CONNECT] [%s:%d] ERROR: {}' %
                               (self.target, self.port), rep_headers)
                return False
        else:
            return False

    def closeRemoteSession(self):
        try:
            if not self.connect_closed:
                self.connect_closed = True
                try:
                    self.pSocket.close()
                except Exception:
                    if hasattr(self, 'target'):
                        ...
                if hasattr(self, 'mark'):
                    headers = {K["X-CMD"]: self.mark + V["DISCONNECT"]}
                    self.headerupdate(headers)
                    self.conn.get(self.url_sample(), headers=headers)
                if not self.connect_closed:
                    if hasattr(self, 'target'):
                        ...
                    else:
                        ...
        except requests.exceptions.ConnectionError:
            ...

    def reader(self):
        try:
            headers = {K["X-CMD"]: self.mark + V["READ"]}
            self.headerupdate(headers)
            n = 0
            while True:
                try:
                    if self.connect_closed or self.pSocket.fileno() == -1:
                        break
                    response = self.conn.get(
                        self.url_sample(), headers=headers)
                    rep_headers = response.headers
                    if K['X-STATUS'] in rep_headers:
                        status = rep_headers[K["X-STATUS"]]
                        if status == V["OK"]:
                            data = response.content
                            if len(data) == 0:
                                sleep(READINTERVAL)
                                continue
                            else:
                                data = self.decode_body(data)
                        else:
                            msg = "[READ] [%s:%d] HTTP [%d]: Status: [%s]: Message [{}] Shutting down" % (
                                self.target, self.port, response.status_code, rV[status])
                            self.error_log(msg, rep_headers)
                            break
                    else:
                        break

                    if len(data) > 0:
                        n += 1
                        data_len = len(data)
                        while data:
                            writed_size = self.pSocket.send(data)
                            data = data[writed_size:]
                        if data_len < 500:
                            sleep(READINTERVAL)

                except error:  # python2 socket.send error
                    pass
                except requests.exceptions.ConnectionError:
                    ...
                except requests.exceptions.ChunkedEncodingError:  # python2 requests error
                    ...
                except Exception as ex:
                    raise ex
        finally:
            self.closeRemoteSession()

    def writer(self):
        try:
            headers = {K["X-CMD"]: self.mark + V["FORWARD"],
                       'Content-type': 'application/octet-stream'}
            self.headerupdate(headers)
            n = 0
            while True:
                try:
                    raw_data = self.pSocket.recv(READBUFSIZE)
                    if not raw_data:
                        break
                    data = self.encode_body(raw_data)
                    response = self.conn.post(
                        self.url_sample(), headers=headers, data=data, proxies=self.conn.proxies)
                    rep_headers = response.headers
                    if K['X-STATUS'] in rep_headers:
                        status = rep_headers[K["X-STATUS"]]
                        if status != V["OK"]:
                            msg = "[FORWARD] [%s:%d] HTTP [%d]: Status: [%s]: Message [{}] Shutting down" % (
                                self.target, self.port, response.status_code, rV[status])
                            self.error_log(msg, rep_headers)
                            break
                    else:
                        break
                    n += 1
                    if len(raw_data) < READBUFSIZE:
                        sleep(WRITEINTERVAL)
                except timeout:
                    continue
                except error:
                    break
                except OSError:
                    break
                except requests.exceptions.ConnectionError as e:  # python2 socket.send error
                    break
                except Exception as ex:
                    raise ex
                    break
        finally:
            self.closeRemoteSession()

    def run(self):
        try:
            if self.fwd_target:
                self.session_connected = self.handleFwd(self.pSocket)
            else:
                self.session_connected = self.handleSocks(self.pSocket)

            if self.session_connected:
                r = Thread(target=self.reader)
                r.start()
                w = Thread(target=self.writer)
                w.start()
                r.join()
                w.join()
        except SocksCmdNotImplemented:
            ...
        except requests.exceptions.ConnectionError:
            ...
        except Exception as e:
            ...
            raise e
        finally:
            if self.session_connected:
                self.closeRemoteSession()


def askGeorg(conn, connectURLs):
    headers = {}
    headers.update(HEADERS)

    if INIT_COOKIE:
        headers['Cookie'] = INIT_COOKIE

    need_exit = False
    try:
        response = conn.get(connectURLs[0], headers=headers, timeout=10)
        if 'Expires' in response.headers:
            expires = response.headers['Expires']
            try:
                expires_date = datetime.strptime(
                    expires, '%a, %d %b %Y %H:%M:%S %Z')
                if mktime(expires_date.timetuple()) < time():
                    if 'Set-Cookie' in response.headers:
                        cookie = ''
                        for k, v in response.cookies.items():
                            cookie += '{}={};'.format(k, v)
                        HEADERS.update({'Cookie': cookie})
                    else:
                        need_exit = True
            except ValueError:
                ...
    except Exception:
        exit()

    if need_exit:
        exit()

    if BASICCHECKSTRING == response.content.strip():
        return True
    else:
        ...
        # if not args.skip:
        #     if K['X-ERROR'] in response.headers:
        #         message = response.headers[K["X-ERROR"]]
        #         if message in rV:
        #             message = rV[message]
        #     else:
        #         ...
        #     exit()


def generate(httpcode=200, read_buff=513, max_read_size=512):
    global READBUF, MAXREADSIZE, BASE64CHARS, M_BASE64CHARS

    READBUF = read_buff - (read_buff % 3)
    MAXREADSIZE = max_read_size * 1024
    M_BASE64ARRAY = []

    for i in range(128):
        if chr(i) in BASE64CHARS:
            num = M_BASE64CHARS.index(chr(i))
            M_BASE64ARRAY.append(num)
        else:
            M_BASE64ARRAY.append(-1)

    http_get_content = BASICCHECKSTRING.decode()

    filepath = os.path.join(CPATH, "tunnel.php")
    text = file_read(filepath)
    text = text.replace(
        r"Georg says, 'All seems fine'", http_get_content)
    text = re.sub(r"BASE64 CHARSLIST", M_BASE64CHARS, text)

    for k, v in chain(K.items(), V.items()):
        text = re.sub(r'\b%s\b' % k, v, text)

    text = re.sub(r"\bHTTPCODE\b", str(httpcode), text)

    return text


def connectTunnel(url, listen_on, listen_port, local_dns=False, read_buff=7,
                  read_interval=300, write_interval=200, max_threads=1000, proxy=""):
    global LOCALDNS, PROXY, INIT_COOKIE, READBUFSIZE, MAXTHERADS, READINTERVAL, WRITEINTERVAL

    LOCALDNS = local_dns
    USERAGENT = choice_useragent()

    urls = (url, )

    # for header in headers:
    #     if ':' in header:
    #         key, value = header.split(':', 1)
    #         HEADERS[key.strip()] = value.strip()
    #     else:
    #         print("\nError parameter: -H %s" % header)
    #         exit()

    # INIT_COOKIE = args.cookie
    PROXY = {'http': proxy, 'https': proxy} if proxy else None
    print("test", proxy)

    try:
        conn = requests.Session()
        conn.proxies = PROXY
        conn.verify = False
        conn.headers['Accept-Encoding'] = 'gzip, deflate'
        conn.headers['User-Agent'] = USERAGENT

        servSock_start = False
        askGeorg(conn, urls)

        READBUFSIZE = min(read_buff, 50) * 1024
        MAXTHERADS = max_threads
        READINTERVAL = read_interval / 1000.0
        WRITEINTERVAL = write_interval / 1000.0

        try:
            servSock = socket(AF_INET, SOCK_STREAM)
            servSock_start = True
            servSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            servSock.bind((listen_on, listen_port))
            servSock.listen(MAXTHERADS)
        except Exception:
            exit()

        while True:
            try:
                sock, addr_info = servSock.accept()
                sock.settimeout(SOCKTIMEOUT)
                session(conn, sock, urls, None, None).start()
            except KeyboardInterrupt:
                break
            except timeout:
                if sock:
                    sock.close()
            except OSError:
                if sock:
                    sock.close()
            except error:
                pass
            except Exception as e:
                raise e
    except requests.exceptions.ProxyError:
        ...
    except requests.exceptions.ConnectionError:
        ...
    finally:
        print("\nSocks server stop\n")
        if servSock_start:
            servSock.close()


def init(key):
    global EncodeMap, DecodeMap, BASICCHECKSTRING, K, V, rV, BASE64CHARS, M_BASE64CHARS

    rand = Rand(key)

    M_BASE64CHARS = list(BASE64CHARS)
    rand.base64_chars(M_BASE64CHARS)
    M_BASE64CHARS = ''.join(M_BASE64CHARS)

    maketrans = str.maketrans

    EncodeMap = maketrans(BASE64CHARS, M_BASE64CHARS)
    DecodeMap = maketrans(M_BASE64CHARS, BASE64CHARS)
    BASICCHECKSTRING = ('<!-- ' + rand.header_value() + ' -->').encode()

    K = {}
    for name in ["X-STATUS", "X-ERROR", "X-CMD", "X-TARGET", "X-REDIRECTURL"]:
        K[name] = rand.header_key()

    V = {}
    rV = {}

    for name in ["FAIL", "Failed creating socket", "Failed connecting to target", "OK", "Failed writing socket",
                 "CONNECT", "DISCONNECT", "READ", "FORWARD", "Failed reading from socket", "No more running, close now",
                 "POST request read filed", "Intranet forwarding failed"]:
        value = rand.header_value()
        V[name] = value
        rV[value] = name


def choice_useragent():
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/8.0.6 Safari/600.6.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.11 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.11",
        "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:38.0) Gecko/20100101 Firefox/38.0"
    ]
    return random.choice(user_agents)


def file_read(filename):
    with codecs.open(filename, encoding="utf-8") as f:
        return f.read()
