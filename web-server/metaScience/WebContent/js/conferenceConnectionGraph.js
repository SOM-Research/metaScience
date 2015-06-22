/**
 *  conference Connection graph
 */
 
 var widthConferenceGraph = 718;
 var heightConferenceGraph = 600;

 var maxAttendance;
 var maxPublication;
 
 var conferenceConnectionGraph = d3.select(".conferenceConnectionGraphContainer")
 .append("svg")
 .attr("width",widthConferenceGraph)
 .attr("height",heightConferenceGraph)
 .append("svg:g")
 .attr("id","conferenceConnectionGraph");
 
 function generateConferenceConnectionGraph(authorId) {
 	// remove previous graph if exists
 	if( $("#conferenceConnectionGraph").children().size() > 0) {
 		$("#conferenceConnectionGraph").empty();
 	}

 	getConferenceConnectionGraph(authorId);
 }

 function getConferenceConnectionGraph(authorId) {
 	onLoadingGraph(d3.select("#conferenceConnectionGraph"),"conferenceConnectionGraphLoading",heightConferenceGraph,widthConferenceGraph);

 	d3.json(metaScienceServlet + "/conferenceConnection?id="+authorId, function(errorJson,jsonNodes) {
 		var conferenceJsonArray = jsonNodes.conferences;
 		var authorJson = jsonNodes.author;

          maxAttendance = authorJson.max_attendance;
          maxPublication = authorJson.max_publications;

 		//var nodes = mapSource2Node(conferenceJsonArray);
 		//nodes[0] = authorJson;

 		//Create links
		var links = new Array();
		var i = 0;

		conferenceJsonArray.forEach(function(node) {
			links[i] = {
				source: authorJson,
				target: node,
				value: node.attendance
			};
			i = i + 1;
		});

          removeLoadingImage("conferenceConnectionGraphLoading");
		if(links.length > 0) {
			$("#info_conferenceConnectionGraph").css("visibility","visible");
			drawConferenceConnectionGraph(authorJson,conferenceJsonArray,links,maxAttendance,maxPublication);
		}
 	});
 }

