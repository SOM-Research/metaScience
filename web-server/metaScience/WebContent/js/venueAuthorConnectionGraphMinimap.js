/*
 *	Venue Author Connection Graph
 */

var widthAuthor = 718;
var heightAuthor = 600;
var minimapScale = 0.2;
var linkedByIndex = {};

var d3links;
var d3nodes;
var d3nodesCircle;

var JsonNodes,JsonLinks;
var JsonNodesMap;

var maxCollaborations,maxPublications;
var minimap;

var graphForce = d3.layout.force()
		.gravity(0.2)
		.charge(-1500)
		.friction(0.8)
		.size([widthAuthor,heightAuthor])
		.linkDistance(200);

var venueAuthorConnectionGraph = d3.select("#venueAuthorConnectionGraphContainer")
		.append("svg")
		.attr("width", widthAuthor)
		.attr("height", heightAuthor)
		.append("svg:g")
		.attr("id", "venueAuthorConnectionGraph");

var minimapContainer = d3.select("#minimapContainer")
		.append("svg")
		.attr("width",((widthAuthor*minimapScale) + 10))
		.attr("height",((heightAuthor*minimapScale) + 10))
		.attr("class","center-block")
		.attr("id","minimap");

function createMinimap(zoom,nodeContainer) {
	var zoomScale = zoom.scale();

	minimap = venueGraph.minimap()
		.zoom(zoom)
		.targetGraph(nodeContainer);

	minimapContainer.call(minimap);
	minimap.scale(zoomScale).render();
}

function generateVenueAuthorConnectionGraph(venueId,subvenueId) {
	
	//remove previous graph if exists
	if ($("#venueAuthorConnectionGraph").children().size() > 0) {
		$("#venueAuthorConnectionGraph").empty();
		$("#coAuthorCollaborationSlider").empty();
	}
	getVenueAutorConnectionGraph(venueId,subvenueId);

}

function neighboring(id_a, id_b) {
  return linkedByIndex[id_a + "," + id_b] || linkedByIndex[id_b + "," + id_a];
}

function getVenueAutorConnectionGraph(venueId,subvenueId) {

	onLoadingGraph(d3.select("#venueAuthorConnectionGraph"), "loaderVenueAuthorConnectionGraph", heightAuthor, widthAuthor);
	onLoadingGraph(d3.select("#minimap"),"loaderMinimap",(heightAuthor*minimapScale) + 10,(widthAuthor*minimapScale) + 10);

	d3.json(metaScienceServlet + "/venueAuthorCollaboration?id="+ venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : ""), function(errornodes,jsonnodes) {
		JsonNodes = jsonnodes.nodes;
		JsonLinks = jsonnodes.links;
		maxCollaborations = jsonnodes.prop.maxCollaborations;
		maxPublications = jsonnodes.prop.maxPublications;

		JsonNodesMap = mapId2Node(JsonNodes);

		// Copy elements to avoid adding d3 metadata to json nodes & links
		var nodes = JSON.parse(JSON.stringify(jsonnodes.nodes));
		var links = JSON.parse(JSON.stringify(jsonnodes.links));

		var mapNodes = mapId2Node(nodes);

		// neighboring
		links.forEach(function(link) {
			linkedByIndex[link.source + "," + link.target] = 1;
	 	 	linkedByIndex[link.source + "," + link.source] = 1;
	  		linkedByIndex[link.target + "," + link.target] = 1;
	  		linkedByIndex[link.target + "," + link.source] = 1;
			link.source = mapNodes[link.source];
			link.target = mapNodes[link.target];

		});
		
		
		if(links.length > 0) {
			drawVenueAuthorConnectionGraph(nodes,links,maxCollaborations,maxPublications);	
		}

		var comboboxNodes = new Array();
		comboboxNodes.push({id:-1,name:" - All Collaborations -"});
		comboboxNodes = comboboxNodes.concat(JsonNodes);

		$("#coAuthorCombobox").jqxComboBox(
	    {
	        width: "100%",
	        height: 25,
	        source: comboboxNodes,
	        selectedIndex: 0,
	        displayMember: "name",
	        valueMember: "id",
	        placeHolder: "author",
	        showArrow : true,
	        search: function (searchString) {
	        	$(".jqx-combobox-input, .jqx-combobox-content").css({ "background": "url('imgs/loading_project.gif') no-repeat right 5px center" });
	            //dataAdapter.dataBind();
	        }
	    });

	    $("#coAuthorCombobox").on('bindingComplete', function (event) {
	    	$(".jqx-combobox-input, .jqx-combobox-content").css({ "background-image": "none" });
	    });
	    
	    $("#coAuthorCombobox").on('select', function (event) {
	    	if (typeof event.args != 'undefined') {
		        var selecteditem = event.args.item;
		        var selectedIndex = event.args.index;
		        if (selecteditem) {
		        	var node = d3.select(selecteditem.originalItem);
		        	if(node.length == 1) {
			        	node = node[0][0];

			        	if(selectedIndex != 0) {

				        	d3links.style("stroke", function(l) {
								if(node.id == l.source.id || node.id == l.target.id){
									return d3.rgb('#9E00D9');
								} else
									return 'gray';
							});
							d3links.style('opacity', function(o) {
								return o.source.id == node.id || o.target.id == node.id ? 1 : 0;
							});
							d3nodes.style('opacity', function(o) {
								if(o.id != node.id)
									return neighboring(node.id,o.id) ? 1 : 0;
							});
						} else {
							d3links.style("stroke", function(l) {
								return 'gray';
							});
							d3links.style('opacity', function(o) {
								return 1;
							});
							d3nodes.style('opacity', function(o) {
								return 1;
							});
						}
					}
					            //venueName = selecteditem.originalItem.name;
					            //venueId = selecteditem.originalItem.id;
				}
		  	}
		});

		$("#resetCoAuthorCombobox").on('click', function(event) {
        	$("#coAuthorCombobox").jqxComboBox('selectIndex',0);
       	});

       	$("#coAuthorCombobox").on('click', function (event) {
            $("#coAuthorCombobox").jqxComboBox({selectedIndex: -1});
       	});

       	createSlider("coAuthorCollaborationSlider","Number of collaborations",1,maxCollaborations,sliderChangeFunction);
		
	});
	
	
}

