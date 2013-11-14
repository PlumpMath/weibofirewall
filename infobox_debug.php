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
<style>
.postdiv {
	opacity: 1 !important;
}
.marker {
	position: absolute;
	color: red;
}
</style>
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
<script src="js/jquery.ae.image.resize.min.js"></script> 
<script src="js/d3.v3.min.js"></script>
<script src="js/weibo_shared.js"></script>
<script src="js/weibo_index.js"></script>
-->
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
		  $('.marker').css({'top': 400 + 0, 'left': 200 + 0});
		  $('.postdiv').css({'top': 400 + 10, 'left': 200 + 10});

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
	<div id="durdiv"></div>
	<div class="marker">x</div>
	<div id="postsdiv">
<div class="postdiv post-3621259898107062 user-20587"><div class="section_info_wrapper"><div class="section_info"><div class="postinfo"><div class="user_name">ANON</div><div class="post_created_at">2013-09-11 08:25 CST</div><div class="post_text"><span class="text_quote">"</span>【蠢】一个大厦摇摇欲坠，一个大堤千疮百孔，一个高压锅眼见爆炸，不是修，不是补，也不是疏通和改善，是用镰刀和锤子胁迫觉醒者失声，用劳教和判刑让反抗者闭嘴。一个2高让某个组织愚蠢的嘴脸昭然示众。想想其实愚蠢其实是它们与生俱来的特性。不愚蠢，能做到前三十年把人饿死，后三十年把人毒死？！</div></div><div class="userinfo"><div class="post_lifespan">Deleted within <span class="post_lifespan">1 hours, 35 minutes</span></div><div class="lifespan_avg">Average deletion time of this user's posts:<span class="lifespan_avg">1 hours, 43 minutes</span></div></div></div></div><div class="section_image"><img class="post_image" src="https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?url=http://vps.provolot.com/SIDL/firewall_dev/weibo_blurred_images/3621259898107062.jpg&amp;container=focus&amp;resize_h=200&amp;refresh=2592000"></div></div>
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

