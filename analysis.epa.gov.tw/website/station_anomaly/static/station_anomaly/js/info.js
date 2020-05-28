
var anomalyData = { result: [] };
var anomalyStationItemHourMap = {};

function generateStationHourMap(inputData){
    // reset
    anomalyStationItemHourMap = {};

    inputData["result"].forEach(function(data) {
        var station = data["station"];
        var item = data["item"];
        var strHour = data["datetime"].substring(11, 13);
        if( !anomalyStationItemHourMap[station] ) anomalyStationItemHourMap[ station ] = {};
        if( !anomalyStationItemHourMap[station][item] ) anomalyStationItemHourMap[station][item] = {};
        anomalyStationItemHourMap[station][item][strHour] = {
            anomalyLevel: data["anomalyLevel"],
            value: data["value"]
        }
    });
}

var showErrors = true;
// for the show error rows
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        // data[index]: index is in the order of columns.
        if(showErrors){
            var station = data[1],
                item = data[2];
            return !!(
                anomalyStationItemHourMap[station] && 
                anomalyStationItemHourMap[station][item]
            );
        }

        // means ignore filter
        return true;
    }
);

// Return a cell renderer for styling each cells instead JQuery selections
function makeRendererWithHour(strHour){
    return function( data, type, row, meta ){
        var station = row["station"],
            item = row["item"];

        // filter the #
        if(data && data[data.length-1] == "#") {
            data = data.substr(0, data.length - 1);
        }

        if(anomalyStationItemHourMap[station] && 
            anomalyStationItemHourMap[station][item] &&
            anomalyStationItemHourMap[station][item][strHour]) {
            // Anomaly Level: anomalyStationItemHourMap[station][item][strHour]["anomalyLevel"];
            return '<span class="error-highlight">' + data + '</span>';
        }

        return data;
    };
}

var todayDate = new Date();
var previousDate = new Date();
var minDate = new Date();

previousDate.setDate( todayDate.getDate() - 7 );
minDate.setDate( todayDate.getDate() - 30);

var previousDateStr = previousDate.yymmdd();
var todayDateStr = todayDate.yymmdd();

var dataTable = $("#station-data").DataTable( {
    data: [],
    columns: [
        { data: "date" },
        { data: "station" },
        { data: "item" },
        { data: "00", render: makeRendererWithHour("00") },
        { data: "01", render: makeRendererWithHour("01") },
        { data: "02", render: makeRendererWithHour("02") },
        { data: "03", render: makeRendererWithHour("03") },
        { data: "04", render: makeRendererWithHour("04") },
        { data: "05", render: makeRendererWithHour("05") },
        { data: "06", render: makeRendererWithHour("06") },
        { data: "07", render: makeRendererWithHour("07") },
        { data: "08", render: makeRendererWithHour("08") },
        { data: "09", render: makeRendererWithHour("09") },
        { data: "10", render: makeRendererWithHour("10") },
        { data: "11", render: makeRendererWithHour("11") },
        { data: "12", render: makeRendererWithHour("12") },
        { data: "13", render: makeRendererWithHour("13") },
        { data: "14", render: makeRendererWithHour("14") },
        { data: "15", render: makeRendererWithHour("15") },
        { data: "16", render: makeRendererWithHour("16") },
        { data: "17", render: makeRendererWithHour("17") },
        { data: "18", render: makeRendererWithHour("18") },
        { data: "19", render: makeRendererWithHour("19") },
        { data: "20", render: makeRendererWithHour("20") },
        { data: "21", render: makeRendererWithHour("21") },
        { data: "22", render: makeRendererWithHour("22") },
        { data: "23", render: makeRendererWithHour("23") }
    ]
} );

new $.fn.dataTable.Buttons( dataTable, {
    buttons: [
        {
            extend: 'csv',
            text: '匯出CSV'
        },
        {
            extend: 'excel',
            text: '匯出Excel'
        }
    ]
} );
dataTable.buttons().container().css("float", "right").appendTo( $("#data_1 h3") );

$( "#fromDate" ).datepicker({
	dateFormat: "yy-mm-dd",
    minDate: minDate.yymmdd(),
    maxDate: todayDateStr,
    onClose: function( selectedDate ) {
        $( "#toDate" ).datepicker( "option", "minDate", selectedDate );
    }
});

$( "#toDate" ).datepicker({
	dateFormat: "yy-mm-dd",
    minDate: previousDateStr,
    maxDate: todayDateStr,
    onClose: function( selectedDate ) {
        $( "#fromDate" ).datepicker( "option", "maxDate", selectedDate );
    }
});

function datePickerOnChange(){
    var self = this;
    if (self.value == self.oldvalue) return;

    // cache
    self.oldvalue = self.value;

    var strStart = $( "#fromDate" ).val();
    var strEnd = $( "#toDate" ).val();

    Promise.all([
    	nsd24_data,
    	anomaly_data
    ])
    .then(function(results){

    	var nsd24Result = results[0];
    	var anomalyResult = results[1];

    	// anomalyData = anomalyResult;
        generateStationHourMap(anomalyResult);

    	// renew
		dataTable.clear();
		dataTable.rows.add(nsd24Result.result);
		dataTable.draw();

    })
    .catch( function(err){ console.error(err); } );
}

$("#fromDate").on('change', datePickerOnChange);
$("#toDate").on('change', datePickerOnChange);

$("#fromDate").val(previousDateStr);
$("#toDate").val(todayDateStr).trigger('change');

$("#showAll").on('change', function() {
    showErrors = !this.checked;
    dataTable.draw();
});

