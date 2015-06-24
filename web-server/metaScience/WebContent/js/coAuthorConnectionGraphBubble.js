/**
 *  Co author Connection graph
 */
 
 var widthCoAuthorGraph = 718;
 var heightCoAuthorGraph = 600;
 
var d3nodes;

 var coAuthorConnectionGraph = d3.select("#coAuthorConnectionGraphContainer")
 .append("svg")
 .attr("width",widthCoAuthorGraph)
 .attr("height",heightCoAuthorGraph)
 .append("svg:g")
 .attr("id","coAuthorConnectionGraph");
 
 function generateCoAuthorConnectionGraph(authorId) {
 	// remove previous graph if exists
 	if( $("#coAuthorConnectionGraph").children().size() > 0) {
 		$("#coAuthorConnectionGraph").empty();
 		$("collabSlider").empty();
 	}

 	getCoAuthorConnectionGraphBubble(authorId);
 }

function getCoAuthorConnectionGraphBubble(authorId) {

     onLoadingGraph(d3.select("#coAuthorConnectionGraph"), "loaderCoAuthorConnectionGraph", heightCoAuthorGraph, widthCoAuthorGraph);

     d3.json(metaScienceServlet + "/coAuthorConnection?id="+authorId, function(errorJson,jsonNodes) {
          if(jsonNodes == undefined) {

              removeLoadingImage("loaderCoAuthorConnectionGraph");

              $("#totalCollaborations").text("Not available");
              $("#avgCollaborations").text("Not available");

              creatingWarningMessage(d3.select("#coAuthorConnectionGraph"),heightCoAuthorGraph/2,widthCoAuthorGraph/2,"An error occured");

          } else {
              
              var authorNodes = jsonNodes.coAuthors;
              var maxCollaborations = jsonNodes.author.max_collaborations;
              var totalCollaborations = jsonNodes.author.total_collaborators;
              var averageCollaborations = jsonNodes.author.average_collaborations;

              $("#totalCollaborationsLoading").css("visibility","hidden");
              $("#totalCollaborations").text(totalCollaborations);
              $("#avgCollaborationsLoading").css("visibility","hidden");
              $("#avgCollaborations").text(averageCollaborations);

              // d3.layout.pack work with hierarchic; this is to flatten the hierarchy and respect the input format of pack
              if(authorNodes.length > 0) {
                  var nodes = {
                      children : authorNodes
                  }
               };

               removeLoadingImage("loaderCoAuthorConnectionGraph");
               $("#info_coAuthorConnectionGraph").css("visibility","visibile");
               drawCoAuthorConnectionGraphBubble(nodes,maxCollaborations);


               createSlider("collabSlider","Number of collaborations", 1,maxCollaborations,sliderCollaborationChangeFunction);


               

               var comboboxNodes = new Array();
               comboboxNodes.push({name : " - All co authors - ", id: -1});
               comboboxNodes = comboboxNodes.concat(authorNodes);

               $("#coAuthorCombobox").jqxComboBox(
              {
                  width: "100%",
                  height: 25,
                  source: comboboxNodes,
                  selectedIndex: 0,
                  displayMember: "name",
                  valueMember: "id",
                  placeHolder: "author name",
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
                         if (selecteditem) {
                              var node = d3.select(selecteditem.originalItem);
                              if(node.length == 1) {
                                   node = node[0][0];
                                   if(node.id != -1) {
                                        d3nodes.style("opacity", function(n) {
                                             if(node.id != n.id) {
                                                  return 0.05;
                                             }
                                        })
                                   } else {
                                      d3nodes.style("opacity", function(n) {
                                             if(node.id != n.id) {
                                                  return 1;
                                             }
                                        })
                                   }
                              }
                         }
                    }
               });

              $("#coAuthorCombobox").on('click', function (event) {
                    $("#coAuthorCombobox").jqxComboBox({selectedIndex: -1});
               });

              $("#resetAuthorBtn").on('click', function(event) {
                    $("#coAuthorCombobox").jqxComboBox('selectIndex',0);
               });
          }
          
     });

     
}

function drawCoAuthorConnectionGraphBubble(nodes,maxCollaborations) {

     
    var circleColor = d3.scale.category20();

    var bubbleGraph = d3.layout.pack()
          .sort(null)
          .size([widthCoAuthorGraph,heightCoAuthorGraph])
          .value(function(d) { return d.num_collaborations;})
          .padding(1.5);

    var zoom = d3.behavior.zoom()
        .scaleExtent([1,10])
        .on("zoom",function() {
          container.attr("transform","translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");           
        });

     var panrect = coAuthorConnectionGraph.append("rect")
                                        .attr("width",widthCoAuthorGraph)
                                        .attr("height",heightCoAuthorGraph)
                                        .style("fill","none")
                                        .style("pointer-events","all");

     var container = coAuthorConnectionGraph.append("g")
                                        .attr("id","container");

    // Zoom behavior
    var zoom = d3.behavior.zoom()
        .scaleExtent([1,10])
        .on("zoom",function() {
          container.attr("transform","translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");           
        });

    coAuthorConnectionGraph.call(zoom);

     var node = container.selectAll("circle.authorNode")
                                        .data(bubbleGraph.nodes(nodes).filter(function(d) { return !d.children;}))
                                        .enter()
                                        .append("g")
                                        .attr("class","authorNode")
                                        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
     d3nodes = node;

     var nodeCircle = node.append("svg:circle")
                    .attr("r", function(d) {
                         return d.r;
                    }).attr("fill", function(d) { return circleColor(d.num_collaborations);});

     var nodeTooltip = d3.select("body").append("div")
          .attr("class","coAuthorTooltip")
          .style("opacity",1e-6);

     // Add mouse events
     nodeCircle.on("mousemove", function(d, index, element) {
          nodeTooltip.selectAll("p").remove();
          nodeTooltip.style("left", (d3.event.pageX+15)+"px")
                    .style("top",(d3.event.pageY-10) + "px");

          nodeTooltip.append("p").attr("class","tooltiptext").html("<span> name: <span>" + d.name);
          nodeTooltip.append("p").attr("class","tooltiptext").html("<span> number of collaborations: <span>" + d.num_collaborations);
     });

     nodeCircle.on("mouseover", function(d, index, element) {
          nodeTooltip.transition()
                    .duration(500)
                    .style("opacity",1);
     });

     nodeCircle.on("mouseout", function(d, index, element) {
          nodeTooltip.transition()
                    .duration(500)
                    .style("opacity", 1e-6);
     });

     addZoomMoveIcon("#coAuthorConnectionGraph");
                

}

function sliderCollaborationChangeFunction(numStart,numEnd) {
    d3nodes.style("opacity", function(n) {
      console.log(n.num_collaborations)
         if(n.num_collaborations < numStart || n.num_collaborations > numEnd) {
              return 0.1;
         }
    });
}