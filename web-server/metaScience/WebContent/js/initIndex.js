var venueName = "";
var venueId = "";
var authorName ="";
var authorId = ""
var searchstring= "";
var authorSearchstring = "";

window.onload = function() {
  if(window.location.protocol !== 'http:') {
    $("#error").html('<p>You are accessing from an HTTPS connection and our service is located in an HTTP server.</p><p>Please access to our HTTP server <a href="http://atlanmod.github.io/metaScience">here</p>');
    $("#error").css("visibility" ,"visible");
    $("#selectionBox").css("visibility", "hidden");
  }
    $.ajax({
        url : metaScienceServlet + "/version",
        success : function(data) {
            version = data.version;
            $("#metascienceVersion").text(version);// Searching for satellite events
        },
        error : function(data) {
            $("#metascienceVersion").text("ERROR");// Searching for satellite events
        }
    });

    var venueSource =
        {
            datatype: "json",
            datafields: [
                { name: 'name', type : 'string' },
                { name: 'id', type : 'string' },
            ],
            url: metaScienceServlet + "/venues"
        };

    var venueDataAdapter = new $.jqx.dataAdapter(venueSource,
        {
            beforeSend: function (jqxhr, settings) {
                searchstring = $("#vcombobox").jqxComboBox('searchString');
                if (searchstring != undefined || searchstring != '') {
                    settings.url = settings.url + "&search=" + searchstring + "&type=1";
                } else {
                    console.log("venue WAS undefined");
                }
            },
            formatData: function(data) {
            	if($("#vcombobox").jqxComboBox('searchString') != undefined) {
            		return data;
            	}
            },
            loadComplete: function() {
            }
        }
    );

    $("#vcombobox").jqxComboBox(
        {
            width: "100%",
            height: 30,
            source: venueDataAdapter,
            displayMember: "name",
            valueMember: "id",
            remoteAutoComplete: true,
            remoteAutoCompleteDelay: 500,
            minLength: 3,
            placeHolder: "Conference Name (enter at least three letters to search)",
            showArrow : false,
            autoOpen: false,
            autoDropDownHeight: true,
            search: function (searchString) {
            	venueId = '';
            	venueName = '';
                $("#vcombobox").find(".jqx-combobox-input, .jqx-combobox-content").css({ "background": "url('imgs/loading_project.gif') no-repeat right 5px center" });
                venueDataAdapter.dataBind();
            }
        });

    $("#vcombobox").on('bindingComplete', function (event) {
        $("#vcombobox").find(".jqx-combobox-input, .jqx-combobox-content").css({ "background-image": "none" });
    });

    $("#vcombobox").on('select', function (event) {
        if (typeof event.args != 'undefined') {
            var selecteditem = event.args.item;
            if (selecteditem) {
                venueName = selecteditem.label;
                venueId = selecteditem.value;
            }
        }
    });

    var authorSource =
        {
            datatype: "json",
            datafields: [
                { name: 'authorName', type : 'string' },
                { name: 'authorId', type : 'string' },
            ],
            url: metaScienceServlet + "/authors"
        };

    var authorDataAdapter = new $.jqx.dataAdapter(authorSource,
    	{
	        beforeSend: function (jqxhr, settings) {
	        	authorSearchstring = $("#acombobox").jqxComboBox('searchString');
	            if (authorSearchstring != undefined) {
            		settings.url = settings.url + "&search=" + authorSearchstring +"&type=1";
	            } else {
                    console.log("it WAS undefined");
                }
	        },
            downloadComplete: function (edata, textStatus, jqXHR) {
            },
            contentType : "application/x-www-form-urlencoded; charset=UTF-8"
    	}
    );

    $("#acombobox").jqxComboBox(
        {
            width: "100%",
            height: 30,
            source: authorDataAdapter,
            displayMember: "authorName",
            valueMember: "authorId",
            remoteAutoComplete: true,
            remoteAutoCompleteDelay: 500,
            minLength: 3,
            placeHolder: "Author Name (enter at least three letters to search)",
            showArrow : false,
            search: function (authorSearchString) {
            	authorId = '';
            	authorName = '';
                $("#acombobox").find(".jqx-combobox-input, .jqx-combobox-content").css({ "background": "url('imgs/loading_project.gif') no-repeat right 5px center" });
                authorDataAdapter.dataBind();
            }
        });

    $("#acombobox").on('bindingComplete', function (event) {
        $("#acombobox").find(".jqx-combobox-input, .jqx-combobox-content").css({ "background-image": "none" });
    });

    $("#acombobox").on('select', function (event) {
    	if (typeof event.args != 'undefined') {
	        var selecteditem = event.args.item;
	        if (selecteditem) {
	            authorName = selecteditem.label;
	            authorId = selecteditem.value;
	        }
    	}
    });
    
    
    //Button listener
    $("#venueSearchBtn").on("click", function() {
    	if(venueId === undefined || venueId === '') {
	    	var searchedVenue = $('#vcombobox').jqxComboBox('searchString');
	    	$.ajax({
				url : metaScienceServlet + "/venues?search=" + searchedVenue + "&type=2",
				dataType: "json",
				success : function(data) {
					venueCount = data.count;
					venues = data.venues;
					if(venueCount == 1) {
						//Go to venue page
						venueId = venues[0].id;
						window.location.href = metaScienceServlet + "/venue.html?id=" + venueId;
					} else {
						// display list of possible venues
						$("#vcombobox").jqxComboBox("clear");
						for(var i= 0 ; i < venueCount ; i++) {
							var venue = venues[i];
							$("#vcombobox").jqxComboBox("addItem",venue);
						}
					}
				},
				error : function(data) {
					
				}
			});
    	} else {
    		window.location.href = metaScienceServlet + "/venue.html?id=" + venueId;
    	}
    })
    
    $("#authorSearchBtn").on('click', function() {
    	if(authorId === undefined || authorId === '') {
	    	var searchedVenue = $('#acombobox').jqxComboBox('searchString');
	    	$.ajax({
				url : metaScienceServlet + "/authors?search=" + searchedVenue + "&type=2",
				dataType: "json",
				success : function(data) {
					authorCount = data.count;
					authors = data.authors;
					if(authorCount == 1) {
						//Go to venue page
						authorId = authors[0].authorId;
						window.location.href = metaScienceServlet + "/author.html?id=" + authorId;
					} else {
						// display list of possible venues
						$("#acombobox").jqxComboBox("clear");
						for(var i= 0 ; i < authorCount ; i++) {
							var author = authors[i];
							$("#acombobox").jqxComboBox("addItem",author);
						}
					}
				},
				error : function(data) {
					
				}
			});
    	} else {
    		window.location.href = metaScienceServlet + "/author.html?id=" + authorId;
    	}
    })
    
};