function sliderChangeFunction(numStart,numEnd) {

	var filteredNodes = new Set();
	var filteredLinks = JSON.parse(JSON.stringify(JsonLinks.filter( function(l) {
		if(l.value >= numStart && l.value <= numEnd) {
			filteredNodes.add(JsonNodesMap[l.source]);
			filteredNodes.add(JsonNodesMap[l.target]);
			return l;
		}
	})));

	// convert Set to Array for d3 compliance
	var filteredNodesArray = new Array();
	filteredNodes.forEach( function(node) {
		filteredNodesArray.push(node);
	})

	var filteredNodesMap = mapId2Node(filteredNodesArray);
	linkedByIndex = {};
	filteredLinks.forEach(function(link) {
			linkedByIndex[link.source + "," + link.target] = 1;
	 	 	linkedByIndex[link.source + "," + link.source] = 1;
	  		linkedByIndex[link.target + "," + link.target] = 1;
	  		linkedByIndex[link.target + "," + link.source] = 1;
			link.source = filteredNodesMap[link.source];
			link.target = filteredNodesMap[link.target];

		});

	//remove previous graph if exists
	if ($("#venueAuthorConnectionGraph").children().size() > 0) {
		$("#venueAuthorConnectionGraph").empty();
	}
	drawVenueAuthorConnectionGraph(filteredNodesArray,filteredLinks,maxCollaborations,maxPublications);

}

function mapId2Node(jsonnodes) {
	var mappingarray = new Array();
	for (var i = 0; i < jsonnodes.length; i++) {
		var node = jsonnodes[i];
		mappingarray[node.id] = node;
	}
	return mappingarray;
}


