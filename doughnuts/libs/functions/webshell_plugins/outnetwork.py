
def get_php_outnetwork():
    return """function udpGet($sendMsg,$ip,$port){
    $handle=stream_socket_client("udp://{$ip}:{$port}", $errno, $errstr);
    if(!$handle){
        echo("[-][UDP] {$errno} - {$errstr}\\n");
        return;
    }
    $sendMsg=hex2bin($sendMsg);
    @fwrite($handle, $sendMsg);
    $result = fread($handle,1024);
    @fclose($handle);
    return $result;
    }
    function checkUDP($dns_server){
        if(stristr(urlencode(udpGet('02ed010000010000000000000862696c6962696c6903636f6d0000010001',$dns_server,'53')), 'bilibili%03com')) {
        echo "[+][UDP] {$dns_server}:53\\n";
        }else{
        echo "[-][UDP] {$dns_server}:53\\n";
        }
    }

    function checkDNS($domain){
    $dnsres = dns_get_record($domain,DNS_A);
    if(sizeof($dnsres)>0){
        echo("[+][DNS] ${domain}\\n");
    } else {
        echo("[-][DNS] ${domain}\\n");
    }
    }
    function checkTCP(){
    $ips = ['bilibili.com', 'jetbrains.com', 'microsoft.com'];
    foreach($ips as $ip) {
        $context = stream_context_create(array('http' => array('follow_location' => false, 'timeout' => 5)));
        $httpres = file_get_contents("http://${ip}", false, $context);
        if($httpres===false){
        echo("[-][TCP] ${ip}\\n");
        continue;
        };
        echo("[+][TCP] ${ip}\\n");
        break;
    }
    }

    checkTCP();
    checkUDP("8.8.8.8");
    checkUDP("223.5.5.5");
    checkUDP("119.29.29.29");
    checkDNS("bilibili.com");
    """