
var initCenterPoints = [23.764097871800434, 120.90621471405031];
var initZoomLevel = 7;

var areaSearch = decodeURIParameter(location.search).area;
var areaMeta = areaMetaMap[areaSearch];
var areaBounds = areaMeta.bounds;
var loadingLayer = $("#loading-layer"), mainMap;
var dateRangeValues = [
	document.getElementById('fromDatePicker'),
	document.getElementById('toDatePicker')
];

var collectInKilometer = 25.0;
var eventFromButton = false;
var eventFromMap = false;
var skipHandlerOnce = false;
var stopSetHandler = false;
var showEventLevel = "高";	// 高, 中, 低
var markerSwitchShow = true;

var thirtyDays = 30 * 24 * 60 * 60 * 1000;

var windDirection = {
	_ranges: [11.25, 33.75, 56.25, 78.75, 101.25, 123.75, 146.25, 168.75, 191.25, 213.75, 236.25, 258.75, 281.25, 303.75, 326.25, 348.75],
	_targets: ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N'],
	getShort: function(wd){
		var value = parseFloat(wd || 0);
		var ranges = this._ranges.slice(0);
		ranges.push(value);
		ranges.sort(function(a,b) { return a - b;});
		return this._targets[ranges.indexOf(value)];
	}
};

// init slider for use in global
var slider = document.getElementById('slider');

var eventIsInShowLevel = function(count, duration){
	if ( markerSwitchShow ) {
		return showEventLevel == getRiskLevel(count, duration);
	}
	return false;
};

var onDatetimePickerShow = function(){
	// cache the datestr
	this._dateCache = $(this).val();
};
var onDatetimePickerClose = function(selectDateStr) {
	var strFromDate = $(dateRangeValues[0]).val();
	var strToDate = $(dateRangeValues[1]).val();
	var cacheDate = this._dateCache;

	if( cacheDate && ( (strFromDate == cacheDate && dateRangeValues[0] == this ) || 
		(strToDate == cacheDate && dateRangeValues[1] == this) ) ) return;

	var fromDate = parseDateString( strFromDate + ":00" );
	var toDate = parseDateString( strToDate + ":00" );

	if ( toDate.getTime() - fromDate.getTime() > thirtyDays ) {
		if ( selectDateStr == strToDate ) {	// event from toDatePicker
			fromDate.setTime( toDate.getTime() - thirtyDays );
		} else if ( selectDateStr == strFromDate ) {	// event from fromDatePicker
			toDate.setTime( fromDate.getTime() + thirtyDays );
		}
	}

	skipHandlerOnce = true;
	slider.noUiSlider.set( [fromDate.getTime(), toDate.getTime()] );
};

var mapForceTriggerSliderSet = function(){
	var strFromDate = $(dateRangeValues[0]).val();
	var strToDate = $(dateRangeValues[1]).val();
	var fromDate = parseDateString( strFromDate + ":00" );
	var toDate = parseDateString( strToDate + ":00" );
	skipHandlerOnce = true;
	eventFromMap = true;
	slider.noUiSlider.set( [fromDate.getTime(), toDate.getTime()] );
	eventFromMap = false;
}

// All stations and rectangles
var allRectangles = [];
var allStations = [];
var allEventMarkers = [];
var allEventTotalMap = {};
var allDeviceMap = {};

var levelToEventInfo = {
	"高": {
		case: 'danger',
		eventMarkers: []
	},
	"中": {
		case: 'warning',
		eventMarkers: []
	},
	"低": {
		case: 'default',
		eventMarkers: []
	}
};

var gradiantColors = new Rainbow(); 

// set color range
gradiantColors.setSpectrum('#338866', '#c6b63c', '#dd4b45', '#a01515');

// generate for color range
(function(){
	var rainbowHeight = 60;
	var rainbowWidth = 30;
	gradiantColors.setNumberRange(0, rainbowHeight - 1);
	var canvas = document.getElementById('color-range');
	var context = canvas.getContext('2d');

	context.lineWidth = 1;
	
	for (var i = 0, len = rainbowHeight - 1; i <= len; i++) {
		context.beginPath();
		context.strokeStyle = '#' + gradiantColors.colorAt(i);
		context.moveTo(0, rainbowHeight - i);
		context.lineTo(rainbowWidth, rainbowHeight - i);
		context.stroke();
	}
})();

