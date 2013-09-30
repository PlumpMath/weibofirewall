//var datafile = "../_archive/firewall_pre_git/data/130616_deleted_weibo.csv";
var datafile = "data/deleted_weibo_log.csv";
var datastartindex = 15;
var imgdir = "weibo_images/";
var chartwidth = 3960;
//var chartheight = 960;
var chartheight_padding = 80;
var chartpadding=100;
var barheight = 10;
var heightscale = 10; // reposts per pixel
var bargap = 1;
var bar_dateformat = d3.time.format("%b %e, %Y %H:%M");
var timepadding = 3600; //one hour
var colorMin = 50;
var colorMax = 220;
var randomTimeRange= 20;
var tickstrokecolor = "#444";
var url = document.URL;
var baseurl=url.substring(0,url.lastIndexOf("/"));

function pad (str, max) {
  str = str.toString();
  return str.length < max ? pad("0" + str, max) : str;
}

function lifespanFormat(seconds) {
	var minutes = Math.floor(seconds / 60);
	var hours = Math.floor(seconds / 3600);
	minutes = minutes % 60;
	seconds = seconds % 60;
	return pad(hours,2) + ":" + pad(minutes,2) + ":" + pad(seconds,2);
}

function dec2hex(i) {
	var hex = i.toString(16);
  	var padhex = hex.length < 2 ? dec2hex("0" + hex, 2) : hex;
	return padhex;

}

function randomTimeOffset() {
	return Math.ceil((Math.random() * randomTimeRange) + (randomTimeRange / 2));
}

function epochToDate(epoch) {
	return new Date(epoch * 1000);
}

function getcolor_byuser(d) {
// generate colors per user 
	var dig = dec2hex((d.user_id) % 256);
	var thiscolor_byuser = "#" + dig + "FF" + dig;
	var thiscolor_byuser_2 = "#" + ((d.user_id) % 16777216).toString(16);

	////console.log(thiscolor_bytime);
	//return thiscolor_bytime;
//	var thiscolor_byuser = getcolor_byuser(d.user_id);
	return thiscolor_byuser_2;
}

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
post_repostlog

 */


//get delimiter from weibo_settings.py
var dsv = d3.dsv("|||", "text/plain");

