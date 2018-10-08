$(function () {

	getData("data/authors_ratio.json", drawLineCharts);


	/***  charts  ***/

	function drawLineRatioChart(dev, id){
		// console.log(dev)
		Highcharts.chart(id, {
	    chart: {
	        plotBackgroundColor: null,
	        plotBorderWidth: null,
	        plotShadow: false,
	        type: 'pie'
	    },
	    title: {
	        text: dev.author
	    },
	    tooltip: {
	        pointFormat: '{data.name}: <b>{point.percentage:.1f}%</b>'
	    },
	    credits: {
			enabled: false
		},
	    plotOptions: {
	        pie: {
	            allowPointSelect: true,
	            cursor: 'pointer',
	            dataLabels: {
	                enabled: false
	            },
	            showInLegend: true
	        }
	    },
	    series: [{
	        name: 'Buggy to Good Lines Ratio',
	        colorByPoint: true,
	        data : dev.ratio
	    }]
	});
	}

	function drawLineCharts(result){
		devs = prep_line_data(result);
		var count = 1;
	    devs.forEach(function(dev){
	    	var id = 'dev_line' + count;
	    	$('#dev_line').clone().attr('id', id).appendTo("body>#lines>#per_dev");
	    	drawLineRatioChart(dev, id);

	    	// daily
	    	daily_id = 'dev_line_daily' + count;
	    	daily = dev.daily_ratio >= 0 ? dev.daily_ratio.toFixed(5) : 'Negative ' + dev.daily_ratio.toFixed(5);
	    	ratio = dev.sum_ratio >= 0 ? dev.sum_ratio.toFixed(5) : 'Negative' + dev.sum_ratio.toFixed(5);
	    	$('#dev_line_daily').clone().attr('id', daily_id).html("Average Daily Ratio: " + daily + "<br>Ratio: " + ratio).appendTo("body>#lines>#per_dev>#"+id);
	    	
	    	count++;
	    });
	    $('#dev_line').css('display', 'none');
	}


	/*** data prep ***/

function prep_line_data(devs){
	dev_data = Array();
	devs.forEach(function(dev){
    	var dev_ratio = [{
    		'name' : 'Good',
    		'y' : dev['commits']['good']
    	}, {
    		'name' : 'Buggy',
    		'y' : dev['commits']['buggy']
    	}];
    	dev_data.push({'author' : dev.dev, 'ratio' : dev_ratio, 'daily_ratio' : dev['commits']['daily_ratio'], 'sum_ratio' : dev['commits']['ratio']  });
    });
    return dev_data;
}

function getData(file, callback){
	$.getJSON( file, function( data ) {
  		console.log(file, data);
  		callback(data)
	});
}
	 

});