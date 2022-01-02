

def get_php_ls():
    return """
    $umap=array();$gmap=array();
    function unamemap() {
    global $umap, $gmap;
    $lines = @explode(PHP_EOL, file_get_contents('/etc/passwd'));
    if ($lines) {
    foreach ($lines as $line) {
        $els = explode(':', $line);
        $uname = $els[0];
        if (strlen($uname) > 8) $uname = substr($uname, 0, 7) . '+';
        $umap[$els[2]] = $uname;}
    }
    $lines = @explode(PHP_EOL, file_get_contents('/etc/group'));
    if ($lines) {
    foreach ($lines as $line) {
        $els = explode(':', $line);
        $gname = $els[0];
        if (strlen($gname) > 8) $gname = substr($gname, 0, 7) . '+';
        $gmap[$els[2]] = $gname;}
    }
    }
    function getuname($uid) {
    global $umap;
    $uname = $umap[$uid];
    if (!$uname) return $uid;
    return $uname;
    }
    function getgname($gid) {
    global $gmap;
    $gname = $gmap[$gid];
    if (!$gname) return $gid;
    return $gname;
    }
    function getprems($file){
    $perms = fileperms($file);
    $strs='upcudubu-ulusuuuuu';$tstrs='tss';$Tstrs='TSS';$wrstrs='wr';
    $info=$strs[($perms&0xF000)>>12];
    for($bit=8;$bit>=0;$bit--){
      $info .= ($perms&0x01ff)>>$bit & 1 ? ( !($bit%%3) ? (((($perms >> 9) & 0x7) >> ($bit / 3)) & 1 ? $tstrs[$bit/3] :'x') :$wrstrs[($bit-1)%%3] ): ( !($bit%%3) ? (((($perms >> 9) & 0x7) >> ($bit / 3)) & 1 ? $Tstrs[$bit/3] : '-'):'-');
    }

    return $info;
    }
    function getfilesize($file){
        $bytes = filesize($file);
        $sz = 'BKMGTP';
        $factor = floor((strlen($bytes) - 1) / 3);
        return sprintf("%%.1f", $bytes / pow(1024, $factor)) . @$sz[$factor];
    }
    function getmtime($file){
        return date("m-d H:i",filemtime($file));
    }
    function getinfo($file,$filter=true){
        $islinux = strtoupper(substr(PHP_OS,0,3))==='WIN'?FALSE:TRUE;
        $format="%%s %%s %%s %%s %%s %%s";
        $filename=!is_link($file)?basename($file):basename($file).' -> '.readlink($file);
        if($filter && in_array($filename, array(".", ".."))){return "";}
        $owner=getuname(fileowner($file));
        $group=getgname(filegroup($file));
        return sprintf($format, getprems($file), $owner, $group, getfilesize($file),getmtime($file),$filename);
    }
    unamemap();
    %s
    echo "Listing: ".realpath("%s")."\\n";
    echo "==============================\\n";
    printf("%%-10s  %%-8s  %%-8s  %%6s  %%-12s %%s\\n","MODE","UID","GID","SIZE","MTIME","NAME");
    echo getinfo(".", false)."\\n";
    echo getinfo("..", false)."\\n";
    foreach($files as $file) {echo getinfo($file)."\\n";}"""
