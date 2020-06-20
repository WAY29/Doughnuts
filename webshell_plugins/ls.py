from libs.config import alias, color
from libs.myapp import send
from libs.app import readline


def get_php(path):
    return """function getprems($file){
$perms = fileperms($file);
$info='upcudubu-ulusuuuuu'[($perms&0xF000)>>12];
for($bit=8;$bit>=0;$bit--){
  $info .= ($perms&0x01ff)>>$bit & 1 ? ( !($bit%%3) ? (((($perms >> 9) & 0x7) >> ($bit / 3)) & 1 ? 'tss'[$bit/3] :'x') :'wr'[($bit-1)%%3] ): ( !($bit%%3) ? (((($perms >> 9) & 0x7) >> ($bit / 3)) & 1 ? 'TSS'[$bit/3] : '-'):'-');
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
function getinfo($file){
    $islinux = strtoupper(substr(PHP_OS,0,3))==='WIN'?FALSE:TRUE;
    $format="%%s %%s %%s %%s %%s %%s";
    $filename=!is_link($file)?basename($file):basename($file).' -> '.readlink($file);
    $owner=fileowner($file);
    $group=filegroup($file);
    return sprintf($format, getprems($file), $owner, $group, getfilesize($file),getmtime($file),$filename);
}
$files=glob("%s/*");
echo "Listing: ".realpath("%s")."\\n";
echo "==============================\\n";
echo "MODE        UID   GID     Size  MTIME         NAME\\n";
foreach($files as $file) {echo getinfo($file)."\\n";}""" % (path, path)


@alias(True, func_alias="dir", p="path")
def run(path: str = "."):
    """
    ls

    List information about the files.

    eg: ls {path=.}
    """
    res = send(get_php(path))
    if (not res):
        return
    info_list = res.r_text.strip().split('\n')
    print('\n'.join(info_list[:3]))
    ls_wordlist = []
    for line in info_list[3:]:
        info = line.split(" ")
        if (len(info) < 7):
            continue
        prems, name = info[0], info[-1]
        if (prems[0] == 'd'):
            info[-1] = color.cyan(name)
            info[3] = ''
        elif ('x' in prems):
            info[-1] = color.green(name)
        print("%s  %-4s  %-4s  %6s  %s  %s  %s" % (info[0], info[1], info[2], info[3], info[4], info[5], info[6]))
        ls_wordlist.append(info[6])
    readline.add_wordlist("ls_wordlist", ls_wordlist)
