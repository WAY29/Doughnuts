def get_php_db_dump(connect_type):
    if connect_type == "pdo":
        return """
        set_time_limit(0); ignore_user_abort(1);
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
Sqldump();"""
    if connect_type == "mysqli":
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
Sqldump();"""
