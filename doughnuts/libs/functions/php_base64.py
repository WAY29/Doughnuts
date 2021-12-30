#  base64函数实现
def get_php_base64_encode():
    return """
function b64e($s){$l=strlen($s);$t="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";$r="";$p=$l%3;for($i=0;$i<$l;){$a=array(ord($s[$i++]),($i<$l)?ord($s[$i++]):0,($i<$l)?ord($s[$i++]):0);$r.=$t[($a[0]>>2)&0x3f].$t[(($a[0]<<4)|($a[1]>>4))&0x3f].$t[(($a[1]<<2)|($a[2]>>6))&0x3f].$t[$a[2]&0x3f];}return $p?substr_replace($r,str_repeat("=",3-$p),strlen($r)+$p-3):$r;}
"""
def get_php_base64_decode():
    return """
function b64d($s){$l=strlen($s);$t="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";$r="";for($i=0;$i<65;$i++){$f[ord($t[$i])]=$i;}for($i=0;$i<$l;){$e=array($f[ord($s[$i++])],$f[ord($s[$i++])],$f[ord($s[$i++])],$f[ord($s[$i++])]); $r.=chr((($e[0]<<2)|($e[1]>>4))).chr((($e[1]<<4)|($e[2]>>2))).chr((($e[2]<<6)|($e[3])));}return substr($r,0,floor(strlen($s=str_replace("=","",$s))/4*3));}
  """
