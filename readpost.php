<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html>
<head>
<link href='http://fonts.googleapis.com/css?family=Fjalla+One' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=Alef' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=PT+Sans:400,700' rel='stylesheet' type='text/css'>
<link rel="stylesheet" href="css/firewall.less" type="text/css" />
<style type ="text/css">
#container {
	width: 800px;
	margin: auto;
	padding: 30px 50px;
	background-color: white;
}
body {
	background-color: #666;
	font-family: Helvetica Neue, Helvetica, Arial, sans-serif;
}
a {
	color: #888;
}
a:hover {
	color: #BBB;
}

</style>
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
$imgdir = "weibo_blurred_images/";
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

	$mintimestamp = PHP_INT_MAX;
	$maxtimestamp= -1;

	//grab the post
	foreach($jsondata as $thisjson) {
		if($thisjson['started_tracking_at_epoch'] < $mintimestamp)
			$mintimestamp = $thisjson['started_tracking_at_epoch'];
		if($thisjson['last_checked_at_epoch'] > $maxtimestamp)
			$maxtimestamp = $thisjson['last_checked_at_epoch'];

		if($thisjson['post_id'] == $post_id) 
			$returndata["post"] = $thisjson;
	}

	// exit upon failure
	if(!$returndata["post"]) return -1;


	$sameuserposts = array();
	// grab other posts by same user
	foreach($jsondata as $thisjson) {
		if($thisjson['user_id'] == $returndata["post"]["user_id"]) {
			array_push($sameuserposts,$thisjson);
		}
	}

	$totallifespan = array_reduce($sameuserposts, function ($a, $thispost) { return $a += $thispost["post_lifespan"]; });

	$returndata["lifespan_tot"] =  $totallifespan;
	$returndata["num_other_posts"] = count($sameuserposts);
	$returndata["lifespan_avg"] =  $totallifespan  * 1.0 / count($sameuserposts);
	$returndata["mintimestamp"] = $mintimestamp;
	$returndata["maxtimestamp"] = $maxtimestamp;

	return $returndata;
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
	$returndata = json_get_post($post_id, $datafile, chr(31));

	if($returndata == -1) {
		print '<h1>POST #' . $post_id .' NOT FOUND</h1>';
	} else {

		$data = $returndata["post"];

		$thistext = $data["post_text"]; 
		print '
			<h1>Post #' . $post_id . ' info</h1>
			<h5>Tracking data from between ' . date('Y-m-d H:i:s', $returndata["mintimestamp"]) . " and " . date('Y-m-d H:i:s', $returndata["maxtimestamp"]) . ' -- ' . date('z \d\a\y\s H:i:s', $returndata["maxtimestamp"] - $returndata["mintimestamp"]) . '</h5>
			<h3>Post Text by user &lt;' . $data["user_name"] . '&gt;</h3>';
		print "<a href=http://translate.google.com/#zh-CN/en/" . $thistext . ">" . $thistext . "</a>";
		print "<h3>Lifespan: " .  gmdate("H:i:s", $data["post_lifespan"]) . "</h3>";
		print "<h3>Number of other deleted posts: " .  $returndata["num_other_posts"] . "</h3>";
		print "<h3>Average lifespan of other posts: " .  gmdate("H:i:s", $returndata["lifespan_avg"]) . "</h3>";
		print "<h4>Post created at " . $data["post_created_at"] . " Beijing time</h4>";
		print "<h4>Post last seen at " . $data["last_checked_at"] . " Beijing time</h4>";
		print	'<h3>Post Image</h3>';

		$ext = pathinfo($data["post_original_pic"], PATHINFO_EXTENSION);
		$imgname = $post_id . "." . $ext;

		if($do_tesseract == "true") { get_ocr_image($imgname); }

			print "<img src=" . $imgdir . $imgname .  ">";
		print "<h1>Raw Post Info</h1>";
		print '<pre>';
		print_r($data);
		print '</pre>';
	}
?>

</div>
</body>

</html>

