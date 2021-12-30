
def get_php_download():
    return """
        function download($fd){
        if (@file_exists($fd)){
        $fileinfo = pathinfo($fd);
        header("Content-type: application/x-" . $fileinfo["extension"]);
        header("Content-Disposition: attachment; filename=" . $fileinfo["basename"]);
        @readfile($fd);
        }
        }
        download(base64_decode("%s"));
    """