function stampsToDateStr(stamps){
	var d = new Date( parseInt(stamps) );
	return d.yymmddHH() + ":00";
}

// auto detect ranges and generate buttons.
function generateDateRangeButtons(minDate, maxDate){
	var buttons = [
		// { text: "全部" },
		// { text: "近一年", daysago: 365 },
		// { text: "近半年", daysago: 183 },
		{ text: "近一個月", daysago: 30, is_default: true },
		{ text: "近一週", daysago: 7 },
		{ text: "近三天", daysago: 3 }
	];

	var filteredButtons = [];

	buttons.forEach(function(item){
		var minTime = minDate.getTime();
		if ( item.daysago > 0 ) {
			// clone
			var compareDate = new Date(maxDate.getTime());
			
			// pin to days ago
			compareDate.setDate( compareDate.getDate() - item.daysago );

			if(minTime <= compareDate.getTime()) {
				item.minTime = compareDate.getTime();
				filteredButtons.push(item);
			}
		}
	});

	if ( filteredButtons.length && filteredButtons.filter(function(item){ return item.is_default === true; }).length == 0 ) {
		filteredButtons[0].is_default = true;
	}

	filteredButtons.forEach(function(item, idx){
		var b = document.createElement("button");

		$(b).text(item.text).val(item.daysago)
			.addClass("btn btn-sm " + (item.is_default? "btn-success" : "btn-default"))
			.click(
				(function(minStamp, maxStamp){
					return function(){
						var jqSelf = $(this);
						jqSelf.siblings().removeClass("btn-success").addClass("btn-default");
						jqSelf.removeClass("btn-default").addClass("btn-success");

						skipHandlerOnce = true;
						eventFromButton = true;
						slider.noUiSlider.set( [minStamp, maxStamp] );
						eventFromButton = false;
					};
				})(item.minTime, maxDate.getTime())
			);

		$("#filterDaterange").append(b);
	});
}

function resetAllMarkers(){
	Object.keys(levelToEventInfo).forEach(function(key){
		levelToEventInfo[key].eventMarkers.forEach(function(m){ m.remove(); });
	});
}

function removeAllMarkers() {
	allEventTotalMap = {};
	Object.keys(levelToEventInfo).forEach(function(key){
		levelToEventInfo[key].eventMarkers.forEach(function(marker){
			mainMap.removeLayer(marker);
		})
		levelToEventInfo[key].eventMarkers = [];
	});

	allEventMarkers.forEach(function(marker){
		mainMap.removeLayer(marker);
	});
	
	allEventMarkers = [];
}

function triggerMarkersWithLevel(toShow){
	var showDesc = showEventLevel;
	var levelInfo = levelToEventInfo[showEventLevel];
	if(toShow === true){
		if (levelInfo.eventMarkers.length){
			$("#event-alert").hide();
			levelInfo.eventMarkers.forEach(function(m){ m.addTo(mainMap); });
		} else {
			var alertText = $("#event-alert");
			alertText.children("span").text(showDesc);
			alertText.show();
			levelInfo.eventMarkers.forEach(function(m){ m.remove(); });	
		}
	} else {
		$("#event-alert").hide();
	}
}

