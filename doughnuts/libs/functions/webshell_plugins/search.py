
def get_php_search():
    return """
    function rglob($pattern, $flags = 0) {
        $files = glob($pattern, $flags);
        foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir) {
            $files = array_merge($files, rglob($dir.'/'.basename($pattern), $flags));
        }
        return $files;
    }
    ini_set('memory_limit', '-1');
    foreach(rglob("%s/*") as $v){
        if(preg_match("/%s/", $v)){
            print($v."\\n");
        }
    }
    """
