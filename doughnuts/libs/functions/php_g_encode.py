
def get_php_g_encode(key):
    return """$ooDoo=ob_get_clean();
                    $encode = mb_detect_encoding($ooDoo, array('ASCII','UTF-8',"GB2312","GBK",'BIG5','ISO-8859-1','latin1'));
                    $ooDoo = mb_convert_encoding($ooDoo, 'UTF-8', $encode);
                    function encode_g($result,$key){
                        $easy_en = strrev(str_rot13($result));
                        $rlen = strlen($result);
                        $klen = strlen($key);
                        $s = str_repeat("\x00",$rlen);
                        for($c=0;$c<$klen;$c++){
                            $kr = strrev($key);
                            for($i=0;$i<$rlen;$i++){
                                $s[$i] = chr(base_convert(strrev(str_pad(base_convert(ord($easy_en[$i])^ord($key[$i%$klen]),10,2),8,"0",STR_PAD_LEFT)),2,10)^ord($kr[$i%$klen]));
                            }
                            $easy_en = $s;if($c == $klen - 1){
                                break;
                            }
                            for($k=0;$k<$klen;$k++){
                                $key[$k] = chr((ord($key[($k + 1)%$klen])^ord($key[$k])));
                                }
                            }
                        return $s;
                    }
                print(urlencode(encode_g($ooDoo, """ + '"' + key + '"' + """)));"""