function pinEventMarkers(){

	var showDesc = showEventLevel;
	var levelInfo = levelToEventInfo[showEventLevel];

	if ( levelInfo.eventMarkers.length ) return;

	for(var pos in allEventTotalMap){
		var eventList = allEventTotalMap[pos];
		var position = pos.split('-').map(function(v){return parseFloat(v);});

		var filteredEvents = eventList.filter(function(ev){ return eventIsInShowLevel(ev.count, ev.duration); });

		var eventCount = filteredEvents.length;

		if(!eventCount) continue;

		var redMarker = L.ExtraMarkers.icon({
			icon: 'fa-number',
			number: eventCount.toString(),
			markerColor: 'green',
			shape: 'square',
			prefix: 'fa'
		});

		// generate event list
		var popupHtml = "<div style='width:410px;height:100%;'><table style='width:100%;height:100%;border-spacing: 0px 3px;border-collapse: separate;'>";

		popupHtml += "<thead><tr><th>等級</th><th>風向</th><th>開始時間</th><th>結束時間</th><th>播放</th></tr></thead>";
		popupHtml += "<tbody>";
		popupHtml += filteredEvents.map(function(item){
			var tuple = ['<tr>'];

			var labelCase = levelInfo.case;
			
			tuple.push('<td><span class="label label-' + labelCase + '">' + showDesc + '污染</span></td>');
			tuple.push('<td>' + item.wind_direction + '</td>');
			tuple.push('<td>' + item.start + '</td>');
			tuple.push('<td>' + item.end + '</td>');
			
			var currentAreaBounds = areaMetaMap[item.area] ? areaMetaMap[item.area].bounds : null;
			if ( currentAreaBounds ) {
				var paramStr = encodeParamPairs({
					start: item.start,
					end: item.end,
					start_lon: currentAreaBounds[0],
					end_lon: currentAreaBounds[1],
					start_lat: currentAreaBounds[2],
					end_lat: currentAreaBounds[3]
				});

	            // TODO: need to pass CAMEO_SUB_PATH here
				tuple.push('<td><a href="/web/iot/history/animation?' + paramStr + '" class="btn btn-sm btn-primary" target="_blank" style="color:white;"><i class="fa fa-external-link"></i></a></td>');
			} else {
				// insert empty
				tuple.push('<td></td>');
			}
			
			tuple.push('</tr>');
			return tuple.join('');
		}).join('');

		popupHtml += "</tbody></table></div>";

		levelInfo.eventMarkers.push(
			L.marker(position, {icon: redMarker})
			.bindPopup(popupHtml, { maxWidth: 450, maxHeight: 300 })
		);
	}
}


// iot show switch
var iotShowSwitcherEl = document.querySelector('#iotShowSwitch');
var showSwitcherInstance = new Switchery(iotShowSwitcherEl, { size: 'small' });
var onIotShowSwitcherChange = function(){
	if(iotShowSwitcherEl.checked) {
		allStations.forEach(function(m){ m.addTo(mainMap); });
		allRectangles.forEach(function(r){r.bringToFront()});
	}else allStations.forEach(function(m){ m.remove(); });
};
iotShowSwitcherEl.addEventListener('change', onIotShowSwitcherChange);

// markerShowSwitch
var markerShowSwitchEl = document.querySelector('#markerShowSwitch');
var markerSwitcherInstance = new Switchery(markerShowSwitch, { size: 'small' });
markerShowSwitchEl.addEventListener('change', function(){
	markerSwitchShow = markerShowSwitchEl.checked;
	resetAllMarkers();
	pinEventMarkers();
	triggerMarkersWithLevel(markerSwitchShow);
});

var markerOptions = {
	radius: 5.5,
    fillColor: "#4988cc",
    color: "#ccf",
    opacity: 1,
    fillOpacity: 1
};

var regionParams = {
	min_lat: areaBounds[2],
	max_lat: areaBounds[3],
	min_lon: areaBounds[0],
	max_lon: areaBounds[1]
};

var rectangleControl = {
	getSettings: function(zoomLevel){
		if ( zoomLevel >= 15 ) return { threshold: 0 };
		else if ( zoomLevel >= 13 ) return { threshold: 20 };
		else return { threshold: 40 };
	},
	shouldTrigger: function(oldLevel, newLevel){
		newLevel = newLevel || oldLevel;
		var newSettings = this.getSettings(newLevel);
		if ( newLevel == oldLevel ) return newSettings.threshold < 40;
		else {
			var oldSettings = this.getSettings(oldLevel);
			return newLevel < oldLevel || oldSettings.threshold != newSettings.threshold;
		}
	},
	getCurrentThreshold: function(map){
		return this.getSettings(map.getZoom()).threshold;
	},
	getCurrentBounds: function(map){
		var settings = this.getSettings(map.getZoom());
		if ( settings.threshold >= 40 ) return regionParams;
		else {
			var bounds = map.getBounds();

			// bound offsets
			// var nePoint = map.latLngToContainerPoint( bounds.getNorthEast() );
			// var swPoint = map.latLngToContainerPoint( bounds.getSouthWest() );
			// var neNew = map.containerPointToLatLng( [nePoint.x + 100, nePoint.y - 100] );
			// var swNew = map.containerPointToLatLng( [swPoint.x - 100, swPoint.y + 100] );

			var neNew = bounds.getNorthEast();
			var swNew = bounds.getSouthWest();

			// check bounds and get intersaction
			if ( regionParams.min_lon > neNew.lng || regionParams.min_lat > neNew.lat ||
				regionParams.max_lon < swNew.lng || regionParams.max_lat < swNew.lat ) {
				return false;
			} else {
				return {
					min_lat: Math.max( swNew.lat, regionParams.min_lat ),
					max_lat: Math.min( neNew.lat, regionParams.max_lat ),
					min_lon: Math.max( swNew.lng, regionParams.min_lon ),
					max_lon: Math.min( neNew.lng, regionParams.max_lon )
				};
			}
		}
	}
};


