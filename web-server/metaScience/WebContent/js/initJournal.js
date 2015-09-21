// Journal/subjournal ids
var journalId;
var subjournalId;

window.onload = function() {

  if(window.location.protocol !== 'http:') {
    $("#error").html('<p>You are accessing from an HTTPS connection and our service is located in an HTTP server.</p><p>Please access to our HTTP server <a href="http://som-research.uoc.edu/tools/metaScience">here</p>');
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
		journalId = decodeURI(params.id);	
		$("#journalName").text(journalId);
		updateGraphs(journalId);
	} else {
		journalNotFound();
	}


      // Twitter buttons update
      var tweetBtn1 = $('<a></a>')
          .addClass('twitter-share-button')
          .attr('href', 'http://twitter.com/share')
          .attr('data-url', metaScienceServlet + '/journal.html?id=' + journalId)
          .attr('data-count', 'none')
          .attr('data-text', "Discover who are the top five authors in " + journalId + " thanks to #metascience");
      $('#tweetBtn1').append(tweetBtn1);
      twttr.widgets.load();

      var tweetBtn2 = $('<a></a>')
          .addClass('twitter-share-button')
          .attr('href', 'http://twitter.com/share')
          .attr('data-url', metaScienceServlet + '/journal.html?id=' + journalId)
          .attr('data-count', 'none')
          .attr('data-text', "Discover who's who in " + journalId + " thanks to #metascience");
      $('#tweetBtn2').append(tweetBtn2);
      twttr.widgets.load();
      
      
}

function journalNotFound() {
  $("#journalName").text('Journal not found');
  $(".topBox").css("visibility", "hidden");
  $("#mainRow").css("visibility","hidden");
  $("#rankAuthorsRow").css("visibility","hidden");
  $("#activityChartRow").css("visibility","hidden");
  $("#ratiosChartRow").css("visibility","hidden");
  $("#journalAuthorConnectionRow").css("visibility","hidden");
  $("#notFoundRow").css("display", "block");
}

function updateGraphs(journalId, subjournalId) {
	updateBasic(journalId);
	updateRank(journalId);
	generateJournalAuthorConnectionGraph(journalId);
}

function updateBasic(journalId, subjournalId) {
	$.ajax({
		url: metaScienceServlet + "/journalActivity?id=" + journalId + ((journalId != subjournalId && subjournalId != undefined) ? "&subid=" + subjournalId : ""),
		success : function(data) {
			showRow("activityChartRow");
			showRow("ratiosChartRow");
			
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
                    ],
                    names: {
                      AuthorsPerPaper: "Authors per paper",
                      PapersPerAuthor: "Papers per author"
                    },
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
			hideRow("activityChartRow");
			hideRow("ratiosChartRow");
		}
	});
}

function updateRank(journalId,subjournalId) {
  $.ajax( {
    url: metaScienceServlet + "/journalAuthorRank?id=" + journalId + ((journalId != subjournalId && subjournalId != undefined) ? "&subid=" + subjournalId : ""),
    success: function(data) {
      $("#topAuthor1").text(data.top[1].name);
      $("#topAuthor2").text(data.top[2].name);
      $("#topAuthor3").text(data.top[3].name);
      $("#topAuthor4").text(data.top[4].name);
      $("#topAuthor5").text(data.top[5].name);

      $("#numAuthor1").text(data.top[1].publications);
      $("#numAuthor2").text(data.top[2].publications);
      $("#numAuthor3").text(data.top[3].publications);
      $("#numAuthor4").text(data.top[4].publications);
      $("#numAuthor5").text(data.top[5].publications);

      $("#regularAuthor1").text(data.regular[1].name);
      $("#regularAuthor2").text(data.regular[2].name);
      $("#regularAuthor3").text(data.regular[3].name);
      $("#regularAuthor4").text(data.regular[4].name);
      $("#regularAuthor5").text(data.regular[5].name);

      $("#presenceAuthor1").text(data.regular[1].presence);
      $("#presenceAuthor2").text(data.regular[2].presence);
      $("#presenceAuthor3").text(data.regular[3].presence);
      $("#presenceAuthor4").text(data.regular[4].presence);
      $("#presenceAuthor5").text(data.regular[5].presence);
    },
    error: function(xhr, status, error) {

    }
  });
}