// read the datafile.START
dsv(datafile, function(d, i) {
//		////console.log(d);
	//
	// this is the format of what we need, adopted from weibo_module's make_csvline_from_post 
	if(i < datastartindex) {
		return null;
	} 
	//console.log(d);
	return {
		post_id: +d.post_id,
		user_id: parseFloat(d.user_id),
		user_name: d.user_name,
		user_follower_count_initial: +d.user_follower_count_initial,
		user_follower_count: +d.user_follower_count,
		post_original_pic: d.post_original_pic,
		post_created_at : epochToDate(d.post_created_at_epoch),
		post_repost_count_initial: +d.post_repost_count_initial,
		post_repost_count: +d.post_repost_count,
		post_text: d.post_text,
		started_tracking_at: epochToDate(+d.started_tracking_at_epoch),
		is_deleted: d.is_deleted,
		is_retired: d.is_retired,
		error_message: d.error_message,
		error_code: +d.error_code,
		last_checked_at: epochToDate(+d.last_checked_at_epoch),
		post_lifespan: +d.post_lifespan,
		post_repostlog: d.post_repostlog
	};
}, function(error, rows) {

	// now let's massage that data
	var data = rows;
	var chartheight = ((barheight + bargap) * data.length) + chartheight_padding;

//	////console.log(data.length);
	data.sort(function(a,b) { return a.post_created_at - b.post_created_at; });
//	////console.log(data.length);
	//console.log(data)

	var mindate = d3.min(data, function(d) { return d["post_created_at"]; });
	var maxdate = d3.max(data, function(d) { return d["last_checked_at"]; });


	////console.log(data.length);	

	////console.log("mindate = " + mindate)
	////console.log("maxdate = " + maxdate)

	// create chart, set dimensions based on # of deleted posts
	var chart = d3.select("#chartdiv")
		.append("svg")
		.attr("class", "chart")
		.attr("width", chartwidth)
		.attr("height", chartheight)
		.append("g");

	// let's specify the x-axis scale
	var scaleTime = d3.time.scale()
		// domain is min max of time
		.domain([mindate, maxdate])
		.range([chartpadding, chartwidth - chartpadding])

	// let's specify color scale
	var scaleTimeForColor = d3.time.scale.utc()
		.domain([mindate, maxdate])
		.range([colorMin, colorMax])
		.nice(d3.time.hour);

	// let's specify x-axis
	var axisTime = d3.svg.axis()
		.scale(scaleTime)
		.orient("top")
		.ticks(d3.time.hour, 12)
		.tickFormat(d3.time.format("%m-%d %H:%m"));

	var barselect_mouseover = function(d, i) {
//		console.log(d["post_id"]);
//		d3.select(d3.event.target).classed("highlight", true); 
		//d3.selectAll(".postdiv .post-" + d["post_id"]).classed("hover", true); 
		d3.selectAll(".postdiv.post-" + d["post_id"]).classed("posthover", true); 

		//highlight same users
		d3.selectAll(".user-" + d["user_id"]).classed("same-user-hover", true);
	}

	var barselect_mouseout = function(d, i) {
//		d3.select(d3.event.target).classed("highlight", false); 
//		d3.select(".postdiv .post-" + d["post_id"]).classed("hover", false);
//		d3.selectAll(".postdiv.post-" + d["post_id"]).classed("posthover", false); 
//		d3.select("text[name='" + d["post_id"] + "']").classed("hover", false);

		//highlight same users
		d3.selectAll(".user-" + d["user_id"]).classed("same-user-hover", false);
	}

	var barselect_click = function(d, i) {
		var thispostid = d["post_id"];
		//alert(imgdir + (data[thisid].post_id) + ".jpg");
		window.location = "readpost.php?post_id=" + thispostid;
		//window.location = (imgdir + (thispostid) + ".jpg");
	}

	// add x-axis ticks
	chart.selectAll("line")
		.data(scaleTime.ticks(d3.time.day, 1)).enter()
		.append("line")
		.attr("class", "tickline")
		.attr("x1", scaleTime)
		.attr("x2", scaleTime)
		.attr("y1", 0)
		.attr("y2", chartheight)
		.style("stroke", tickstrokecolor);

	// Add the x-axis labels
	chart.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + (chartheight - 1) + ")")
		.call(axisTime)
		//rotate the text, too
		.selectAll("text")  
            .style("text-anchor", "start")
            .attr("dx", "5em")
            .attr("dy", "4em")
            .attr("transform", function(d) {
                return "rotate(-45)" 
                });

	// let's select the postsdiv, and add our images to it that will hover
	var postsdiv = d3.select("#postsdiv");
	postsdiv.selectAll("div")
		// plug in our data
		.data(data).enter()
		// wrap everything in a div
		.append("div")
			.attr("class", function(d, i) { return "postdiv post-" + d["post_id"] + " user-" + d["user_id"]; })
		//let's add an img tag with all this stuff
		.append("img")
			.attr("src", function(d) { 
					var thisimage = imgdir + d["post_id"] + "." + d["post_original_pic"].split(/[\.]+/).pop(); 
					var thisresizedimage = "https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?url=" 
						+ baseurl 
						+ thisimage 
						+ "&container=focus&resize_w=300&resize_h=300&refresh=2592000";
					return thisimage;
					return thisresizedimage;
			})
			.attr("class", "resizeme")
//			.attr("id", function(d,i) { return "hoverpost-" + d["post_id"]; });

	// let's select the chart and add our bars to it	
	chart.selectAll("bar")
		// plug in our data
		.data(data).enter()
		//and now:
		 .append("rect")
		 .attr("x", function(d, i) { 
			 ////console.log("post_created_at " + d["post_created_at"]);
			 ////console.log("scaled = " + scaleTime((d["post_created_at"]))); 
			 return scaleTime(d["post_created_at"]); 
		 })

		.attr("y", function(d, i) { return i * (barheight + bargap); })
		 //.attr("width", function(d) { return (scaleTime(d["post_created_at"])); })
		.attr("width", function(d) { 
			elapsedtime = scaleTime(d["last_checked_at"]) - scaleTime(d["post_created_at"]); 
			////console.log(elapsedtime);
			//return (scaleTime(maxdate) - scaleTime(d["post_created_at"])); 
//			return 100;
			return elapsedtime;
		})
		 //.attr("width", function(d) { return ; })
		 .attr("height", barheight)
		 .attr("name", function(d, i) { return d["post_id"]; })
		 .attr("fill", function(d) { 

				// generate colors per user 

				// generate colors by time
				elapsedtimecolor = scaleTimeForColor(d["last_checked_at"]) - scaleTimeForColor(d["post_created_at"]); 
				var thiscolor_value = dec2hex(colorMax - (Math.round(elapsedtimecolor)));
				// create hexvalue
				thiscolor_bytime = "#" + thiscolor_value + thiscolor_value + thiscolor_value;				
				var thiscolor_byuser = getcolor_byuser(d);
				return thiscolor_bytime;
				//return thiscolor_byuser;
			})
	  .on("mouseover", barselect_mouseover)
	  .on("mouseout", barselect_mouseout) 
	  .on("click", barselect_click);

	// let's select the chart and add our bars to it	
	chart.selectAll("wedge")
		// plug in our data
		.data(data).enter()
		//and now:
		 .append("path")
		.attr('d', function(d, i) { 
			

			// GET X Y COORDINATES
			var x = scaleTime(d["post_created_at"]); 
			var y = i * (barheight + bargap) + (barheight / 2);

			// WIDTH = TIME, SCALED
			var width = scaleTime(d["last_checked_at"]) - scaleTime(d["post_created_at"]); 
			width += 5;
			var height = (d["post_repost_count"] - d["post_repost_count_initial"]);
			height /= heightscale;
			height += (barheight / 2); // have a minimum height
		
			// M syntax
			// MOVE TO (x-value) (y-value) 
			// RELATIVE LINE TO (width, height / w), 
			// RELATIVE LINE TO (0, -height), 
			// CLOSE LINE
			wedgestring =  'M ' + x +' '+ y + ' l ' + width + ' ' + (height / 2) + ' l 0 -' + height + ' z';


			if (d["post_repostlog"] == "") {
				return wedgestring;
			}

			// OKAY LET'S TRY A SPARKLINE
			//console.log("okay this is try :: " + i + " -- ");
			var repostlog = d["post_repostlog"].split(",");
			//console.log(repostlog.length);
			var repostlog_post_repost_count = [];
			var repostlog_checked_at = [];

			var checked_at_format = d3.time.format("%Y-%m-%d %H:%M:%S");

			for (var j = 0; j < repostlog.length; j+= 2) {
				repostlog_post_repost_count.push(repostlog[j]);
				repostlog_checked_at.push(checked_at_format.parse(repostlog[j+1]));
			}

			sparklinestring = 'M ' + x + ' ' + y + ' ';
			//string goes up
			for (var j = 0; j < repostlog_checked_at.length; j++) {
				var thisX = scaleTime(repostlog_checked_at[j]);
				var thisY = y - (repostlog_post_repost_count[j] / heightscale / 2);
				sparklinestring += 'L ' + thisX + ' ' + thisY + ' ';
			}
			//mirror this; string goes back to origin
			for (var j = repostlog_checked_at.length - 1; j >= 0; j--) {
//				//console.log("repostlog_checked_at " + j + " ::: " +repostlog_checked_at[j]);
				var thisX = scaleTime(repostlog_checked_at[j]);
//				//console.log("scaletTime = " + thisX);
				var thisY = y + (repostlog_post_repost_count[j] / heightscale / 2);
//				//console.log("thisY = " + thisY);
				sparklinestring += 'L ' + thisX + ' ' + thisY + ' ';
			}

			sparklinestring += ' z';

			//console.log(sparklinestring);
			return sparklinestring;
			//return wedgestring;
		})
		.style('opacity', .5)
		.attr("class", function(d, i) { return "post-" + d["post_id"] + " user-" + d["user_id"]; })
		 .attr("name", function(d, i) { return d["post_id"]; })
//		 .attr("fill", "none")
		 .attr("stroke-width", 1)
		 .attr("fill", function(d) { 

				// generate colors per user 
			 	var dig = dec2hex((d.user_id) % 256);
				var thiscolor_byuser = "#" + dig + "FF" + dig;
				var thiscolor_byuser_2 = "#" + ((d.user_id) % 16777216).toString(16);

				// generate colors by time
				elapsedtimecolor = scaleTimeForColor(d["last_checked_at"]) - scaleTimeForColor(d["post_created_at"]); 
				var thiscolor_value = dec2hex(colorMax - (Math.round(elapsedtimecolor)));
				// create hexvalue
				thiscolor_bytime = "#" + thiscolor_value + thiscolor_value + thiscolor_value;				
				////console.log(thiscolor_bytime);
				return thiscolor_bytime;
				var thiscolor_byuser = getcolor_byuser(d);
				return thiscolor_byuser;
			})
	  .on("mouseover", barselect_mouseover)
	  .on("mouseout", barselect_mouseout) 
	  .on("click", barselect_click);


	// add bar labels
	chart.selectAll("bar")
		.data(data).enter()
		.append("text")
//		.attr("x", function(d) { return 300; })
		.attr("x", function(d, i) { return scaleTime(d["post_created_at"]); })
		.attr("y", function(d, i) { return (i * (barheight + bargap)) + (barheight / 2); })
		.attr("dx", -3) // padding-right
		.attr("dy", ".35em") // vertical-align: middle
		.attr("text-anchor", "end") // text-align: right
		.attr("name", function(d, i) { return d["post_id"]; })
		.attr("class", function(d, i) { return "post-" + d["post_id"] + " user-" + d["user_id"]; })
//		.attr("fill", "#CCC")
		.text(function(d,i) { 
			////console.log(i);
			////console.log(d["last_checked_at"]);
			////console.log(d["post_created_at"]);
			////console.log(d["last_checked_at"].getTime());
			////console.log(d["post_created_at"].getTime());
			elapsedtimeseconds = (d["last_checked_at"].getTime() - d["post_created_at"].getTime()) / 1000; 
			////console.log(elapsedtimeseconds);
			return d["user_name"] + ":" + "lifespan: " + lifespanFormat(elapsedtimeseconds);
			return d["user_name"] + ": " + bar_dateformat(d["post_created_at"]) + "-- lifespan: " + lifespanFormat(elapsedtimeseconds);
		})
	  .on("mouseover", barselect_mouseover)
	  .on("mouseout", barselect_mouseout)
	  .on("click", barselect_click);


chart.selectAll("rect")
		 .data(data)
		.enter().append("rect")
		.attr("x", function(d) { return 0; })
		.attr("y", function(d, i) { return i * (barheight + bargap); })
		 .attr("width", function(d) { return chartwidth; })
		 .attr("height", barheight)
		 .attr("fill", "#FA3");

/*
postsdiv.selectAll("div").
		data(data).enter()
		.append("img")
		.attr("src", function(d) { return imgdir + d["post_id"] + "." + d["post_original_pic"].split(/[\.]+/).pop(); })
		.attr("class", "hoverpost resizeme")
		.attr("id", function(d,i) { return "hoverpost-" + d["post_id"]; });
*/

var durdiv = d3.select("#durdiv");
durdiv.selectAll("div")
		.data(data)
		.enter()
		.append("div")
		.text(function(d) { return rehumanize(moment.duration(maxdate - d["post_created_at"], 'seconds')); })
		 .attr("class", "duration")
		 .attr("name", function(d, i) { return i; })


//	chart.append("g").attr("class", "axis").call(axisTime);
	


	$( ".resizeme" ).aeImageResize({ height: 400, width: 400 });

	$("body").mousemove(function(e){
		  $('.posthover').css({'top': e.pageY + 10, 'left': e.pageX + 10});
	});
}); 
//END



