
var replaceAndLabel = function(v){
  var replaced = v.replace("T", " ");
  var splits = replaced.split(' ');
  // just only HH:mm
  var hourMin = splits[1].split(':').slice(0, 2).join(':');
  return '<span class="label label-default">' + splits[0] + '</span>&nbsp;&nbsp;&nbsp;' + hourMin;
};

var loadingLayer = $("#loading-layer");
var controlPanelWrap = $(".table-responsive");

// show area that event active is true.
var areaSet = Object.keys(areaMetaMap).filter(function(key){
  return areaMetaMap[key].eventActive;
});

var daterangeSelectSet = [
  { text: "近一個月", daysago: 30 },
  { text: "近一週", daysago: 7 },
  { text: "近三天", daysago: 3 }
];
var riskRangeSelectSet = [
  "高污染", "中污染", "低污染"
];

// for date range
var todayDate = new Date();
var thirtyDaysAgoDate = new Date( todayDate.getTime() - 1000 * 60 * 60 * 24 * 30 );
var fromDateCache = thirtyDaysAgoDate.yymmdd(); // 30 days ago
var toDateCache = "";

// for area buttons
var areaCache = areaSet.length ? areaSet[0] : "全部";
var selectedRisks = [ "高污染", "中污染" ];   // default: High and medium

$( "#fromDate" ).datepicker({
  dateFormat: "yy-mm-dd",
  maxDate: todayDate.yymmdd(),
  onClose: function( selectedDate ) {
    if ( selectedDate ) $( "#toDate" ).datepicker( "option", "minDate", selectedDate );
  }
}).val(fromDateCache);

$( "#toDate" ).datepicker({
  dateFormat: "yy-mm-dd",
  minDate: fromDateCache,
  maxDate: todayDate.yymmdd(),
  onClose: function( selectedDate ) {
    if ( selectedDate ) $( "#fromDate" ).datepicker( "option", "maxDate", selectedDate );
  }
});

var thetable = new EventTable({
  appendTo: $(".ibox-content"),
  defaultSearch: selectedRisks
});

function triggerEventLoading() {
  thetable.loadData(
    areaCache != "全部" ? areaCache : null, 
    fromDateCache ? (fromDateCache + " 00:00:00") : null,
    toDateCache ? (toDateCache + " 23:59:59") : (todayDate.yymmddHHmm() + ":00")
  );
}

$("#fromDate").on('change', function(){
  if(fromDateCache != this.value){
    fromDateCache = this.value;

    $("#filterDaterange button").removeClass("btn-success").addClass("btn-default");

    triggerEventLoading();
  }
});

$("#toDate").on('change', function(){
  if(toDateCache != this.value){
    toDateCache = this.value;

    $("#filterDaterange button").removeClass("btn-success").addClass("btn-default");

    triggerEventLoading();
  }
});

// Date range selection render/handler
$("#filterDaterange").append(
  daterangeSelectSet.map(function(item, idx){
    var b = document.createElement("button");
    
    $(b).text(item.text).val(item.daysago)
      .addClass("btn btn-sm " + (idx == 0? "btn-success" : "btn-default"))
      .click(function(){
        var jqSelf = $(this);
        jqSelf.siblings().removeClass("btn-success").addClass("btn-default");
        jqSelf.removeClass("btn-default").addClass("btn-success");

        var fromDateStr = "";

        if(jqSelf.val()){
          var newdate = new Date();
          newdate.setDate( newdate.getDate() - parseInt(jqSelf.val()) );
          fromDateStr = newdate.yymmdd();
        }

        fromDateCache = fromDateStr;
        toDateCache = "";

        $("#toDate").datepicker('setDate', "");
        $("#fromDate").datepicker('setDate', fromDateStr);

        triggerEventLoading();
      });

    return b;
  })
);

// Risk selection render/handler
$("#riskChecks").append(
  riskRangeSelectSet.map(function(item, idx){
    var d = document.createElement("div");

    $(d).addClass("form-check form-check-inline");

    var input = document.createElement("input");

    $(input).attr("type", "checkbox")
      .attr("id", "risk-check-" +  idx)
      .val(item)
      .addClass("form-check-input")
      .change(function(){
        if(this.checked){
          thetable.addSearch(this.value);
        } else {
          thetable.removeSearch(this.value);
        }
      });

    if ( selectedRisks.indexOf(item) != -1 ) $(input).prop("checked", true);

    $(d).append(input);
    
    $(d).append('<label class="form-check-label" for="' + 'risk-check-' +  idx + '">' + item + '</label>');

    return d;    
  })
);

// Area selection render/handler
$("#filterArea").append(
  areaSet.map(function(item){
    var b = document.createElement("button");

    $(b).text(item)
      .addClass("btn btn-sm " + (item == areaSet[0]? "btn-success" : "btn-default"))
      .click(function(){
        var jqSelf = $(this);
        jqSelf.siblings().removeClass("btn-success").addClass("btn-default");
        jqSelf.removeClass("btn-default").addClass("btn-success");
        areaCache = $(this).text();

        triggerEventLoading();
      });

    return b;
  })
);

// Tooltips demo
$('.ibox-title').tooltip({
    selector: "[data-toggle=tooltip]",
    container: ".ibox"
});

// initialize
triggerEventLoading();
