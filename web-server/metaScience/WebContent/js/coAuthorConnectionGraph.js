/**
 *  Co author Connection graph
 */
 
 var widthCoAuthorGraph = 718;
 var heightCoAuthorGraph = 600;

 var maxCollaborations;
 
 var coAuthorConnectionGraph = d3.select(".coAuthorConnectionGraphContainer")
 .append("svg")
 .attr("width",widthCoAuthorGraph)
 .attr("height",heightCoAuthorGraph)
 .append("svg:g")
 .attr("id","coAuthorConnectionGraph");
 
 function generateCoAuthorConnectionGraph(authorId) {
 	// remove previous graph if exists
 	if( $("#coAuthorConnectionGraph").children().size() > 0) {
 		$("#coAuthorConnectionGraph").empty();
 	}

 	getCoAuthorConnectionGraph(authorId);
 }

 function getCoAuthorConnectionGraph(authorId) {
 	onLoadingGraph(d3.select("#coAuthorConnectionGraph"),"coAuthorConnectionGraphLoading",heightCoAuthorGraph,widthCoAuthorGraph);

 	d3.json(metaScienceServlet + "/coAuthorConnection?id="+authorId, function(errorJson,jsonNodes) {
 		var coAuthorJsonArray = jsonNodes.coAuthors;
 		var authorJson = jsonNodes.author;
 		maxCollaborations = authorJson.max_collaborations;
 		console.log(maxCollaborations)

 		var nodes = mapId2Node(coAuthorJsonArray);
 		nodes[0] = authorJson;

 		//DEbug
 		//authorId = 12;


 		//Create links
		var links = new Array();
		var i = 0;

		coAuthorJsonArray.forEach(function(node) {
			links[i] = {
				source: nodes[0],
				target: node,
				value: node.num_collaborations
			};
			i = i + 1;
		});

		console.log(links);

          removeLoadingImage("coAuthorConnectionGraphLoading");
		if(links.length > 0) {
			$("#info_coAuthorConnectionGraph").css("visibility","visible");
			drawCoAuthorConnectionGraph(authorId,nodes,links,maxCollaborations);
		}
 	});
 }

function drawCoAuthorConnectionGraph(authorId,innodes,links,maxCollaborations) {
	console.log(innodes)
     var coAuthorNodes = innodes.filter(function(d) { return !(typeof d == "undefined") && (d.id != authorId);});

	var authorNode = innodes.filter(function(d) { return d.id== authorId;});

	var nodes = authorNode.concat(coAuthorNodes);
     //var nodes = innodes;
	console.log(nodes)

	//Set author position
	authorNode[0].x = widthCoAuthorGraph/2;
	authorNode[0].y = heightCoAuthorGraph/2;

	//define a scale for line thickness
	var linethickness = d3.scale.linear()
	.domain([0,maxCollaborations])
	.range([1,10])

	//create author node tooltip
	var authorNodeTooltip = d3.select("body").append("div")
										.attr("class","authorNodeTooltip")
										.style("opacity",1e-6);

	//create co-authors node tooltip
	var coAuthorNodeTooltip = d3.select("body").append("div")
										.attr("class","coAuthorNodeTooltip")
										.style("opacity",1e-6);


	//force directed graph
	var force = d3.layout.force()
	.nodes(nodes)
	.links(links)
	.charge(-1000)
	.size([widthCoAuthorGraph, heightCoAuthorGraph])
	.linkDistance(100)
	.friction(0.8);

	force.start();

	var panrect = coAuthorConnectionGraph.append("rect")
								.attr("width",widthCoAuthorGraph)
								.attr("height",heightCoAuthorGraph)
								.style("fill","none")
								.style("pointer-events","all");

	//add zoom behavior
	var container = coAuthorConnectionGraph.append("g")
								.attr("id","container");

	var zoom = d3.behavior.zoom()
					.scaleExtent([1,10])
					.on("zoom",function() {
						container.attr("transform","translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");						
					});

	coAuthorConnectionGraph.call(zoom);

	//add drag behavior
	var circleCoAuthorDrag = d3.behavior.drag()
               .origin(function(d) { return d; })
               .on("dragstart", function(d) {
    	               d3.event.sourceEvent.stopPropagation();
    	               d3.select(this).classed("dragging", true);
    	               force.start();
               })
               .on("drag", circlecoauthordragged)
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
     var coAuthorNodesHTML = container.selectAll("circle.coauthorNode")
     							.data(coAuthorNodes)
     							.enter()
     							.append("g")
     							.attr("class","coAuthorNode");

     var coAuthorCircle = coAuthorNodesHTML.append("svg:circle")
                         .attr("r",10)
                         .attr("fill", d3.rgb("#c2a267"))
     				.call(circleCoAuthorDrag);

     //co Author mouse events
     coAuthorCircle.on("mousemove", function(d, index, element) {
     	coAuthorNodeTooltip.selectAll("p").remove();
     	coAuthorNodeTooltip.style("left", (d3.event.pageX+15)+"px")
     			.style("top",(d3.event.pageY-10) + "px");

     	coAuthorNodeTooltip.append("p").attr("class","tooltiptext").html("<span> name: <span>" + d.name);
     	coAuthorNodeTooltip.append("p").attr("class","tooltiptext").html("<span> number of collaborations: <span>" + d.num_collaborations);
     });

     coAuthorCircle.on("mouseover", function(d, index, element) {
     	coAuthorNodeTooltip.transition()
     			.duration(500)
     			.style("opacity",1);
     });

     coAuthorCircle.on("mouseout", function(d, index, element) {
     	coAuthorNodeTooltip.transition()
     			.duration(500)
     			.style("opacity", 1e-6);
     });

     var coAuthorCircleText = coAuthorNodesHTML.append("svg:text")
     						.text( function(d) { return d.name;})
     						.attr("class","coAuthorNodeText");

     // author node
     var authorNodeHTML = container.selectAll("circle.authorNode")
     							.data(authorNode)
     							.enter()
     							.append("g")
     							.attr("class","authorNode");

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
     	authorNodeTooltip.append("p").attr("class","tooltiptext").html("<span> total collaborations </span>" + d.total_collaborations);

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
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y;});
     
          coAuthorCircle.attr('cx', function (d) { return d.x; })
         .attr('cy', function (d) { return d.y; });
     
         coAuthorCircleText.attr("x", function(d) { return d.x-15; })
               .attr("y", function(d) { return d.y-15; });
         
         authorCircle.attr("cx", function(d) { return d.x; })
         .attr("cy", function(d) { return d.y; });
         
//       circle.attr("cx", function(d) { d.x = w2/2; return d.x; })
//       .attr("cy", function(d) { d.y = h2/2; return d.y; });
         
       });

     addZoomMoveIcon("#coAuthorConnectionGraph");

}

/*
 * Dragging functions
 */
function circlecoauthordragged(d) {
	d3.select(this).attr("cx",d.x = d3.event.x).attr("cy",d.y = d3.event.y);
}

function circleauthordragged(d) {
	d3.select(this).attr("cx", d.x = d3.event.x).attr("cy",d.y = d3.event.y);
}

function dragended(d) {
	d3.select(this).classed("dragging",false);
}


 function mapId2Node(data) {
 	var mappingArray = new Array();
 	for(var i = 0 ; i < data.length ; i++) {
 		var node = data[i];
 		mappingArray[node.id] = node;
 	}
 	return mappingArray;
 }

 
