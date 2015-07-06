var metaScienceServlet = 'http://localhost:8080/metaScience';
//var metaScienceServlet = 'http://atlanmodexp.info.emn.fr:8800/metaScience';

// Journal id
var journalId;
var subjournalId;

window.onload = function() {

  if(window.location.protocol !== 'http:') {
    $("#error").html('<p>You are accessing from an HTTPS connection and our service is located in an HTTP server.</p><p>Please access to our HTTP server <a href="http://atlanmod.github.io/metaScience">here</p>');
    $("#error").css("visibility" ,"visible");
  }

	var params = {};
	var journalName;

	// Getting the param from the URL
	if (location.search) {
	    var parts = location.search.substring(1).split('&');

	    for (var i = 0; i < parts.length; i++) {
	        var nv = parts[i].split('=');
	        if (!nv[0]) continue;
	        params[nv[0]] = nv[1] || -1;
	    }
	}
	
	// Getting the full name of the journal
	if(params.id) {
		journalId = params.id;	
    $("#journalName").text(journalId);
	} else {
		$("#journalName").text('No journal found');
	}

	// Searching for satellite events
 	updateGraphs(journalId);
	
}

function updateGraphs(journalId) {
	updateBasic(journalId);
  updateRank(journalId);
  generateJournalAuthorConnectionGraph(journalId);
}

function updateBasic(journalId) {
	$.ajax({
		url: metaScienceServlet + "/journalActivity?id=" + journalId + ((journalId != subjournalId && subjournalId != undefined) ? "&subid=" + subjournalId : ""),
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

function updateRank(journalId,subjournalId) {
  $.ajax( {
    url: metaScienceServlet + "/journalAuthorRank?id=" + journalId + ((journalId != subjournalId && subjournalId != undefined) ? "&subid=" + subjournalId : ""),
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



