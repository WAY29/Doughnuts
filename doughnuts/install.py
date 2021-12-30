from os import path, chmod
from sys import path as pyfpath, executable, argv
from libs.config import color
from libs.myapp import is_windows
from os import environ

# doughnuts.py所在/启动目录
cpath = path.split(path.realpath(__file__))[0]
# python可执行文件目录
pypath = executable
# 添加doughnuts.py所在/启动目录到python环境变量中
pyfpath.append(cpath)
# 默认执行名称
filename = "doughnuts" if len(argv) != 2 or not argv[2] else argv[2]

def install():
    # 如果非windows
    if not is_windows(False):
        if "/usr/local/bin" not in environ["PATH"]:
            print(color.red("please add /usr/local/bin to $PATH"))
            exit(1)
        # 写入执行脚本
        fpath =  f"/usr/local/bin/{filename}"
        fcontents = f"#!/bin/sh\n{pypath} {cpath}/doughnuts.py $*"
        print(color.green(f"Try to generate {fpath}"))
        with open(fpath,"w+") as f:
            f.write(fcontents)
        chmod(fpath, 0o755)
        # 判断是否成功写入
        if (path.exists(fpath)):
            print(color.green("generate success!"))
        else:
            print(color.red("generate error!"))
    else:
        # windows安装
        fpath = f"{path.dirname(pypath)}\\{ filename}.bat"
        fcontents = f"""@echo off
:param
set str=%1
if "%str%"=="" (
    goto end
)
set allparam=%allparam% %str%
shift /0
goto param
:end
{pypath} {cpath}\\doughnuts.py %allparam%
"""
        print(color.green(f"Try to generate {fpath}"))
        with open(fpath, "w+") as f:
            f.write(fcontents)
        # 判断是否写入
        if (path.exists(fpath)):
            print(color.green("generate success!"))
        else:
            print(color.red("generate error!"))

if __name__ == '__main__':
    install()
