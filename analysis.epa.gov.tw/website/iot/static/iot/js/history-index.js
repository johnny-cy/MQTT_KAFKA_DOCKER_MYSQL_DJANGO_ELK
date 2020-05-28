
var initCenterPoints = [23.764097871800434, 120.90621471405031];
var initZoomLevel = 7;

var minPassZoom = 12;
var fromChooseMapEvent = false;

var passToMap = {
	start_lat: null,
	end_lat: null,
	start_lon: null,
	end_lon: null
};

var centerMarker, mainMap;

// auto detect ranges and generate buttons.
function initializeButtons(){
	var buttonToggle = function(){
		var jqSelf = $(this);
		jqSelf.parents("td").find("button").removeClass("btn-success").addClass("btn-default");
		jqSelf.removeClass("btn-default").addClass("btn-success");
	};

	// show area that event active is true.
	var buttons = Object.keys(areaMetaMap)
		.filter(function(key){
			return areaMetaMap[key].eventActive;
		})
		.map(function(key){
			var item = areaMetaMap[key];
			var bounds = item.bounds;
			return { 
				text: item.showText || key,
				start_lat: bounds[2],
				end_lat: bounds[3],
				start_lon: bounds[0],
				end_lon: bounds[1]
			};
		});

	buttons.forEach(function(item, idx){
		
		var b = document.createElement("button");

		$(b).text(item.text)
			.addClass("btn btn-default")
			.click(
				(function(it){
					return function(){
						buttonToggle.call(this);

						fromChooseMapEvent = false;
						
						passToMap.start_lat = it.start_lat;
						passToMap.end_lat = it.end_lat;
						passToMap.start_lon = it.start_lon;
						passToMap.end_lon = it.end_lon;

						$("#chooseMapText").text("");
					};
				})(item)
			);

		$("#panButtons").append(b);
	});

	// generate choose from map
	$("#confirmLocation").click(function(){
		buttonToggle.call( $("#chooseMapButton") );
		var leafletPoints = mainMap.getCenter();

		if ( mainMap.getZoom() < minPassZoom ) {
			mainMap.setZoom(minPassZoom);
		}

		fromChooseMapEvent = true;

		$("#chooseMapText").text( "您選擇了地圖中心點：" + [leafletPoints.lat,leafletPoints.lng].join(',') );
	});
}

L.mapbox.accessToken = 'pk.eyJ1IjoieWlrYWkiLCJhIjoiY2lvYTJ4b2pkMDM4dHZna3FqcGFjaHFnZiJ9.5ryPOdNr9TafMBk4AQcI6w';

mainMap = L.mapbox.map('map', 'mapbox.emerald').setView(initCenterPoints, initZoomLevel);

centerMarker = L.marker(initCenterPoints).addTo(mainMap);

mainMap.on('move', function () {
	centerMarker.setLatLng(mainMap.getCenter());
});

// fix bug about not show map at first time.
$('#chooseMapModal').on('show.bs.modal', function(){
	setTimeout(function() { 
		mainMap.invalidateSize(); 
	}, 300);
 });

initializeButtons();

var twelveHours = 1000 * 60 * 60 * 12;
var todayDate = new Date();
var initMinDate = new Date();
initMinDate.setTime( initMinDate.getTime() - twelveHours );

var dateRangeValues = [
	document.getElementById('fromDatePicker'),
	document.getElementById('toDatePicker')
];
// From datetime picker
$( dateRangeValues[0] ).datetimepicker({
	timeFormat: "HH:mm",
	dateFormat: 'yy-mm-dd',
	maxDateTime: todayDate,
	// showMinute: false,
	onClose: function(datestr){
		var currentDate = new Date( datestr + ":00" );
		var endDate = new Date( $(dateRangeValues[1]).val() + ":00" );

		var jqDateTimePicker = $( dateRangeValues[1] ).datepicker('option', "minDate", currentDate ).datetimepicker('option', "minDateTime", currentDate );
		if ( Math.abs( currentDate.getTime() - endDate.getTime() ) > twelveHours ) {
			var changeDate = new Date(currentDate.getTime() + twelveHours);
			jqDateTimePicker.val( changeDate.yymmddHHmm() );
		} else {
			jqDateTimePicker.val( endDate.yymmddHHmm() );
		}
	}
}).val(initMinDate.yymmddHHmm());

// To datetime picker
$( dateRangeValues[1] ).datetimepicker({
	timeFormat: "HH:mm",
	dateFormat: 'yy-mm-dd',
	minDateTime: initMinDate,
	maxDateTime: todayDate,
	// showMinute: false,
	onClose: function(datestr){
		var currentDate = new Date( datestr + ":00" );
		var startDate = new Date( $(dateRangeValues[0]).val() + ":00" );

		var jqDateTimePicker = $( dateRangeValues[0] ).datepicker('option', "maxDate", currentDate ).datetimepicker('option', "maxDateTime", currentDate );
		if ( Math.abs( currentDate.getTime() - startDate.getTime() ) > twelveHours ) {
			var changeDate = new Date(currentDate.getTime() - twelveHours);
			jqDateTimePicker.val( changeDate.yymmddHHmm() );
		} else {
			jqDateTimePicker.val( startDate.yymmddHHmm() );
		}
	}
}).val(todayDate.yymmddHHmm());

$( "#popupModal" ).on('hidden.bs.modal', function(){
	$(this).find('iframe').html("").attr("src", "");
});

$( "#playButton" ).click(function(e){

	if ( fromChooseMapEvent ) {
		var currentBounds = mainMap.getBounds(),
			ne = currentBounds.getNorthEast(),
			sw = currentBounds.getSouthWest();

		passToMap.start_lat = sw.lat;
		passToMap.end_lat = ne.lat;
		passToMap.start_lon = sw.lng;
		passToMap.end_lon = ne.lng;

		fromChooseMapEvent = false;
	}

	if ( !passToMap.start_lat || !passToMap.end_lat || !passToMap.start_lon || !passToMap.end_lon ) {
		$( "#errorMsg" ).text("請選擇地點").show();
		e.stopPropagation();
		return;
	}
	
	$( "#errorMsg" ).hide();

	var allowFullscreen = $(this).attr('data-bmdVideoFullscreen') || false;

	var strParams = [
		'start=' + $(dateRangeValues[0]).val(),
		'end=' + $(dateRangeValues[1]).val(),
		'start_lat=' + passToMap.start_lat,
		'end_lat=' + passToMap.end_lat,
		'start_lon=' + passToMap.start_lon,
		'end_lon=' + passToMap.end_lon
	].join("&");

	var props = {
        // TODO: Need to pass CAMEO_SUB_PATH here
		'src': "/web/iot/history/animation?" + strParams
	};

	if ( allowFullscreen ) props.allowfullscreen = "";

	$("#popupModal").find("iframe").attr(props);
});
