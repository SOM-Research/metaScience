var metaScienceServlet = 'http://localhost:8080/metaScience';
//var metaScienceServlet = 'http://atlanmodexp.info.emn.fr:8800/metaScience';

// Venue/subvenue ids
var venueId;
var subvenueId;

// This is the graph about turnover
var perishingChart;

// Turnover information is stored to improve performance
var turnover1;
var turnover3;

window.onload = function() {

  if(window.location.protocol !== 'http:') {
    $("#error").html('<p>You are accessing from an HTTPS connection and our service is located in an HTTP server.</p><p>Please access to our HTTP server <a href="http://atlanmod.github.io/metaScience">here</p>');
    $("#error").css("visibility" ,"visible");
  }

	var params = {};
	var venueName;

	// Getting the param from the URL
	if (location.search) {
	    var parts = location.search.substring(1).split('&');

	    for (var i = 0; i < parts.length; i++) {
	        var nv = parts[i].split('=');
	        if (!nv[0]) continue;
	        params[nv[0]] = nv[1] || -1;
	    }
	}
	
	// Getting the full name of the venue
	if(params.id) {
		venueId = params.id;	
		$.ajax({
			url : metaScienceServlet + "/venueName?id=" + params.id,
			success : function(data) {
				venueName = data.name;
				$("#venueName").text(venueName);
			},
			error : function(data) {
				$("#venueName").text(params.id);
			}
		});
	} else {
		$("#venueName").text('No venue found');
	}

	// Searching for satellite events
	var subvenues =
    {
        datatype: "json",
        datafields: [
            { name: 'name', type : 'string' },
            { name: 'id', type : 'string' },
        ],
        url: metaScienceServlet + "/subvenues"
    };
        
  var dataAdapter = new $.jqx.dataAdapter(subvenues,
    {
        beforeSend: function (jqxhr, settings) {
          searchstring = $("#satelliteCombobox").jqxComboBox('searchString');
            if (searchstring != undefined) {
              settings.url = settings.url + "&id=" + params.id + "&search=" + searchstring;
            } else {
                  settings.url = settings.url + "&id=" + params.id
              }
        },

        loadComplete: function() {
        }
    }
  );

 	$("#satelliteCombobox").jqxComboBox(
    {
        width: "100%",
        height: 25,
        source: dataAdapter,
        displayMember: "name",
        valueMember: "id",
        remoteAutoComplete: true,
        remoteAutoCompleteDelay: 500,
        minLength: 1,
        placeHolder: "Main Conference track",
        showArrow : true,
        search: function (searchString) {
        	$(".jqx-combobox-input, .jqx-combobox-content").css({ "background": "url('imgs/loading_project.gif') no-repeat right 5px center" });
            dataAdapter.dataBind();
        }
    });

 	dataAdapter.dataBind();
 	updateGraphs(venueId, venueId);
 	subvenueId = venueId;
	
	$("#satelliteCombobox").on('bindingComplete', function (event) {
    	$(".jqx-combobox-input, .jqx-combobox-content").css({ "background-image": "none" });
    });

    $("#satelliteCombobox").on('select', function (event) {
    	if (typeof event.args != 'undefined') {
        var selecteditem = event.args.item;
        subvenueId = selecteditem;
        if (selecteditem) {
          $("#avgAuthorsLoading").css("visibility", "visible");
          $("#avgPapersLoading").css("visibility", "visible");
          $("#avgAuthorsPerPaperLoading").css("visibility", "visible");
          $("#avgPapersPerAuthorLoading").css("visibility", "visible");
          $("#avgPerishingRateLoading").css("visibility", "visible");
          $("#avgOpennessLoading").css("visibility", "visible");
          updateGraphs(venueId, selecteditem.originalItem.id);
        }
    	}
    });

    $("#turnover1").on('click', function(event) {
    	updateTurnover(venueId, subvenueId, "1");
    });

    $("#turnover3").on('click', function(event) {
    	updateTurnover(venueId, subvenueId, "3");
    });
}

function updateGraphs(venueId, subvenueId) {
	updateBasic(venueId, subvenueId);
  updateRank(venueId,subvenueId);
	updateTurnover(venueId, subvenueId, "1");
  updateOpenness(venueId, subvenueId);
  //generateVenueAuthorConnectionGraph(venueId,subvenueId);
  generateVenueTitleTagCloudGraph(venueId,subvenueId);
}

