

def get_php_ps():
    return """
    $umap=array();$gmap=array();
        $s="%s";
        function getuname($uid) {
        global $umap;
        $uname = $umap[$uid];
        if (!$uname) return $uid;
        return $uname;
        }
        $dirs=scandir("/proc");
        $cmds = array();
        foreach ($dirs as $dir){
            if (is_numeric($dir)){
                $cmds[] = $dir;
            }
        }
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
        }

        if (is_readable("/proc")){
            unamemap();
            echo "PID".$s."UID".$s."STATUS".$s."CMDLINE\\n";
            foreach ($cmds as $pid){
                $cmdline = str_replace(urldecode("%%00"), " ", file_get_contents("/proc/$pid/cmdline"));
                $status = explode("\\n",file_get_contents("/proc/$pid/status"));
                $state = explode("\\t", $status[2]);
                $state = trim($state[1]);
                $uid = explode("\\t", $status[8]);
                $uid = trim($uid[1]);
                $uid = getuname($uid);
                echo "$pid$s$uid$s$state$s$cmdline\\n";
            }
        } else{
            echo "[-] /proc not readable";
        }
"""
