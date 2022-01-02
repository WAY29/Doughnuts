
def get_php_fwpf():
    return """
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
            else if(preg_match('/ph*/i',end(explode('.', $item))) && is_writable($item)){
                $res[] = base64_encode(basename($item));
            }
        }
        return $res;
    }
    print(json_encode(scan_rescursive("%s")));
    """
