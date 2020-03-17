"""
@Description: command-function: exit
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from libs.config import alias, color
from os import path


@alias(True, "s")
def run():
    """
    show

    Show log webshells
    """
    if not path.exists("webshell.log"):
        print(color.red("No webshell.Log"))
        return 0
    with open("webshell.log", "r") as f:
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
