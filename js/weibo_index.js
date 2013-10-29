///////////////////////////////////////////////////
///////////////////////////////////////////////////
//D3 START
///////////////////////////////////////////////////
///////////////////////////////////////////////////
//
//get delimiter from weibo_settings.py
var dsv = d3.dsv("|||", "text/plain");
var wedges;
var scattertoggle = true;
var clickeduserid = null;

// read the datafile.START
dsv(datafile, dsvaccessor, function(error, rows) {

	params = purl().param();
	params = cleanparams(params);

	// now let's massage that data
	//var data = rows;
	var data = _.first(rows, 1000);

	// sort data by created
	data.sort(function(a,b) { return a.post_created_at - b.post_created_at; });

	// get chart height
	//var chartheight = ((barheight + bargap) * data.length) + chartheight_padding;
	var chartheight = screen.height; //((barheight + bargap) * data.length) + chartheight_padding;

	var chartlegend = d3.select("#chartlegend");

	// create chart, set dimensions based on # of deleted posts
	var chart = d3.select("#chartdiv")
		.append("svg")
		.attr("class", "chart")
		.attr("width", chartwidth)
		.attr("height", chartheight)
		.append("g");

	d3.select("#chartdiv").on("click", chart_click);
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

	// add horizon line
	chart.selectAll("line")
		.append("line")
		.attr("class", "horizonline")
		.attr("x1", scaleTime.range()[0])
		.attr("x2", scaleTime.range()[1])
		.attr("y1", yHorizon)
		.attr("y2", yHorizon)
		.style("stroke", "pink");

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

	/*
//BARS
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
*/

///WEDGES
// let's select the chart and add our wedges to it	
	wedges = chart.selectAll("wedge")
		// plug in our data
		.data(data)
		.enter()
		//and now:
		.append("path")
		.attr('d', function(d, i) { return wedgesparkline("wedge", d, i, scaleTime); })
		.attr('transform', function(d, i) { return transformwedgesparkline(d, i, scaleTime); })
		.style('opacity', 0.2)
		.attr("class", function(d, i) { return "wedge post-" + d["post_id"] + " user-" + d["user_id"]; })
		.attr("name", function(d, i) { return d["post_id"]; })
	.attr("stroke-width", 0.75)
		.attr("fill", "none")
//		.attr("stroke", function(d) { return getthiscolor(d, scaleTimeForColor); })
		.attr("fill", function(d) { return getthiscolor(d, scaleTimeForColor); })
	.on("mouseover", barselect_mouseover)
	.on("mouseout", barselect_mouseout) 
	.on("click", barselect_click);

	/*
///SPARKLINES
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
		.attr("style", function () {
			return "-webkit-transform: perspective(800) scale(1) scale3d(1, 1, 1) rotate3d(1, 0, 0, 0deg) translate3d(0, 0, 0);";
		})
	.on("mouseover", barselect_mouseover)
	.on("mouseout", barselect_mouseout) 
	.on("click", barselect_click);
*/

	/*
	// add labels
	chart.selectAll("label")
		.data(data).enter()
		.append("text")
		.attr("x", function(d, i) { return scaleTime(d["post_created_at"]); })
		.attr("transform", function(d, i) { return "translate(0, " + yFunction(d, i) + ")"; })
		.attr("dx", -3) // padding-right
		.attr("dy", ".35em") // vertical-align: middle
		.attr("text-anchor", "end") // text-align: right
		.attr("name", function(d, i) { return d["post_id"]; })
		.attr("class", function(d, i) { return "username post-" + d["post_id"] + " user-" + d["user_id"]; })
		.text(function(d,i) { 
			elapsedtimeseconds = (d["last_checked_at"].getTime() - d["post_created_at"].getTime()) / 1000; 
//			return d["user_name"] + ":" + "lifespan: " + lifespanFormat(elapsedtimeseconds);
			return d["user_name"];
//			return d["user_name"] + ": " + bar_dateformat(d["post_created_at"]) + "-- lifespan: " + lifespanFormat(elapsedtimeseconds);
		})
	  .on("mouseover", barselect_mouseover)
	  .on("mouseout", barselect_mouseout)
	  .on("click", barselect_click);


*/

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


// used to switch between view modes with the menu
	function d3update(delay) {
		/*
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
		} */
	}

	function chart_click(d, i) { 
		console.log("chart_click");
		if ($(".hover").length ) {

			// WE CLICKED ON A WEDGE - SO SPLIT
			
			// this is messy - but get userid from classes
			var hoverclasses = $(".hover").attr("class");
			var hovermatch = hoverclasses.match(/user-(\d*)/);
			var thisuserid = hovermatch[1];

			//TRANSITION WEDGES
			d3.selectAll("path.wedge").transition().duration(1000)
				.attr("style", function(d, i) {
					if(d["user_id"] == thisuserid) { 
						return crossplatformtransform("translate(0px, " + yHorizon + "px)");
					} else { 
							return crossplatformtransform("translate(0px, " + scatterrandom(0, 1000, d["user_id"], yHorizon) + "px)"); 
					}
				}) 

		} else {

			// WE CLICKED OUTSIDE - SO COLLAPSE
		
			d3.selectAll("path").transition().duration(1000)
				.attr("style", function(d, i) {
							return crossplatformtransform("translate(0px, " + yHorizon + "px)");
				}) 
		}
	}

// define click function
function barselect_click(d, i) {
	return
	alert("barselect_click");

	var thispostid = d["post_id"];
	var thisuserid = d["user_id"];
	clickeduserid = thisuserid;

	//window.location = (imgdir + (thispostid) + ".jpg");
	var newData = [];
	for (var i = 0; i < d.length; d++) {
		newData.push(300);
	}

//	console.log("clicked = ")
//		console.log(d);
//	console.log("clicked");

/*	d3.selectAll("path").transition().duration(1000)
		.attr("fill", "red")
		.attr("transform", function(d, i) {
			if(d["user_id"] == thisuserid) { 
				return "translate(0,300)"; 
			} else { 
				console.log(d3.select(this).attr("transform"));
				return d3.select(this).attr("transform");
			} 
		});*/

	d3.selectAll("text.username").transition().duration(1000)
		.attr("style", function(d, i) {
			if(d["user_id"] == thisuserid) { 
				console.log("foundthisusername");
				return crossplatformtransform("translate(0px, " + yHorizon + "px)");
			} else { 
				if(scattertoggle == true) 
					return crossplatformtransform("translate(0px, " + scatterrandom(0, 1000, d["user_id"], yHorizon) + "px)"); 
				else 
					return crossplatformtransform("translate(0px, " + yHorizon + "px)");
			} 
		});

	d3.selectAll("path.wedge").transition().duration(1000)
		.attr("style", function(d, i) {
			if(d["user_id"] == thisuserid) { 
				return crossplatformtransform("translate(0px, " + yHorizon + "px)");
			} else { 
				if(scattertoggle == true) 
					return crossplatformtransform("translate(0px, " + scatterrandom(0, 1000, d["user_id"], yHorizon) + "px)"); 
				else
					return crossplatformtransform("translate(0px, " + yHorizon + "px)");
				//console.log( d3.select("post-" + d["post_id"]ext.username").attr("transform"))
				//return d3.select(this).attr("transform");
			}
		}) 

		if(scattertoggle == true)
			scattertoggle = false;
		else
			scattertoggle = true;

/*	d3.selectAll("path").transition().duration(1000)
		.attr("fill", "red")
		.attr("transform", function(d, i) {
			if(d["user_id"] == thisuserid) { 
				return "translate(0,800)"; 
			} else { 
				return "translate(0,400)"; 
				console.log(d["post_id"]);
				//console.log( d3.select("post-" + d["post_id"]ext.username").attr("transform"))
				return "translate(0," + _.random(0, 1000) + ")"; 
				//return d3.select(this).attr("transform");
			}
		}) 
		.attr("style", function(d, i) {
			return "-webkit-transform: translate(0px, 19px);";
		});
*/
//	console.log(newData)
//	console.log("fire click");
//	console.log(wedges);
//	wedges.data(newData)
//		.transition().duration(1000)
//		.attr("fill", "cyan");
}
