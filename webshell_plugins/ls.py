from libs.config import alias, color
from libs.myapp import send


def get_php(path):
    return """function getprems($file){
$perms = fileperms($file);
switch ($perms & 0xF000) {
case 0xC000:
    $info = 's';
    break;
case 0xA000:
    $info = 'l';
    break;
case 0x8000:
    $info = '-';
    break;
case 0x6000:
    $info = 'b';
    break;
case 0x4000:
    $info = 'd';
    break;
case 0x2000:
    $info = 'c';
    break;
case 0x1000:
    $info = 'p';
    break;
default:
    $info = 'u';
}
$info .= (($perms & 0x0100)?'r':'-');
$info .= (($perms & 0x0080)?'w':'-');
$info .= (($perms & 0x0040)?(($perms & 0x0800)?'s':'x'):(($perms & 0x0800)?'S':'-'));
$info .= (($perms & 0x0020)?'r':'-');
$info .= (($perms & 0x0010)?'w':'-');
$info .= (($perms & 0x0008)?(($perms & 0x0400)?'s':'x'):(($perms & 0x0400)?'S':'-'));
$info .= (($perms & 0x0004)?'r':'-');
$info .= (($perms & 0x0002)?'w':'-');
$info .= (($perms & 0x0001)?(($perms & 0x0200)?'t':'x'):(($perms & 0x0200)?'T':'-'));
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
    # print("test,", info_list)
    for line in info_list[3:]:
        info = line.split(" ")
        prems, name = info[0], info[-1]
        # color_line = line
        # info[0] = color.cyan(name)
        if (prems[0] == 'd'):
            info[-1] = color.cyan(name)
            # color_line = color_line.replace(name, color.cyan(name))
        elif ('x' in prems):
            info[-1] = color.green(name)
            # color_line = color_line.replace(name, color.green(name))
        print("%s  %-4s  %-4s  %6s  %s  %s  %s" % (info[0], info[1], info[2], info[3], info[4], info[5], info[6]))
        # print(color_line)
