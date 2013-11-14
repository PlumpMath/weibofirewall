///////////////////////////////////////////////////
///////////////////////////////////////////////////
//D3 START
///////////////////////////////////////////////////
///////////////////////////////////////////////////
//
//get delimiter from weibo_settings.py
var dsv = d3.dsv(datadelim, "text/plain");
var wedges;
var scattertoggle = true;
var clickeduserid = null;

var data;

d3.json(datafile_json, function(error, json) {
	if (error) return console.warn(error);

	params = purl().param();
	params = cleanparams(params);

	// now let's clean and massage that data
	data = cleanjson(json)
//	json.map(cleanjson);


	// sort data by created
	data.sort(function(a,b) { return a.post_created_at - b.post_created_at; });

////	console.log(data);

	// get chart height
	//var chartheight = ((barheight + bargap) * data.length) + chartheight_padding;
	var chartheight = $(window).height();
	//screen.height; //((barheight + bargap) * data.length) + chartheight_padding;

//	var chartlegend = d3.select("#chartlegend");

	// create chart, set dimensions based on # of deleted posts
	var chart = d3.select("#chartdiv")
		.append("svg")
		.attr("class", "chart")
		.attr("width", chartwidth)
		.attr("height", chartheight)

	d3.select("#chartdiv").on("click", chart_click);

	// get min and max dates
	var mindate = d3.min(data, function(d) { return d["post_created_at"]; });
	var maxdate = d3.max(data, function(d) { return d["last_checked_at"]; });

	// let's specify the x-axis scale
	var scaleTime = d3.time.scale()
		// domain is min max of time
		.domain([mindate, maxdate])
		.range([chartpadding, chartwidth - chartpadding])

	// store the scaled X values in data - this is convenient	
	for (var i = 0; i < data.length; i++) {
		data[i]['post_created_at_scaled'] = scaleTime(data[i]['post_created_at']); 
		data[i]['scatter_height'] = scatterrandom(0, 1000, data[i]["user_id"], yHorizon);
	}

	// get min and max elapsed time
	var mindateelapsed = d3.min(data, function(d) { return d["last_checked_at"] - d["post_created_at"]; });
	var maxdateelapsed = d3.max(data, function(d) { return d["last_checked_at"] - d["post_created_at"]; });

	// let's specify color scale -- by elapsed time..
	var scaleTimeForColor = d3.time.scale.utc()
		//.domain([mindateelapsed, maxdateelapsed])
		.domain([mindate, maxdate])
		.range([colorMin, colorMax])

	// let's specify x-axis ticks
	var axisTime = d3.svg.axis()
		.scale(scaleTime)
		.orient("top")
		.ticks(d3.time.hour, 12)
		.tickFormat(d3.time.format("%m-%d %H:%m"));

	// add x-axis ticks
	chart.append("g").attr("class","ticklines")
		.selectAll("line")
		.data(scaleTime.ticks(d3.time.day, tickinterval)).enter()
		.append("line")
		.attr("class", "tickline")
		.attr("x1", scaleTime)
		.attr("x2", scaleTime)
		.attr("y1", 0)
		.attr("y2", chartheight)
		.style("stroke", tickstrokecolor);

	// add horizon line
	chart.append("g").attr("class","horizonlines")
		.selectAll("line")
		.append("line")
		.attr("class", "horizonline")
		.attr("x1", scaleTime.range()[0])
		.attr("x2", scaleTime.range()[1])
		.attr("y1", yHorizon)
		.attr("y2", yHorizon)
		.style("stroke", "pink");

	// Add the x-axis labels
	chart.append("g").attr("class", "xaxislabels")
		.attr("transform", "translate3d(0px," + (chartheight - 1) + ", 0)")
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
	var thispostdiv = postsdiv.selectAll("div")
		// plug in our data
		.data(data).enter()
		// wrap everything in a div
		.append("div")
			.attr("class", function(d, i) { return "postdiv post-" + d["post_id"] + " user-" + d["user_id"]; })

	var thispostdiv_image = thispostdiv.append("div").attr("class", "section_image_wrapper")
		.append("div").attr("class", "section_image");
	var thispostdiv_info = thispostdiv.append("div").attr("class", "section_info_wrapper")
		.append("div").attr("class", "section_info");
	
	var created_at_format = d3.time.format("%Y-%m-%d %H:%M CST");

	//let's add an img tag with all this stuff
	thispostdiv_image.append("img")
			.attr("class", "post_image")
			.attr("src", function(d) { 
					var thisimage = imgdir + d["post_id"] + "." + d["post_original_pic"].split(/[\.]+/).pop(); 
					return resizeimage(thisimage);
			})

	thispostdiv_info.append("div")
		.attr("class", "postinfo")
		.html(function(d) {
				returntext = "";
				returntext += "<div class='user_name'>";
				returntext += d["user_name"];
				returntext += ":</div>";

				returntext += "<div class='post_created_at'>";
				returntext += created_at_format(d["post_created_at"]);
				returntext += "</div>";

				returntext += "<div class='post_text'><span class='text_quote'>\"</span>";
				returntext += d["post_text"];
				returntext += "<span class='text_quote'>\"</span></div>";
				return returntext;
			})

	thispostdiv_info.append("div")
		.attr("class", "userinfo")
		.html(function(d) {
				returntext = "";
				returntext += "<div class='post_lifespan'>Deleted within <span class='post_lifespan'>" + lifespanFormat(d["post_lifespan"]) + "</span></div>";
				returntext += "<div class='lifespan_avg'>Average deletion time of this user's posts:<span class='lifespan_avg'>" + lifespanFormat(d["user_info"]["lifespan_avg"]) + "</span></div>";
				return returntext;
			})


	/*
//BARS
	// let's select the chart and add our bars to it	
	chart.append("g").attr("class", "bars")
		.selectAll("bar")
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
		.attr("fill", function(d, i) { 
			return getthiscolor(d, i, scaleTimeForColor);
		})
*/

///WEDGES
// let's select the chart and add our wedges to it	
	wedges = chart.append("g").attr("class", "wedges")
		.selectAll("wedge")
		// plug in our data
		.data(data)
		.enter()
		//and now:
		.append("path")
		.attr('d', function(d, i) { return wedgesparkline("wedge", d, i, scaleTime); })
		.attr('style', function(d, i) { return transformwedgesparkline(d, "wedge", "horizon"); })
		.attr("class", function(d, i) { return "wedge post-" + d["post_id"] + " user-" + d["user_id"]; })
		.attr("name", function(d, i) { return d["post_id"]; })
	.attr("stroke-width", 0.75)
//		.attr("fill", "none")
//		.attr("stroke", function(d, i) { return getthiscolor(d, i, scaleTimeForColor); })
		.attr("fill", function(d, i) { return getthiscolor(d, i, scaleTimeForColor); })
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
		.attr("stroke", function(d, i) { return "#FF00FF"; return getthiscolor(d, i, scaleTimeForColor); })
		.attr("style", function () {
			return "-webkit-transform: perspective(800) scale(1) scale3d(1, 1, 1) rotate3d(1, 0, 0, 0deg) translate3d(0, 0, 0);";
		})
	.on("mouseover", barselect_mouseover)
	.on("mouseout", barselect_mouseout) 
	.on("click", barselect_click);
*/
	// add text labels
	d3.select("#chartdiv").append("g").attr("class", "textlabels")
		.selectAll("text")
		.data(data).enter()
		.append("text")
		.attr('style', function(d, i) { return transformwedgesparkline(d, "username", "horizon"); })
		.attr("text-anchor", "end") // text-align: right
		.attr("name", function(d, i) { return d["post_id"]; })
		.attr("class", function(d, i) { return "username post-" + d["post_id"] + " user-" + d["user_id"]; })
		.text(function(d,i) { 
			elapsedtimeseconds = (d["last_checked_at"].getTime() - d["post_created_at"].getTime()) / 1000; 
			return d["user_name"];
		})
	  .on("mouseover", barselect_mouseover)
	  .on("mouseout", barselect_mouseout)
	  .on("click", barselect_click);

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
		  $('.postdiv.hover').css({'top': e.pageY+ 0, 'left': e.pageX + 10});
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
			var thisuserid = getuseridfromclasses($(".hover").attr("class"));

			if(thisuserid == clickeduserid) {

				//we clicked on OLD wedge
				//
				//so grab post id
				var thispostid = getpostidfromclasses($(".hover").attr("class"));

				// and send us there
//				console.log('window.location = "readpost.php?post_id="' + thispostid);
//				window.location = "readpost.php?post_id=" + thispostid;

			} else {

				//we clicked on NEW wedge
				//store global so we know when we clicked on existing
				clickeduserid = thisuserid;

				//TRANSITION WEDGES
				d3.selectAll("path.wedge").transition().duration(1000)
					.attr("style", function(d, i) {
						//get x, since wedges are all oriented at 0, 0
						var thisx = d["post_created_at_scaled"]; 
						if(d["user_id"] == thisuserid) { 
							//return wedgeopacity() + crossplatformtransform("translate3d(" + thisx + "px, " + yHorizon + "px, 0px)");
							return transformwedgesparkline(d, "wedge", "horizon");
						} else { 
							return transformwedgesparkline(d, "wedge", "scatter");
						}
					}) 

				//TRANSITION USERNAMES
				d3.selectAll(".username").transition().duration(1000)
					.attr("style", function(d, i) {
						var thisx = d["post_created_at_scaled"]; 
						if(d["user_id"] == thisuserid) { 
							return transformwedgesparkline(d, "username", "horizon");
							//return crossplatformtransform("translate3d(" + (thisx + usernameOffsetX) + "px, " + yHorizon + "px, 0px)");
							//return yHorizon;
						} else { 
							return transformwedgesparkline(d, "username", "scatter");
							//return crossplatformtransform("translate3d(" + (thisx + usernameOffsetX) + "px, " + scatterrandom(0, 1000, d["user_id"], yHorizon) + "px, 0px)"); 
							//return "fill: #F00FFF;";
							//return crossplatformtransform("translate3d(0px, 0px, 0px)");
							//return scatterrandom(0, 1000, d["user_id"], yHorizon);
						}
					}) 

			}

		} else {

			// WE CLICKED OUTSIDE - SO COLLAPSE
			//void global
			clickeduserid = null;
	
			console.log("clicked outside");
			d3.selectAll("path.wedge").transition().duration(1000)
				.attr("style", function(d, i) {
						//return wedgeopacity() + crossplatformtransform("translate3d(" + d["post_created_at_scaled"] + "px, " + yHorizon + "px, 0px)");
						return transformwedgesparkline(d, "wedge", "horizon");
				}) 
	
			d3.selectAll("text.username").transition().duration(1000)
				.attr("style", function(d, i) {
						return transformwedgesparkline(d, "username", "horizon");
						//return crossplatformtransform("translate3d(" + (d["post_created_at_scaled"] + usernameOffsetX) + "px, " + yHorizon + "px, 0px)");
				}) 


		}
	}

// define click function
function barselect_click(d, i) {
	return;
}

