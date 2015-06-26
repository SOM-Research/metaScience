//var metaScienceServlet = 'http://localhost:8080/metaScience';
var metaScienceServlet = 'http://som.uoc.es/metaScience';
//var metaScienceServlet = 'http://atlanmodexp.info.emn.fr:8800/metaScience';

// Author/subauthor ids
var authorId;
var subAuthorId;

window.onload = function() {

  if(window.location.protocol !== 'http:') {
    $("#error").html('<p>You are accessing from an HTTPS connection and our service is located in an HTTP server.</p><p>Please access to our HTTP server <a href="http://atlanmod.github.io/metaScience">here</p>');
    $("#error").css("visibility" ,"visible");
  }

	var params = {};
	var authorName;

	// Getting the param from the URL
	if (location.search) {
	    var parts = location.search.substring(1).split('&');

	    for (var i = 0; i < parts.length; i++) {
	        var nv = parts[i].split('=');
	        if (!nv[0]) continue;
	        params[nv[0]] = nv[1] || -1;
	    }
	}
	
	console.log(params.id)
	// Getting the full name of the author
	if(params.id) {
		authorId = params.id;	
		$.ajax({
			url : metaScienceServlet + "/authorName?id=" + params.id,
			success : function(data) {
				authorName = data.name;
				$("#authorName").text(authorName);

				updateGraphs(authorId);

				$(".pubSubCategory").on("show.bs.collapse", function() {
					$(".collapseIcon").empty();
					d3.select(".collapseIcon").append("img")
						.attr("src","imgs/expanded.png");

				})

				$(".pubSubCategory").on("hidden.bs.collapse", function() {
					$(".collapseIcon").empty();
					d3.select(".collapseIcon").append("img")
						.attr("src","imgs/collapsed.png");

				})
			},
			error : function(data) {
				authorNotFound();
			}
		});
	} else {
		authorNotFound();
	}
}

function authorNotFound() {
	hideRow("conferenceConnectionRow");
	hideRow("coAuthorConnectionRow");
	hideRow("collaborationsEvolutionRow");
	hideRow("activityChartRow");
	hideRow("mainRow");
	$("#authorName").text('Author not found');
	$("#notFoundRow").css("display", "block");
}

function updateGraphs(authorId) {
	updateActivity(authorId);
	updatePaperEvolution(authorId);
	updateCollaborations(authorId);
	updateConferences(authorId);
}

function updateActivity(authorId) {
	$.ajax({
		url: metaScienceServlet + "/authorActivity?id=" + authorId,
		success : function(data) {

	        showRow("activityChartRow");
	   
	   		// Main data - Publications Update
	   	  	$("#totalPubLoading").css("visibility","hidden");
	   	  	$("#totalPub").text(data.pub.total);
	   	  	$("#totalPubArticleLoading").css("visibility","hidden");
	   	  	$("#totalPubArticle").text(data.pub.totalArticles);
	   	  	$("#totalPubProceedingLoading").css("visibility","hidden");
	   	  	$("#totalPubProceeding").text(data.pub.totalProceedings);
	   	  	$("#totalPubBookLoading").css("visibility","hidden");
	   	  	$("#totalPubBook").text(data.pub.totalBooks);
	   	  	$("#totalPubIncollectionLoading").css("visibility","hidden");
	   	  	$("#totalPubIncollection").text(data.pub.totalIncollections);
	   	  	$("#totalPubInproceedingLoading").css("visibility","hidden");
	   	  	$("#totalPubInproceeding").text(data.pub.totalInproceedings);
	   	  	$('#totalOthersLoading').css("visibility","hidden");
			$('#totalOthers').text(data.pub.totalOthers); // Issue #15
	   	  	$("#avgPublicationsLoading").css("visibility","hidden");
	   	  	$("#avgPublications").text(data.pub.avgPublications);
	   	  	
	   	  	// Publication Chart update
	   	  	generateActivityDiagram(data.publications);
		},
		error : function(xhr, status, error) {
	   	  	$("#totalPub").text("Not available");
	   	  	$("#totalPubArticle").text("Not available");
	   	  	$("#totalPubProceeding").text("Not available");
	   	  	$("#totalPubBook").text("Not available");
	   	  	$("#totalPubIncollection").text("Not available");
	   	  	$("#totalPubInproceeding").text("Not available");
			$("#totalOthers").text("Not available");
	   	  	$("#avgPublications").text("Not available");
	   	  	
	   	  	hideRow("activityChartRow");
		}
	});
}

function generateActivityDiagram(activityData) {
	var pages = ['Pages'];
	for(var i = 1; i < activityData.years.length + 1; i++) {
		var artP = activityData.articles.pages[i];
		var bookP = activityData.books.pages[i];
		var incollectionP = activityData.incollections.pages[i];
		var inproceedingsP = activityData.inproceedings.pages[i];
		var othersP = activityData.others.pages[i];
		var proceedingsP = activityData.proceedings.pages[i];
		
		var sumP = artP + bookP + incollectionP + inproceedingsP + othersP + proceedingsP;
		pages.push(sumP);
	}
	
	showRow("activityChartRow");
	
  	activityChart = c3.generate({
	    bindto : "#activityChart",
	    data: {
	      columns: [
	        activityData.articles.publications,
	        activityData.books.publications,
	        activityData.inproceedings.publications,
			activityData.incollections.publications,
	        activityData.proceedings.publications,
	        activityData.others.publications,
	        pages
	      ],
	      type: 'bar',
	      types: {
	    	  "Journal papers": 'bar',
	    	  "Books": 'bar',
	    	  "Conference papers": 'bar',
	    	  "Part of book or collection": 'bar',
	    	  "Editor": 'bar',
	    	  "Others": 'bar',
	    	  "Pages": 'line'
	    	  
	      },
	      axes: {
	    	  "Journal papers": 'y',
	    	  "Books": 'y',
	    	  "Conference papers": 'y',
	    	  "Part of book or collection": 'y',
	    	  "Editor": 'y',
	    	  "Others": 'y',
	    	  "Pages": 'y2'
	      },
	      groups: [
	          ["Journal papers", "Books","Conference papers", "Part of book or collection", "Editor", "Others"]
	      ]
      },
      axis: {
      	x: {
      		type: 'category',
      		categories: activityData.years
      	},
      	y: {
      		label: "publications"
      	},
      	y2: {
      		show: true,
      		label: "pages",
      		min:0,
      		center: 0
      	}
      }
 	});


}

function updatePaperEvolution(authorId) {
	$.ajax({
		url: metaScienceServlet + "/collaborationEvolution?id=" + authorId,
		success : function(data) {
	   	  	
	   	  	// Publication Chart update
	   	  	generatePaperEvolutionDiagram(data);
		},
		error : function(xhr, status, error) {
	   	  	hideRow("collaborationEvolutionRow");
		}
	});
}
function generatePaperEvolutionDiagram(data) {
	showRow("collaborationEvolutionRow");

  	activityChart = c3.generate({
    	bindto : "#collaborationEvolutionChart",
    	data: {
      		columns: [
        		data.coauthors,
				data.participation
      		],
      		names: {
      			coAuthors: "Average number of coauthors",
				participation: "Number of co-authored papers"
      		},
      		type: 'bar',
      	},
      	axis: {
      		x: {
      			type: 'category',
      			categories: data.years
      		}
      	}
  	});
}

function updateCollaborations(authorId) {
	generateCoAuthorConnectionGraph(authorId);
}

function updateConferences(authorId) {
	generateConferenceConnectionGraph(authorId);
}