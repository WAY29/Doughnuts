from libs.config import alias, color
from libs.myapp import send, randstr, is_windows

PREFIX_LIST = ["c", "cat", "w", "write", "e", "edit", "u", "upload", "mupload", "cp", "copy",
               "d", "download", "mdownload", "dump", "mv", "rm", "cd", "ls", "chmod", "touch"]


def get_php(splitchars):
    return """$umap=array();$gmap=array();
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
""" % splitchars


@alias(True, _type="COMMON")
def run():
    """
    ps

    (Only for *unix) Report a snapshot of the current processes.

    eg: ps

    """
    if (is_windows()):
        print(color.red(f"Only for target system is linux."))
        return False
    splitchars = randstr("!@#$%^&*()1234567890")
    res = send(get_php(splitchars))
    if (not res):
        return
    info_list = res.r_text.strip().split('\n')
    for line in info_list:
        info = line.split(splitchars)
        if (len(info) < 4):
            continue
        if (info[-1] != "CMDLINE"):
            info[-1] = color.cyan(info[-1])
        print("%-4s  %-8s  %-12s  %s" %
              (info[0], info[1], info[2], info[3]))