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
<script>

//var datafile = "../_archive/firewall_pre_git/data/130616_deleted_weibo.csv";
var datafile = "data/deleted_weibo_log.csv";
var imgdir = "weibo_images/"
var chartwidth = 960;
var chartheight = 960;
var barheight = 10;
var bargap = 1;
var dateformat = d3.time.format("%b %e, %Y %H:%M");
var timepadding = 3600; //one hour
var colorMin = 50;
var colorMax = 200;
var randomTimeRange= 20;

function make_y_axis() {        
    return d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(5)
}

function dec2hex(i) {
	var hex = i.toString(16);
  	var padhex = hex.length < 2 ? dec2hex("0" + hex, 2) : hex;
	return padhex;

}

function randomTimeOffset() {
	return Math.ceil((Math.random() * randomTimeRange) + (randomTimeRange / 2));
}

/* THIS IS THE CSVLINE 
	*
	post_id,
user_id,
user_name,
user_follower_count_initial,
user_follower_count,
post_original_pic,
post_created_at,
post_created_at_epoch ,post_repost_count_initial,
post_repost_count,
post_text,
started_tracking_at,
started_tracking_at_epoch,
is_deleted,
is_retired,
error_message,
error_code,
last_checked_at,
last_checked_at_epoch,
post_lifespan

 */