var devicesParams = Object.assign({ fields: "device_id,lat,lon" }, regionParams);

Promise.resolve($.getJSON(API_URLS.iot_devices + '?' + encodeParamPairs(devicesParams)))
	.then(function(result){
		if(result && result.count){
			allDeviceMap = arrayToObjectWithKey(result.data, "device_id");

			allStations = result.data.map(function(item){
				return L.circleMarker(L.latLng(item.lat, item.lon), markerOptions);
			});
			onIotShowSwitcherChange();
		}
	})
	.catch(function(err){
		console.error(err);
	});

Promise.resolve($.getJSON(API_URLS.iot_event_earliest + '?' + encodeParamPairs(regionParams)))
	.then(function(result){
		var todayDate = new Date(),
			defaultMinDate = new Date();

		// default min date is last year
		defaultMinDate.setFullYear( todayDate.getFullYear() - 1 );

		var minDateStr = result.count ? result.data.start_time : (defaultMinDate.yymmddHHmm() + ":00"),
			maxDateStr = (new Date()).yymmdd() + " 00:00:00";	// default today
		
		var minDate = parseDateString(minDateStr),
			maxDate = parseDateString(maxDateStr),
			initStartDate;

		$("#controller-container span.from-date").text( stampsToDateStr(minDate.getTime()) );
		$("#controller-container span.to-date").text( stampsToDateStr(maxDate.getTime()) );

		initStartDate = parseDateString(maxDateStr);
		initStartDate.setDate(initStartDate.getDate() - 30);

		generateDateRangeButtons(minDate, maxDate);

		noUiSlider.create(slider, {
		    animate: false,

			start: [ initStartDate.getTime(), maxDate.getTime() ],

			// one hour
			step: 60 * 60 * 1000,
			connect: true,
			range: {
				'min': minDate.getTime(),
				'max': maxDate.getTime()
			},
			format: {
				to: function(v){ return stampsToDateStr(v); },
				from: function(v){return v;}
			}
		});

		function onSliderSetHandler(values, handle, unencoded, tap, positions){
			if(stopSetHandler) return;
			if(skipHandlerOnce) { 
				skipHandlerOnce = false;
				return;
			}

			var dateStrFrom = stampsToDateStr(unencoded[0]) + ":00";
			var dateStrTo = stampsToDateStr(unencoded[1]) + ":00";

			if(!eventFromButton) $("#filterDaterange button").removeClass("btn-success").addClass("btn-default");

			!eventFromMap && loadingLayer.show();

			var requestProcess = [];

			// change to query by bounds
			var computedBounds = rectangleControl.getCurrentBounds(mainMap);
			var circlesAvgParams = Object.assign({
				start_time: dateStrFrom,
				end_time: dateStrTo,
				score_threshold: rectangleControl.getCurrentThreshold(mainMap)
			}, computedBounds );

			computedBounds && requestProcess.push(
				Promise.resolve($.getJSON(API_URLS.iot_circles_avg + '?' + encodeParamPairs(circlesAvgParams)))
				.then(function(averageResult){
					var allRawResults = averageResult.count? averageResult.data : [];

					if(allRectangles.length){
						allRectangles.forEach(function(rect){ mainMap.removeLayer(rect); });
						allRectangles = [];
					}

					var resultsPositionMap = arrayToObjectWithKey(
						allRawResults, 
						function(item){
							if ( item['lat'] && item['lon'] ) return item['lat'] + '-' + item['lon'];
						}
					);

					var scoreLikeRe = /^score.*$/g;

					var allResults = [];

					Object.keys(resultsPositionMap).forEach(function(key){
						var resultObj = resultsPositionMap[key];
						var sumScore = 0;

						if ( resultObj ) {
							var scoreProps = Object.keys(resultObj).filter(function(prop){ return scoreLikeRe.test(prop); });
							if ( scoreProps && scoreProps.length ) {
								var radius = 0.3 / 2 - 0.3 * 0.02;	// for spacing
								allResults.push({
									lat: resultObj.lat,
									lon: resultObj.lon,
									score: resultObj[ scoreProps[0] ],
									squareBounds: [
										[ resultObj.lat + radius * latitudeDiffPerKm, resultObj.lon + radius * longitudeDiffPerKm ],
										[ resultObj.lat - radius * latitudeDiffPerKm, resultObj.lon - radius * longitudeDiffPerKm ]
									]
								});								
							}
						}
					});

					if(allResults.length){
						// get min score and max score
						var minScore = 0, maxScore;
						allResults.forEach(function(point){
							minScore = Math.min(minScore, point.score);
							maxScore = Math.max(maxScore || point.score, point.score);
						});

						gradiantColors.setNumberRange(minScore, maxScore);

						var getLevelText = (function(min, max){
							var bounds = [ (max - min) / 3, (max - min) * 2 / 3 ];
							return function(score){
								var strText, percentage;

								// low
								if ( score < bounds[0] ) strText = "低污染潛勢";
								// medium
								else if ( bounds[0] <= score && score < bounds[1] ) strText = "中污染潛勢";
								// high
								else strText = "高污染潛勢";

								percentage = fixedFloat( (score - min) / (max - min) * 100, 1 );

								return strText + " " + percentage + " %";
							};
						})(minScore, maxScore);

						allResults.forEach(function(point){
							var rect = L.rectangle(point.squareBounds ,{ stroke: false, fillOpacity: 0.6 })
								.bindTooltip(
									(function(lat, lng, levelText){
										return function(o){
											return [
												"<div class='inner-tooltip-wrap'>",
												"<h2>" + levelText + "</h2>",
												"<p>============================</p>",
												"<br/>",
												"<h5>位置: </h5>",
												"Lat: <span>" + lat + "</span>&nbsp;&nbsp;" + "Lng: <span>" + lng + "</span>",
												"</div>"
											].join("");
										};
									})( fixedFloat(point.lat, 4), fixedFloat(point.lon, 4), getLevelText(point.score) ),
									{offset: L.point(8, 0)}
								)
								.addTo(mainMap);

							rect.setStyle({fillColor: '#' + gradiantColors.colorAt(point.score) });

							allRectangles.push(rect);
						});
					}else alert("此區間無資料");
				})
				.catch(function(err){
					console.error(err);
				})
			);

			var oneHour = 60 * 60 * 1000;
			var shiftBackDate = new Date( parseDateString(dateStrFrom).getTime() - oneHour );
			var shiftForwardDate = new Date( parseDateString(dateStrTo).getTime() + oneHour );

			!eventFromMap && requestProcess.push(
				Promise.all([
					$.getJSON(API_URLS.iot_events + '?' + encodeParamPairs(
						Object.assign({
							start_time: dateStrFrom,
							end_time: dateStrTo
						}, regionParams)
					)),
					new Promise(function(resolve, reject){
						var mapCenter = mainMap.getCenter();
						var centerPoints = [ mapCenter.lat, mapCenter.lng ];
						Promise.resolve($.getJSON(API_URLS.epa_station_devices + '?' + encodeParamPairs({ fields: "device_id,name,lat,lon" })))
							.then(function(stationResult){
								// get nearly stations
								var nearlyStations = stationResult.data.filter(function(item){
									return distanceMeasure(item.lat, item.lon, centerPoints[0], centerPoints[1]) <= collectInKilometer;
								});
								return nearlyStations;
							})
							.then(function(nearlyStations){
								var rawdataParameters = {
									fields: "wind_direct,wind_speed",
									start_time: shiftBackDate.yymmddHHmm(),
									end_time: shiftForwardDate.yymmddHHmm(),
									// center for the init value
									min_lat: centerPoints[0],
									max_lat: centerPoints[0],
									min_lon: centerPoints[1],
									max_lon: centerPoints[1]
								};
								// find min/max lat/lon as bounds
								nearlyStations.forEach(function(item){
									rawdataParameters.min_lat = Math.min(rawdataParameters.min_lat, item.lat);
									rawdataParameters.max_lat = Math.max(rawdataParameters.max_lat, item.lat);
									rawdataParameters.min_lon = Math.min(rawdataParameters.min_lon, item.lon);
									rawdataParameters.max_lon = Math.max(rawdataParameters.max_lon, item.lon);
								});
								return Promise.resolve($.getJSON(API_URLS.epa_station_rawdata + '?' + encodeParamPairs(rawdataParameters)));
							})
							.then(function(nearlyStationRaw){
								var finnalResults = nearlyStationRaw.data
									.filter(function(item){ return item.name && item.lat && item.lon })
									.map(function(item){
										return {
						     				WS: item.wind_speed,
						     				WD: item.wind_direct,
						     				datetime: item.time,
						     				station: item.name,
						     				lat: item.lat,
						     				lon: item.lon
						     			};
									});
								resolve(finnalResults);
							})
							.catch(function(err){ reject(err); });
					})
				])
				.then(function(results){
					// {WD: "15.4", lat: 24.9948, station: "桃園", WS: "2.26", lon: 121.32, datetime: "2018-02-01 00:00:00"}
					var eventsResult = results[0];
					var stationsResult = results[1];

					// distinct the data
					var stationLatLngMap = {};
					stationsResult.forEach(function(witem){ 
						stationLatLngMap[witem.station] = [witem.lat, witem.lon];
					});

					// station name to wind short map
					var stationWindShortMap = {};
					stationsResult.forEach(function(witem){ 
						if ( !stationWindShortMap[witem.station] ) stationWindShortMap[witem.station] = {};
						var currentDate = parseDateString(witem.datetime);
						stationWindShortMap[witem.station][currentDate.yymmddHH()] = windDirection.getShort(witem.WD);
					});

					var getNearedStation = function(lat, lon){
						// find station
						var sortedStation = Object.keys(stationLatLngMap);
						sortedStation.sort(function(keya, keyb){
							var keyaDistance = distanceMeasure( stationLatLngMap[keya][0], stationLatLngMap[keya][1], lat, lon);
							var keybDistance = distanceMeasure( stationLatLngMap[keyb][0], stationLatLngMap[keyb][1], lat, lon);
							return keyaDistance < keybDistance ? -1 : 1;
						});
						return sortedStation[0];
					};

					var getWindDirects = function(station, datetime){
						var inputDate = parseDateString( datetime );
						var laterHourDate = new Date( inputDate.getTime() + 1000 * 60 * 60 );

						var resDirects = [];

						if ( stationWindShortMap[station] ) {
							var inputWD = stationWindShortMap[station][inputDate.yymmddHH()];
							var laterWD = stationWindShortMap[station][laterHourDate.yymmddHH()];
							inputWD && resDirects.push(inputWD);
							laterWD && resDirects.push(laterWD);
						}
						
						return resDirects.unique();
					};

					var summaryMap = arrayToObjectWithKey(
						eventsResult.data, 
						function(item){ 
							return item.device_list.map(function(device){ 
								var devPoint = allDeviceMap[ device['device_id'] ];
								if (devPoint) return devPoint['lat'] + "-" + devPoint['lon'];
							});
						},
						true
					);

					// reset allEventMarkers
					removeAllMarkers();

					Object.keys(summaryMap).forEach(function(position){
						var point = position.split('-').map(function(v){return parseFloat(v);});
						var stationName = getNearedStation(point[0], point[1]);
						allEventTotalMap[position] = summaryMap[position].map( 
							function(item){ 
								var res = {
									max_value: item.max_value,
									count: item.event_count,
									duration: item.duration,
									start: item.start_time,
									end: item.end_time,
									area: item.area
								};
								
								// same event should not calculate again
								if ( !item.wind_direction ) {
									item.wind_direction = getWindDirects(stationName, item.start_time)
										.concat(getWindDirects(stationName, item.end_time))
										.unique()
										.join(',');
								}

								res.wind_direction = item.wind_direction;

								return res;
							} 
						).sort(function(a, b){
							return a.count > b.count? -1 : 1;
						});
					});

					pinEventMarkers();

					triggerMarkersWithLevel(markerSwitchShow);
				})
				.catch(function(err){ console.error(err); })
			);

			Promise.all(requestProcess).then(function(){ loadingLayer.hide(); });
		}

		// From datetime picker
		$( dateRangeValues[0] ).datetimepicker({
			timeFormat: "HH:mm",
			dateFormat: 'yy-mm-dd',
			minDateTime: minDate,
			maxDateTime: maxDate,
			showMinute: false,
			onClose: onDatetimePickerClose,
			beforeShow: onDatetimePickerShow
		});

		// To datetime picker
		$( dateRangeValues[1] ).datetimepicker({
			timeFormat: "HH:mm",
			dateFormat: 'yy-mm-dd',
			minDateTime: initStartDate,
			maxDateTime: maxDate,
			showMinute: false,
			onClose: onDatetimePickerClose,
			beforeShow: onDatetimePickerShow
		});

		slider.noUiSlider.on('set', onSliderSetHandler);

		slider.noUiSlider.on('update', function( values, handle ){
			if (stopSetHandler) return;
			var restricts = [ "maxDate", "minDate" ];

			// make 1 to 0, 0 to 1
			var idx = (handle + 1) % dateRangeValues.length;
			$( dateRangeValues[idx] ).datepicker('option', restricts[idx], parseDateString(values[handle] + ":00") ).datetimepicker( "option", restricts[idx] + "Time", parseDateString(values[handle] + ":00") );

			// dateRangeValues[handle].innerHTML = stampsToDateStr( updatedDate.getTime() );
			// update all; note: 這邊會有很奇怪的觸發，讓日期一直維持在一個月間；為了避免錯誤只能先這樣寫
			values.forEach(function(v, hidx) {
				$( dateRangeValues[hidx] ).val( (parseDateString(v + ":00")).yymmddHHmm() );
			});
		});

		slider.noUiSlider.on('start', function(){ 
			// stop all events
			stopSetHandler = true;
		});

		slider.noUiSlider.on('slide', function( values, handle ){
			// handle 0, 1
			var fromDate = parseDateString( values[0] + ":00" );
			var toDate = parseDateString( values[1] + ":00" );

			if ( toDate.getTime() - fromDate.getTime() > thirtyDays ) {
				if ( handle == 0 ) {
					toDate.setTime( fromDate.getTime() + thirtyDays );
				} else {
					fromDate.setTime( toDate.getTime() - thirtyDays );
				}
				slider.noUiSlider.set( [ fromDate.getTime(), toDate.getTime() ] );
			}
		});

		slider.noUiSlider.on('end', function( values ){ 
			// continue to set handler
			stopSetHandler = false;

			var fromDate = parseDateString( values[0] + ":00" );
			var toDate = parseDateString( values[1] + ":00" );

			skipHandlerOnce = true;
			slider.noUiSlider.set( [ fromDate.getTime(), toDate.getTime() ] );
		});

		// hook map pane and zoom
		mainMap.on('zoomstart', function(){ mainMap._fromZoom = mainMap.getZoom(); });
		mainMap.on('zoomend', function(){
			if ( rectangleControl.shouldTrigger(mainMap._fromZoom, mainMap.getZoom()) ) mapForceTriggerSliderSet();
		});
	    mainMap.on('dragend', function(){
	    	if ( rectangleControl.shouldTrigger(mainMap.getZoom()) ) mapForceTriggerSliderSet();
	    });

		// init using button click
		$("#filterDaterange button.btn-success").trigger('click');
	})
	.catch(function(err){
		console.error(err);
	});

