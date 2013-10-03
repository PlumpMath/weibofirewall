///////////////////////////////////////////////////
///////////////////////////////////////////////////
//D3 START
///////////////////////////////////////////////////
///////////////////////////////////////////////////
//
//get delimiter from weibo_settings.py
var dsv = d3.dsv("|||", "text/plain");

// read the datafile.START
dsv(datafile, function(d, i) {
//		////console.log(d);
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

	// sort data by created
	data.sort(function(a,b) { return a.post_created_at - b.post_created_at; });

	// get chart height
	var chartheight = ((barheight + bargap) * data.length) + chartheight_padding;

	// create chart, set dimensions based on # of deleted posts
	var chart = d3.select("#chartdiv")
		.append("svg")
		.attr("class", "chart")
		.attr("width", chartwidth)
		.attr("height", chartheight)
		.append("g");

	// get min and max dates
	var mindate = d3.min(data, function(d) { return d["post_created_at"]; });
	var maxdate = d3.max(data, function(d) { return d["last_checked_at"]; });

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

	// let's specify x-axis ticks
	var axisTime = d3.svg.axis()
		.scale(scaleTime)
		.orient("top")
		.ticks(d3.time.hour, 12)
		.tickFormat(d3.time.format("%m-%d %H:%m"));

	// add x-axis ticks
	chart.selectAll("line")
		.data(scaleTime.ticks(d3.time.day, tickinterval)).enter()
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
					return resizeimage(thisimage);
			})

	if(params["bar"] == "true") {

		// let's select the chart and add our bars to it	
		chart.selectAll("bar")
			// plug in our data
			.data(data).enter()
			//and now:
			.append("rect")
			.attr("x", function(d, i) { return scaleTime(d["post_created_at"]); })
			.attr("y", function(d, i) { return i * (barheight + bargap); })
			.attr("width", function(d) { return scaleTime(d["last_checked_at"]) - scaleTime(d["post_created_at"]); })
			.attr("height", barheight)
			.attr("name", function(d, i) { return d["post_id"]; })
			.attr("fill", function(d) { 

				if(params["colorbytime"] == "true") {
					// generate colors by time
					var thiscolor_bytime = getcolor_bytime(d);
					return thiscolor_bytime;
				} else {
					// generate colors per user 
					var thiscolor_byuser = getcolor_byuser(d);
					//return thiscolor_byuser;
				}	

			})
	}


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
				var thisX = scaleTime(repostlog_checked_at[j]) + wedgeMinimumX;
				var thisY = y - (repostlog_post_repost_count[j] / heightscale / 2);
				thisY -= wedgeMinimumY; //minimum so that unshared posts are still visible
				sparklinestring += 'L ' + thisX + ' ' + thisY + ' ';
			}
			//mirror this; string goes back to origin
			for (var j = repostlog_checked_at.length - 1; j >= 0; j--) {
				var thisX = scaleTime(repostlog_checked_at[j]) + wedgeMinimumX;
				var thisY = y + (repostlog_post_repost_count[j] / heightscale / 2);
				thisY += wedgeMinimumY; //minimum
				sparklinestring += 'L ' + thisX + ' ' + thisY + ' ';
			}

			sparklinestring += ' z';

			//console.log(sparklinestring);
			return sparklinestring;
			//return wedgestring;
		})
		.style('opacity', .5)
		.attr("class", function(d, i) { return "sparkline post-" + d["post_id"] + " user-" + d["user_id"]; })
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
			return d["user_name"];
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
		  $('.postdiv.hover').css({'top': e.pageY + 10, 'left': e.pageX + 10});
	});
}).on("progress", function(event){
        //update progress bar
		if (d3.event.lengthComputable) {
          var percentComplete = Math.round(d3.event.loaded * 100 / d3.event.total);
		  if(percentComplete == 100) { hideLoadingSplash(); }
          //console.log(percentComplete);
       }
    });
//END



