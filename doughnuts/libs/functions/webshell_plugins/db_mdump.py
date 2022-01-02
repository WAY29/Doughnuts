def get_php_table_name(connect_type):
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
    """
    if (connect_type == "mysqli"):
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
    """
    else:
        return ""


def get_php_table_row_number(connect_type):

    if (connect_type == "pdo"):
        return """%s
            if(!$con){
                die("Error : connect to sql failed...");
            }
            $content="";
            $table="%s";
            $table_list = $con->query("select count(*) from $table;");
            $result = $table_list->fetchAll();
            echo $result[0][0];
    """

    if (connect_type == "mysqli"):
        return """%s
            if(!$con){
                die("Error : connect to sql failed...");
            }
            $table="%s";
            $table_list = mysqli_query($con,"select count(*) from $table;");
            $result = mysqli_fetch_all($table_list);
            echo $result[0][0];
    """
    else:
        return ""


def get_php_table_construct(connect_type):

    if (connect_type == "pdo"):
        return """%s
            if(!$con){
                die("Error : connect to sql failed...");
            }
            $table_name="%s";
            $table_created_data = $con->query("show create table `$table_name`");
            $table_created_data_array = $table_created_data->fetch(PDO::FETCH_BOTH);
            $struct=str_replace("NOT NULL", "", $table_created_data_array['Create Table']);
            $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".$struct.";\\r\\n\\r\\n";
            echo base64_encode(gzdeflate($content));
    """

    if (connect_type == "mysqli"):
        return """%s
            if(!$con){
                die("Error : connect to sql failed...");
            }
            $table_name="%s";
            $table_created_data = mysqli_query($con,"show create table `$table_name`");
            $table_created_data_array = mysqli_fetch_array($table_created_data);
            $struct=str_replace("NOT NULL", "", $table_created_data_array['Create Table']);
            $content .= "DROP TABLE IF EXISTS `$table_name`;\\r\\n".$struct.";\\r\\n\\r\\n";
            echo base64_encode(gzdeflate($content));
            """
    else:
        return ""


def get_php_data(connect_type):

    if (connect_type == "pdo"):
        return """%s
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
        $vals = str_replace("''", "null", $vals);
        $content .= "insert into `$table_name` values($vals);\\r\\n";
        }
        echo base64_encode(gzdeflate($content));
    """

    if (connect_type == "mysqli"):
        return """%s
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
        $vals = str_replace("''", "null", $vals);
        $content .= "insert into `$table_name` values($vals);\\r\\n";
        }
        echo base64_encode(gzdeflate($content));
    """
    else:
        return ""
