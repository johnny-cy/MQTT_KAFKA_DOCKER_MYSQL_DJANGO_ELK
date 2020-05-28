
// for date range
var todayDate = new Date();
var thirtyDaysAgoDate = new Date( todayDate.getTime() - 1000 * 60 * 60 * 24 * 30 );
var fromDateCache = thirtyDaysAgoDate.yymmddHHmm(); // 30 days ago
var toDateCache = todayDate.yymmddHHmm();

var levelCache = "";

// used for bar size calculation.
var defaultMaxCount = 30;

var loadingLayer = $("#loading-layer");
var searchResult = $("#searchResult");

var apiValueMap = {
	"高污染": 3,
	"中污染": 2,
	"低污染": 1
};

function destroyAllTable(){
	document.querySelectorAll("[id^=collapseTable-]").forEach(function(target){
		if ( target._eventTable ) target._eventTable.destroy();
	});
	searchResult.empty();
}

function fetchRankings(){

	var levelText = $("#levelDropdown").val();

	loadingLayer.show();

	Promise.resolve(
		$.getJSON(API_URLS.iot_event_count + '?' + encodeParamPairs({
			start_time: fromDateCache,
			end_time: toDateCache,
			min_level: apiValueMap[levelText],
			max_level: apiValueMap[levelText]
		}))
	).then(function(result){
		levelCache = levelText;
		
		if(result && result.count){
			var rankingList = result.data,
				maxCount = defaultMaxCount;

			rankingList.sort(function(a, b){ return a.counts > b.counts ? -1 : 1; });

			rankingList.forEach(function(item){
				maxCount = Math.max(maxCount, item.counts);
			});

			var iboxOuterWrap = $('<div class="ibox-content"></div>');

			rankingList.forEach(function(item, idx){
				var areaInfo = areaMetaMap[item.area] || {},
					iboxInnerWrap = $('<div class="ibox result-cell result-collapse"><div class="ibox-title"></div><div id="collapseTable-' + idx + '" class="ibox-content collapse" data-area="' + item.area + '"></div></div>'),
					iboxTitle = iboxInnerWrap.children(".ibox-title"),
					rowWrap = $('<div class="row"></div>'),
					itemCounts = item.counts;

				rowWrap.append('<div class="col-lg-2"><a data-toggle="collapse" data-parent="#searchResult" class="btn btn-sm btn-w-m btn-default" href="#collapseTable-' + idx + '" value="' + item.area + '">污染事件</a></div>');
				// rowWrap.append('<div class="col-lg-1"><button type="button" class="btn btn-sm btn-default">裝置資訊</button></div>');
				rowWrap.append('<div class="col-lg-2"><h3>' + (areaInfo.showText || item.area) + '</h3></div>');

				var progress = $('<div class="col-lg-8 progress-striped"></div>');

				progress.append('<div style="width: ' + (itemCounts/maxCount*100).toFixed(2) + '%" aria-valuemax="' + maxCount + '" aria-valuemin="0" aria-valuenow="' + itemCounts + '" role="progressbar" class="progress progress-bar progress-bar-gray"><span>' + itemCounts + ' 次</span></div>');

				rowWrap.append(progress);

				iboxTitle.append(rowWrap);
				iboxOuterWrap.append(iboxInnerWrap);
			});

			searchResult.append(iboxOuterWrap);
		}
		loadingLayer.hide();
	}).catch(function(err){
		console.error(err);
	});
}

$( "#fromDate" ).datetimepicker({
	timeFormat: "HH:mm",
	dateFormat: "yy-mm-dd",
	maxDateTime: todayDate,
	onClose: function( selectedDate ) {
		if ( selectedDate ) {
			fromDateCache = selectedDate;
			var parsedDate = parseDateString(selectedDate + ":00");
			$( "#toDate" ).datepicker( "option", "minDate", parsedDate ).datetimepicker( "option", "minDateTime", parsedDate);
		}
	}
}).val(fromDateCache);

$( "#toDate" ).datetimepicker({
	timeFormat: "HH:mm",
	dateFormat: "yy-mm-dd",
	minDateTime: thirtyDaysAgoDate,
	maxDateTime: todayDate,
	onClose: function( selectedDate ) {
		if ( selectedDate ) {
			toDateCache = selectedDate;
			var parsedDate = parseDateString(selectedDate + ":00");
			$( "#fromDate" ).datepicker( "option", "maxDate", parsedDate ).datetimepicker( "option", "maxDateTime", parsedDate);
		}
	}
}).val(toDateCache);

// level dropdown events
$("#levelItems li a").click(function(){
	$(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
	$(this).parents(".dropdown").find('.btn').val($(this).data('value'));
});

$("#searchBtn").click(function(){
	destroyAllTable();
	fetchRankings();
});

$('#searchResult').on('show.bs.collapse', function (e) {
	// The event during expanding
	var cellTarget = $(e.target).parents(".result-cell");
	cellTarget.find("a[data-toggle=collapse]").addClass("active");
});

$('#searchResult').on('shown.bs.collapse', function (e) {
	var tableTarget = e.target;
	if ( !tableTarget._eventTable ) {
		tableTarget._eventTable = new EventTable({
			appendTo: e.target,
			defaultSearch: levelCache
		});
		tableTarget._eventTable.loadData($(tableTarget).data("area"), fromDateCache, toDateCache);
	}
});

$('#searchResult').on('hide.bs.collapse', function (e) {
	// The event during expanding	
	var cellTarget = $(e.target).parents(".result-cell");
	cellTarget.find("a[data-toggle=collapse]").removeClass("active");
});
