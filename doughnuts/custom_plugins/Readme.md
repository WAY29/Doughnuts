# custom plugins example

```python
# example.py

from libs.config import alias
from libs.myapp import send

# ? alias装饰器第一个参数为none_named_arg(true/FALSE),True即把没有参数名时传入的参数值顺序传入
# 更多插件编写方法请查看其它官方插件
@alias(True)
def run():
    """
    test

    just print test
    """
    # send函数向连接的webshell发送任意php命令
    res = send(f"print('test');")
    if (not res):
        return
    text = res.r_text.strip()
    print(text)
```