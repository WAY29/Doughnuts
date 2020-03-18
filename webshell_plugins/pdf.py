from libs.config import color
from libs.myapp import send


def run():
    """
    pdf

    print disable_functions of website
    """
    text = send(f"print(ini_get('disable_functions'));").r_text.strip()
    disable_func_list = ["    " + f.strip() for f in text.split(",")]
    if len(text):
        print(color.green("\ndisable_functions:\n"))
        print("\n".join(disable_func_list) + "\n")
    else:
        print(f"{color.green('No disable_functions')} / {color.red('Read error')}")