function updateBasic(venueId, subvenueId) {
	$.ajax({
		url: metaScienceServlet + "/venueActivity?id=" + venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : ""),
		success : function(data) {
	        $("#activityChartRow").css("visibility", "visible");
	        $("#ratiosChartRow").css("visibility", "visible");
      $("#avgAuthorsLoading").css("visibility", "hidden");
			$("#avgAuthors").text(data.authors.avg);
      $("#avgPapersLoading").css("visibility", "hidden");
			$("#avgPapers").text(data.papers.avg);
			var activityChart = c3.generate({		
			    bindto: '#activityChart',
			    data: {
			    	xs: {
			    		'Authors'  : 'x1',
			    		'Papers'   : 'x2'
			    	},
			      	columns: [
			        	data.authors.yearly[0],
			        	data.authors.yearly[1],
			        	data.papers.yearly[0],
			        	data.papers.yearly[1]
			      ]
			    }
			});

      $("#avgAuthorsPerPaperLoading").css("visibility", "hidden");
			$("#avgAuthorsPerPaper").text(data.authorsPerPaper.avg);
      $("#avgPapersPerAuthorLoading").css("visibility", "hidden");
			$("#avgPapersPerAuthor").text(data.papersPerAuthor.avg);
			var ratiosChart = c3.generate({		
			    bindto: '#ratiosChart',
			    data: {
			    	xs: {
			    		'AuthorsPerPaper'  : 'x1',
			    		'PapersPerAuthor'  : 'x2'
			    	},
			      	columns: [
			        	data.authorsPerPaper.yearly[0],
			        	data.authorsPerPaper.yearly[1],
			        	data.papersPerAuthor.yearly[0],
			        	data.papersPerAuthor.yearly[1]
			      ]
			    },
		        axis : {
		        	y : {
		        		tick : {
		        			format : d3.format(".2")
		        		}
		        	}
		        }
			});
		},
		error : function(xhr, status, error) {
			$("#avgAuthors").text("Not available");
			$("#avgPapers").text("Not available");
			$("#avgAuthorsPerPaper").text("Not available");
			$("#avgPapersPerAuthor").text("Not available");
	        $("#activityChartRow").css("visibility", "hidden");
	        $("#ratiosChartRow").css("visibility", "hidden");
		}
	});
}

function updateRank(venueId,subvenueId) {
  $.ajax( {
    url: metaScienceServlet + "/venueAuthorRank?id=" + venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : ""),
    success: function(data) {
      $("#topAuthor1").text(data.top["1"].name);
      $("#topAuthor2").text(data.top[2].name);
      $("#topAuthor3").text(data.top[3].name);
      $("#topAuthor4").text(data.top[4].name);
      $("#topAuthor5").text(data.top[5].name);

      $("#regularAuthor1").text(data.regular[1].name);
      $("#regularAuthor2").text(data.regular[2].name);
      $("#regularAuthor3").text(data.regular[3].name);
      $("#regularAuthor4").text(data.regular[4].name);
      $("#regularAuthor5").text(data.regular[5].name);
    },
    error: function(xhr, status, error) {

    }
  });
}

function updateTurnover(venueId, subvenueId, span) {
  if (span == undefined)
    span = 1;

  if(venueId != subvenueId && subvenueId != undefined) {
    $("#avgPerishingRate").text("Not available");
    $("#perishingChartRow").css("visibility", "hidden");
  } else {
    if(turnover1 == undefined || turnover3 == undefined) {
      $.ajax({
        url: metaScienceServlet + "/venueTurnover?id=" + venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : "") + "&span=1",
        success : function(data1) {
          turnover1 = data1;
          $.ajax({
            url: metaScienceServlet + "/venueTurnover?id=" + venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : "") + "&span=3",
            success : function(data3) {
              turnover3 = data3;
              $("#avgPerishingRateLoading").css("visibility", "hidden");
              //$("#avgPerishingRate").text(turnover1.perished.avg + "% / " + turnover3.perished.avg + "% ");
              $("#avgPerishingRate").text(turnover1.perished.avg + "%");
              updateTurnoverGraph(turnover1);
            },
            error : function(xhr, status, error) {
              $("#avgPerishingRate").text("Not available");
              $("#perishingChartRow").css("visibility", "hidden");
            }
          });
        },
        error : function(xhr, status, error) {
          $("#avgPerishingRate").text("Not available");
          $("#perishingChartRow").css("visibility", "hidden");
        }
      });
    } else if (span == 1 && turnover1 != undefined) {
      updateTurnoverGraph(turnover1);
    } else if (span == 3 && turnover3 != undefined) {
      updateTurnoverGraph(turnover3);
    }
  }
}

function updateTurnoverGraph(turnoverData) {
  if(perishingChart != undefined)
    perishingChart.unload();

  $("#perishingChartRow").css("visibility" ,"visible");
  perishingChart = c3.generate({
    bindto : "#turnoverChart",
    data: {
      xs: {
        'Perished' : 'x1',
        'Survived' : 'x2'
      },
      columns: [
        turnoverData.perished.yearly[1],
        turnoverData.perished.yearly[2],
        turnoverData.survived.yearly[1],
        turnoverData.survived.yearly[2]
      ],
      type: 'bar',
      groups: [
          ['Perished', 'Survived']
      ]
      },
    axis : {
      y : {
        min : 0,
        max : 1,
        padding : {
          top : 0,
          bottom : 0
        },
        tick : {
          format : d3.format(".2%")
        }
      },
      x : {
        type : 'category',
        tick : {
          rotate : (turnoverData.survived.yearly[1].length > 9) ? -60 : 0
        }
      },
    },
    legend : {
      position : (turnoverData.survived.yearly[1].length > 9) ? 'inset' : 'bottom',
      inset : {
        anchor: 'top-right',
        x: 20,
        y: 20,
        step: 2
      }
    },
    padding : {
      bottom : (turnoverData.survived.yearly[1].length > 9) ? 40 : 0
    }
  });
}

