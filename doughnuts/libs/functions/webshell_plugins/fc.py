
def get_php_fc():
    return """$cfgs=array("cfg","config","db","database");
    function filter($v,$vv){
        return strstr($v, $vv);
    }
    function scan_rescursive($directory) {
        global $cfgs;
        $res = array();
        foreach(glob("$directory/*") as $item) {
            if(is_dir($item)) {
                $items=explode('/', $item);
                $folder = base64_encode(end($items));
                $res[$folder] = scan_rescursive($item);
                continue;
            }
            else if (count(array_filter(array_map("filter", array_fill(0, count($cfgs), $item), $cfgs)))){
                $res[] = base64_encode(basename($item));
            }
        }
        return $res;
    }
    print(json_encode(scan_rescursive("%s")));"""