function drawVenueAuthorConnectionGraph(nodes, links, maxCollaborations, maxPublications) {

	if(d3.select("#loaderVenueAuthorConnectionGraph").empty()) {
		onLoadingGraph(d3.select("#venueAuthorConnectionGraph"), "loaderVenueAuthorConnectionGraph", heightAuthor, widthAuthor);
	}

	// Creating structure
	var panrect = venueAuthorConnectionGraph.append("rect")
		.attr("width",widthAuthor)
		.attr("height",heightAuthor)
		.style("fill","none")
		.style("pointer-events","all");

	var container = venueAuthorConnectionGraph.append("g")
		.attr("class","nodeContainer")
		.attr("height",heightAuthor)
		.attr("width",widthAuthor);

	//On loading
	container.style("visibility","hidden");

	// Creating tooltip
	var authorNodeTooltip = d3.select("body").append("div")
		.attr("class","authorNodeTooltip")
		.style("opacity",1e-6);

	var linkTooltip = d3.select("body").append("div")
		.attr("class","authorNodeTooltip")
		.style("opacity",1e-6);

	// Zoom behavior 
	var zoom = d3.behavior.zoom()
		.scaleExtent([0, 10])
		.on("zoom" , function() {
			container.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
			minimap.scale(d3.event.scale).render();
		});

	venueAuthorConnectionGraph.call(zoom);


	//Create the force diagram
	graphForce.nodes(nodes)
		.links(links);

	graphForce.start();

	//Drag Behavior 
	var authorNodeCircleDrag = d3.behavior.drag()
	   .origin(function(d) { return d; })
	   .on("dragstart", function(d) {
	           d3.event.sourceEvent.stopPropagation();
	           d3.select(this).classed("dragging", true);
	           graphForce.start();
	   })
	   .on("drag", authornodecircledragged)
	   .on("dragend", dragended);


	// scale functions
	var linethickness = d3.scale.linear()
		.domain([0,maxCollaborations])
		.range([1,12]);

	var nodeRadius = d3.scale.linear()
		.domain([0,maxPublications])
		.range([10,50]);

	// Creating nodes & edges
	var link =container.selectAll(".line")
		.data(links)
		.enter()
		.append("line")
		.attr("stroke-width",4)
		.attr("stroke-width", function(d) {
			return linethickness(d.value);
		})
		.style("stroke","gray");

	var authorNode = container.selectAll("circle.authorNode")
		.data(nodes)
		.enter()
		.append("g")
		.attr("class","authorNode")
		.call(authorNodeCircleDrag)

	var authorNodeCircle = authorNode.append("svg:circle")
		.attr("r", function(d) {
			return nodeRadius(d.publications);
		})
		.attr("fill", d3.rgb("#c2a267"));

	var authorNodeCircleText = authorNode.append("svg:text")
		.text(function(d) {
			return d.name;
		})
		.attr("class","authorNodeText")
		.style("pointer-events","none");

	// Mouse Event Handling
	// Links
	link.on("mousemove", function(d, index, element) {
		linkTooltip.selectAll("p").remove();
		linkTooltip.style("left", (d3.event.pageX+15) +"px")
			.style("top", (d3.event.pageY-10) + "px");
		linkTooltip.append("p")
			.attr("class","tooltiptext")
			.html("<span>Collaborations: </span>" + d.value);

	});

	link.on("mouseover", function(d) {
		linkTooltip.transition()
			.duration(500)
			.style("opacity",1);
		link.style("stroke", function(l) {
			if(d.source === l.source && d.target === l.target)
				return d3.rgb('#9E00D9');
			else
				return 'gray';
		});
	});

	link.on("mouseout", function(d) {
		linkTooltip.transition()
			.duration(500)
			.style("opacity",1e-6);
		link.style("stroke","gray")
			.style("opacity",1);
	});

	// Authors
	authorNodeCircle.on("mousemove", function(d, index, element) {
		authorNodeTooltip.selectAll("p").remove();
		authorNodeTooltip.style("left", (d3.event.pageX+15) +"px")
			.style("top", (d3.event.pageY-10) + "px");
		authorNodeTooltip.append("p")
			.attr("class","tooltiptext")
			.html("<span>name: </span>" + d.name);

	});

	authorNodeCircle.on("mouseover", function(d) {
		authorNodeTooltip.transition()
			.duration(500)
			.style("opacity",1);
		link.style("stroke", function(l) {
			if(d === l.source || d === l.target)
				return d3.rgb('#9E00D9');
			else
				return 'gray';
		});
		link.style('opacity', function(o) {
			return o.source === d || o.target === d ? 1 : 0;
		});
		authorNode.style('opacity', function(o) {
			if(o.id != d.id)
				return neighboring(d.id,o.id) ? 1 : 0;
		});
	});

	authorNodeCircle.on("mouseout", function(d) {
		authorNodeTooltip.transition()
			.duration(500)
			.style("opacity",1e-6);
		link.style("stroke","gray")
			.style("opacity",1);
		authorNode.style("opacity",1);
	}); 
	
	d3links = link;

	d3nodes = authorNode;

	d3nodesCircle = authorNodeCircle;

	graphForce.on("tick", function() {
		
		link.attr("x1", function(d) { return d.source.x; })
		.attr("y1", function(d) { return d.source.y; })
		.attr("x2", function(d) { return d.target.x; })
		.attr("y2", function(d) { return d.target.y; });
		//var r = +authorNodeCircle.attr("r");

		authorNodeCircle.attr('cx', function (d) { return d.x; })
         .attr('cy', function (d) { return d.y; })
         .attr('fixed',true);

		//authorNodeCircle.attr("cx", function(d) { return d.x = Math.max(r + 100, Math.min(widthAuthor - r - 100, d.x)); })
        //.attr("cy", function(d) { return d.y = Math.max(r + 100, Math.min(heightAuthor - r - 100, d.y)); });

        authorNodeCircleText.attr("x", function(d) {
        	return d.x-15;
        });
        authorNodeCircleText.attr("y", function(d) {
        	return d.y-15;
        });

		//circletext.attr("x", function(d) { return d.x-25; });
		//circletext.attr("y", function(d) { return d.y-25;});
	});

	graphForce.on("end", function() {
		scaleToContent(container,zoom,venueAuthorConnectionGraph,graphForce);
		removeLoadingImage("loaderVenueAuthorConnectionGraph");
		container.style("visibility","visible");

		//Remove existing minimap
		$("#minimap").empty();
		createMinimap(zoom,container);
	});

	addZoomMoveIcon("#venueAuthorConnectionGraph");

}

