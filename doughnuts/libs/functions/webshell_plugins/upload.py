
def get_php_upload():
    return """$errors = array(
        0 => 'There is no error, the file uploaded with success',
        1 => 'The uploaded file exceeds the upload_max_filesize directive in php.ini',
        2 => 'The uploaded file exceeds the MAX_FILE_SIZE directive that was specified in the HTML form',
        3 => 'The uploaded file was only partially uploaded',
        4 => 'No file was uploaded',
        6 => 'Missing a temporary folder',
        7 => 'Failed to write file to disk.',
        8 => 'A PHP extension stopped the file upload.',
    );
    if (isset($_FILES)){
        $upload_path="%s";
        if (file_exists($upload_path)) {$upload_path=realpath($upload_path);}
        $fname="%s";
        if (is_dir($upload_path)) {
            $upload_path .= DIRECTORY_SEPARATOR.$fname;
        }
        if (%s and file_exists($upload_path)){
            print("$upload_path exist");
        }
        else if (move_uploaded_file($_FILES["file"]["tmp_name"], $upload_path)){
            print("Upload $upload_path success");
        } else {
            print($errors[$_FILES["file"]["error"]]);
        }
    }"""

def get_php_file_put_contents():
    return """
        $upload_path="%s";
        if (file_exists($upload_path)) {$upload_path=realpath($upload_path);}
        $fname="%s";
        if (is_dir($upload_path)) {
            $upload_path .= DIRECTORY_SEPARATOR.$fname;
        }
        if (%s and file_exists($upload_path)){
            print("$upload_path exist");
        }
        else if(file_put_contents($upload_path, base64_decode("%s"))) {
            print("Upload $upload_path success");
        } else {
            print("Upload $upload_path error");
        }
    """