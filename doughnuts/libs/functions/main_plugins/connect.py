
def get_php_detectd_exec(php_init):
    return """
    $a=array('system', 'exec', 'shell_exec', 'passthru', 'proc_open', 'popen','pcntl_exec');
    if(@!function_exists('get_ini_value')) {
        %s
    }
    $disabled = explode(',', get_ini_value('disable_functions'));
    foreach ($a as $v){
        if (function_exists($v) && !in_array($v, $disabled)){
            echo $v;
            break;
        }
    }""" % php_init


def get_php_version(*argv):
    return """
        function call($f){
            @$r = $f();
            if(empty($r)){
                    if(PHP_VERSION != ""){
                        return PHP_VERSION;
                    }
                return "Unknown";
            }
            return $r;
        }
    print("%s"."|".call('phpversion')."|"."%s"."|".@base64_decode("%s"));""" % argv


def get_php_uname(php_init):
    return """
        %s
        function call($f) {
            @$r=$f();
            if(empty($r)){return "Unknown";}
            return $r;
        }
        if(PHP_INT_SIZE == 4){
            $bit = 32;
        }else{
            $bit = 64;
        }
    print($_SERVER['DOCUMENT_ROOT'].
    '|'.call('php_uname').
    '|'.$_SERVER['SERVER_SOFTWARE'].
    '|'.call('getcwd').
    '|'.call('sys_get_temp_dir').
    '|'.get_ini_value('disable_functions').
    '|'.get_ini_value('open_basedir').
    '|'.$bit.
    '|'.DIRECTORY_SEPARATOR.
    '|'.get_ini_value('disable_classes'));
""".strip() % php_init


def get_php_loaded_extensions():
    return """
    function call($f){
        @$r=$f();
        if(empty($r)){return "Unknown";}
        return join("|",$r);
    }
    print(call('get_loaded_extensions'));
    """