function authornodecircledragged(d) {
	d3.select(this).attr("cx",d.x = d3.event.x).attr("cy",d.y = d3.event.y);
}

function dragended(d) {
	d3.select(this).classed("dragging",false);
}

function scaleToContent(container,zoom,graph,graphForce) {
	var gNodes = graphForce.nodes();

		// Find coordinate of top left and bottomm right corner of graph container
		var maxX= 0;
		var maxY = 0;
		var minX = 10000;
		var minY = 10000;
		for(n=0 ; n < gNodes.length; n++) {
			var gNode = gNodes[n];
			var x = gNode.x;
			var y = gNode.y;
			if(x > maxX) maxX=x;
			if(x < minX) minX=x;
			if(y > maxY) maxY=y;
			if(y < minY) minY=y;
		}

		maxX += 20;
		maxY += 20;
		minX -= 20;
		minY -= 20;
		var scaleXMin = (widthAuthor -10) / (Math.abs(maxX - minX));
		var scaleYMin = (heightAuthor -10) / (Math.abs(maxY - minY));
		var scaleMin = Math.min(scaleXMin,scaleYMin,1);

		var graphContainerWidth = Math.abs(maxX - minX);
		var graphContainerHeight = Math.abs(maxY - minY);

		// Center of the graph Container
		var graphContainerCenterX = maxX - (graphContainerWidth/2);
		var graphContainerCenterY = maxY - (graphContainerHeight/2);

		var graphContainerScaledCenterX = graphContainerCenterX * scaleMin;
		var graphContainerScaledCenterY = graphContainerCenterY * scaleMin;

		var containerCenterX = widthAuthor/2;
		var containerCenterY = heightAuthor/2;

		var translationX = containerCenterX - graphContainerScaledCenterX;
		var translationY = containerCenterY - graphContainerScaledCenterY;

		container.attr("transform", "translate(" + [translationX,translationY] + ")scale(" + scaleMin + ")");
		zoom.translate([translationX,translationY]);
		zoom.scale(scaleMin);
		graph.call(zoom);
}

/* ******** */
/* MINIMAP */
/* ******** */

venueGraph = {};
venueGraph.util = {};
venueGraph.util.getVarsFromTransform = function(transformString) {
	var split = transformString.split(",");
	var x = split[0] ? ~~split[0].split("(")[1] : 0;
    var y = split[1] ? ~~split[1].split(")")[0] : 0;

    var splitScale = transformString.split("scale(");
    var scale = splitScale[1] ? splitScale[1].replace(")","") : 1;
    return [x, y, scale];
};

