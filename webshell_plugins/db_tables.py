from libs.config import alias, color, gget
from webshell_plugins.db_shell import execute_sql_command


@alias(True, db="database")
def run(database: str = ""):
    """
    db_tables

    Output all tables of a database.
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    database = database if database else gget("db_dbname", "webshell")
    print(execute_sql_command("show tables;", database))
