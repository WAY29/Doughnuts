from libs.config import alias, color
from libs.myapp import send, is_windows


@alias(True, f="web_file_path", m="mode")
def run(mode: str, *web_file_paths):
    """
    chmod

    (Only for *unix) Changes file(s) mode.

    eg: chmod {mode} {web_file_path}
    """
    if (is_windows()):
        print(color.red("Target system is windows."))
        return
    mode = str(mode)
    if (len(mode) < 4):
        mode = "0" + mode
    for each_file_path in web_file_paths:
        print(f"print(chmod('{each_file_path}', {mode}));")
        res = send(f"print(chmod('{each_file_path}', {mode}));")
        if (not res):
            return
        text = res.r_text.strip()
        if len(text):
            print(f"\nchmod {each_file_path} {mode} {color.green('success')}\n")
        else:
            print(f"\nchmod {each_file_path} {mode} {color.red('failed')}\n")
