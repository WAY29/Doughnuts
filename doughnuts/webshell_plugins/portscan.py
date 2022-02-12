from libs.config import alias, color
from libs.myapp import send
from libs.functions.webshell_plugins.portscan import get_php_portscan


def get_php(type, ip, ports, timeout):
    return get_php_portscan() % (type, ip, ports, timeout)


def human_friendly_list_print(l: list) -> str:
    str_dict = {}
    for i in l:
        if (isinstance(i, int)):
            if ((i - 1) in str_dict):
                temp = str_dict[(i - 1)]
                del str_dict[(i - 1)]
                str_dict[i] = temp.split("-")[0] + "-" + str(i)
            else:
                str_dict[i] = str(i)
    return " ".join(str_dict.values())


@alias(True, _type="OTHER", t="type", p="ports", to="timeout")
def run(ip: str, ports: str, _type: int = 2, timeout: float = 0.5):
    """
    portscan

    Scan intranet ports.

    eg: portscan {ip} {ports} {_type=[socket|file_get_contents|curl]{1|2|3},default = 2} {timeout=0.5}
    """
    if (_type not in [1, 2, 3]):
        print(color.red("\nType error!\n"))
        return
    php = get_php(_type, ip, ports, timeout)
    res = send(php)
    if (not res):
        return
    port_result = res.r_json()
    # ------------------------------------------
    if(len(port_result[0])):
        print(color.green('Open') + ' port:\n' + " " *
              4 + human_friendly_list_print(sorted(port_result[0])) + '\n')
    if(len(port_result[1])):
        print(color.red('Close') + ' port:\n' + " " *
              4 + human_friendly_list_print(sorted(port_result[1])) + '\n')
    if (len(port_result[2])):
        print(color.magenta('Timeout') + ' port:\n' + " " *
              4 + human_friendly_list_print(sorted(port_result[2])) + '\n')
    print("")
