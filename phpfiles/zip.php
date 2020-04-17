<?php
ini_set('memory_limit', '2048M');
set_time_limit(0);
class PHPzip
{
var $file_count = 0 ;
var $datastr_len   = 0;
var $dirstr_len = 0;
var $filedata = '';
var $gzfilename;
var $fp;
var $dirstr='';
var $filefilters = array();
var $data;

function SetFileFilter($filetype)
{
$this->filefilters = explode('|',$filetype);
}
function unix2DosTime($unixtime = 0)
{
   $timearray = ($unixtime == 0) ? getdate() : getdate($unixtime);
   if ($timearray['year'] < 1980)
   {
    $timearray['year']    = 1980;
    $timearray['mon']     = 1;
    $timearray['mday']    = 1;
    $timearray['hours']   = 0;
    $timearray['minutes'] = 0;
    $timearray['seconds'] = 0;
   }
   return (($timearray['year'] - 1980) << 25) | ($timearray['mon'] << 21) | ($timearray['mday'] << 16) | ($timearray['hours'] << 11) | ($timearray['minutes'] << 5) | ($timearray['seconds'] >> 1);
}
function startfile($path = 'dodo.zip')
{
   $this->gzfilename=$path;
   $mypathdir=array();
   do
   {
    $mypathdir[] = $path = dirname($path);
   } while($path != '.');
   @end($mypathdir);
   do
   {
    $path = @current($mypathdir);
    @mkdir($path);
   }while(@prev($mypathdir));

   if($this->fp=@fopen($this->gzfilename,"w"))
   {
    @fclose($this->fp);
    return true;
   }
   return false;
}
function addfile($data, $name)
{
   $name = iconv("UTF-8","gbk//TRANSLIT",str_replace('\\', '/', $name));
   if(strrchr($name,'/')=='/')
    return $this->adddir($name);
   if(!empty($this->filefilters))
   {
    if (!in_array(end(explode(".",$name)), $this->filefilters))
    {
     return;
    }
   }
   $dtime = dechex($this->unix2DosTime());
   $hexdtime = '\x' . $dtime[6] . $dtime[7] . '\x' . $dtime[4] . $dtime[5] . '\x' . $dtime[2] . $dtime[3] . '\x' . $dtime[0] . $dtime[1];
   eval('$hexdtime = "' . $hexdtime . '";');
   $unc_len = strlen($data);
   $crc = crc32($data);
   $zdata   = gzcompress($data);
   $c_len   = strlen($zdata);
   $zdata   = substr(substr($zdata, 0, strlen($zdata) - 4), 2);
   $datastr = "\x50\x4b\x03\x04";
   $datastr .= "\x14\x00";            // ver needed to extract
   $datastr .= "\x00\x00";            // gen purpose bit flag
   $datastr .= "\x08\x00";            // compression method
   $datastr .= $hexdtime;             // last mod time and date
   $datastr .= pack('V', $crc);             // crc32
   $datastr .= pack('V', $c_len);           // compressed filesize
   $datastr .= pack('V', $unc_len);         // uncompressed filesize
   $datastr .= pack('v', strlen($name));    // length of filename
   $datastr .= pack('v', 0);                // extra field length
   $datastr .= $name;
   $datastr .= $zdata;
   $datastr .= pack('V', $crc);                 // crc32
   $datastr .= pack('V', $c_len);               // compressed filesize
   $datastr .= pack('V', $unc_len);             // uncompressed filesize
   $this->data.=$datastr;
   $my_datastr_len = strlen($datastr);
   unset($datastr);
   $dirstr = "\x50\x4b\x01\x02";
   $dirstr .= "\x00\x00";                 // version made by
   $dirstr .= "\x14\x00";                 // version needed to extract
   $dirstr .= "\x00\x00";                 // gen purpose bit flag
   $dirstr .= "\x08\x00";                 // compression method
   $dirstr .= $hexdtime;                  // last mod time & date
   $dirstr .= pack('V', $crc);            // crc32
   $dirstr .= pack('V', $c_len);          // compressed filesize
   $dirstr .= pack('V', $unc_len);        // uncompressed filesize
   $dirstr .= pack('v', strlen($name) ); // length of filename
   $dirstr .= pack('v', 0 );              // extra field length
   $dirstr .= pack('v', 0 );              // file comment length
   $dirstr .= pack('v', 0 );              // disk number start
   $dirstr .= pack('v', 0 );              // internal file attributes
   $dirstr .= pack('V', 32 );             // external file attributes - 'archive' bit set
   $dirstr .= pack('V',$this->datastr_len ); // relative offset of local header
   $dirstr .= $name;
   $this->dirstr .= $dirstr;
   $this -> file_count ++;
   $this -> dirstr_len += strlen($dirstr);
   $this -> datastr_len += $my_datastr_len;
}
function adddir($name)
{
   $name = str_replace("\\", "/", $name);
   $datastr = "\x50\x4b\x03\x04\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00";
   $datastr .= pack("V",0).pack("V",0).pack("V",0).pack("v", strlen($name) );
   $datastr .= pack("v", 0 ).$name.pack("V", 0).pack("V", 0).pack("V", 0);
   $this->data.=$datastr;
   $my_datastr_len = strlen($datastr);
   unset($datastr);
   $dirstr = "\x50\x4b\x01\x02\x00\x00\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00";
   $dirstr .= pack("V",0).pack("V",0).pack("V",0).pack("v", strlen($name) );
   $dirstr .= pack("v", 0 ).pack("v", 0 ).pack("v", 0 ).pack("v", 0 );
   $dirstr .= pack("V", 16 ).pack("V",$this->datastr_len).$name;
   $this->dirstr .= $dirstr;
   $this -> file_count ++;
   $this -> dirstr_len += strlen($dirstr);
   $this -> datastr_len += $my_datastr_len;
}
function createfile()
{
   $endstr = "\x50\x4b\x05\x06\x00\x00\x00\x00" .
   pack('v', $this -> file_count) .
   pack('v', $this -> file_count) .
   pack('V', $this -> dirstr_len) .
   pack('V', $this -> datastr_len) .
   "\x00\x00";
   return $this->data.$this->dirstr.$endstr;
}
}
function listfiles($dir=".")
{
  global $dodozip;
  $sub_file_num = 0;
  if(is_file("$dir"))
  {
    if(realpath($dodozip ->gzfilename)!=realpath("$dir"))
    {
      $dodozip -> addfile(implode('',file("$dir")),"$dir");
      return 1;
    }
    return 0;
  }

  $handle=opendir("$dir");
  while ($file = readdir($handle))
  {
    if($file=="."||$file==".."){
      continue;
    }

    if(is_dir("$dir/$file")){
      $sub_file_num += listfiles("$dir/$file");
    }else{
      if(realpath($dodozip ->gzfilename)!=realpath("$dir/$file")){
        $dodozip -> addfile(implode('',file("$dir/$file")),"$dir/$file");
        $sub_file_num ++;
      }
    }
  }
  closedir($handle);
  if(!$sub_file_num){
    $dodozip -> addfile("","$dir/");}
  return $sub_file_num;}
function Zip_action($dfiles){
  global $dodozip;
  $filenum = 0;
  foreach($dfiles as $file){
    if(is_file($file)){
      if(!empty($dodozip -> filefilters)){
        if (!in_array(end(explode(".",$file)), $dodozip -> filefilters)){
          continue;
        }
      }
    }
    $filenum += listfiles($file);
  }
   $filecode = $dodozip -> createfile();
   $filename=$_SERVER['HTTP_HOST'].".zip";
   header("Content-type: application/unknown");
   header("Accept-Ranges: bytes");
   header("Content-Disposition: attachment; filename=$filename");
   echo $filecode;
}
$params_=array();
$dodozip = new PHPzip();
$dfiles = array_diff(scandir("%s"),['.','..']);
Zip_action($dfiles);