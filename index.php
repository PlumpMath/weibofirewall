<!DOCTYPE html>
<html>
<head>
<title>Jumping The Great Firewall v9.999</title>
<link href='http://fonts.googleapis.com/css?family=Crete+Round' rel='stylesheet' type='text/css'>
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

	$('input').on('ifChecked', function(event){
		if(event.target.name == "graphstyle") {
			if(event.target.id == "wedge") params["graphstyle"] = "wedge"; 
			else if(event.target.id == "bar") params["graphstyle"] = "bar"; 
			else params["graphstyle"] = "sparkline"; 
			history.pushState(null, null, "?" + makeparamstring(params));
		}
		d3update(1000);
	}); 
	$('input').iCheck({
		checkboxClass: 'icheckbox_flat',
		radioClass: 'iradio_flat'
});

});
</script>

<div id="container">
	<div id="chartdiv"></div>
	<!--<div id="chartlegend"></div> -->
	<div id="durdiv"></div>
	<div id="postsdiv">
	</div>

	<div id="loadingsplash">
		<img src="images/loading.gif">
	</div>

	<div id="infobox">
		<div id="infobox-inner">
			<div class="logo">
			   Jumping The Great Firewall (alpha)
			</div><br>
			
			<div class="options">
				<div class="one_option">
					<input type="radio" name="graphstyle" id="bar" checked>
					<label for="bar">Bar</label>
				</div>
				<div class="one_option">
					<input type="radio" name="graphstyle" id="wedge" checked>
					<label for="wedge">Wedge</label>
				</div>
				<div class="one_option">
					<input type="radio" name="graphstyle" id="sparkline" checked>
					<label for="sparkline">Sparkline</label>
				</div>
			</div>
			<div class="info">
<i>In collaboration with Penn Voices, and Mark Hansen, Brown Institute, School of Journalism</i>
<br><br>
<b>Project Director</b><br>
Laura Kurgan<br>
<b>Research Associate and Data Visualization<br></b>
Dan Taeyoung Lee<br>
<b>Research Associate, School of Journalism<br></b>
Yi Du
<br><br>
This project is an attempt at the visualization of new phenomenon, which can be called free expression in China. The title, .Jumping the Great Firewall. derives from something that already is happening in China by the users of Weibo a Chinese, Twitter-like microblog. 
<br><br>
As we have all read on media around the world, The Internet in China is policed by something known as the Great Firewall. It is a name for a human and technological program that keeps unacceptable or .sensitive. content (words and articles about the Tiananmen Square massacre, for example), off the Chinese Internet and from the computers of those who could, potentially, create a movement inside the country. It is a system of control. Twitter and Facebook are therefore, blocked, as are many western news outlets and human rights web sites; web searches are seriously curtailed; sensitive words are blocked; and content is often removed. Those in China who wish to access blocked web sites, must do so via a Virtual Private Network, (VPN). This is known as jumping the Great Firewall.
<br><br>
There is a significant difference between Weibo, and Twitter: you can insert images directly into your post, without links. Images are a lot less searchable than text, which implies that content can spread more widely before it is detected. Those who know this, now take screenshots of controversial posts before they.re removed and re-post them. 
			</div>
		</div>
	</div>
</div>


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

