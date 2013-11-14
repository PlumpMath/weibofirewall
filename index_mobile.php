<!DOCTYPE html>
<html>
<head>
<title>Jumping The Great Firewall</title>
<link href='http://fonts.googleapis.com/css?family=Crete+Round' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,300' rel='stylesheet' type='text/css'>
<!-- <link rel="stylesheet" href="css/firewall.css" type="text/css" /> -->
<link rel="stylesheet/less" href="css/firewall.less" type="text/css" />
</head>

<body class="mobile">
<script src="js/jquery-latest.min.js"></script>
<script src="js/less-1.4.1.min.js"></script>
<script src="js/flowtype.min.js"></script>
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
	less.watch();
});
</script>

<div id="container">

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
			<div class="mobilewarning">
			   The full visualization is not viewable on mobile devices. Please visit this page on a desktop browser.
			</div>
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
	<div id="mouseinfo">23pm</div>

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

