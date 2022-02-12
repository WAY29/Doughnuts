from libs.config import alias, color
from libs.myapp import send, base64_decode
from libs.functions.webshell_plugins.agent import get_php_agent
from re import findall, I, M
from os import makedirs, urandom
from os.path import dirname, exists
from time import time


@alias(True, _type="OTHER", func_alias="ag", u="url", m="method", d="data", p="params", c="cookie", t="type",
       to="timeout", re_m="redirect_method")
def run(url: str, method: str,
        data: str = '', params: str = '', cookie: str = '', type: int = 1, timeout: float = 3,
        redirect_method: str = "POST", redirect_auto: int = 1, redirect_cookie_use: int = 1, create_dir: int = 0):
    """
    agent

    Lightweight intranet browsing.

    eg: agent {url} {method} {data=''} {params=''} {cookie=''} {type=[socket|file_get_contents|curl]{1|2|3},default = 1} {timeout=3} {redirect_method=POST} {redirect_auto=1} {redirect_cookie_use=1} {create_dir=0}
    """

    php = get_php_agent(
        url,
        method.upper(), redirect_method.upper(),
        data, params, cookie,
        redirect_auto, redirect_cookie_use, timeout, type
    )
    res = send(php)
    if (not res):
        return
    text = res.r_text

    # ------------------------------------------

    try:

        current_status = findall(
            '<CurrentStatus>(.*)</CurrentStatus>', text, I + M)
        assert len(current_status), "Can't get status```"
        current_status = current_status[0]

        current_url = findall('<CurrentUrl>(.*)</CurrentUrl>', text, I + M)
        current_url = base64_decode(current_url[0]) if len(current_url) else ''

        current_cookie = findall(
            '<CurrentCookie>(.*)</CurrentCookie>', text, I + M)
        current_cookie = base64_decode(
            current_cookie[0]) if len(current_cookie) else ''

        current_header = findall(
            '<CurrentHeader>(.*)</CurrentHeader>', text, I + M)
        current_header = "\n    ".join(base64_decode(line) for line in current_header[0].split("|")) if len(
            current_header) else ''

        if (current_status == "success"):
            print(color.magenta("Current Url: ") +
                  color.cyan(current_url) + "\n")
            print(color.blue("Response Headers: \n\n") +
                  " " * 4 + color.white(current_header))
            print(color.blue("Cookie: \n\n") + " " *
                  4 + color.red(current_cookie) + "\n")
            print(color.yellow("*" * 20 + " Body " + "*" * 20) + "\n\n")
            print(color.cyan(text) + "\n\n")
            print(color.yellow("*" * 20 + " END " + "*" * 21) + "\n\n")
            if (create_dir == 1):
                dir_path = dirname(current_url.split("//", maxsplit=1)[1])
                dir_path = dir_path.replace(":", "-")
                dir_path = dir_path.replace('.', "_")
                file_name = "".join(hex(each)[2:].zfill(
                    2) for each in urandom(20)) + "_" + str(time()) + '.html'

                if(not exists(dir_path)):
                    makedirs(dir_path)

                method = "w"
                try:
                    contents = text.encode()
                    method = "wb"
                except Exception:
                    contents = text

                with open(dir_path + "/" + file_name, method) as out_file:
                    out_file.write(contents)

                print(color.blue("Outfile: ") +
                      color.cyan(dir_path + "/" + file_name) + "\n\n")

    except Exception as e:
        print("Agent error.", e)
