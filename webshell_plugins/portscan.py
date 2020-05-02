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
    }else{
        echo $port." ";
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
    ports = str(ports)
    split_ports = ports.split(",")
    all_ports = set()
    for each in split_ports:
        if ("-" in each):
            each_list = each.split("-")
            start_port, end_port = each_list[0], each_list[1]
            all_ports = all_ports | set(range(int(start_port), int(end_port) + 1))
        else:
            all_ports.add(int(each))
    if ('' in all_ports):
        all_ports.remove('')
    # ------------------------------------------
    try:
        open_port = set(text.split(" "))
        open_port.remove('')
        open_port = set(int(x) for x in open_port)
        close_port = list(all_ports - open_port)
        close_port.sort()
        print(f"\n{color.green(ip)} [{color.yellow(str(ports))}] :\n")
        if (len(open_port)):
            print(f"""{color.green("Open")} port:""")
            print(" " * 4 + text + "\n")
        if (len(close_port)):
            print(f"""{color.red("Close")} port:""")
            print(" " * 4 + " ".join(str(x) for x in close_port) + "\n")
    except Exception:
        print("PortScan error.")
