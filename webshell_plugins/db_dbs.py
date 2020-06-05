from libs.config import alias, color, gget
from webshell_plugins.db_shell import execute_sql_command


@alias()
def run():
    """
    db_dbs

    Output all databases.
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    print(execute_sql_command("show databases;", ""))
