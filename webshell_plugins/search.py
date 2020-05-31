from libs.config import alias, color
from libs.myapp import send


def get_php(pattern: str):
    return """function rglob($pattern, $flags = 0) {
    $files = glob($pattern, $flags);
    foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir) {
        $files = array_merge($files, rglob($dir.'/'.basename($pattern), $flags));
    }
    return $files;
}
print(join("\\n",rglob("%s")));""" % pattern


@alias(True, p="pattern")
def run(pattern: str):
    """
    read

    Search file(s) from target system.

    eg: search {pattern}
    """
    res = send(get_php(pattern))
    if (not res):
        return
    files = res.r_text.strip()
    if (len(files)):
        print("\n" + color.green("Search Result:") + "\n    " + files.replace("./", "").replace("\n", "\n    ") + "\n")
    else:
        print("\n" + color.red("File not exist / Search error") + "\n")
