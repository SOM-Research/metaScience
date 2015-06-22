var metaScienceServlet = 'http://localhost:8080/metaScience';
//var metaScienceServlet = 'http://atlanmodexp.info.emn.fr:8800/metaScience';

window.onload = function() {
	var topicsChart = c3.generate({		
	    bindto: '#topicsChart',
	    data: {
	    	xs: {
	    		'UML'      : 'x1',
	    		'Grid'     : 'x2',
	    		'Aspect'   : 'x3',
	    		'Agile'    : 'x4',
	    		'MDA'      : 'x5'
	    	},
	      	columns: [
	        	['UML', 1, 4, 22, 30, 67, 61, 84, 100, 98, 111, 102, 114, 67, 67, 66, 42, 57, 17],
	        	['x1', 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014],
	        	['Grid', 1, 2, 2, 2, 2, 1, 1, 1, 3, 13, 19, 26, 45, 82, 70, 55, 32, 52, 46, 30, 6],
	        	['x2', 1988, 1990, 1993, 1994, 1995, 1996, 1997, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014],
	        	['Aspect', 1, 4, 2, 4, 9, 11, 30, 48, 72, 68, 68, 56, 43, 46, 36, 19, 1],
	        	['x3', 1988, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014],
	        	['Agile', 1, 4, 2, 4, 9, 11, 30, 48, 72, 68, 68, 56, 43, 46, 36, 19, 1],
	        	['x4', 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014],
	        	['MDA', 2, 1, 1, 14, 15, 23, 23, 21, 8, 7, 7, 1, 3, 1],
	        	['x5', 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]
	      ]
	    }
	});

	/*drawNgramChart('#n1gramChart', 
		['n1', 43349+42690, 70187, 53326, 35059, 34734], 
		['Systems', 'Based', 'Using', 'Data', 'Analysis']
	);
	drawNgramChart('#n2gramChart', 
		['n2', 9008, 7006, 5842, 5522, 5274], 
		['A new', 'Sensor Networks', 'Case Study', 'Wireless Sensor', 'A novel']
	);
	drawNgramChart('#n3gramChart', 
		['n3', 5163, 3663, 2820, 1626, 1303], 
		['Wireless Sensor Networks', 'A Case Study', 'Ad Hoc Networks', 'Particle Swam Optimization', 'A New Approach']
	);*/
}

function drawNgramChart(container, data, labels) {
	var ngramChart = c3.generate({
		bindto : container,
		data : {
			columns : [
				data
			],
			type : 'bar'
		},
		axis : {
			x : {
				type : 'category',
				categories : labels
			}
		},
		tooltip : {
			show : false
		},
		grid : {
        	y : {
            	show: true
            }
        },
        legend : {
        	show : false
    	}
	});
}


