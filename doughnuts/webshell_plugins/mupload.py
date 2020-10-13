from genericpath import exists
from os import path, truncate
import zlib
from base64 import b64encode, encode
from time import sleep
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, wait, as_completed, FIRST_EXCEPTION, ALL_COMPLETED

from libs.config import alias, color
from libs.myapp import send, base64_encode, md5_encode


UPLOAD_SUCCESS = True
COLOR_PRINT_LOCK = Lock()

class UploadBreakException(Exception):
    pass


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
if(file_exists($p) && filesize($p) !== 0){echo "success ".md5($data);}
}""" % (web_file_path, total_number)


def thread_upload(web_file_path: str, data: str, number : int, blocksize: int):
    global UPLOAD_SUCCESS, COLOR_PRINT_LOCK
    retry_time = 5
    try:
        with COLOR_PRINT_LOCK:
            print(color.yellow("[Try] Upload block [%d]" % number))
        if (not UPLOAD_SUCCESS):
            return
        while retry_time:
            res = send(get_php_upload(web_file_path, data, number))
            if (res.r_text.strip() == "success"):
                with COLOR_PRINT_LOCK:
                    print(color.yellow("[Successs] Upload block [%d]" % number))
                break
            else:
                retry_time -= 1
                with COLOR_PRINT_LOCK:
                    print(color.red("[Failed] Upload block [%d]" % number))
                continue
        if (not retry_time):
            with COLOR_PRINT_LOCK:
                print(color.red("\n[Failed] Upload break [%d]\n" % number))
            UPLOAD_SUCCESS = False
            raise UploadBreakException("")
    except Exception:
        UPLOAD_SUCCESS = False
        raise UploadBreakException("")


@alias(True, func_alias="mu", s="blocksize")
def run(file_path: str, web_file_path: str = "", force: bool = False, blocksize: int = 1024):
    """
    mupload

    Upload file by Block compression and multi threads.

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
    global UPLOAD_SUCCESS
    UPLOAD_SUCCESS = True
    decode_retry_time = 5
    with open(file_path, "rb+") as fp, ThreadPoolExecutor() as tp:
        fdata = fp.read()
        file_md5_hash = md5_encode(fdata)
        print(color.yellow(f"\n[Try] Upload {file_path} HASH: {file_md5_hash} \n"))
        compressor = zlib.compressobj(wbits=(16+zlib.MAX_WBITS))
        compressed = compressor.compress(fdata)
        compressed += compressor.flush()
        tdata = b64encode(compressed).decode()
        all_task = []
        for n, i in enumerate(range(0, len(tdata), blocksize)):
            all_task.append(tp.submit(thread_upload, web_file_path, tdata[i:i+blocksize], n, blocksize))
        count = len(all_task)
        wait(all_task, return_when=FIRST_EXCEPTION)
        for task in reversed(all_task):
            task.cancel()
        wait(all_task, return_when=ALL_COMPLETED)
        if (not UPLOAD_SUCCESS):
            return
        while decode_retry_time:
            res = send(get_php_decode(web_file_path, count))
            if (not res):
                return
            text = res.r_text.strip()
            if "success" in text:
                if (flag):
                    print(color.green(
                        f"\n[Success] Upload {file_path} as {web_file_path} success"))
                else:
                    print(color.green(f"\n[Success] Upload {web_file_path} success"))
                check_md5_hash = text.split(" ")[1]
                if (check_md5_hash == file_md5_hash):
                    print(color.green(f"[Success] Hash check\n"))
                else:
                    print(color.red(f"[Failed] Hash check\n"))
                return True
            else:
                print(color.red(f"\n[Failed] Upload error / Request error, retry..."))
                decode_retry_time -= 1