// initialize
L.mapbox.accessToken = 'pk.eyJ1IjoieWlrYWkiLCJhIjoiY2lvYTJ4b2pkMDM4dHZna3FqcGFjaHFnZiJ9.5ryPOdNr9TafMBk4AQcI6w';
// The center of taiwan
mainMap = L.mapbox.map('map', 'mapbox.emerald')
	.fitBounds([
	  [ areaBounds[3], areaBounds[1] ],
	  [ areaBounds[2], areaBounds[0] ]
	]);

L.control.scale({
	maxWidth: 150,
	position: 'bottomright'
}).addTo(mainMap);

// for the show event level
$("input[name=radio]").change(function(){
	showEventLevel = this.value;
	if( markerSwitchShow == true && this.checked && showEventLevel){
		resetAllMarkers();
		pinEventMarkers();
		triggerMarkersWithLevel(markerSwitchShow);
	}
});

$("#headerAreaText").text(areaMeta.showText);

// bind full scrren methods.
(function(){
	var btn = document.getElementById('fullscreenBtn'),
		possibleMethods = ["requestFullscreen", "msRequestFullscreen", "mozRequestFullScreen", "webkitRequestFullscreen"],
		method = possibleMethods.filter(function(m){ return !!btn[m]; })[0];
	btn.addEventListener('click', function(){
		var themap = document.getElementById('map');
		method && themap[method]();
	});
})();
