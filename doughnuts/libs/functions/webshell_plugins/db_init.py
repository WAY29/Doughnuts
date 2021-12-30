
def get_php_db_init(connect_type):

    if connect_type == "mysqli":
        return """try{%s
            $r=$con->query('%s');
            $rr=$r->fetch();echo $rr[0]."\\n";
            $r=$con->query('%s');
            $rr=$r->fetch();echo $rr[0]."\\n";
            } catch (PDOException $e){
            die("Connect error: ". $e->getMessage());
        }"""
    if connect_type == "pdo":
        return """%s
            if (!$con)
            {
            die("Connect error: ".mysqli_connect_error());
            } else{
            $r=$con->query('%s');
            $rr=$r->fetch_all(MYSQLI_NUM);echo $rr[0][0]."\\n";$r->close();
            $r=$con->query('%s');
            $rr=$r->fetch_all(MYSQLI_NUM);echo $rr[0][0]."\\n";$r->close();
            $con->close();
        }"""