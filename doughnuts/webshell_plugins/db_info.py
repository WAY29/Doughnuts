from libs.config import alias, color, gget
from webshell_plugins.db_init import print_db_info


@alias(_type="DATABASE")
def run():
    """
    db_info

    Output database information.
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    print_db_info()
