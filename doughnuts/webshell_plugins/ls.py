from libs.config import alias, color, order_alias
from libs.myapp import send
from libs.app import readline

PREFIX_LIST = []

def get_php(path, mode):
    scan_code = f'$files=scandir("{path}");sort($files);'
    if (mode == 2):
        scan_code = f'$files=glob("{path}/*");$pfiles=glob("{path}/.*");$files=array_merge($files,$pfiles);sort($files);'
    return """function getprems($file){
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
    $owner=fileowner($file);
    $group=filegroup($file);
    return sprintf($format, getprems($file), $owner, $group, getfilesize($file),getmtime($file),$filename);
}
%s
echo "Listing: ".realpath("%s")."\\n";
echo "==============================\\n";
echo "MODE        UID   GID     Size  MTIME         NAME\\n";
echo getinfo(".", false)."\\n";
echo getinfo("..", false)."\\n";
foreach($files as $file) {echo getinfo($file)."\\n";}""" % (scan_code, path)


@alias(True, func_alias="dir", p="path", m="mode")
def run(path: str = ".", mode: int = 1):
    """
    ls

    List information about the files.

    eg: ls {path=.} {mode=1}

    mode:
      - 1 : scandir
      - 2 : glob
    """
    global PREFIX_LIST
    if (not PREFIX_LIST):
        prefix_list = ["c", "w", "e", "u", "d", "mv", "rm", "chmod", "touch"]
        PREFIX_LIST = prefix_list + [order_alias(c) for c in prefix_list]
    res = send(get_php(path, mode))
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
   
    for prefix in prefix_list:
        readline.add_prefix_wordlist(prefix, ls_wordlist)
