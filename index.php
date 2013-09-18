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
<script src="js/weibo_index.js" charset="utf-8"></script>

<div id="container">
	<div id="chartdiv"></div>
	<div id="durdiv"></div>
	<div id="imagesdiv">
		<div id="imgdiv"></div>
	</div>

	<div id="infobox">
		<div id="infobox-inner">
			 <div class="logo">
			   Jumping The Great Firewall (alpha) </div>

			 <div class="info">
				Using data collected by Yi Du, the visualization seeks to outline a timeline of Weibo image posts, and their subsequent deletion by the human censors of the Great Firewall.
<br>
<br>
Note: This visualization prototype is currently working with limited data. For example, we are currently missing the specific deletion times for all Weibo posts. We hope to change the data collection process and to collect not only deletion times, but to track the increase in repost rate through time. As such, we hope to find a relationship between repost rate and deletion time -- suspecting that the faster a post is reposted, the faster it is deleted. 
<br>
<br>
			 The end goal is not to visualize censorship within a straightforward timeline, which displays a series of events as within an immutable, sealed-off history. Rather, the desire is to find an appropriate visualization that would express censorship as a series of sudden and violent acts, in order to posit a desired alternative to work towards -- namely, non-censored expression. 
			</div>
		</div>
	</div>
</div>
</body>

</html>

