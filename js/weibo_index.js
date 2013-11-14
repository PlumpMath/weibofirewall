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
	chartheight = $(document).height() - 300;
	yHorizon = chartheight / 2;
	//screen.height; //((barheight + bargap) * data.length) + chartheight_padding;


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
		.range([chartxpadding, chartwidth - chartxpadding])

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

	// let's specify x-axis ticks - not drawing yet
	var axisTime = d3.svg.axis()
		.scale(scaleTime)
		.orient("top")
		.ticks(d3.time.day, 1)
		.tickFormat(d3.time.format("%m-%d %H:%m"));

	// add x-axis time lines
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
		//.selectAll("line")
		.append("line")
		.attr("class", "horizonline")
		.attr("x1", scaleTime.range()[0])
		.attr("x2", scaleTime.range()[1])
		.attr("y1", yHorizon)
		.attr("y2", yHorizon)
		.style("stroke", tickstrokecolor);

/*
	// Add the x-axis time labels
	chart.append("g").attr("class", "xaxislabels")
      .attr("transform", "translate(0," + chartheight + ")")

//		.attr("transform", "translate3d(0px," + (chartheight - 1) + ", 0)")
		.call(axisTime) */
		//rotate the text, too
/*		.selectAll("text")  
            .style("text-anchor", "start")
            .attr("dx", "5em")
            .attr("dy", "4em")
            .attr("transform", function(d) {
                return "rotate(-45)" 
                });*/

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
				returntext += " <span class='pseudonym'>(pseudonym)</span>:</div>";

				returntext += "<div class='last_checked_at'>Deleted at ";
				returntext += "<span>" + created_at_format(d["last_checked_at"]) + "</span>";
				returntext += "</div>";

				returntext += "<div class='post_created_at'>";
				returntext += created_at_format(d["post_created_at"]);
				returntext += "</div>";

				returntext += "<div class='post_text'><span class='text_quote'>&ldquo;</span>";
				returntext += d["post_text"];
				returntext += "<span class='text_quote'>&rdquo;</span></div>";
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
		.attr("stroke", function(d, i) { return theme_color; })
	//	.attr("fill", function(d, i) { return getthiscolor(d, i, scaleTimeForColor); })
		//.attr("fill", "none")
	.on("mouseover", barselect_mouseover)
	.on("mouseout", barselect_mouseout) 
	.on("click", barselect_click);

	// add text labels - usernames
/*
	d3.select("#chartdiv").append("g").attr("class", "textlabels")
		.selectAll("text")
		.data(data).enter()
		.append("text")
		.attr('style', function(d, i) { return wedgeopacity(0) + transformwedgesparkline(d, "username", "scatter"); })
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
*/
/*var durdiv = d3.select("#durdiv");
durdiv.selectAll("div")
		.data(data)
		.enter()
		.append("div")
		.text(function(d) { return rehumanize(moment.duration(maxdate - d["post_created_at"], 'seconds')); })
		 .attr("class", "duration")
		 .attr("name", function(d, i) { return i; })

*/
	d3update(0);


// scroll tracking
	//$("body").mousemove(function(e){
	$(document).mousemove(function(e){
		  $('#mouseinfo').css({'top': e.pageY+ 0, 'left': e.pageX + 0})
			.html(created_at_format(scaleTime.invert(e.pageX)));
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



