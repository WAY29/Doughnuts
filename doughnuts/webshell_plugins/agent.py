from libs.config import alias, color
from libs.myapp import send, base64_encode, base64_decode
from re import findall, I, M
from os import makedirs, urandom
from os.path import dirname, exists
from time import time


def get_php(request_target, request_method, request_redirect_method, request_data, request_params, request_cookie,
            redirect_auto, redirect_cookie_use, timeout, type):
    return base64_encode("""
# 代理目标
$REQUEST_URL= "%s";

# 代理请求方法
$REQUEST_METHOD= '%s';

# 遇到跳转时的请求方法
$REQUEST_REDIRECT_METHOD = '%s';

# POST数据
$REQUEST_DATA='%s';

# GET数据
$REQUEST_PARAMS='%s';

# COOKIE数据
$REQUEST_COOKIE='%s';

# 是否自动跳转
$REDIRECT_AUTO = %d;

# 跳转时使用自动获取的COOKIE
$REDIRECT_COOKIE_USE = %d;

# 超时时间
$TIMEOUT = %f;

# 有4种。
# 前3种分别对应 socket file_get_contents curl 的内网代理
# 最后1种是单纯的file_get_contents()，可以玩php伪协议
$TYPE = %d;


class Agent{

    private $page_content;
    private $type;
    private $timeout;
    private $redirect_auto;
    private $redirect_cookie_use;

    private $request_method;
    private $request_redirect_method;
    private $request_allowed_method;

    private $request_params;
    private $request_data;
    private $request_cookie;

    private $request_url;
    private $request_url_group;
    private $current_url;
    private $header_data;
    private function get_cookie($header_lines){
        foreach ($header_lines as $line) {
            preg_match_all('/set-cookie:(.*)/i', $line, $cookie);
            if (@$cookie[1][0] != NULL) {
                return trim($cookie[1][0]);
            }
        }
        return false;
    }

    private function get_redirect($header_lines){
        foreach($header_lines as $line){
            preg_match_all('/location:(.*)/i',$line,$url);
            if(@$url[1][0]!=NULL){
                return trim($url[1][0]);
            }
        }
        return false;
    }

    private function get_params($params){
        $re_params=[];
        if($params == '') return [''=>''];
        foreach(explode('&',$params) as $line){
            $key_value=explode('=',$line);
            $re_params[urldecode(isset($key_value[0])?$key_value[0]:'')]=urldecode(isset($key_value[1])?$key_value[1]:'');
        }
        return $re_params;
    }

    private function get_query($params_group){
        return isset($params_group['']) and $params_group['']=='' ? '' : http_build_query($params_group);
    }

    private function url_cut($url){
        return parse_url($url);
    }

    private function get_host($url){
        $url_group=$this->url_cut($url);
        if(isset($url_group['scheme'])){
            return $url;
        }else{
            return $url_group['scheme'].'://'.$url_group['host'].(isset($url_group['port'])?'':':'.$url_group['port']);
        }
    }

    private function get_element($host,$body){
        preg_match_all("/<link[\s\S]*?href=['\\"](.*?[.]css.*?)[\\"'][\s\S]*?>/i", $body, $css);
        preg_match_all("/<script[\s\S]*?src=['\\"](.*?[.]js.*?)[\\"'][\s\S]*?>/i", $body, $js);

        foreach ($css[1] as $css_url) {
            $body .= "<style>".@file_get_contents(strpos($css_url, 'http://') == false ? $host . '/' . $css_url:$css_url)."</style>";
        }
        foreach ($js[1] as $js_url) {
            $body .= "<script>" . @file_get_contents(strpos($js_url, 'http://') == false ? $host . '/' . $js_url : $js_url) . "</script>";
        }

        $body.="\\n<!-- \\n<CurrentUrl>".base64_encode($this->current_url)."</CurrentUrl>";
        $body.="<CurrentCookie>".base64_encode($this->request_cookie)."</CurrentCookie>";
        $body.="<CurrentHeader>";
        if(is_array($this->header_data)){
            foreach($this->header_data as $tag){
                if($tag){
                    $body.=base64_encode("[{$tag}]")."|";
                }
            }
        }
        $body.="</CurrentHeader>";
        $body.="<CurrentStatus>success</CurrentStatus>\\n -->";
        return $body;
    }

    private function get302_socket($url)
    {
        try {
            $result="";
            $url_group = $this->url_cut($url);
            $fp = @fsockopen($url_group['host'], isset($url_group['port']) ? $url_group['port'] : (isset($this->request_url_group['port']) ? $this->request_url_group['port'] : 80), $erro, $errostr, $this->timeout);
            if (!$fp) {
                throw new Exception("Can't connect```");
            } else {

                if(in_array($this->request_redirect_method,$this->request_allowed_method)){
                    if ($this->request_redirect_method === 'POST') {
                        $r = 'POST ' . $url_group['path'] . " HTTP/1.1\\r\\n";
                        $type = "application/x-www-form-urlencoded";
                        $len = 0;
                    } else {
                        $r = 'GET ' . $url_group['path'] . " HTTP/1.1\\r\\n";
                        $type = '';
                        $len = 0;
                    }
                }

                $r .= "Host: " . $url_group['host'] . ':' . (isset($url_group['port']) ? $url_group['port'] : (isset($this->request_url_group['port']) ? $this->request_url_group['port'] : '80')) . "\r\n";
                $r .= $this->request_cookie ? "Cookie: " . $this->request_cookie . "\\r\\n":'';
                $r .= "Content-Type: " . $type . "\\r\\n";
                $r .= "Content-Length: " . $len . "\\r\\n";
                $r .= "Connection: close\\r\\n\\r\\n";
                fputs($fp, $r);
                while (!feof($fp)) {
                    $result .= fgets($fp, 1024);
                }
                fclose($fp);
                if ($result) {
                    list($header, $body) = explode("\\r\\n\\r\\n" , $result, 2);
                    preg_match("#HTTP/[0-9\.]+\s+([0-9]+)#", explode("\\r\\n", $header)[0], $code);
                    $header = explode("\\r\\n",$header);
                    $this->header_data = $header;

                    if (300 <= $code[1] and $code[1] < 400) {
                        $redirect_url = $this->get_redirect($header);
                        $cookie = $this->get_cookie($header) ? $this->get_cookie($header) : $this->request_cookie;
                        if($this->redirect_cookie_use and $cookie  != ''){
                            $this->request_cookie = $cookie;
                        }
                        if(stripos($redirect_url,'http://') == false){
                            if($redirect_url[0] == '/'){
                                $redirect_url = $this->get_host($url).$redirect_url;
                            }else{
                                $redirect_url = $url_group['scheme'].'://'.$url_group['host']. ':' . (isset($url_group['port']) ? $url_group['port'] : '80').(isset($url_group['path'])?($url_group['path'] == '/'?'/':substr($url_group['path'],0,strripos($url_group['path'],'/') + 1)):'/').$redirect_url;
                            }
                        }
                        $this->current_url = $redirect_url;
                        return $this->redirect_auto ? $this->get302_socket($redirect_url) : $body;
                    } else {
                        return $body;
                    }
                }
            }
        } catch (Exception $e) {
            die("File_Get_Contents_Redirect_error #:" . $e);
        }
    }

    private function get302_fg($url)
    {
        try {
            $url_group = $this->url_cut($url);
            if (in_array($this->request_redirect_method, $this->request_allowed_method)) {
                if ($this->request_redirect_method === 'POST') {
                    $type = "application/x-www-form-urlencoded";
                }
            }
            $opts = array(
                'http' => array(
                    'method' => $this->request_method,
                    'timeout' => $this->timeout,
                    'header' => 'Content-Type: ' . (isset($type) ? '' : $type) . "\\r\\n" .
                        'Content-Length: 0' . "\\r\\n".
                        ($this->request_cookie ? 'Cookie: ' . $this->request_cookie . "\\r\\n":'' )
                )
            );
            $context = stream_context_create($opts);
            $body = @file_get_contents($url, false, $context);
            $result = $http_response_header;
            $this->header_data = $result;
            preg_match("#HTTP/[0-9\.]+\s+([0-9]+)#", $result[0], $code);
            if (300 <= $code[1] and $code[1] < 400) {
                $redirect_url = $this->get_redirect($result);
                $cookie = $this->get_cookie($result) ? $this->get_cookie($result) : $this->request_cookie;
                if($this->redirect_cookie_use and $cookie  != ''){
                            $this->request_cookie = $cookie;
                        }
                        if(stripos($redirect_url,'http://') == false){
                            if($redirect_url[0] == '/'){
                                $redirect_url = $this->get_host($url).$redirect_url;
                            }else{
                                $redirect_url = $url_group['scheme'].'://'.$url_group['host']. ':' . (isset($url_group['port']) ? $url_group['port'] : '80').(isset($url_group['path'])?($url_group['path'] == '/'?'/':substr($url_group['path'],0,strripos($url_group['path'],'/') + 1)):'/').$redirect_url;
                            }
                        }
                        $this->current_url = $redirect_url;
                        return $this->redirect_auto ? $this->get302_fg($redirect_url) : ($body === false ? "Can't fetch contents```" : $body);
            } else {
                return $body === false ? "Can't fetch contents```" : $body;
            }
        } catch (Exception $e) {
            die("File_Get_Contents_Redirect_error #:" . $e);
        }
    }

    private function get302_c($url){
        try{
            $r = curl_init();
            $url_group = $this->url_cut($url);

            curl_setopt($r, CURLOPT_URL, $url);
            curl_setopt($r, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($r, CURLOPT_CONNECTTIMEOUT, $this->timeout);
            curl_setopt($r, CURLOPT_HEADER, true);

            if($this->request_cookie){
                curl_setopt($r,CURLOPT_COOKIE,$this->request_cookie);
            }

            if(in_array($this->request_redirect_method,$this->request_allowed_method)){
                if ($this->request_redirect_method === 'POST') {
                    curl_setopt($r, CURLOPT_POST, 1);
                }
            }

            $result = curl_exec($r);

            if($result){
                $header_size = curl_getinfo($r, CURLINFO_HEADER_SIZE);
                $header = explode("\\r\\n", substr($result, 0, $header_size));
                $body = substr($result, $header_size);
                $status_code = intval(curl_getinfo($r, CURLINFO_HTTP_CODE));
                $this->header_data = $header;

                curl_close($r);

                if (300 <= $status_code and $status_code < 400) {
                    $redirect_url = $this->get_redirect($header);
                    $cookie = $this->get_cookie($header) ? $this->get_cookie($header) : $this->request_cookie;
                    if($this->redirect_cookie_use and $cookie  != ''){
                            $this->request_cookie = $cookie;
                        }
                        if(stripos($redirect_url,'http://') == false){
                            if($redirect_url[0] == '/'){
                                $redirect_url = $this->get_host($url).$redirect_url;
                            }else{
                                $redirect_url = $url_group['scheme'].'://'.$url_group['host']. ':' . (isset($url_group['port']) ? $url_group['port'] : '80').(isset($url_group['path'])?($url_group['path'] == '/'?'/':substr($url_group['path'],0,strripos($url_group['path'],'/') + 1)):'/').$redirect_url;
                            }
                        }
                        $this->current_url = $redirect_url;
                        return $this->redirect_auto ? $this->get302_c($redirect_url) : $body;
                }else{
                    return $body;
                }
            }
        } catch(Exception $e){
            die("CURL_Redirect_error #:" . $e);
        }
    }

    public function getContent_sock()
    {
        try {
            $result = '';
            $fp = @fsockopen($this->request_url_group['host'], isset($this->request_url_group['port']) ? $this->request_url_group['port'] : 80, $erro, $errostr, $this->timeout);

            if (!$fp) {
                var_dump($this->request_url_group['scheme'] . '://' . $this->request_url_group['host'] . (isset($this->request_url_group['path']) ? $this->request_url_group['path'] : '/' . '?' . $this->get_query($this->request_params)));
                var_dump(isset($this->request_url_group['port']) ? $this->request_url_group['port'] : 80);
                throw new Exception("Can't connect```");
            } else {

                if (in_array($this->request_method, $this->request_allowed_method)) {
                    if ($this->request_method === 'POST') {
                        $r = 'POST ' . (isset($this->request_url_group['path']) ? $this->request_url_group['path'] : '/') . '?' . $this->get_query($this->request_params) . " HTTP/1.1\r\n";
                        $type = "application/x-www-form-urlencoded";
                        $len = strlen($this->get_query($this->request_data));
                    } else {
                        $r = 'GET ' . (isset($this->request_url_group['path']) ? $this->request_url_group['path'] : '/') . '?' . $this->get_query($this->request_params) . " HTTP/1.1\r\n";
                        $type = '';
                        $len = 0;
                    }
                }
                $r .= "Host: " . $this->request_url_group['host'] . ':' . (isset($this->request_url_group['port']) ? $this->request_url_group['port'] : '80') . "\r\n";
                $r .= $this->request_cookie ? "Cookie: " . $this->request_cookie . "\\r\\n" : '';
                $r .= "Content-Type: " . $type . "\\r\\n";
                $r .= "Content-Length: " . $len . "\\r\\n";
                $r .= "Connection: close\\r\\n";
                $r .= "\\r\\n" . $this->get_query($this->request_data);

                fputs($fp, $r);
                while (!feof($fp)) {
                    $result .= fgets($fp, 1024);
                }
                fclose($fp);

                if ($result) {
                    list($header, $body) = explode("\\r\\n\\r\\n" , $result, 2);
                    preg_match("#HTTP/[0-9\.]+\s+([0-9]+)#", explode("\\r\\n", $header)[0], $code);
                    $header = explode("\\r\\n",$header);
                    $this->header_data = $header;
                    
                    if (300 <= $code[1] and $code[1] < 400) {
                        $redirect_url = $this->get_redirect($header);
                        $cookie = $this->redirect_cookie_use ? ($this->get_cookie($header) ? $this->get_cookie($header) : $this->request_cookie) : '';
                        if($this->redirect_cookie_use and $cookie  != ''){
                            $this->request_cookie = $cookie;
                        }
                        if(stripos($redirect_url,'http://') == false){
                            if($redirect_url[0] == '/'){
                                $redirect_url = $this->get_host($this->request_url).$redirect_url;
                            }else{
                                $redirect_url = $this->request_url_group['scheme'].'://'.$this->request_url_group['host']. ':' . (isset($this->request_url_group['port']) ? $this->request_url_group['port'] : '80').(isset($this->request_url_group['path'])?($this->request_url_group['path'] == '/'?'/':substr($this->request_url_group['path'],0,strripos($this->request_url_group['path'],'/') + 1)):'/').$redirect_url;
                            }
                        }
                        $this->current_url = $redirect_url;
                        return $this->redirect_auto ? $this->get302_socket($redirect_url) : $body;
                    } else {
                        return $body;
                    }
                }
            }
        } catch (Exception $e) {
            die("SOCKET_error #:" . $e);
        }
    }

    public function getContent_fg(){
        try{

            if(in_array($this->request_method,$this->request_allowed_method)){
                if($this->request_method === 'POST'){
                    $type = "application/x-www-form-urlencoded";
                }
            }

            $opts = array(
                'http'=>array(
                    'method' => $this->request_method,
                    'content' => $this->get_query($this->request_data),
                    'timeout' => $this->timeout,
                    'header' => 'Content-Type: '.(isset($type)?'':$type)."\\r\\n".
                                'Content-Length: '.strlen($this->get_query($this->request_data))."\\r\\n".
                                ($this->request_cookie ? 'Cookie: ' . $this->request_cookie . "\\r\\n" : '')
                )
            );
            $context = stream_context_create($opts);
            $body = @file_get_contents($this->request_url.'?'.$this->get_query($this->request_params),false,$context);
            $result = $http_response_header;
            $this->header_data = $result;

            preg_match("#HTTP/[0-9\.]+\s+([0-9]+)#", $result[0], $code);
            if (300 <= $code[1] and $code[1] < 400) {
                $redirect_url = $this->get_redirect($result);
                $cookie = $this->redirect_cookie_use ? ($this->get_cookie($result) ? $this->get_cookie($result) : $this->request_cookie) : '';
                if($this->redirect_cookie_use and $cookie  != ''){
                            $this->request_cookie = $cookie;
                        }
                        if(stripos($redirect_url,'http://') == false){
                            if($redirect_url[0] == '/'){
                                $redirect_url = $this->get_host($this->request_url).$redirect_url;
                            }else{
                                $redirect_url = $this->request_url_group['scheme'].'://'.$this->request_url_group['host']. ':' . (isset($this->request_url_group['port']) ? $this->request_url_group['port'] : '80').(isset($this->request_url_group['path'])?($this->request_url_group['path'] == '/'?'/':substr($this->request_url_group['path'],0,strripos($this->request_url_group['path'],'/') + 1)):'/').$redirect_url;
                            }
                        }
                        $this->current_url = $redirect_url;
                        return $this->redirect_auto ? $this->get302_fg($redirect_url) : ($body===false?"Can't fetch contents```":$body);
            }else{
                return $body === false ? "Can't fetch contents```" : $body;
            }
        } catch(Exception $e){
            die("File_Get_Contents_error #:" . $e);
        }
    }
    public function getContent_c(){
        try{
            if(in_array($this->request_method,$this->request_allowed_method)){
                $curl = curl_init();

                curl_setopt($curl,CURLOPT_URL,$this->request_url.'?'.$this->get_query($this->request_params));
                curl_setopt($curl,CURLOPT_RETURNTRANSFER,1);
                curl_setopt($curl,CURLOPT_CONNECTTIMEOUT,$this->timeout);
                curl_setopt($curl,CURLOPT_HEADER,true);

                if($this->request_cookie){
                    curl_setopt($curl,CURLOPT_COOKIE,$this->request_cookie);
                }

                if (in_array($this->request_method, $this->request_allowed_method)) {
                    if($this->request_method === 'POST'){
                        curl_setopt($curl,CURLOPT_POST,1);
                        curl_setopt($curl,CURLOPT_POSTFIELDS,$this->get_query($this->request_data));
                    }
                }
                $result = curl_exec($curl);
                if($result){
                    $header_size = curl_getinfo($curl,CURLINFO_HEADER_SIZE);
                    $header = explode("\\r\\n",substr($result,0,$header_size));
                    $body = substr($result,$header_size);
                    $status_code = intval(curl_getinfo($curl,CURLINFO_HTTP_CODE));
                    $this->header_data = $header;

                    curl_close($curl);

                    if(300 <= $status_code and $status_code < 400){
                        $redirect_url = $this->get_redirect($header);
                        $cookie = $this->redirect_cookie_use ? ($this->get_cookie($header) ? $this->get_cookie($header) : $this->request_cookie) : '';
                        if($this->redirect_cookie_use and $cookie  != ''){
                            $this->request_cookie = $cookie;
                        }
                        if(stripos($redirect_url,'http://') == false){
                            if($redirect_url[0] == '/'){
                                $redirect_url = $this->get_host($this->request_url).$redirect_url;
                            }else{
                                $redirect_url = $this->request_url_group['scheme'].'://'.$this->request_url_group['host']. ':' . (isset($this->request_url_group['port']) ? $this->request_url_group['port'] : '80').(isset($this->request_url_group['path'])?($this->request_url_group['path'] == '/'?'/':substr($this->request_url_group['path'],0,strripos($this->request_url_group['path'],'/') + 1)):'/').$redirect_url;
                            }
                        }
                        $this->current_url = $redirect_url;
                        return $this->redirect_auto ? $this->get302_c($redirect_url) : $body;
                    }else{
                        return $body;
                    }
                }
            }

        } catch (Exception $e) {
            die("CURL_error #:" . $e);
        }
    }

    public function get_content(){
        $contents = @file_get_contents($this->request_url);
        return $contents === false ? "Can't fetch contents```" : $contents;
    }

    public function __construct($request_url,$request_method,$request_redirect_method,$redirect_auto,$redirect_cookie_use,$params,$data,$cookie,$timeout,$type){
        $this->request_url = $request_url;
        $this->request_url_group = $this->url_cut($request_url);
        $this->current_url = $request_url;
        $this->request_method = $request_method;
        $this->request_redirect_method = $request_redirect_method;
        $this->redirect_auto = $redirect_auto;
        $this->redirect_cookie_use = $redirect_cookie_use;
        $this->request_params = $this->get_params($params);
        $this->request_data = $this->get_params($data);
        $this->request_cookie = $cookie;
        $this->request_allowed_method = ['GET','POST'];
        $this->timeout = $timeout;
        $this->type = $type;
    }

    public function __toString(){

        switch($this->type){
            case 1:
                $this->page_content = $this->get_element($this->request_url,$this->getContent_sock());
                break;
            case 2:
                $this->page_content = $this->get_element($this->request_url, $this->getContent_fg());
                break;
            case 3:
                $this->page_content = $this->get_element($this->request_url, $this->getContent_c());
                break;
            case 4:
                $this->page_content = $this->get_content();
                break;
        }

        return $this->page_content;
    }
}

$this_request = new Agent($REQUEST_URL,$REQUEST_METHOD,$REQUEST_REDIRECT_METHOD,$REDIRECT_AUTO,$REDIRECT_COOKIE_USE,$REQUEST_PARAMS,$REQUEST_DATA,$REQUEST_COOKIE,$TIMEOUT,$TYPE);

echo $this_request;
""" % (request_target, request_method, request_redirect_method, request_data, request_params, request_cookie,
       redirect_auto, redirect_cookie_use, timeout, type))


