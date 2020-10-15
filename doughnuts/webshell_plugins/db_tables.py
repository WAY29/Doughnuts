from libs.config import alias, color, gget
from libs.myapp import execute_sql_command


@alias(True, _type="DATABASE", db="database")
def run(database: str = ""):
    """
    db_tables

    Output all tables of a database.

    eg: db_init {database=current_database}
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    database = database if database else gget("db_dbname", "webshell")
    print(execute_sql_command("show tables;", database))
