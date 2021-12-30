
def get_php_handle__sql_command(connect_type):
    if (connect_type == "pdo"):
        return """try{%s
$r=$con->query(base64_decode('%s'));
$rows=$r->fetchAll(PDO::FETCH_ASSOC);
foreach($rows[0] as $k=>$v){
    echo "$k"."%s";
}
echo "%s";
foreach($rows as $array){foreach($array as $k=>$v){echo "$v"."%s";};echo "%s";}
} catch (PDOException $e){
die("Connect error: ". $e->getMessage());
}"""
    elif (connect_type == "mysqli"):
        return """%s
$r=$con->query(base64_decode('%s'));
$rows=$r->fetch_all(MYSQLI_ASSOC);
foreach($rows[0] as $k=>$v){
    echo "$k"."%s";
}
echo "%s";
foreach($rows as $array){foreach($array as $k=>$v){echo "$v"."%s";};echo "%s";}"""
    else:
        return ""
