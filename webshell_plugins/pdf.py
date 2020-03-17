"""
@Description: command-function: whoami
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from libs.config import color
from libs.myapp import send


def run():
    """
    pdf

    print disable_functions of website
    """
    text = send(f"print(ini_get('disable_functions'));").r_text.strip()
    disable_func_list = ["    " + f.strip() for f in text.split(",")]
    if len(text):
        print(color.green("\ndisable_functions:\n"))
        print("\n".join(disable_func_list) + "\n")
    else:
        print(f"{color.green('No disable_functions')} / {color.red('Read error')}")
