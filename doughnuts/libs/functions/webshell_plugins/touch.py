
def get_php_touch():
    return  """
    $arr = glob("*.*");
    $reference = $arr[mt_rand(0, count($arr) - 1)];
    $file='%s';
    if ($file==''){$file=basename($_SERVER['SCRIPT_NAME']);}
    
    if (file_exists($file)){
    touch($file, filectime($reference));
    echo $file.' as '.$reference;} else{
    print(file_put_contents($file,''));}
    """