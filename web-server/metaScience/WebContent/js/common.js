var metaScienceServlet = 'http://localhost:8080/metaScience';
//var metaScienceServlet = 'http://som.uoc.es/metaScience';
//var metaScienceServlet = 'http://atlanmodexp.info.emn.fr:8800/metaScience';

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

function hideRow(rowId) {
    d3.select("#" + rowId)
        .style("visibility","hidden")
        .style("overflow","hidden")
        .style("height","0");
}

function showRow(rowId) {
    d3.select("#" + rowId)
        .style("visibility","visible")
        .style("overflow","auto")
        .style("height",null);
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

function createSlider(selectorId,labelText, min, max,changeFunction) {
    var sliderContainerSelector = d3.select("#" + selectorId);
    sliderContainerSelector.attr("class","sliderContainer");

    var labelContainer = sliderContainerSelector.append("p").append("div").attr("class","sliderLabelContainer");

    var labelTextElement = labelContainer.append("span").attr("class","sliderLabelText");
    var labelRangeText = labelContainer.append("span").attr("class","sliderLabelRangeText");
    labelRangeText.html("[ <span id='startRangeText'></span> - <span id='endRangeText'></span> ]");

    var sliderContainer = sliderContainerSelector.append("div").attr("class","slider");

    var sliderResetContainer = sliderContainerSelector.append("div").attr("class","sliderResetBtnContainer");

    //Label
    labelTextElement.text(labelText);

    var labelStartRangeText = $("#" + selectorId + " #startRangeText");
    var labelEndRangeText = $("#" + selectorId + " #endRangeText");

    labelStartRangeText.text(min);
    labelEndRangeText.text(max);


    //Slider
    var slider = $("#" + selectorId + " .slider");

    slider.jqxSlider({
        width: "100%",
        max: max,
        min: min,
        mode: 'fixed',
        rangeSlider: true,
        value: { rangeStart: min, rangeEnd: max }
    });

    slider.bind('change', function(event) {
        var numStart = event.args.value.rangeStart;
        var numEnd = event.args.value.rangeEnd;

        labelStartRangeText.text(numStart);
        labelEndRangeText.text(numEnd);
        changeFunction(numStart,numEnd);
    });

    /*slider.on('change', function(event) {
        var numStart = event.args.value.rangeStart;
        var numEnd = event.args.value.rangeEnd;

        labelStartRangeText.text(numStart);
        labelEndRangeText.text(numEnd);
        changeFunction(numStart,numEnd);
    });*/

    // Reset Button
    
    sliderResetContainer.append("button").attr("class","sliderResetBtn btn btn-block").text("Reset");
    var resetBtn = $("#" + selectorId + " .sliderResetBtn");
    resetBtn.attr("style", "margin-top:12px");
    resetBtn.on('click', function(event) {
        slider.jqxSlider('setValue',[min,max]);
    });
}
