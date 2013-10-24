///////////////////////////////////////////////////
///////////////////////////////////////////////////
//D3 START
///////////////////////////////////////////////////
///////////////////////////////////////////////////
//
//get delimiter from weibo_settings.py
var dsv = d3.dsv("|||", "text/plain");
var wedges;

// read the datafile.START
dsv(datafile, dsvaccessor, function(error, rows) {

	params = purl().param();
	params = cleanparams(params);

	// now let's massage that data
	//var data = rows;
	var data = _.first(rows, 100);

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
		.attr("class", "x-axis")
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


	// let's select the chart and add our bars to it	
	chart.selectAll("bar")
		// plug in our data
		.data(data).enter()
		//and now:
		.append("rect")
		.attr("x", function(d, i) { return scaleTime(d["post_created_at"]); })
		.attr("y", function(d, i) { return yFunction(d, i) - barheight / 2; })
		.attr("width", function(d) { return scaleTime(d["last_checked_at"]) - scaleTime(d["post_created_at"]); })
		.attr("height", barheight)
		.attr("class", function(d, i) { return "bar post-" + d["post_id"] + " user-" + d["user_id"]; })
		.attr("name", function(d, i) { return d["post_id"]; })
		.attr("fill", function(d) { 

			return getthiscolor(d, scaleTimeForColor);

		})



// let's select the chart and add our wedges to it	
	wedges = chart.selectAll("wedge")
		// plug in our data
		.data(data)
		.enter()
		//and now:
		.append("path")
		.attr('d', function(d, i) { return wedgesparkline("wedge", d, i, scaleTime); })
		.attr('transform', function(d, i) { return transformwedgesparkline(d, i, scaleTime); })
		.style('opacity', 0.1)
		.attr("class", function(d, i) { return "wedge post-" + d["post_id"] + " user-" + d["user_id"]; })
		.attr("name", function(d, i) { return d["post_id"]; })
	.attr("stroke-width", 0.75)
		.attr("fill", "none")
//		.attr("stroke", function(d) { return getthiscolor(d, scaleTimeForColor); })
		.attr("fill", function(d) { return getthiscolor(d, scaleTimeForColor); })
	.on("mouseover", barselect_mouseover)
	.on("mouseout", barselect_mouseout) 
	.on("click", barselect_click);


// let's select the chart and add our sparklines to it	
	chart.selectAll(".sparkline")
		// plug in our data
		.data(data).enter()
		//and now:
		.append("path")
		.attr('d', function(d, i) { return wedgesparkline("sparkline", d, i, scaleTime); })
		.attr('transform', function(d, i) { return transformwedgesparkline(d, i, scaleTime); })
		.style('opacity', .5)
		.attr("class", function(d, i) { return "sparkline post-" + d["post_id"] + " user-" + d["user_id"]; })
		.attr("name", function(d, i) { return d["post_id"]; })
		.attr("stroke-width", 0.75)
		.attr("fill", "none")
		.attr("stroke", function(d) { return "#FF00FF"; return getthiscolor(d, scaleTimeForColor); })
	.on("mouseover", barselect_mouseover)
	.on("mouseout", barselect_mouseout) 
	.on("click", barselect_click);


	// add bar labels
	chart.selectAll("bar")
		.data(data).enter()
		.append("text")
		.attr("x", function(d, i) { return scaleTime(d["post_created_at"]); })
		.attr("y", yFunction)
		.attr("dx", -3) // padding-right
		.attr("dy", ".35em") // vertical-align: middle
		.attr("text-anchor", "end") // text-align: right
		.attr("name", function(d, i) { return d["post_id"]; })
		.attr("class", function(d, i) { return "post-" + d["post_id"] + " user-" + d["user_id"]; })
		.text(function(d,i) { 
			elapsedtimeseconds = (d["last_checked_at"].getTime() - d["post_created_at"].getTime()) / 1000; 
//			return d["user_name"] + ":" + "lifespan: " + lifespanFormat(elapsedtimeseconds);
			return d["user_name"];
//			return d["user_name"] + ": " + bar_dateformat(d["post_created_at"]) + "-- lifespan: " + lifespanFormat(elapsedtimeseconds);
		})
	  .on("mouseover", barselect_mouseover)
	  .on("mouseout", barselect_mouseout)
	  .on("click", barselect_click);




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


	d3update(0);

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


	function d3update(delay) {
		if(params["graphstyle"] == "bar") {
			d3.selectAll("path.sparkline").transition().duration(delay).style('opacity', 0);
			d3.selectAll("path.wedge").transition().duration(delay).style('opacity', 0);
			d3.selectAll("rect.bar").transition().duration(delay).style('opacity', 1);
		} else {
			if(params["graphstyle"] == "wedge") {
				d3.selectAll("path.sparkline").transition().duration(delay).style('opacity', 0);
				d3.selectAll("path.wedge").transition().duration(delay).style('opacity', 1);
				d3.selectAll("rect.bar").transition().duration(delay).style('opacity', 0);
			} else {
				d3.selectAll("path.sparkline").transition().duration(delay).style('opacity', 1);
				d3.selectAll("path.wedge").transition().duration(delay).style('opacity', 0);
				d3.selectAll("rect.bar").transition().duration(delay).style('opacity', 0);
			}
		}
	}

// define click function
function barselect_click(d, i) {

	var thispostid = d["post_id"];
	var thisuserid = d["user_id"];

	//window.location = (imgdir + (thispostid) + ".jpg");
	//
	var newData = [];
	for (var i = 0; i < d.length; d++) {
		newData.push(300);
	}

	console.log("clicked = ")
		console.log(d);
	console.log("clicked");
	d3.selectAll("path").transition().duration(1000)
		.attr("fill", "red")
		.attr("transform", function(d, i) {
				if(d["user_id"] == thisuserid) {return "translate(100,100)"; }
				});

//	console.log(newData)
//	console.log("fire click");
//	console.log(wedges);
//	wedges.data(newData)
//		.transition().duration(1000)
//		.attr("fill", "cyan");
}
