
//for requiring a script loaded asynchronously.
function asyncLoadScript(src, callback){
    var script = document.createElement('script');
    if(typeof callback === "function"){
        if (script.readyState) { // IE, incl. IE9
            script.onreadystatechange = function() {
                if (script.readyState == "loaded" || script.readyState == "complete") {
                    script.onreadystatechange = null;
                    callback();
                }
            };
        } else {
            script.onload = function() { // Other browsers
                callback();
            };
        }
    }
    script.src = src; 
    document.getElementsByTagName('head')[0].appendChild(script);
}

function fixedFloat(v, decimals){ return parseFloat(v.toFixed(decimals || 2)); }

function lessTenAddZero(v) { return v < 10? ("0" + v) : v; };

// copy from: https://stackoverflow.com/a/11172685
function distanceMeasure(lat1, lon1, lat2, lon2){  // generally used geo measurement function
    var R = 6378.137; // Radius of earth in KM
    var dLat = lat2 * Math.PI / 180 - lat1 * Math.PI / 180;
    var dLon = lon2 * Math.PI / 180 - lon1 * Math.PI / 180;
    var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    var d = R * c;
    return d; // KM
}

// Parse datestring like: "2018-07-22 06:32:03" or "2018-07-22 06:34"
function parseDateString(datestr){
    var resDate = new Date(datestr);    // Chrome: OK, Android Chrome: OK, Safari: NO
    if ( resDate.toString() == "Invalid Date" ) {
        var datetimeSplits = datestr.split(' ');
        var dateSplits = datetimeSplits[0].split('-').map( function(v){ return parseInt(v); } );
        var timeSplits = datetimeSplits[1].split(':').map( function(v){ return parseInt(v); } );
        resDate = new Date(dateSplits[0], dateSplits[1] - 1, dateSplits[2], timeSplits[0], timeSplits[1], timeSplits[2] || 0);
    }
    return resDate;
}

function decodeURIParameter(uriStr) {
    var resPairs = {};
    uriStr.substring(1)
        .split('&')
        .forEach(function(item){
            var pair = item.split('='); 
            resPairs[pair[0]] = decodeURIComponent(pair[1]); 
        });
    return resPairs;
}

function encodeParamPairs(param){
    return Object.keys(param)
        .map(function(key){ return key + "=" + encodeURIComponent(param[key]); })
        .join('&');
}

// make array like: [ { id: xx1, }, { id: xx2, }... ] to { xx1: { id: xx1, }, xx2: { id: xx2 } }
function arrayToObjectWithKey(list, key, handleKeyToList){
    var res = {};
    var keyFn = typeof key == 'function'? key : null;
    handleKeyToList = handleKeyToList === true;
    list && list.forEach(function(item){
        var mapkeys = keyFn? keyFn(item) : item[key];
        if ( mapkeys ) {
            if ( !Array.isArray(mapkeys) ) mapkeys = [mapkeys];
            if(handleKeyToList){
                mapkeys.forEach(function(mk){
                    if (typeof mk != 'undefined' && mk != null) {
                        if(!res[mk]) res[mk] = [];
                        res[mk].push(item);
                    }
                });
            } else {
                mapkeys.forEach(function(mk){ 
                    if (typeof mk != 'undefined' && mk != null) res[mk] = item;
                });
            }
        }
    });
    return res;
}

function getRiskLevel(count, duration){
    var score = count * duration;
    if ( score >= 225 ) {
        return '高';
    } else if ( score >= 100 ) {
        return '中';
    } else if ( score >= 25 ) {
        return '低';
    }
}


function getRiskLevel_v2(level){
    if ( level == 3 ) {
        return '高';
    } else if ( level == 2 ) {
        return '中';
    } else if ( level == 1 ) {
        return '低';
    }
}

// For browser integration (IE)
if (typeof Object.assign != 'function') {
    Object.assign = function (target, varArgs) { // .length of function is 2
        'use strict';
        if (target == null) { // TypeError if undefined or null
            throw new TypeError('Cannot convert undefined or null to object');
        }

        var to = Object(target);

        for (var index = 1; index < arguments.length; index++) {
            var nextSource = arguments[index];

            if (nextSource != null) { // Skip over if undefined or null
                for (var nextKey in nextSource) {
                    // Avoid bugs when hasOwnProperty is shadowed
                    if (Object.prototype.hasOwnProperty.call(nextSource, nextKey)) {
                        to[nextKey] = nextSource[nextKey];
                    }
                }
            }
        }
        return to;
    };
}

Array.prototype.unique = function(){
    return this.filter(function(value, index, self){    // to unique
        return self.indexOf(value) === index;
    });
};

Array.prototype.leftJoin = function(arr, key){
    var tempMap = {}, res = [];
    arr.forEach(function(item){
        tempMap[ item[key] ] = item;
    });
    this.forEach(function(item){
        var resobj = {};
        for (var p in item) { resobj[p] = item[p]; }
        
        var target = tempMap[ item[key] ];
        if ( target ) for (var p in target) { resobj[p] = target[p]; }

        res.push(resobj);
    });
    return res;
};

Date.prototype.yymmdd = function(){
    var mm = this.getMonth() + 1, // getMonth() is zero-based
        dd = this.getDate();
    return [ this.getFullYear(), lessTenAddZero(mm), lessTenAddZero(dd) ].join('-');
};

Date.prototype.yymmddHH = function(){
    return [ this.yymmdd(), lessTenAddZero(this.getHours()) ].join(" ");
};

Date.prototype.yymmddHHmm = function() {
    return [ this.yymmddHH(), lessTenAddZero(this.getMinutes()) ].join(":");
};

var latitudeDiffPerKm = 0.0089831528;
var longitudeDiffPerKm = 0.0098494508;

