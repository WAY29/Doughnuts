from libs.config import alias, color
from libs.myapp import send, is_windows


sep = "\\" if is_windows() else "/"


def get_php(web_file_path: str, pattern: str):
    return """function rglob($pattern, $flags = 0) {
    $files = glob($pattern, $flags);
    foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir) {
        $files = array_merge($files, rglob($dir.'/'.basename($pattern), $flags));
    }
    return $files;
}
foreach(rglob("%s/*") as $v){
    if(preg_match("/%s/", $v)){print(str_replace(realpath("%s")."\\\\","",realpath($v))."\\n");}
}
""" % (web_file_path, pattern, web_file_path)


@alias(True, _type="DETECT", w="web_file_path", p="pattern")
def run(pattern: str, web_file_path: str = "."):
    """
    search

    Search file(s) from target system (Support regular expression).

    eg: search {pattern} {web_file_path="."}
    """
    web_file_path = str(web_file_path)
    res = send(get_php(web_file_path, pattern))
    if (not res):
        return
    files = res.r_text.strip()
    if (len(files)):
        print(f"\n{color.green('Search Result:')}")
        if (web_file_path == "./"):
            web_file_path = ""
        for f in files.split("\n"):
            print("    " + (f"{web_file_path}{sep}{f}" if web_file_path != "." else f))
        print()
    else:
        print(f"\n{color.red('File not exist / Search error')}\n")