@alias(True, _type="OTHER", func_alias="ag", u="url", m="method", d="data", p="params", c="cookie", t="type",
       to="timeout", re_m="redirect_method")
def run(url: str, method: str,
        data: str = '', params: str = '', cookie: str = '', type: int = 1, timeout: float = 3,
        redirect_method: str = "POST", redirect_auto: int = 1, redirect_cookie_use: int = 1, create_dir: int = 0):
    """
    agent

    Lightweight intranet browsing.

    eg: agent {url} {method} {data=''} {params=''} {cookie=''} {type=[socket|file_get_contents|curl]{1|2|3},default = 1} {timeout=3} {redirect_method=POST} {redirect_auto=1} {redirect_cookie_use=1} {create_dir=0}
    """

    php = get_php(
        url,
        method.upper(), redirect_method.upper(),
        data, params, cookie,
        redirect_auto, redirect_cookie_use, timeout, type
    )
    res = send(php)
    if (not res):
        return
    text = res.r_text

    # ------------------------------------------

    try:

        current_status = findall(
            '<CurrentStatus>(.*)</CurrentStatus>', text, I + M)
        assert len(current_status), "Can't get status```"
        current_status = current_status[0]

        current_url = findall('<CurrentUrl>(.*)</CurrentUrl>', text, I + M)
        current_url = base64_decode(current_url[0]) if len(current_url) else ''

        current_cookie = findall(
            '<CurrentCookie>(.*)</CurrentCookie>', text, I + M)
        current_cookie = base64_decode(
            current_cookie[0]) if len(current_cookie) else ''

        current_header = findall(
            '<CurrentHeader>(.*)</CurrentHeader>', text, I + M)
        current_header = "\n    ".join(base64_decode(line) for line in current_header[0].split("|")) if len(
            current_header) else ''

        if (current_status == "success"):
            print(color.magenta("Current Url: ") +
                  color.cyan(current_url) + "\n")
            print(color.blue("Response Headers: \n\n") +
                  " " * 4 + color.white(current_header))
            print(color.blue("Cookie: \n\n") + " " *
                  4 + color.red(current_cookie) + "\n")
            print(color.yellow("*" * 20 + " Body " + "*" * 20) + "\n\n")
            print(color.cyan(text) + "\n\n")
            print(color.yellow("*" * 20 + " END " + "*" * 21) + "\n\n")
            if (create_dir == 1):
                dir_path = dirname(current_url.split("//", maxsplit=1)[1])
                dir_path = dir_path.replace(":", "-")
                dir_path = dir_path.replace('.', "_")
                file_name = "".join(hex(each)[2:].zfill(
                    2) for each in urandom(20)) + "_" + str(time()) + '.html'

                if(not exists(dir_path)):
                    makedirs(dir_path)

                method = "w"
                try:
                    contents = text.encode()
                    method = "wb"
                except Exception:
                    contents = text

                with open(dir_path + "/" + file_name, method) as out_file:
                    out_file.write(contents)

                print(color.blue("Outfile: ") +
                      color.cyan(dir_path + "/" + file_name) + "\n\n")

    except Exception as e:
        print("Agent error.", e)
