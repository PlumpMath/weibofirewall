<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html>
<head>
<link href='http://fonts.googleapis.com/css?family=Fjalla+One' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=Alef' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=PT+Sans:400,700' rel='stylesheet' type='text/css'>
<link rel="stylesheet" href="css/firewall.less" type="text/css" />
</head>
<body>
<script src="js/d3.v3.min.js"></script>
<script src="js/jquery-latest.min.js"></script>
<script src="js/less-1.4.1.min.js"></script>
<script src="js/moment.min.js"></script>
<script src="js/jquery.hoverIntent.minified.js"></script>
<script src="js/jquery.ae.image.resize.min.js"></script>

<?php
$datafile = "data/deleted_weibo_log.json";
$imgdir = "weibo_images/";
$ocrimgdir = "weibo_ocr_images/";
$post_id = $_GET["post_id"];
$do_tesseract = $_GET["tesseract"];
$tesseractpath = "/usr/local/bin/tesseract";

function fopen_utf8($filename){
    $encoding='';
    $handle = fopen($filename, 'r');
    $bom = fread($handle, 2);
//    fclose($handle);
    rewind($handle);
    

    if($bom === chr(0xff).chr(0xfe)  || $bom === chr(0xfe).chr(0xff)){
            // UTF16 Byte Order Mark present
            $encoding = 'UTF-16';
    } else {
        $file_sample = fread($handle, 1000) + 'e'; //read first 1000 bytes
        // + e is a workaround for mb_string bug
        rewind($handle);
    
        $encoding = mb_detect_encoding($file_sample , 'UTF-8, UTF-7, ASCII, EUC-JP,SJIS, eucJP-win, SJIS-win, JIS, ISO-2022-JP');
    }
    if ($encoding){
        stream_filter_append($handle, 'convert.iconv.'.$encoding.'/UTF-8');
    }
    return  ($handle);
} 

function process_loginfo($loginfo) {
	$loginfo = str_getcsv($loginfo);
	$data = array();
	for($i = 0; $i < (count($loginfo)); $i+=2) {
		$thislog = array();
		$thislog['post_repost_count'] = $loginfo[$i];
		$thislog['checked_at'] = $loginfo[$i + 1];
		array_push($data, $thislog);
	}

	return $data;
}

function csv_get_post($post_id, $filename='', $delimiter=',')
{


	if(!$post_id)
		return FALSE;

	//cast to number
	$post_id += 0;

    if(!file_exists($filename) || !is_readable($filename))
        return FALSE;

    $header = NULL;
    $data = array();
    if (($handle = fopen_utf8($filename, 'r')) !== FALSE)
    {
		while (($row = fgets($handle, 4096)) !== FALSE) {
			$row_csv = mb_split($delimiter, $row);
			print $delimiter;

            if(!$header) {
				$header = $row_csv;
			}
			else
				if($row_csv[0] == $post_id) {
					$headerlen = count($header);
					// okay we got it. let's split data into post info and log info
					$postinfo = array_combine(array_slice($header, 0, $headerlen - 1), array_slice($row_csv, 0, $headerlen - 1));
					$loginfo = $row_csv[$headerlen - 1];
					$loginfo = process_loginfo($loginfo);
					$data["postinfo"] = $postinfo; 
					$data["loginfo"] = $loginfo; 
					return $data;
				}
		}
        fclose($handle);
    }
//    return $data;
}


function json_get_post($post_id, $filename='', $delimiter=',')
{
	// given filename and post id, get post

	if(!$post_id)
		return FALSE;


    if(!file_exists($filename) || !is_readable($filename))
        return FALSE;

	$context = stream_context_create(array('http' => array('header'=>'Connection: close\r\n')));
	$jsondata = json_Decode(file_get_contents($filename, false, $context), true);

	foreach($jsondata as $thisjson) {
		if($thisjson['post_id'] == $post_id) 
			return $thisjson;
	}
	
}


function get_ocr_image($imgname) {
	global $tesseractpath, $imgdir, $ocrimgdir;
	if(file_exists("$ocrimgdir$imgname.txt") == false && file_exists("$ocrimgdir$imgname.txt.txt") == false) {
		print `$tesseractpath $imgdir$imgname $ocrimgdir$imgname.txt -l chi_sim 2>&1`;
	}
}

?>


<div id="container">


<?php
	$data = json_get_post($post_id, $datafile, chr(31));
	$thistext = $data["post_text"]; 
	print "<h2>Post info</h2>";
	print "<a href=http://translate.google.com/#zh-CN/en/" . $thistext . ">" . $thistext . "</a>";
	print "<br>";

	$ext = pathinfo($data["post_original_pic"], PATHINFO_EXTENSION);
	$imgname = $post_id . "." . $ext;

	if($do_tesseract == "true") { get_ocr_image($imgname); }

	print "<img src=" . $imgdir . $imgname .  ">";
	print '<pre>';
	print_r($data);
	print '</pre>';
?>

</div>
</body>

</html>

