from libs.config import alias, gset, gget, color
from libs.myapp import Session


@alias(True, p="proxy_url")
def run(proxy_url: str = ""):
    """
    proxy

    Set proxy for requests, Support socks and http, Set None to unset.

    eg: proxy {proxy_url='http://127.0.0.1:10808'}
    """
    if (proxy_url == ""):
        print("\n" + color.green(f"Current proxy: {gget('proxy_url', 'webshell')}") + "\n")
    else:
        if (proxy_url.lower() == "none"):
            proxy_url = None
        Session.proxies = {'http': proxy_url, 'https': proxy_url}
        print("\n" + color.green(f"Set proxy: proxy {proxy_url}") + "\n")
        gset("proxy_url", proxy_url, True, namespace="webshell")
