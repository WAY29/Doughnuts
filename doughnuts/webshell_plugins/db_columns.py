from libs.config import alias, color, gget
from webshell_plugins.db_shell import execute_sql_command


@alias(True, t="table")
def run(table: str):
    """
    db_columns

    Output all columns of a table.

    eg: db_columns {table}
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    database = gget("db_dbname", "webshell")
    print(execute_sql_command(f"show columns from {table};", database))
