$(function () {

	getData("data/entropy_daily.json", display_daily);
	getData("data/entropy_all.json", all);
	getData('data/entropy_ranges_vis.json', ranges)
	getData("data/entropy_yearly.json", yearly);
	getData("data/entropy_per_dev.json", perDevChart);
	getData("data/entropy_per_year.json", display_per_year);
	getData("data/entropy_ext_distribution.json", ext_distr);
	getData("data/entropy_exts_popular.json", display_popular);

	function perDevChart(data){
		Highcharts.chart('overall', {
		    chart: {
		        type: 'scatter',
		        zoomType: 'xy'
		    },
		    title: {
		        text: 'Good vs Bad Devs - Over 4 Years'
		    },
		    subtitle: {
		        text: 'Buggy ratio and extension based entropy'
		    },
		    xAxis: {
		        title: {
		            enabled: true,
		            text: 'Ratio (buggy/inserted)'
		        },
		        startOnTick: true,
		        endOnTick: true,
		        showLastLabel: true,
		        min: 0,
		        max: 0.2
		    },
		    yAxis: {
		        title: {
		            text: 'Entropy (extension based)'
		        },
		        max: 3.5
		    },
		    legend: {
		        layout: 'vertical',
		        align: 'left',
		        verticalAlign: 'top',
		        x: 100,
		        y: 70,
		        floating: true,
		        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
		        borderWidth: 1
		    },
		    plotOptions: {
		        scatter: {
		            marker: {
		                radius: 5,
		                states: {
		                    hover: {
		                        enabled: true,
		                        lineColor: 'rgb(100,100,100)'
		                    }
		                }
		            },
		            states: {
		                hover: {
		                    marker: {
		                        enabled: false
		                    }
		                }
		            },
		            tooltip: {
		                headerFormat: '<b>{series.name}</b><br>',
		                pointFormat: 'Ratio:{point.x:.5f}, Entropy:{point.y:.6f}'
		            }
		        }
		    },
		    credits: {
				enabled: false
			},
		    series: [{
		        name: 'Good',
		        color: 'rgba(119, 152, 191, .5)',
		        data: data.good
		    }, {
		        name: 'Bad',
		        color: 'rgba(223, 83, 83, .5)',
		        data: data.bad
		    }]
		});
	}

	function yearly(data){
		Highcharts.chart('yearly', {
		    chart: {
		        type: 'area'
		    },
		    title: {
		        text: 'Yearly Entropy'
		    },
		    subtitle: {
		        text: 'Good vs Bad Devs'
		    },
		    xAxis: {
		        categories: [
		            '2014',
		            '2015',
		            '2016',
		            '2017'
		        ],
		        startOnTick: true,
        		endOnTick: true
		    },
		    yAxis: {
		        min: 0,
		        title: {
		            text: 'Entropy (extension based)'
		        }
		    },
		    legend: false,
		    tooltip: {
		        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
		        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
		            '<td style="padding:0"><b>{point.y:.6f}</b></td></tr>',
		        footerFormat: '</table>',
		        shared: false,
		        useHTML: true
		    },
		    plotOptions: {
		        column: {
		            pointPadding: 0,
		            borderWidth: 0
		        },
		        area:{
		        	stacking: 'number'
		        }
		    },
		    credits: {
				enabled: false
			},
		    series: data.all
		});
	}

	function fix_date(data){
		data.forEach(function(dev){
			dev.data.forEach(function(day){
				date = new Date(day[0]);
				date_UTC = Date.UTC(date.getFullYear(), date.getMonth(), date.getDate());
				day[0] = date_UTC;
			});
		});
		return data;
	}

	function display_daily(data){
		good = fix_date(data.good);
		bad = fix_date(data.bad);
		daily(good, 'Good Devs', 'daily-good')
		daily(bad, 'Bad Devs', 'daily-bad')
	}

	function daily(data, name, c){
		Highcharts.chart(c, {
		    chart: {
		        type: 'column',
		        zoomType: 'xy'
		    },
		    title: {
		        text: 'Daily Entropy'
		    },
		    subtitle: {
		        text: name
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
		            text: 'Entropy (extension based)'
		        }
		    },
		    tooltip: {
		        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
		        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
		            '<td style="padding:0"><b>{point.y:.6f}</b></td></tr>',
		        footerFormat: '</table>',
		        shared: false,
		        useHTML: true
		    },
		    plotOptions: {
		        column: {
		            pointPadding: 0.2,
		            borderWidth: 0
		        }
		    },
		    legend: false,
		    credits: {
				enabled: false
			},
		    series: data
		});
	}

	function ranges(data){
		Highcharts.chart('ranges', {
		    chart: {
		        type: 'column'
		    },
		    title: {
		        text: 'Number of developers within the entropy range'
		    },
		    subtitle: {
		        text: 'Over 4 years'
		    },
		    xAxis: {
		    	categories: data.categories,
		        title: {
		            text: 'Entropy ranges'
		        }
		    },
		    yAxis: {
		        min: 0,
		        title: {
		            text: 'Number of developers'
		        }
		    },
		    legend: {
		        reversed: true
		    },
		    credits: {
				enabled: false
			},
		    series: [{
		        name: 'Good',
		        color: 'rgba(119, 152, 191, 0.9)',
		        data: data.good
		    }, {
		        name: 'Bad',
		        color: 'rgba(223, 83, 83, 0.9)',
		        data: data.bad
		    }]
		});
	}

	function display_per_year(data){
		Object.keys(data).forEach(function(year){
			var container = 'per_year_' + year;
			var series = [];
			Object.keys(data[year]).forEach(function(group){
				var color = group == 'good' ? 'rgba(119, 152, 191, 0.3)' : 'rgba(223, 83, 83, 0.5)';
				var s = {
					'name' : group,
					'color' : color,
					'data': data[year][group]
				}
				series.push(s);
			});
			per_year(series, year, container)
		});
	}

	function per_year(series, year, container){
		Highcharts.chart(container, {
		    chart: {
		        type: 'area'
		    },
		    title: {
		        text: 'Yearly Entropy'
		    },
		    subtitle: {
		        text: year
		    },
		    xAxis: {
		        labels: {
		            formatter: function () {
		                return null; // clean, unformatted number for year
		            }
		        },
		        title: {
		            text: 'Developers'
		        }
		    },
		    yAxis: {
		        title: {
		            text: 'Yearly entropy'
		        }
		    },
		    credits: {
				enabled: false
			},
		    tooltip: {
		        pointFormat: '{series.name} dev entropy <b>{point.y}</b><br/> for ' + year
		    },
		    plotOptions: {
		        area: {
		            marker: {
		                enabled: false,
		                symbol: 'circle',
		                radius: 2,
		                states: {
		                    hover: {
		                        enabled: true
		                    }
		                }
		            }
		        }
		    },
		    series: series
		});
	}

	function ext_distr(data){
		Highcharts.chart('ext_distr', {
		    chart: {
		        type: 'area',
		        zoomType: 'xy'
		    },
		    title: {
		        text: 'Extensions entropy distribution for developer - extension pair'
		    },
		    subtitle: {
		        text: 'good vs bad'
		    },
		    boost: {
		        useGPUTranslations: true,
		        usePreAllocated: true
		    },
		    xAxis: {
		        labels: {
		            formatter: function () {
		                return null; // clean, unformatted number for year
		            }
		        },
		        title: {
		            text: 'Developer - Extension Pair'
		        }
		    },
		    yAxis: {
		    	min: 0, 
		    	minPadding: 0,
        		maxPadding: 0,
		        title: {
		            text: 'Extension entropy'
		        }
		    },
		    credits: {
				enabled: false
			},
		    tooltip: {
		        pointFormat: '{series.name} dev entropy <b>{point.y}</b><br/>'
		    },
		    plotOptions: {
		    },
		    series: [{
		    	'name' : 'bad',
		    	'data' : data.bad,
		    	'color' : 'rgba(223, 83, 83, 0.3)', 
		    	'turboThreshold' : 6130
		    },
		    {
		    	'name' : 'good',
		    	'data' : data.good,
		    	'color' : 'rgba(119, 152, 191, 0.7)', 
		    	'turboThreshold' : 6130
		    }]
		});
	}

	function all(data){
		Highcharts.chart('all', {
		    chart: {
		        type: 'area'
		    },
		    title: {
		        text: 'Entropy per developer over 4 years'
		    },
		    subtitle: {
		        text: 'Good vs Bad'
		    },
		    xAxis: {
		        labels: {
		            formatter: function () {
		                return null; // clean, unformatted number for year
		            }
		        },
		        title: {
		            text: 'Developers'
		        }
		    },
		    yAxis: {
		        title: {
		            text: 'Extension entropy'
		        }
		    },
		    credits: {
				enabled: false
			},
		    tooltip: {
		        pointFormat: '{series.name} dev entropy <b>{point.y}</b><br/>'
		    },
		    plotOptions: {
		    },
		    series: [
		    {
		    	'name' : 'bad',
		    	'data' : data.bad,
		    	'color' : 'rgba(223, 83, 83, 0.3)'
		    },
		    {
		    	'name' : 'good',
		    	'data' : data.good,
		    	'color' : 'rgba(119, 152, 191, 0.4)',
		    	'turboThreshold' : 1300
		    }]
		});
	}


	function popular_log(container, series, title){
		Highcharts.chart(container, {
		    chart: {
		        type: 'area'
		    },
		    title: {
		        text: 'Focus for ' + title
		    },
		    subtitle: {
		        text: 'Good vs Bad'
		    },
		    xAxis: {
		        labels: {
		            formatter: function () {
		                return null; // clean, unformatted number for year
		            }
		        },
		        title: {
		            text: 'Developers'
		        }
		    },
		    yAxis: {
		    	type: 'logarithmic',
		        title: {
		            text: 'Extension entropy'
		        }
		    },
		    credits: {
				enabled: false
			},
		    tooltip: {
		        pointFormat: '{series.name} dev entropy <b>{point.y}</b><br/>'
		    },
		    series: series
		});
	}

	function popular(container, series, title){
		Highcharts.chart(container, {
		    chart: {
		        type: 'area'
		    },
		    title: {
		        text: 'Focus for ' + title
		    },
		    subtitle: {
		        text: 'Good vs Bad'
		    },
		    xAxis: {
		        labels: {
		            formatter: function () {
		                return null; // clean, unformatted number for year
		            }
		        },
		        title: {
		            text: 'Developers'
		        }
		    },
		    yAxis: {
		        title: {
		            text: 'Extension entropy'
		        }
		    },
		    credits: {
				enabled: false
			},
		    tooltip: {
		        pointFormat: '{series.name} dev entropy <b>{point.y}</b><br/>'
		    },
		    series: series
		});
	}


	function display_popular(data){
		Object.keys(data).forEach(function(ext){
			var id = 'ext_popular' + ext;
			$('#ext_popular').clone().attr('id', id).appendTo("body>#exts");
			var id2 = 'ext_popular' + ext + '2';
			$('#ext_popular').clone().attr('id', id2).appendTo("body>#exts_log");
			var title = ext;
			var series = [data[ext].bad, data[ext].good];
			popular(id, series, title);
			popular_log(id2, series, title);
		});
	}


	function getData(file, callback){
		$.getJSON( file, function( data ) {
	  		console.log(file, data);
	  		callback(data)
		});
	}



});