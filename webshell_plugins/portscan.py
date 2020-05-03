from libs.config import alias, color
from libs.myapp import send, base64_encode


def get_php(type, ip, ports, timeout):
    return base64_encode("""
# gettime_
function microtime_float()
{
    list($usec, $sec) = explode(" ", microtime());
    return ((float)$usec + (float)$sec);
}
function Scan($type,$ip,$ports,$timeout){
    try{
        $result = array();
        #socket_
        if($type == 1){
            foreach($ports as $port){
                $tmp_=microtime_float();
                $sock = @fsockopen($ip,$port,$errno,$errstr,$timeout);
                $sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
                socket_set_nonblock($sock);
                socket_connect($sock,$ip, $port);
                socket_set_block($sock);
                   $return = @socket_select($r = array($sock), $w = array($sock), $f = array($sock), 3);
                socket_close($sock);
                if(microtime_float() - $tmp_ < $timeout and $return != 0){
                    if($return == 1)
                        array_push($result,'Open');
                    if($return == 2)
                        array_push($result,'Close');
                }else{
                    array_push($result,'Timeout');
                }
            }
        }
        #file_get_contents_
        if($type == 2){
            foreach($ports as $port){
                $url='http://'.$ip;
                $opts=array(
                    'http'=>array(
                        'method' => 'GET',
                        'timeout' => $timeout
                    )
                );
                $context=stream_context_create($opts);
                if(@file_get_contents($url.':'.$port,false,$context)){
                    array_push($result,'Open');
                }else{
                    array_push($result,'Timeout');
                }
            }
        }
        #curl_
        if($type == 3){
            $url='http://'.$ip;
            $ch=curl_init();
            foreach($ports as $port){
                curl_setopt($ch,CURLOPT_URL,$url.':'.$port);
                curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
                curl_setopt($ch,CURLOPT_CONNECTTIMEOUT,$timeout);
                $exec=curl_exec($ch);
                if($exec){
                    array_push($result,'Open');
                }else{
                    array_push($result,'Timeout');
                }
            }
        }
        foreach($result as $k => $v){
            echo '['.$ports[$k].'] => ['.$v."]\n";
        }
    }
    catch (customException $e){
        die("");
    }

}


$type = %d;
$ip = "%s";
$ports = explode(",","%s");
$timeout = %f;

# port_range
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

Scan($type,$ip,$new_ports,$timeout);
""" % (type, ip, ports, timeout))


@alias(True, func_alias="ps", t="type", p="ports", to="timeout")
def run(ip: str, ports: str, type: int = 2, timeout: float = 0.5):
    """
    portscan

    Scan intranet ports
    """
    php = get_php(type, ip, ports, timeout)
    text = send(f'eval(base64_decode("{php}"));').r_text
    ports = str(ports)
    split_ports = ports.split(",")
    all_ports = set()
    for each in split_ports:
        if ("-" in each):
            each_list = each.split("-")
            start_port, end_port = each_list[0], each_list[1]
            all_ports = all_ports | set(
                range(int(start_port), int(end_port) + 1))
        else:
            all_ports.add(int(each.strip()))
    if ('' in all_ports):
        all_ports.remove('')
    # ------------------------------------------
    try:
        port_data = set(text.strip().split("\n"))
        port_dict = {}
        data = [line.split('=>') for line in port_data]
        [port_dict.update({port: status}) for port, status in
            zip((line[0].strip() for line in data), (line[1].strip() for line in data))].clear()
        print(f"\n{color.green(ip)} [{color.yellow(str(ports))}] :\n")
        port_result = [[], [], []]
        port_format = {'[Open]': 0, '[Close]': 1, '[Timeout]': 2}
        [port_result[port_format[value]].append(
            int(key[1:-1])) if value in port_format.keys() else None for key, value in port_dict.items()].clear()

        if(len(port_result[0])):
            print(color.green('Open') + ' port:\n' + " " *
                  4 + " ".join(str(port) for port in sorted(port_result[0])) + '\n')
        if(len(port_result[1])):
            print(color.red('Close') + ' port:\n' + " " *
                  4 + " ".join(str(port) for port in sorted(port_result[1])) + '\n')
        if (len(port_result[2])):
            print(color.magenta('Timeout') + ' port:\n' + " " *
                  4 + " ".join(str(port) for port in sorted(port_result[2])) + '\n')
        print("")
    except Exception:
        print("PortScan error.")
