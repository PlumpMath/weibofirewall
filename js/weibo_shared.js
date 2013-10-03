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
var thisurl = document.URL;
var baseurl=thisurl.substring(0,thisurl.lastIndexOf("/"));

var wedgeMinimumX = 5;
var wedgeMinimumY = 1;

var tickinterval = 1; //interval between ticks, in days




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


function hideLoadingSplash() {
	$("#loadingsplash").fadeOut(2000);
}

function handleMouse(e) {

  //what we weant to do: proportional to client, scroll page.
	//so: if cursor is 25% of clientX and 25% of clientY, scroll page to 25% of pageX and 25% of pageY.
	var scrollToX = e.clientX / $(window).width() * $(document).width();
	var scrollToY = e.clientY / $(window).height() * $(document).height();
  //

//	console.log("client: " + e.clientX + "," + e.clientY);
//	console.log("windowmax: " + $(window).width() + "," + $(window).height());
//	console.log(scrollToX + " " +  scrollToY);
	window.scrollTo(scrollToX, scrollToY);

}

//define mouseover functions
function barselect_mouseover(d, i) {
	d3.selectAll(".post-" + d["post_id"]).classed("hover", true); 
	//highlight same users
	d3.selectAll(".user-" + d["user_id"]).classed("same-user-hover", true);
}

// define mouseout
function barselect_mouseout( d, i) {
	d3.selectAll(".post-" + d["post_id"]).classed("hover", false); 
	//highlight same users
	d3.selectAll(".user-" + d["user_id"]).classed("same-user-hover", false);
}

// define click function
function barselect_click(d, i) {
	var thispostid = d["post_id"];
	//alert(imgdir + (data[thisid].post_id) + ".jpg");
	window.location = "readpost.php?post_id=" + thispostid;
	//window.location = (imgdir + (thispostid) + ".jpg");
}


// Assign handleMouse to mouse movement events
document.onmousemove = handleMouse;


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
var params = purl().param();


