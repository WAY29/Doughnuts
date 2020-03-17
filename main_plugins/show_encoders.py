"""
@Description: command-function: exit
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from libs.config import alias, color
from libs.config import gget


@alias(True, "se")
def run():
    """
    show

    Show avilable encoders
    """
    encoders_pf = gget("encode.pf")
    if (not len(encoders_pf)):
        return
    print(color.cyan("Encoders:"))
    for encoder in encoders_pf.names():
        print(f"    {encoder}")