// read the datafile.
d3.csv(datafile, function(d) {
	//	console.log(d);
	//
	// this is the format of what we need, adopted from weibo_module's make_csvline_from_post 
	return {
		post_id: +d.post_id,
		user_id: parseFloat(d.user_id),
		user_name: d.user_name,
		user_follower_count_initial: +d.user_follower_count_initial,
		user_follower_count: +d.user_follower_count,
		post_original_pic: d.post_original_pic,
		post_created_at : +d.post_created_at_epoch,
		post_repost_count_initial: +d.post_repost_count_initial,
		post_repost_count: +d.post_repost_count,
		post_text: d.post_text,
		started_tracking_at: +d.started_tracking_at_epoch,
		is_deleted: d.is_deleted,
		is_retired: d.is_retired,
		error_message: d.error_message,
		error_code: +d.error_code,
		last_checked_at: +d.last_checked_at_epoch,
		post_lifespan: +d.post_lifespan
	};
}, function(error, rows) {


	// now let's massage that data
	var data = rows;
	var chartheight = (barheight + bargap) * data.length;

	data.sort(function(a,b) { return a.post_created_at - b.post_created_at; });
	//data.sort(function(a,b) { return a.user_id - b.user_id; });
	//
//	console.log(data)

//	var maxtime = d3.max(data, function(d) { return d["post_created_at"]; }) + timepadding + (randomTimeRange / 2);
	var mintime = d3.min(data, function(d) { return d["post_created_at"]; });
	var maxtime = d3.max(data, function(d) { return d["last_checked_at"]; });

/*	console.log("hopefully sorted poster ids");
	console.log(data.map(function(d) { return d.user_id; }));	
	console.log(data.length);	*/


	// create chart, set dimensions based on # of deleted posts
	var chart = d3.select("#chartdiv")
		.append("svg")
			.attr("class", "chart")
			.attr("width", chartwidth)
			.attr("height", (barheight + bargap) * data.length)
		.append("g");

	// let's specify the x-axis
	var scaleTime = d3.scale.linear()
		// domain is min max of time
		.domain([mintime, maxtime])
		.range([0, chartwidth]);

	var scaleTimeForColor = d3.scale.linear()
		.domain([mintime, maxtime])
		.range([colorMin, colorMax]);

	var axisTime = d3.svg.axis()
		.scale(scaleTime)
		.orient("bottom")
		.ticks(5)
		.tickFormat(d3.time.format("%Y-%m-%d"));

	var mouseoverFunction = function(d, i) {
		d3.select(d3.event.target).classed("highlight", true); 
		d3.select("#hoverimg-" + i).classed("hover", true); 
	}

	var mouseoutFunction = function(d, i) {
		d3.select(d3.event.target).classed("highlight", false); 
		d3.select("#hoverimg-" + i).classed("hover", false); 
	}

	var imgdiv = d3.select("#imgdiv");


	imgdiv.selectAll("div").
		data(data).enter()
		.append("img")
		.attr("src", function(d) { return imgdir + d["post_id"] + ".jpg"; })
		.attr("class", "hoverimg resizeme")
		.attr("id", function(d,i) { return "hoverimg-" + i; });


	chart.selectAll("rect")
		 .data(data)
		.enter().append("rect")
		.attr("x", function(d) { return scaleTime(d["post_created_at"]); })
		.attr("y", function(d, i) { return i * (barheight + bargap); })
		 //.attr("width", function(d) { return (scaleTime(d["post_created_at"])); })
		 .attr("width", function(d) { return (randomTimeOffset() + scaleTime(maxtime) - scaleTime(d["post_created_at"])); })
		 //.attr("width", function(d) { return ; })
		 .attr("height", barheight)
		 .attr("name", function(d, i) { return i; })
		 .attr("fill", function(d) { 
				//console.log(moment.duration(maxtime - d["post_created_at"], 'seconds').humanize()); //duration
				var dig = dec2hex((d.user_id) % 256);
				var thiscolor = "#" + dig + "FF" + dig;
				var thiscolor2 = "#" + ((d.user_id) % 16777216).toString(16);
				console.log(scaleTimeForColor(maxtime) - scaleTimeForColor(d["post_created_at"]));
				//var thiscolor_time = dec2hex(Math.round(scaleTimeForColor(maxtime) - scaleTimeForColor(d["post_created_at"])));
				var thiscolor_time = dec2hex(colorMax - (Math.round(scaleTimeForColor(maxtime) - scaleTimeForColor(d["post_created_at"]))));
				console.log(thiscolor_time);
				console.log("#" + "FF" + thiscolor_time + thiscolor_time);				
				return "#" + "FF" + thiscolor_time + thiscolor_time;				
				//console.log(thiscolor2);
			});
/*	  .on("mouseover", mouseoverFunction)
	  .on("mouseout", mouseoutFunction);*/

	$("rect").hover(function() {
		var thisid = $(this).attr("name");
		$("#hoverimg-" + thisid).addClass("hover");
		$("text[name=" + thisid + "]").attr("class", "hover");
	}, function() {
		var thisid = $(this).attr("name");
		$("#hoverimg-" + thisid).removeClass("hover");
		$("text[name=" + thisid + "]").attr("class", "");
	});

	$("rect").click(function() {
		var thisid = $(this).attr("name");
		//alert(imgdir + (data[thisid].post_id) + ".jpg");
		window.location = (imgdir + (data[thisid].post_id) + ".jpg");

	});


	chart.selectAll("line")
		 .data(scaleTime.ticks(9))
	   .enter().append("line")
		  .attr("class", "tickline")
		 .attr("x1", scaleTime)
		 .attr("x2", scaleTime)
		 .attr("y1", 0)
		 .attr("y2", chartheight)
		 .style("stroke", "#EEE");

	chart.selectAll("text")
		 .data(data)
	   .enter().append("text")
		.attr("x", function(d) { return scaleTime(d["post_created_at"]) + 0; })
		.attr("y", function(d, i) { return (i * (barheight + bargap)) + (barheight / 2); })
		 .attr("dx", -3) // padding-right
		 .attr("dy", ".35em") // vertical-align: middle
		 .attr("text-anchor", "end") // text-align: right
		 .attr("name", function(d, i) { return i; })
		 .attr("fill", "#CCC")
		 .text(function(d) { 
			return dateformat(new Date(d["post_created_at"] * 1000)) + " -- " + rehumanize(moment.duration(maxtime - d["post_created_at"], 'seconds'));
		});

chart.selectAll("rect")
		 .data(data)
		.enter().append("rect")
		.attr("x", function(d) { return 0; })
		.attr("y", function(d, i) { return i * (barheight + bargap); })
		 .attr("width", function(d) { return chartwidth; })
		 .attr("height", barheight)
		 .attr("fill", "#FA3");


imgdiv.selectAll("div").
		data(data).enter()
		.append("img")
		.attr("src", function(d) { return imgdir + d["post_id"] + ".jpg"; })
		.attr("class", "hoverimg resizeme")
		.attr("id", function(d,i) { return "hoverimg-" + i; });


var durdiv = d3.select("#durdiv");
durdiv.selectAll("div")
		.data(data)
		.enter()
		.append("div")
		.text(function(d) { return rehumanize(moment.duration(maxtime - d["post_created_at"], 'seconds')); })
		 .attr("class", "duration")
		 .attr("name", function(d, i) { return i; })


//	chart.append("g").attr("class", "axis").call(axisTime);
	


	$( ".resizeme" ).aeImageResize({ height: 400, width: 400 });

	$("body").mousemove(function(e){
		  $('.hover').css({'top': e.pageY + 20, 'left': e.pageX + 20});
	});
});

function rehumanize(time){
	time = time._data;
    if(time.years   > 0){   return time.years   + ' years and '     + time.months   + ' months';}
    if(time.months  > 0){   return time.months  + ' months and '    + time.days     + ' days';}
    if(time.days    > 0){   return time.days    + ' days and '      + time.hours    + ' hours';}
    if(time.hours   > 0){   return time.hours   + ' hours and '     + time.minutes  + ' mins and ' + time.seconds + ' secs';}
    if(time.minutes > 0){   return time.minutes + ' mins and '   + time.seconds  + ' secs';}
    if(time.seconds > 0){   return time.seconds + ' secs';}
    return "Time's up!";
}

</script>


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

