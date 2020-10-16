from os import path
from time import sleep
from base64 import b64encode
from time import sleep
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


from tqdm import tqdm


from libs.config import alias, color
from libs.myapp import send, base64_encode, gzdeflate, size_to_human, human_to_size


UPLOAD_SUCCESS = True
LOCK = Lock()
BAR = None
BLOCKSIZE = 0
ALL_TASK = []


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


def get_php_upload(web_file_path: str, data: str, number: int):
    web_file_path = base64_encode(web_file_path + ".tmp%s" % number)
    return """$p=base64_decode("%s");file_put_contents($p, "%s");if(filesize($p) !== 0){echo "success";}""" % (web_file_path, data)


def get_php_decode(web_file_path: str, number: int):
    return """
$p=base64_decode("%s");
$data="";
$f=true;
$fp=@fopen($p, 'wb');
if (fp){
for($i=0;$i<%s;$i++){
    $pp="$p.tmp$i";
    if(filesize($pp)!==0){
        $data=gzinflate(base64_decode(file_get_contents($pp)));
        fwrite($fp, $data);
        fflush($fp);
        unlink($pp);
    } else {
        $f=false;
        break;
    }
}
}
fclose($fp);
if($f){
if(file_exists($p) && filesize($p) !== 0){echo "success";}
}""" % (base64_encode(web_file_path), number)


def get_php_clean(web_file_path: str, number: int):
    return """for($i=0;$i<%s;$i++){
    unlink(base64_decode("%s").".tmp$i");
}""" % (number, base64_encode(web_file_path))


def thread_upload(web_file_path: str, data: str, number: int, blocksize: int):
    global UPLOAD_SUCCESS
    retry_time = 5
    try:
        if (not UPLOAD_SUCCESS):
            return False
        while retry_time:
            res = send(get_php_upload(web_file_path, data, number))
            if ("success" in res.r_text.strip()):
                break
            else:
                retry_time -= 1
                continue
        if (not retry_time):
            UPLOAD_SUCCESS = False
            return False
    except Exception:
        UPLOAD_SUCCESS = False
        return False
    return True


def clean(web_file_path: str, number: int,):
    res = send(get_php_clean(web_file_path, number))
    if (not res):
        return False
    return True


def update(future):
    global BAR, UPLOAD_SUCCESS, BLOCKSIZE, ALL_TASK, LOCK
    result = future.result()
    if (result):
        if (not BAR.disable):
            with LOCK:
                BAR.update(BLOCKSIZE)
    else:
        UPLOAD_SUCCESS = False
        BAR.close()
        for task in reversed(ALL_TASK):
            task.cancel()


@alias(True, func_alias="mu", _type="FILE", s="humansize")
def run(file_path: str, web_file_path: str = "", force: bool = False, humansize: str = "1MB", threads: int = 5):
    """
    mupload

    Upload file by block compression and multi threads.

    eg: mupload {file_path} {web_file_path=file_name} {force=False} {humansize="1MB",eg="10MB"} {threads=5}
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
        print(color.red("\n[Failed] File path not writable\n"))
        return
    global UPLOAD_SUCCESS, BAR, BLOCKSIZE, ALL_TASK
    UPLOAD_SUCCESS = True
    decode_retry_time = 5
    tlen = path.getsize(file_path)
    ALL_TASK = []
    count = 0
    print(color.yellow(f"\n[Try] Upload {file_path}\n"))
    BAR = tqdm(total=tlen, desc="Uploading", unit_scale=True)
    try:
        BLOCKSIZE = human_to_size(humansize)
    except Exception:
        BLOCKSIZE = tlen // 10
        print(color.yellow(
            f"[Warn] Parse humansize error, set it to {size_to_human(BLOCKSIZE)}"))
    if (BLOCKSIZE < tlen / 1000):
        BLOCKSIZE = tlen // 100
        print(color.yellow(
            f"[Warn] Humansize too small, set it to {size_to_human(BLOCKSIZE)}"))
    with open(file_path, "rb+") as fp, ThreadPoolExecutor(max_workers=threads) as tp:
        for n, i in enumerate(range(0, tlen, BLOCKSIZE)):
            future = tp.submit(thread_upload, web_file_path, b64encode(gzdeflate(fp.read(
                BLOCKSIZE))).decode(), n, BLOCKSIZE)
            future.add_done_callback(update)
            ALL_TASK.append(future)
            count += 1
        wait(ALL_TASK, return_when=ALL_COMPLETED)
        sleep(2)
        if (not UPLOAD_SUCCESS):
            clean_result = clean(web_file_path, count)
            if (clean_result):
                print(color.yellow(
                    "\n[Success] Upload error, Clean tmpfile\n"))
            return
        BAR.close()
        while decode_retry_time:
            res = send(get_php_decode(web_file_path, count))
            if (not res):
                return
            text = res.r_text.strip()
            if "success" in text:
                if (flag):
                    print(color.green(
                        f"\n[Success] Upload {file_path} as {web_file_path} success\n"))
                else:
                    print(color.green(
                        f"\n[Success] Upload {web_file_path} success\n"))
                break
            else:
                print(
                    color.red(f"\n[Failed] Upload error / Request error, retry..."))
                decode_retry_time -= 1
        if (not decode_retry_time):
            clean_result = clean(web_file_path, count)
            if (clean_result):
                print(color.yellow(
                    "\n[Success] Upload error, Clean tmpfile\n"))
