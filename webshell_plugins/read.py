"""
@Description: command-function: whoami
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from libs.config import alias, color
from libs.myapp import send


@alias(True, func_alias="r")
def run(*web_file_paths: str):
    """
    read

    Read file(s) from website
    """
    for each_file_path in web_file_paths:
        text = send(f"print(file_get_contents('{each_file_path}'));").r_text.strip()
        if len(text):
            print("\n" + color.green(each_file_path))
            print("\n" + text + "\n")
        else:
            print("\n" + color.yellow(each_file_path))
            print("\n" + color.red("File not exist / Read error") + "\n")
