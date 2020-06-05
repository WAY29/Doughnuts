from libs.config import alias, color, gget


@alias()
def run():
    """
    db_info

    Output database information.
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    print(f"\nCurrenct User:\n  {gget('db_current_user', 'webshell')}\n")
    print(f"\nMysql Version:\n  {gget('db_version', 'webshell')}\n")
