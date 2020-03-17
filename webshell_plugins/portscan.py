"""
@Description: command-function: whoami
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from libs.config import alias, color
from libs.myapp import send, base64_encode


def get_php(ip, ports, timeout):
    return base64_encode("""
$ports = explode(",","%s");
$new_ports = array();
foreach ($ports as $port){
    if (strpos($port, "-")){
        $ps = explode("-", $port);
        for($i=intval($ps[0]);$i<=intval($ps[1]);$i++){
            array_push($new_ports, $i);
        }
    } else{
        array_push($new_ports, intval($port));
    }
}
foreach ($new_ports as $port) {
    $fp = @fsockopen('%s',$port,$errno,$errstr,%s);
    if (!$fp) {
        echo $port." closed\n";
    }else{
        echo $port." opend\n";
    }
}""" % (ports, ip, timeout))


@alias(True, func_alias="ps", p="ports", t="timeout")
def run(ip: str, ports: str, timeout: float = 0.5):
    """
    portscan

    Scan intranet ports
    """
    php = get_php(ip, ports, timeout)
    text = send(f'eval(base64_decode("{php}"));').r_text
    if len(text):
        text = text.replace("opend", color.green("opend")).replace("closed", color.red("closed"))
        print(f"\n{color.green(ip)} [{color.yellow(str(ports))}] :")
        print("\n" + text + "\n")
    else:
        print(color.red("Portscan error."))
