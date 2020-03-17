"""
@Description: command-function: help
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:31:16
"""
from codecs import getencoder
from libs.config import alias


@alias(True)
def run(data: str):
    return getencoder("rot-13")(data)[0]
