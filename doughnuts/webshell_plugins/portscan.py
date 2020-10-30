from libs.config import alias, color
from libs.myapp import send

from pprint import pprint


def get_php(type, ip, ports, timeout):
    return """
# gettime_
function microtime_float()
{
    list($usec, $sec) = explode(" ", microtime());
    return ((float)$usec + (float)$sec);
}
function Scan($type,$ip,$ports,$timeout){
    try{
        $result = array(array(), array(), array());
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
                         array_push($result[0], $port);
                    if($return == 2)
                        array_push($result[1], $port);
                }else{
                    array_push($result[2], $port);
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
                    array_push($result[0], $port);
                }else{
                    array_push($result[2], $port);
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
                    array_push($result[0], $port);
                }else{
                    array_push($result[2], $port);
                }
            }
        }
        echo json_encode($result);
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
""" % (type, ip, ports, timeout)


def human_friendly_list_print(l: list) -> str:
    str_dict = {}
    for i in l:
        if (isinstance(i, int)):
            if ((i-1) in str_dict):
                temp = str_dict[(i-1)]
                del str_dict[(i-1)]
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
    if (_type not in [1,2,3]):
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