venueGraph.minimap = function() {

	var minimapScale 			= 0.2,
		scale 					= 1,
		zoom 					= null,
		base 					= null,
		targetGraph				= null,
		frameWidth 				= 0,
		frameHeight 			= 0,
		frameTranslationX		= 0,
		frameTranslationY		= 0,
		frameScale				= 1,
		initTransform			= null,
		initTranslationX		= 0,
		initTranslationY  		= 0,
		initScale				= 1;


	function minimap(selection) {
		base = selection;

		//Create Structure 
		var minimapContainer = selection.append("g")
			.attr("class","minimap")
			.call(zoom);

		minimap.node = minimapContainer.node();

		var frame = minimapContainer.append("g")
			.attr("class","frame");

		frame.append("rect")
			.attr("class", "background")
			.attr("width",frameWidth)
			.attr("height",frameHeight);

		// minimap zoom
		zoom.on("zoom.minimap", function() {
			scale = d3.event.scale;
		});

		// frame drag
		var drag = d3.behavior.drag()
			.on("drag.minimap", function() {
				d3.event.sourceEvent.stopImmediatePropagation();
				frameTranslationX += d3.event.dx;
				frameTranslationY += d3.event.dy;
				frame.attr("transform","translate("+frameTranslationX + "," + frameTranslationY + ")scale(" + frameScale + ")");
				var targetTransform = venueGraph.util.getVarsFromTransform(targetGraph.attr("transform"));
				var targetTranslateX = targetTransform[0] - (d3.event.dx/frameScale);
				var targetTranslateY = targetTransform[1] - (d3.event.dy/frameScale);
				targetGraph.attr("transform","translate(" + targetTranslateX + "," + targetTranslateY +")scale(" + targetTransform[2] + ")");

				zoom.translate([targetTranslateX,targetTranslateY]);
			});
		frame.call(drag)

	    minimap.render = function() {
	    	scale = zoom.scale();

	    	var node = targetGraph.node().cloneNode(true);

	    	minimapContainer.attr("transform","translate(0,0)scale(" + minimapScale + ")");

	    	//Remove existing minimap node container
	    	base.selectAll(".minimap .nodeContainer").remove();

	    	minimap.node.appendChild(node);

	    	var targetTransform = venueGraph.util.getVarsFromTransform(targetGraph.attr("transform"));

	    	frameTranslationX = initTranslationX - ((targetTransform[0]*initScale)/scale);
	    	frameTranslationY = initTranslationY - ((targetTransform[1]*initScale)/scale);
	    	frameScale = (initScale/scale);
	    	frame.attr("transform", "translate(" + frameTranslationX + "," + frameTranslationY + ")scale("+frameScale+")");
	   
	   		//put the frame on top
	    	frame.node().parentNode.appendChild(frame.node());

	    	d3.select(node).attr("transform", initTransform);


	    };

	}

	//============================================================
    // Accessors
    //============================================================


    minimap.frameWidth = function(value) {
        if (!arguments.length) return width;
        width = parseInt(value, 10);
        return this;
    };


    minimap.frameHeight = function(value) {
        if (!arguments.length) return height;
        height = parseInt(value, 10);
        return this;
    };

    minimap.scale = function(value) {
        if (!arguments.length) { return scale; }
        scale = value;
        return this;
    };


    minimap.minimapScale = function(value) {
        if (!arguments.length) { return minimapScale; }
        minimapScale = value;
        return this;
    };


    minimap.zoom = function(value) {
        if (!arguments.length) return zoom;
        zoom = value;
        return this;
    };


    minimap.targetGraph = function(value) {
        if (!arguments.length) { return target; }
        targetGraph = value;
        frameWidth  = parseInt(targetGraph.attr("width"),  10);
        frameHeight = parseInt(targetGraph.attr("height"), 10);
        initTransform = targetGraph.attr("transform");
        initTranslation = venueGraph.util.getVarsFromTransform(initTransform);
        initTranslationX = initTranslation[0];
        initTranslationY = initTranslation[1];
        initScale = initTranslation[2];
        return this;
    };

    return minimap;





}