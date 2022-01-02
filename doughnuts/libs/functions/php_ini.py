
# 获取.ini配置
def get_ini_value_code():
    return """
    function get_ini_value($key){
    if(function_exists('ini_get')){
        return ini_get($key);
    } else if(function_exists('ini_get_all')) {
        $gev = version_compare(PHP_VERSION,'5.3.0','ge');
        if($gev){
            $values = ini_get_all(null,false);
        } else {
            $values = ini_get_all();
        }
        if(array_key_exists($key, $values)){
            return $gev?$values[$key]:$values[$key]['local_value'];
        } else {
            return '';
        }
    } else if(function_exists('get_cfg_var')) {
        return get_cfg_var($key);
    } else{
        return '';
    }
}
"""
