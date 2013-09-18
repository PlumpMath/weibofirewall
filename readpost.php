<!DOCTYPE html>
<html>
<head>
<link href='http://fonts.googleapis.com/css?family=Fjalla+One' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=Alef' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=PT+Sans:400,700' rel='stylesheet' type='text/css'>
<link rel="stylesheet" href="css/firewall.css" type="text/css" />
</head>
<body>
<script src="http://code.jquery.com/jquery-latest.min.js"></script>
<script src="js/moment.min.js"></script>
<script src="js/jquery.hoverIntent.minified.js"></script>
<script src="js/jquery.ae.image.resize.min.js"></script>
<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>

<?php
$datafile = "data/deleted_weibo_log.csv";
$imgdir = "weibo_images/";
$post_id = $_GET["post_id"];

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

function csv_get_post($post_id, $filename='', $delimiter=',')
{

	if(!$post_id)
		return FALSE;

    if(!file_exists($filename) || !is_readable($filename))
        return FALSE;

    $header = NULL;
    $data = array();
    if (($handle = fopen_utf8($filename, 'r')) !== FALSE)
    {
        while (($row = fgetcsv($handle, 5000, $delimiter)) !== FALSE)
		{

            if(!$header) {
				$header = $row;
//				array_push($data, $header);
			}
			else
//				print_r($row[0]);
				if($row[0] == $post_id) {
					print_r($row);
					//print count($header);
					$headerlen = count($header);
					// okay we got it. let's split data into post info and log info
					$postinfo = array_combine($header, array_slice($row, 0, $headerlen));
					$loginfo = array_slice($row, $headerlen + 1);
					array_push($data, $postinfo);
					array_push($data, $loginfo);
					return $data;
				}
        }
        fclose($handle);
    }
//    return $data;
}
?>


<div id="container">

<?php
	$data = csv_get_post($post_id, $datafile);
	print_r($data);
	print "<img src=" . $imgdir . $post_id . ".jpg>";
?>

</div>
</body>

</html>

