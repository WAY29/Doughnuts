from re import match

from libs.app import readline
from libs.config import alias, color, gget, gset, set_namespace
from libs.myapp import send, execute_sql_command
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


@alias(_type="DATABASE")
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
                        "\n" + color.red("Connection Error / SQL syntax error") + "\n")
                else:
                    print(execute_sql_command(command, database))
    finally:
        gset("db_dbname", database, True, "webshell")
        readline.set_wordlist(wordlist)
