$(function () {
	class JSONReader {
	    constructor(completed = null) {
	        this.onCompleted = completed;
	        this.result = undefined;
		this.input = document.createElement('input');
	        this.input.type = 'file';
	        this.input.accept = 'text/json|application/json';
	        this.input.addEventListener('change', this.onChange.bind(this), false);
	        // this.input.style.display = 'none';
	        $('#buttons').append(this.input);
	        this.input.click();
	    }
	 
	    destroy() {
	        this.input.removeEventListener('change', this.onChange.bind(this), false);
	        $('#buttons').remove('input');    
	    }
	 
	    onChange(event) {
		if (event.target.files.length > 0) {
	            this.readJSON(event.target.files[0]);
	        }
	    }
	 
	    readJSON(file) {
	        const reader = new FileReader();
	        reader.onload = (event) => {
	            if (event.target.readyState === 2) {
	                this.result = JSON.parse(reader.result);
	                if (typeof this.onCompleted === 'function') {
	                    this.onCompleted(this.result);
	                }
			this.destroy();
	            }
	        };
	        reader.readAsText(file);
	    }
	 
	    static read(callback = null) {
	        return new JSONReader(callback);
	    }
	}

	const reader = new JSONReader((result) => {
		$('#per_dev').html('');
	    console.log(result);
	    devs = prepData(result);
	    sums = prepSums(devs);
	    drawSumChart(sums);
	    drawPerDevCharts(devs);

	});

	/***  charts  ***/

	function drawChart(dev, email, id, dev_ratio){

        Highcharts.chart(id, {
            chart: {
                zoomType: 'x',
                type: 'column'
            },
            title: {
                text: dev_ratio
            },
            subtitle: {
                text: document.ontouchstart === undefined ?
                        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
		            day: '%e. %b %y',
				    week: '%e. %b %y',
				    month: '%b \'%y',
				    year: '%Y'
		        }
            },
            yAxis: {
                title: {
                    text: 'Inserted lines'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                column: {
		            stacking: 'number'
		        }
            },
            tooltips: {
            	dateTimeLabelFormats: {
		            day: '%e. %b %y',
				    week: '%e. %b %y',
				    month: '%b \'%y',
				    year: '%Y'
		        }
            },

            series: [
            	{
            		name: 'Good',
            		data: dev.good
            	},
            	{
            		name: 'Buggy',
            		data: dev.buggy
            	}
            ]
        });
	}

	function drawSumChart(sums){

        Highcharts.chart('developers', {
		    chart: {
		        type: 'bar'
		    },
		    title: {
		        text: 'Developers'
		    },
		    subtitle: {
		        text: 'Sum accross 4 years (2014-2017)'
		    },
		    xAxis: {
		        type: 'category',
		        labels: {
		            style: {
		                fontSize: '13px',
		                fontFamily: 'Verdana, sans-serif'
		            }
		        }
		    },
		    yAxis: {
		        min: 0,
		        title: {
		            text: 'Commited lines (total)'
		        },
		        max: 20000
		    },
		    legend: {
		        enabled: false
		    },
		    tooltip: {
		        pointFormat: '{x}: <b>{point.y}</b>'
		    },
		    plotOptions: {
                bar: {
		            stacking: 'normal'
		        }
            },
		    credits: {
				enabled: false
			},
            series: [
            	{
            		name: 'Developers',
            		data: sums
            	}
            ]
		});
	}

	function drawPerDevCharts(devs){
		var count = 1;
	    Object.keys(devs).forEach(function(key, index){
	    	var id = 'container' + count;
	    	var ratio = devs[key].sum.buggy / devs[key].sum.good;
	    	var author = ratio > 0 ? key + " - " + (ratio * 100).toFixed(4) + "%": key + " - " + 0 + "%";
	    	$('#container').clone().attr('id', id).appendTo("body #per_dev");
	    	drawChart(devs[key], key, id, author);
	    	count++;
	    });
	}

	/*** data prep ***/

	function prepData(commits){
		var devs = {};

		function compare(a,b) {
		  if (a[0] < b[0])
		    return -1;
		  if (a[0] > b[0])
		    return 1;
		  return 0;
		}


		Object.keys(commits).forEach(function(key,index) {
			var author = key;
			var author_data = commits[author];
			var good = new Array();
			var buggy = new Array();
			var all = new Array();
			var sum = {
				"all" : 0, 
				"good" : 0,
				"buggy" : 0
			};
			devs[author] = {
				'good' : good, 
				'buggy' : buggy,
				'all' : all,
				'sum' : sum
			};
			Object.keys(author_data).forEach(function(date_key, index){
				c = author_data[date_key];
				date = new Date(date_key);
				date_UTC = Date.UTC(date.getFullYear(), date.getMonth(), date.getDate());
				good.push([date_UTC, c.changes[1]]);
				buggy.push([date_UTC, c.changes[0]]);
				all.push([date_UTC, c.changes[2]]);
				// sum
				devs[author].sum.all += c.changes[2];
				devs[author].sum.good += c.changes[1];
				devs[author].sum.buggy += c.changes[0];
			});
			devs[author].good.sort(compare);
			devs[author].buggy.sort(compare);
			devs[author].all.sort(compare);
		});
		console.log(devs);
		
		return devs;
	}

	function prepSums(devs){

		function compare(a,b) {
		  if (a[1] < b[1])
		    return -1;
		  if (a[1] > b[1])
		    return 1;
		  return 0;
		}

		var sums = new Array();
		Object.keys(devs).forEach(function(key,index) {
			var ratio = devs[key].sum.buggy / devs[key].sum.good;
			var author_ratio = ratio > 0 ? key + " - " + ratio.toFixed(2) : key + " - " + 0;
			sum = [author_ratio, devs[key].sum.all];
			sums.push(sum);
		});
		sums.sort(compare);
		return sums;
	}

	/*

	{
		developer: {
			good: [
				[ date, good_number ]
			],
			buggy: [
				[ date, buggy_number ]
			],
			all: [
				[ date, inserted ]
			],
			sum: {
				all: number of all commits in collection,
				good: sum of good, 
				buggy: sum of buggy
			}
		}
	}

	*/

});