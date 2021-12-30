from os import remove
from uuid import uuid4
from libs.config import alias, color
from libs.myapp import execute_sql_command, open_editor, newfile


@alias(True, _type="DATABASE")
def run(editor: str = "", edit_args: str = ""):
    """
    execute

    execute Custom sql command by notepad / vi as default or your own editor, edit_args split by space.


    eg: db_exec {editor=""} {edit_args=""} execute code '"--wait"'
    """
    file_name = str(uuid4()) + ".sql"
    real_file_path = newfile(file_name)

    open_editor(real_file_path, editor, edit_args)
    with open(real_file_path, "r") as f:
        command = f.read()
        print(color.yellow("Execute sql command..."))
        form = execute_sql_command(command)
        if (form == ''):
            print(
                "\n" + color.red("Connection Error / SQL syntax error") + "\n")
        else:
            print(form)

    remove(real_file_path)
