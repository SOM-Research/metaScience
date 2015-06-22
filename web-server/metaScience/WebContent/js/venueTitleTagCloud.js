/*
 *	Journal Author Connection Graph
 */

var widthTagCloud = 1080;
var heightTagCloud = 1080;

var complete = 0;

var venueTitleTagCloudGraph = d3.select("#venueTitleTagCloudContainer")
		.append("svg")
		.attr("width", widthTagCloud)
		.attr("height", heightTagCloud)
		.append("svg:g")
		.attr("id", "venueTitleTagCloud");


function generateVenueTitleTagCloudGraph(venueId,subVenueId) {
	
	//remove previous graph if exists
	if ($("#venueTitleTagCloud").children().size() > 0) {
		$("#venueTitleTagCloud").empty();
	}
	getVenueTitleTagCloudGraph(venueId,subVenueId);

}

function getVenueTitleTagCloudGraph(venueId,subVenueId) {

	//onLoadingGraph(d3.select("#venueTitleTagCloud"), "loaderVenueTitleTagCloudGraph", heightTagCloud, widthTagCloud);

	d3.json(metaScienceServlet + "/venueTitleCloud?id="+ venueId + ((venueId != subVenueId && subVenueId != undefined) ? "&subid=" + subVenueId : ""), function(errornodes,jsonnodes) {
		var globalJsonObject = jsonnodes.global;
		var yearsJsonObjects = jsonnodes.yearly;
		
		
		if(globalJsonObject.words.length > 0) {
			drawVenueTitleTagCloudGraph(globalJsonObject);	
		}
		
	});
	
	
}



function drawVenueTitleTagCloudGraph(wordsJsonObject) {	

  var fontSize = d3.scale.log().range([10, 85]).domain([1,wordsJsonObject.max])

	d3.layout.cloud()
      .size([widthTagCloud,heightTagCloud])
      .words(wordsJsonObject.words)
      .text(function(d) {
      	return d.text;
      })
      .padding(5)
	    .timeInterval(1000)
      .rotate(function() { return 0; })
      .font("Impact")
      .spiral("rectangular")
      .fontSize(function(d) { return fontSize(+d.occurence); })
      .on("word", progress)
      .on("end", draw)
      .start();

}




function progress(word) {

	console.log(++complete);
  
}

  function draw(words,e) {
  	removeLoadingImage("loaderVenueTitleTagCloudGraph");

  	var fill = d3.scale.category20();
  	scale = e ? Math.min(widthTagCloud / Math.abs(e[1].x - widthTagCloud / 2), widthTagCloud / Math.abs(e[0].x - widthTagCloud / 2), heightTagCloud / Math.abs(e[1].y - heightTagCloud / 2), heightTagCloud / Math.abs(e[0].y - heightTagCloud / 2)) / 2 : 1
    venueTitleTagCloudGraph
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; });
	
    venueTitleTagCloudGraph.attr("transform", "translate(" + [widthTagCloud >> 1, heightTagCloud >> 1] + ")scale(" + scale + ")");
    
  }