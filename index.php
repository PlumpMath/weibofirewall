<?php
$useragent=$_SERVER['HTTP_USER_AGENT'];
if(preg_match('/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i',$useragent)||preg_match('/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i',substr($useragent,0,4)))
header('Location: index_mobile.php');
?>
<!DOCTYPE html>
<html>
<head>
<title>Jumping The Great Firewall</title>
<link href='http://fonts.googleapis.com/css?family=Crete+Round' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,300' rel='stylesheet' type='text/css'>
<!-- <link href='http://fonts.googleapis.com/css?family=Fjalla+One' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=Alef' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=PT+Sans:400,700' rel='stylesheet' type='text/css'> -->
<link href="js/iCheck/skins/flat/flat.css" rel="stylesheet">
<!-- <link rel="stylesheet" href="css/firewall.css" type="text/css" /> -->
<link rel="stylesheet/less" href="css/firewall.less" type="text/css" />
</head>

<body>
<script src="js/jquery-latest.min.js"></script>
<script src="js/less-1.4.1.min.js"></script>
<script src="js/moment.min.js"></script>
<script src="js/flowtype.min.js"></script>
<script src="js/purl.min.js"></script>
<script src="js/iCheck/jquery.icheck.min.js"></script>
<!-- <script src="js/jquery.hoverIntent.minified.js"></script>
<script src="js/lodash.min.js"></script>
<script src="js/jquery.transit.min.js"></script>
<script src="js/jquery.ae.image.resize.min.js"></script> -->
<script src="js/d3.v3.min.js"></script>
<script src="js/weibo_shared.js"></script>
<script src="js/weibo_index.js"></script>
<script type="text/javascript">
// Destroys the localStorage copy of CSS that less.js creates
 
function destroyLessCache(pathToCss) { // e.g. '/css/' or '/stylesheets/'
 
  if (!window.localStorage || !less || less.env !== 'development') {
    return;
  }
  var host = window.location.host;
  var protocol = window.location.protocol;
  var keyPrefix = protocol + '//' + host + pathToCss;
  
  for (var key in window.localStorage) {
    if (key.indexOf(keyPrefix) === 0) {
      delete window.localStorage[key];
    }
  }
}
$(document).ready(function() {
	//	destroyLessCache();
	$("#infobox").click(function() {
		$("#infooverlay, .shadow").fadeToggle(300);
	});
	$("#infooverlay, .shadow").click(function() {
		$("#infooverlay, .shadow").fadeToggle(300);
	});

	less.watch();
});
</script>

<div id="container">
	<div id="loadingsplash">
		<img src="images/loading.gif">
	</div>

	<div id="chartdiv"></div>
	<div id="postsdiv"></div>


	<div id="infobox">
		<div id="infobox-inner">
			<div class="logo">
			   Jumping The Great Firewall
			</div>
			<div class="teaser">
				More
			</div>
		</div>
	</div>

	<div id="infooverlay">
		<div id="infooverlay_inner">
			<div class="info">

<div class="title">Jumping the Great Firewall</div>
<div class="description">
<p>This project is an attempt at the visualization of a relatively new phenomenon: online free expression in China. It examines some innovative strategies employed by users of Weibo, an extremely popular Twitter-like micro-blogging platform.</p>

<p>Use of the Internet in China is policed -- watched over, censored, and punished -- by a human and technological program that has been nicknamed 'The Great Firewall'. The aim is to keep politically unacceptable or "sensitive" content (words and articles about the Tiananmen Square massacre, for example) invisible to Chinese Internet users. Twitter and Facebook are largely blocked, as are many news outlets and human rights web sites; web searches are seriously curtailed; sensitive words are blocked; and online postings and other content is routinely removed, blog posting removed. For many Chinese users who wish to access blocked web sites, the only option is a Virtual Private Network (VPN), a virtual leap over the Great Firewall.</p>

<p>We examined a different strategy that has emerged in Weibo blogging, where users can insert images directly into their postings, without links. Images are much more difficult for automated search programs to analyze, which allows image-based content to spread more widely before it is detected and removed. Taking advantage of this, some users now turning writing into images, taking screenshots of their own and others' controversial posts before they're removed, then posting and re-posting them. Visualized here are many such deleted posts from September 8th to November 13th, in 2013.</p>
</div>
<div class="credits">
Some of the research for this investigation was conducted in collaboration with a team at the <a href="http://www.spatialinformationdesignlab.org/">Spatial Information Design Lab</a> and the <a href="http://brown.stanford.edu/">Brown Institute for Media Innovation</a>, at Columbia University. The Columbia project, called "Jumping the Great Firewall", uses a similar methodology and was pursued in partnership with the <a href="http://www.pen.org/">Pen American Center</a> and <a href="http://thomsonreuters.com/">Thomson Reuters</a>.
</div>
			</div>
		</div>
	</div>

	<div class="shadow"></div>

</div> <!-- container -->


<!-- Start of StatCounter Code for Default Guide -->
<script type="text/javascript">
var sc_project=9375325; 
var sc_invisible=1; 
var sc_security="e5abcdce"; 
var scJsHost = (("https:" == document.location.protocol) ?
	"https://secure." : "http://www.");
document.write("<sc"+"ript type='text/javascript' src='" +
	scJsHost+
	"statcounter.com/counter/counter.js'></"+"script>");
</script>
	<noscript><div class="statcounter"><a title="hit counter"
	href="http://statcounter.com/" target="_blank"><img
	class="statcounter"
src="http://c.statcounter.com/9375325/0/e5abcdce/1/"
alt="hit counter"></a></div></noscript>
<!-- End of StatCounter Code for Default Guide -->


</body>

</html>

