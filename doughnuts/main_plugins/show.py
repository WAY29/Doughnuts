from libs.config import gget, alias, color
from os import path


@alias(True, "s")
def run():
    """
    show

    Show log webshells.
    """
    root_path = gget("root_path")
    webshell_log_path = path.join(root_path, "webshell.log")
    if not path.exists(webshell_log_path):
        print(color.red("No webshell.Log"))
        return 0
    with open(webshell_log_path, "r") as f:
        lines = f.readlines()
        for index, line in enumerate(lines, 1):
            data = line.strip().split("|")
            if (len(data) < 3):
                continue
            data[2] = f"$ {data[2]} $"
            for func in data[3:]:
                data[2] = f"{func}({data[2]})"
            print(
                f"[{color.blue(str(index))}] [{color.yellow(data[1])}] {data[0]}  {color.green(data[2])}"
            )
        return len(lines)
