from genericpath import exists
from os import path
import zlib
from base64 import b64encode
from time import sleep

from libs.config import alias, color
from libs.myapp import send, base64_encode


def get_php_force(web_file_path: str, force):
    web_file_path = base64_encode(web_file_path)
    return """if (not is_writable(base64_encode("%s"))) {
echo "not writable";
} else if (%s and file_exists(base64_decode("%s"))){
print("exist");
}
else{
    unlink(base64_decode("%s"));
}""" % (web_file_path, str(not force).lower(), web_file_path, web_file_path)


def get_php_upload(web_file_path: str, data: str, number : int):
    web_file_path = base64_encode(web_file_path + ".tmp%s" % number)
    return """$p=base64_decode("%s");file_put_contents($p, "%s");if(filesize($p) !== 0){echo "success";}""" % (web_file_path, data)


def get_php_decode(web_file_path: str, total_number : int):
    web_file_path = base64_encode(web_file_path)
    return """function gzipdecode($data)
{
    return gzinflate(substr($data,10,-8));
}
$p=base64_decode("%s");
$data="";
$f=true;
for($i=0;$i<%s;$i++){
    $pp="$p.tmp$i";if(filesize($pp)!==0){
        $data .= file_get_contents($pp);unlink($pp);
    } else {
        $f=false;
        break;
    }
}
if($f){
$data=gzipdecode(base64_decode($data));
file_put_contents($p, $data);
if(file_exists($p) && filesize($p) !== 0){echo "success";}
}""" % (web_file_path, total_number)


@alias(True, func_alias="mu", s="blocksize")
def run(file_path: str, web_file_path: str = "", force: bool = False, blocksize: int = 1024):
    """
    mupload

    Upload file by Block compression.

    eg: mupload {file_path} {web_file_path=file_name} {force=False} {blocksize=1024}
    """
    flag = True
    if (not web_file_path):
        web_file_path = path.basename(file_path)
        flag = False
    if (not path.isfile(file_path)):
        print(color.red("\n[Failed] Local File not exist\n"))
        return
    res = send(get_php_force(web_file_path, force))
    if (not res):
        return
    text = res.r_text.strip()
    if (text == "exist"):
        print(color.red("\n[Failed] File is already exist\n"))
        return
    elif (text == "not writable"):
        print( color.red("\n[Failed] File path not writable\n"))
        return
    count = 0
    decode_retry_time = 5
    with open(file_path, "rb+") as fp:
        compressor = zlib.compressobj(wbits=(16+zlib.MAX_WBITS))
        compressed = compressor.compress(fp.read())
        compressed += compressor.flush()
        tdata = b64encode(compressed).decode()
        for i in range(0, len(tdata), blocksize):
            data = tdata[i:i+blocksize]
            retry_time = 5
            count += 1
            print(color.yellow("[Try] Upload block [%d]" % (count-1)))
            while retry_time:
                res = send(get_php_upload(web_file_path, data, count - 1))
                if (res.r_text.strip() == "success"):
                    print(color.yellow("[Successs] Upload block [%d]" % (count-1)))
                    break
                else:
                    retry_time -= 1
                    print(color.red("[Failed] Upload block [%d]" % (count-1)))
                    continue
            if (not retry_time):
                print(color.red("\n[Failed] Upload break\n"))
                return
    while decode_retry_time:
        res = send(get_php_decode(web_file_path, count))
        if (not res):
            return
        if res.r_text.strip() == "success":
            if (flag):
                print(color.green(
                    f"\n[Success] Upload {file_path} as {web_file_path} success\n"))
            else:
                print(color.green(f"\n[Success] Upload {web_file_path} success\n"))
            return True
        else:
            print(color.red(f"\n[Failed] Upload error / Request error, retry...\n"))
            decode_retry_time -= 1
