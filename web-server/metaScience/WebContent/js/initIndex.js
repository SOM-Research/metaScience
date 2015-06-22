var metaScienceServlet = 'http://localhost:8080/metaScience';
//var metaScienceServlet = 'http://atlanmodexp.info.emn.fr:8800/metaScience';

var venueName = "";
var venueId = "";
var authorName ="";
var authorId = "";
var journalName = "";
var journalId = "";
var searchstring="";
var authorSearchstring = "";
var journalSearchString = "";

window.onload = function() {
  if(window.location.protocol !== 'http:') {
    $("#error").html('<p>You are accessing from an HTTPS connection and our service is located in an HTTP server.</p><p>Please access to our HTTP server <a href="http://atlanmod.github.io/metaScience">here</p>');
    $("#error").css("visibility" ,"visible");
    $("#selectionBox").css("visibility", "hidden");
  }

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
                if (searchstring != undefined) {
                    settings.url = settings.url + "&search=" + searchstring;
                } else {
                    console.log("venue WAS undefined");
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
            search: function (searchString) {
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
                venueName = selecteditem.originalItem.name;
                venueId = selecteditem.originalItem.id;
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
                    console.log("author")
                        settings.url = settings.url + "&search=" + authorSearchstring;
                } else {
                    console.log("it WAS undefined");
                }
            },
            loadComplete: function() {
            }
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
                authorName = selecteditem.originalItem.name;
                authorId = selecteditem.originalItem.authorId;
            }
        }
    });

    var journalSource =
        {
            datatype: "json",
            datafields: [
                { name: 'journalName', type : 'string' },
                { name: 'journalId', type : 'string' },
            ],
            url: metaScienceServlet + "/journals"
        };

    var journalDataAdapter = new $.jqx.dataAdapter(journalSource,
        {
            beforeSend: function (jqxhr, settings) {
                journalSearchstring = $("#jcombobox").jqxComboBox('searchString');
                if (journalSearchstring != undefined) {
                        settings.url = settings.url + "&search=" + journalSearchstring;
                } else {
                    console.log("it WAS undefined");
                }
            },
            loadComplete: function() {
            }
        }
    );

    $("#jcombobox").jqxComboBox(
        {
            width: "100%",
            height: 30,
            source: journalDataAdapter,
            displayMember: "journalName",
            valueMember: "journalId",
            remoteAutoComplete: true,
            remoteAutoCompleteDelay: 500,
            minLength: 3,
            placeHolder: "Journal Name (enter at least three letters to search)",
            showArrow : false,
            search: function (journalSearchString) {
                $("#jcombobox").find(".jqx-combobox-input, .jqx-combobox-content").css({ "background": "url('imgs/loading_project.gif') no-repeat right 5px center" });
                journalDataAdapter.dataBind();
            }
        });

    $("#jcombobox").on('bindingComplete', function (event) {
        $("#jcombobox").find(".jqx-combobox-input, .jqx-combobox-content").css({ "background-image": "none" });
    });

    $("#jcombobox").on('select', function (event) {
        if (typeof event.args != 'undefined') {
            var selecteditem = event.args.item;
            if (selecteditem) {
                journalName = selecteditem.originalItem.name;
                journalId = selecteditem.originalItem.journalId;
            }
        }
    });

};