function drawConferenceConnectionGraph(authorNode,conferenceNodes,links,maxAttendance,maxPublication) {

     var nodes = new Array();
     nodes.push(authorNode);
     var authorNodeAr = nodes.slice();
     nodes = nodes.concat(conferenceNodes);

     console.log(nodes);


	//Set author position
	authorNode.x = widthConferenceGraph/2;
	authorNode.y = heightConferenceGraph/2;

	//define a scale for line thickness
	var linethickness = d3.scale.linear()
	.domain([0,maxAttendance])
	.range([1,10]);

     //define a scale for rect height
     var rectheight = d3.scale.linear()
          .domain([0,maxPublication])
          .range([5,50]);

     console.log("max Publication")
     console.log(maxPublication)

	//create author node tooltip
	var authorNodeTooltip = d3.select("body").append("div")
										.attr("class","authorNodeTooltip")
										.style("opacity",1e-6);

	//create co-authors node tooltip
	var conferenceNodeTooltip = d3.select("body").append("div")
										.attr("class","conferenceNodeTooltip")
										.style("opacity",1e-6);


	//force directed graph
	var force = d3.layout.force()
	.nodes(nodes)
	.links(links)
	.charge(-1000)
	.size([widthConferenceGraph, heightConferenceGraph])
	.linkDistance(200)
	.friction(0.8);

	force.start();

	var panrect = conferenceConnectionGraph.append("rect")
								.attr("width",widthConferenceGraph)
								.attr("height",heightConferenceGraph)
								.style("fill","none")
								.style("pointer-events","all");

	//add zoom behavior
	var container = conferenceConnectionGraph.append("g")
								.attr("id","container");

	var zoom = d3.behavior.zoom()
					.scaleExtent([1,10])
					.on("zoom",function() {
						container.attr("transform","translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");						
					});

	conferenceConnectionGraph.call(zoom);

	//add drag behavior
	var rectConferenceDrag = d3.behavior.drag()
               .origin(function(d) { return d; })
               .on("dragstart", function(d) {
    	               d3.event.sourceEvent.stopPropagation();
    	               d3.select(this).classed("dragging", true);
    	               force.start();
               })
               .on("drag", rectconferencedragged)
               .on("dragend", dragended);

     var circleAuthorDrag = d3.behavior.drag()
     		.origin(function(d) {return d;})
     		.on("dragstart", function(d) {
     			d3.event.sourceEvent.stopPropagation();
     			d3.select(this).classed("dragging",true);
     			force.start();
     		})
     		.on("drag",circleauthordragged)
     		.on("dragend",dragended);

     //add link thickness
     var link = container.selectAll(".line")
     				.data(links)
     				.enter()
     				.append("line")
     				.attr("stroke-width",4)
     				.attr("stroke-width",function(d) { return linethickness(d.value); })
     				.style("stroke","grey");

     //add co-author tooltip
     var conferenceNodesHTML = container.selectAll("rect.conferenceNode")
     							.data(conferenceNodes)
     							.enter()
     							.append("g")
     							.attr("class","conferenceNode");

     var conferenceRect = conferenceNodesHTML.append("svg:rect")
                         .attr("width", function(d) { return rectheight(d.publications); })
                         .attr("height", function(d) { return rectheight(d.publications); })
                         .attr("fill", d3.rgb("#121212"))
     				.call(rectConferenceDrag);

                            

     //co Author mouse events
     conferenceRect.on("mousemove", function(d, index, element) {
     	conferenceNodeTooltip.selectAll("p").remove();
     	conferenceNodeTooltip.style("left", (d3.event.pageX+15)+"px")
     			.style("top",(d3.event.pageY-10) + "px");

     	conferenceNodeTooltip.append("p").attr("class","tooltiptext").html("<span> name: <span>" + d.source);
     	conferenceNodeTooltip.append("p").attr("class","tooltiptext").html("<span> number of attendance: <span>" + d.attendance);
          conferenceNodeTooltip.append("p").attr("class","tooltiptext").html("<span> number of publications: <span>" + d.publications);
     });

     conferenceRect.on("mouseover", function(d, index, element) {
     	conferenceNodeTooltip.transition()
     			.duration(500)
     			.style("opacity",1);
     });

     conferenceRect.on("mouseout", function(d, index, element) {
     	conferenceNodeTooltip.transition()
     			.duration(500)
     			.style("opacity", 1e-6);
     });

     var conferenceRectText = conferenceNodesHTML.append("svg:text")
     						.text( function(d) { return d.source;})
     						.attr("class","conferenceRectText");

     // author node
     var authorNodeHTML = container.selectAll("circle.conf_authorNode")
     							.data(authorNodeAr)
     							.enter()
     							.append("g")
     							.attr("class","conf_authorNode");

     var authorCircle = authorNodeHTML.append("svg:circle")
     							.attr("r",30)
     							.attr("fill",d3.rgb("#16667d"))
     							.call(circleAuthorDrag);

     // author node events
     authorCircle.on("mousemove", function(d, index, element) {
     	authorNodeTooltip.selectAll("p").remove();
     	authorNodeTooltip.style("left", (d3.event.pageX - 50) +"px")
     			.style("top", (d3.event.pageY - 30) + "px");

     	authorNodeTooltip.append("p").attr("class","tooltiptext").html("<span> name: </span>" + d.name);
          authorNodeTooltip.append("p").attr("class","tooltiptext").html("<span> total publications </span>" + d.total_publications);
          authorNodeTooltip.append("p").attr("class","tooltiptext").html("<span> total attendance </span>" + d.total_attendance);

     });

     authorCircle.on("mouseover", function(d, index, element) {
     	authorNodeTooltip.transition()
     			.duration(500)
     			.style("opacity", 1);
     });

     authorCircle.on("mouseout", function(id, index, element) {
     	authorNodeTooltip.transition()
     			.duration(500)
     			.style("opacity",1e-6);
     });

     force.on("tick", function() {
          
          link.attr("x1", function(d) {return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x + rectheight(d.target.publications)/2; })
          .attr("y2", function(d) { return d.target.y + rectheight(d.target.publications)/2});
     
          conferenceRect.attr('x', function (d) { return d.x; })
         .attr('y', function (d) { return d.y; });
     
         conferenceRectText.attr("x", function(d) { return d.x-15; })
               .attr("y", function(d) { return d.y-15; });
         
         authorCircle.attr("cx", function(d) { return d.x; })
         .attr("cy", function(d) { return d.y; });
         
//       circle.attr("cx", function(d) { d.x = w2/2; return d.x; })
//       .attr("cy", function(d) { d.y = h2/2; return d.y; });
         
       });

     addZoomMoveIcon("#conferenceConnectionGraph");

}

/*
 * Dragging functions
 */
function rectconferencedragged(d) {
	d3.select(this).attr("x",d.x = d3.event.x).attr("y",d.y = d3.event.y);
}

function circleauthordragged(d) {
	d3.select(this).attr("cx", d.x = d3.event.x).attr("cy",d.y = d3.event.y);
}

function dragended(d) {
	d3.select(this).classed("dragging",false);
}


 function mapSource2Node(data) {
 	var mappingArray = new Array();
 	for(var i = 0 ; i < data.length ; i++) {
 		var node = data[i];
 		mappingArray[i+1] = node;
 	}
 	return mappingArray;
 }

 
