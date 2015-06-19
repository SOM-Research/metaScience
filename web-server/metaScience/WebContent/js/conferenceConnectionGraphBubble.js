/**
 *  Co author Connection graph
 */
 
 var widthConferenceGraph = 718;
 var heightConferenceGraph = 600;
 
var d3conferenceNodes;

var displayAttendance = true;

var maxAttendance,maxPublications;
var graphNodes;

 var conferenceConnectionGraph = d3.select("#conferenceConnectionGraphContainer")
 .append("svg")
 .attr("width",widthConferenceGraph)
 .attr("height",heightConferenceGraph)
 .append("svg:g")
 .attr("id","conferenceConnectionGraph");
 
 function generateConferenceConnectionGraph(authorId) {
     // remove previous graph if exists
     if( $("#conferenceConnectionGraph").children().size() > 0) {
          $("#conferenceConnectionGraph").empty();
          $("#conferenceSlider").empty();
     }

     getConferenceConnectionGraphBubble(authorId);
 }

function getConferenceConnectionGraphBubble(authorId) {
     onLoadingGraph(d3.select("#conferenceConnectionGraph"), "loaderConferenceConnectionGraph", heightConferenceGraph, widthConferenceGraph);

     d3.json(metaScienceServlet + "/conferenceConnection?id="+authorId, function(errorJson,jsonNodes) {
          if(jsonNodes == undefined) {
              removeLoadingImage("loaderConferenceConnectionGraph");

              $("#totalConferences").text("Not available");
              $("#avgConferences").text("Not available");

              creatingWarningMessage(d3.select("#conferenceConnectionGraph"),heightConferenceGraph/2,widthConferenceGraph/2,"An error occured");
          } else {
              var conferenceNodes = jsonNodes.conferences;
              maxAttendance = jsonNodes.author.max_attendance;
              maxPublications = jsonNodes.author.max_publications;
              var totalConferences = jsonNodes.author.total_conferences;
              var averageConferences = jsonNodes.author.average_conferences;

              $("#totalConferencesLoading").css("visibility","hidden");
              $("#totalConferences").text(totalConferences);
              $("#avgConferencesLoading").css("visibility","hidden");
              $("#avgConferences").text(averageConferences);

              if(conferenceNodes.length > 0) {
                    var nodes = {
                    children : conferenceNodes
                    };

                    graphNodes = nodes;

                   removeLoadingImage("loaderConferenceConnectionGraph");
                   $("#info_conferenceConnectionGraph").css("visibility","visible");

                   loadGraph(true);

                   var comboboxNodes = new Array();
                   comboboxNodes.push({source : " - All conferences - "});
                   comboboxNodes = comboboxNodes.concat(conferenceNodes);

                   $("#conferenceCombobox").jqxComboBox(
                  {
                      width: "100%",
                      height: 25,
                      source: comboboxNodes,
                      selectedIndex: 0,
                      displayMember: "source",
                      valueMember: "source",
                      placeHolder: "conference name",
                      showArrow : true,
                      search: function (searchString) {
                        $(".jqx-combobox-input, .jqx-combobox-content").css({ "background": "url('imgs/loading_project.gif') no-repeat right 5px center" });
                          //dataAdapter.dataBind();
                      }
                  });

                  $("#conferenceCombobox").on('bindingComplete', function (event) {
                        $(".jqx-combobox-input, .jqx-combobox-content").css({ "background-image": "none" });
                  });
                  
                  $("#conferenceCombobox").on('select', function (event) {
                        if (typeof event.args != 'undefined') {
                             var selecteditem = event.args.item;
                             var selectedIndex = event.args.index;
                             if (selecteditem) {
                                  var node = d3.select(selecteditem.originalItem);
                                  if(node.length == 1) {
                                       node = node[0][0];
                                       if(selectedIndex != 0) {
                                            d3conferenceNodes.style("opacity", function(n) {
                                                 if(node.source != n.source) {
                                                      return 0.07;
                                                 }
                                            })
                                       } else {
                                          d3conferenceNodes.style("opacity", function(n) {
                                                 if(node.source != n.source) {
                                                      return 1;
                                                 }
                                            })
                                       }
                                  }
                             }
                        }
                   });

                  $("#conferenceCombobox").on('click', function (event) {
                        $("#conferenceCombobox").jqxComboBox({selectedIndex: -1});
                   });

                   $("#conferenceRadio1").jqxRadioButton( {
                        width: "100%",
                        height: 25,
                        groupName: "conferenceDisplayGroup",
                        checked: true
                   });

                   $("#conferenceRadio2").jqxRadioButton( {
                        width: "100%",
                        height: 25,
                        groupName: "conferenceDisplayGroup"
                   });

                   $("#conferenceRadio1").on('checked', function(event) {
                        loadGraph(true);
                   });

                   $("#conferenceRadio2").on('checked', function(event) {
                        loadGraph(false);
                   });

                   $("#resetConferenceCbxBtn").on('click', function(event) {
                        $("#conferenceCombobox").jqxComboBox('selectIndex',0);
                   });

              }
          }
     });

}