function updateOpenness(venueId, subvenueId) {
	if (venueId != subvenueId && subvenueId != undefined) {
		$("#avgOpenness").text("Not available");
        $("#opChartRow").css("visibility", "hidden");
	} else {
    $("#opChartRow").css("visibility", "visible");
		$.ajax( {
			url: metaScienceServlet + "/venueOpenness?id=" + venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : ""),
			success : function(data) {
        $("#avgOpennessLoading").css("visibility", "hidden");
				$("#avgOpenness").text(data.papers.avg + "% / " + data.authors.avg + "%");
				var pcChart = c3.generate({
					bindto : "#opChart",
					data: {
						xs: {
							'PapersFromNewcomers' : 'x1',
              'PapersFromCommunity' : 'x2'
						},
            columns: [
              data.papers.yearly[0],
              data.papers.yearly[1],
              data.papersCommunity.yearly[0],
              data.papersCommunity.yearly[1]
            ],
            type: 'bar'
          },
          axis : {
            y : {
              min : 0,
              max : 1,
              padding : {
                top : 0,
                bottom : 0
              },
              tick : {
                format : d3.format(".2%")
              }
            }
          }
				});
			},
			error : function(xhr, status, error) {
				$("#avgOpenness").text("Not available");
		        $("#opChartRow").css("visibility", "hidden");
			}
		});
	}
}

function updatePC(venueId, subvenueId) {
	if (venueId != subvenueId && subvenueId != undefined) {
		$("#avgPC").text("Not available");
        $("#pcChartRow").css("visibility", "hidden");
	} else {
        $("#pcChartRow").css("visibility", "visible");
		$.ajax( {
			url: metaScienceServlet + "/venuePC?id=" + venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : ""),
			success : function(data) {
				$("#avgPC").text(data.withPC.avg + "%");
				var pcChart = c3.generate({
					bindto : "#pcChart",
					data: {
						xs: {
							'PCcoauthoredPapers' : 'x1',
							'NoPCcoauthoredPapers' : 'x2'
						},
				        columns: [
				            data.withPC.yearly[0],
				            data.withPC.yearly[1],
				            data.withoutPC.yearly[0],
				            data.withoutPC.yearly[1]
				        ],
				        type: 'bar',
				        groups: [
				            ['PCcoauthoredPapers', 'NoPCcoauthoredPapers']
				        ]
				    },
			        axis : {
			        	y : {
			        		min : 0,
			        		max : 1,
			        		padding : {
			        			top : 0,
			        			bottom : 0
			        		},
			        		tick : {
			        			format : d3.format(".2%")
			        		}
			        	}
			        }
				});
			}
		});
	}
}

function updateTitleCloud(venueId,subvenueId) {
  if (venueId != subvenueId && subvenueId != undefined) {
    //$("#avgPC").text("Not available");
    $("#venueTitleCloudRow").css("visibility", "hidden");
  } else {
        $("#venueTitleCloudRow").css("visibility", "visible");
    $.ajax( {
      url: metaScienceServlet + "/venueTitleCloud?id=" + venueId + ((venueId != subvenueId && subvenueId != undefined) ? "&subid=" + subvenueId : ""),
      success : function(data) {
        var words = data.global;

        var fontSize = d3.scale.log().range([10,100]);

        var titleCloud = d3.layout.cloud()
            .text(function(d) {
              return d.word;
            })
            .fontSize(function(d) {
              return fontSize(d.occurence);
            })
            .words(words)
            .start();

        
      }
    });
  }


}

function onLoadingGraph(svgIdContainer, loaderId, svgHeight, svgWidth) {
  svgIdContainer
  .append("svg:image")
  .attr("id", loaderId)
  .attr("xlink:href", "imgs/ajax-loader.gif")
  .attr("width", "5%")
  .attr("height", "5%")
  .attr("x", function(){ return svgWidth/2;})
  .attr("y", function(){ return svgHeight/2;});
}
 
function removeLoadingImage(loaderId) {
     d3.select('#' + loaderId).remove();
}
 
function creatingWarningMessage(svgIdContainer, posX, posY, text) {
     svgIdContainer.append("svg:image")
     .attr("xlink:href", "imgs/warningimage.png")
     .attr("width", "98%")
     .attr("height", "98%");
                              
     svgIdContainer.append("text")
     .attr("x", posX)
     .attr("y", posY)
     .attr("font-family", "sans-serif")
     .attr("font-size", "28px")
     .attr("text-anchor", "middle")
     .attr("fill", "red")
     .text(text);
}


function addZoomMoveIcon(visId) {
     
     d3.select(visId)
     .append("svg:image")
     .attr("xlink:href", "imgs/move_zoom.svg")
     .attr("width","72")
     .attr("height","72")
     .attr("x","10")
     .attr("y","10")
     .append("svg:title")
     .text("Scroll to zoom, drag to move");
}


