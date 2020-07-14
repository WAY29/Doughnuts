from ast import dump
import requests
from lxml import etree
from json import dumps
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

pool = ThreadPoolExecutor(10)
url = "https://gtfobins.github.io/"
url2 = "https://gtfobins.github.io/gtfobins/"
req = requests.get(url)
tree = etree.HTML(req.text)
clist = {}


def getcode(k):
    global clist
    req2 = requests.get(url2 + k)
    tree2 = etree.HTML(req2.text)
    for i in range(1, 15):
        try:
            title = tree2.xpath(
                "/html[1]/body[1]/h2[%d]/text()" % i)[0].strip()
            code = tree2.xpath(
                "/html[1]/body[1]/ul[3]/li[%d]/pre[1]/code[1]//text()" % i)[0].strip()
            clist[k][title] = code
        except Exception:
            break


for i in range(2, 302):
    try:
        cmd = tree.xpath(
            "/html[1]/body[1]/div[2]/table[1]/tbody[1]/tr[%d]/td[1]/a[1]/text()" % i)[0].strip()
        clist[cmd] = {}
    except Exception:
        break

tlist = [pool.submit(getcode, k) for k in clist.keys()]
wait(tlist, return_when=ALL_COMPLETED)
with open("gtfo.json", "w+") as f:
    f.write(dumps(clist, indent=2))