function loadGraph(loadAttendance) {

     displayAttendance = loadAttendance;

     $("#conferenceConnectionGraph").empty();
     $("#conferenceSlider").empty();

     drawConferenceConnectionGraphBubble(graphNodes);

     $("#conferenceCombobox").jqxComboBox({selectedIndex: -1});

     createSlider("conferenceSlider",getLabelText(),1,getMax(),sliderChangeFunction);

}

function drawConferenceConnectionGraphBubble(nodes) {

     
    var circleColor = d3.scale.category20();

    var bubbleGraph = d3.layout.pack()
          .sort(null)
          .size([widthConferenceGraph,heightConferenceGraph])
          .value(function(d) { return getValue(d);})
          .padding(1.5);

    var zoom = d3.behavior.zoom()
        .scaleExtent([1,10])
        .on("zoom",function() {
          container.attr("transform","translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");           
        });

     var panrect = conferenceConnectionGraph.append("rect")
                                        .attr("width",widthConferenceGraph)
                                        .attr("height",heightConferenceGraph)
                                        .style("fill","none")
                                        .style("pointer-events","all");

     var container = conferenceConnectionGraph.append("g")
                                        .attr("id","container");

    // Zoom behavior
    var zoom = d3.behavior.zoom()
        .scaleExtent([1,10])
        .on("zoom",function() {
          container.attr("transform","translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");           
        });

    conferenceConnectionGraph.call(zoom);

    addZoomMoveIcon("#conferenceConnectionGraph");


     // Conference Nodes
     var nodeR = container.selectAll("circle.conferenceNode")
                                        .data(bubbleGraph.nodes(nodes).filter(function(d) { return !d.children;}))
                                        .enter()
                                        .append("g")
                                        .attr("class","conferenceNode")
                                        .attr("transform", function(d) { return "translate(" + (d.x - (rectWidth(d.r)/2)) + "," + (d.y - (rectWidth(d.r)/2)) + ")"; });
     d3conferenceNodes = nodeR;

     var nodeRect = nodeR.append("svg:rect")
          .attr("height", function(d) {
               return rectWidth(d.r);
          })
          .attr("width", function(d) {
               return rectWidth(d.r);
          })
          .attr("fill", function(d) { return circleColor(getValue(d));});

     var nodeTooltip = d3.select("body").append("div")
          .attr("class","conferenceTooltip")
          .style("opacity",1e-6);

     // Add mouse events
     nodeRect.on("mousemove", function(d, index, element) {
          nodeTooltip.selectAll("p").remove();
          nodeTooltip.style("left", (d3.event.pageX+15)+"px")
                    .style("top",(d3.event.pageY-10) + "px");

          nodeTooltip.append("p").attr("class","tooltiptext").html("<span> name: <span>" + d.source);
          nodeTooltip.append("p").attr("class","tooltiptext").html("<span> number of attendance: <span>" + d.attendance);
          nodeTooltip.append("p").attr("class","tooltiptext").html("<span> number of publication: <span>" + d.publications);

     });

     nodeRect.on("mouseover", function(d, index, element) {
          nodeTooltip.transition()
                    .duration(500)
                    .style("opacity",1);
     });

     nodeRect.on("mouseout", function(d, index, element) {
          nodeTooltip.transition()
                    .duration(500)
                    .style("opacity", 1e-6);
     });
                

}

function sliderChangeFunction(numStart,numEnd) {
    d3conferenceNodes.style("opacity", function(n) {
         var value = getValue(n);
         if(value < numStart || value > numEnd) {
              return 0.07;
         }
    });
}

function getValue(node) {

     if(displayAttendance == true) {
          return node.attendance;
     } else{
          return node.publications;
     }
}

function getMax() {
     console.log(displayAttendance);
     if(displayAttendance == true) {
          return maxAttendance;
     } else {
          return maxPublications;
     }
}

function getLabelText() {
     if(displayAttendance == true) {
          return 'Number of Attendance';
     } else {
          return 'Number of Publications';
     }
}

function rectWidth(r) {
     var hypo = r * (1/ Math.cos(Math.PI/4));
     return hypo;
}




 
