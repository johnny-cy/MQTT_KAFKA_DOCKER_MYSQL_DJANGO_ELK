
function getTriangleInfo(latX, lngX, latY, lngY){
    var increment = ( latY >= latX ) ? 0 : 90;
    var inverse = ( lngY >= lngX ) ? 1 : -1;
    var hypotenuse = distanceMeasure(latX, lngX, latY, lngY);
    var adjacent = increment ? distanceMeasure(latX, lngX, latX, lngY) : distanceMeasure(latX, lngX, latY, lngX);

    return {
        degree: ( Math.acos(adjacent / hypotenuse) * 180 / Math.PI + increment ) * inverse,
        adjacent: adjacent,
        hypotenuse: hypotenuse,
        inverse: inverse,
        increment: increment
    };
}

var loadingLayer = $("#loading-layer"), mainMap, idwLayer;
var initCenterPoints = [23.764097871800434, 120.90621471405031];
var initZoomLevel = 7;
var animateStepTime = 400;

var diffusionDefaultStep = 10;
var diffusionRadius = 50;    // per step in meters
var diffusionRadiusPixel = 10;    // per step in pixels
var diffusionMaxCircles = 5;

// use distanceMeasure method to calculate the differece between two points in 25km.
var longitudeDiffIn25km = 0.2477;
var latitudeDiffIn25km = 0.2245;

var passParams = decodeURIParameter(location.search);

var colorPicker = {
    _undefinedValue: '#ffffff',
    _valuePatterns: [3.04, 6.08, 9.12, 12.16, 15.5, 19.5, 23.5, 27.5, 31.5, 35.5, 39.3, 43.1, 46.9, 50.7, 54.5, 73.7, 92.9, 112.1, 131.3, 150.5, 170.5, 190.5, 210.5, 230.5, 250.5, 300.5, 350.5, 400.5, 450.5, 500.4],
    _colorPatterns: ["#29fd2e", "#53FD30", "#7EFD32", "#a9fd34", "#d4fd36", "#fffd38", "#ffe534", "#fecb30", "#feb12b", "#fd9827", "#fd7e23", "#fd6822", "#fd5220", "#fc3b1f", "#fc241d", "#fc0e1c", "#e30e30", "#ca0e43", "#b10f56", "#970f6a", "#7e0f7e", "#781666", "#731d4e", "#6d2537", "#682c1f", "#623307", "#552E0A", "#49280D", "#3C230F", "#301E12", "#000000"],
    _gradientRatioBound: 0.005,
    getColorByValue: function(val){
        if( typeof val != "number" ) return this._undefinedValue;
        var values = this._valuePatterns.slice(0);
        values.push(val);
        values.sort( function(a,b){ return a-b; } );
        return this._colorPatterns[ values.indexOf(val) ];
    },
    getMaxPatternValue: function(){
        return this._valuePatterns[ this._valuePatterns.length - 1 ];
    },
    getDiffusionGradient: function(){
        var res = {},
            self = this,
            valuePatterns = self._valuePatterns.slice(0),
            baseValue = valuePatterns[ valuePatterns.length - 1 ];

        valuePatterns.unshift(0);
        valuePatterns.push(baseValue);

        for (var idx = 1, len = valuePatterns.length; idx < len; idx++) {
            var ratio = ( valuePatterns[idx] + valuePatterns[idx - 1] ) / 2 / baseValue;
            if ( ratio > self._gradientRatioBound ) {
                res[ ratio.toFixed(3) ] = self._colorPatterns[idx - 1];
            }
        }

        // zero value
        res["0.0"] = self._undefinedValue;

        // bound valud
        res[ self._gradientRatioBound.toString() ] = self._undefinedValue;

        return res;
    },
    renderColorSamples: function(appendEl){
        var body = $('<table><tbody><tr class="color-row"></tr><tr class="linear-text"></tr></tbody></table>'),
            colorRow = body.find(".color-row"),
            colorText = body.find(".linear-text"),
            patterns = this._valuePatterns.slice(0);

        this._colorPatterns.forEach(function(colorCode){
            colorRow.append('<td style="background-color: ' + colorCode + ';"></td>');
        });

        var defaultUnitShow = 5;
        patterns.unshift(0);
        patterns.forEach(function(number, idx){
            if ( idx % defaultUnitShow == 0 ) {
                colorText.append('<td><span>' + number + '</span></td>');
            } else {
                colorText.append('<td></td>');
            }
        });

        $(appendEl).append(body);
    }
};

var latLngScoreTickMap = {};
var latLngPickedTickMap = {};
var latLngWindsMap = {};
var allStations = [];
var foundWindList = [];
var latLngDiffusionMap = {};
var latLngDiffusionPreviousMap = {};

var stationMarkerOptions = {
    radius: 5.5,
    fillColor: "#fff",
    color: "#a0a0a0",
    opacity: 0.2,
    fillOpacity: 0.4
};

var plotOptions = {
    xaxis: {
        mode: 'time',
        timezone: "browser"
    },
    legend: {
        show: false
    },
    colors: ["#1ab394"],
    grid: {
        color: "#999999",
        clickable: true,
        tickColor: "#D4D4D4",
        borderWidth:0,
        hoverable: true //IMPORTANT! this is needed for tooltip to work,
    },
    tooltip: true,
    tooltipOpts: {
        content: "time: %x  score: %y",
        xDateFormat: "%H:%M"
    }
};

// 1 mins
var oneMinute = 60 * 1000;
// 10 mins
var tenMinutes = 10 * oneMinute;
// 1 hour
var oneHour = 60 * oneMinute;
// 2 hours
var twoHours = 2 * oneHour;
// 3 hours
var threeHours = 3 * oneHour;
// 29 mins
var twentyNightMins = 29 * oneMinute;
// 12 hours
var twelveHours = 12 * oneHour;

var nowDate = new Date();
var minDate = parseDateString(passParams.start);
var maxDate = parseDateString(passParams.end);

// Expand the time range to 10 mins ago/later
minDate.setTime( minDate.getTime() - tenMinutes );
maxDate.setTime( maxDate.getTime() + tenMinutes );

// if max date over now, force make Now as maxdate
if ( maxDate.getTime() > nowDate.getTime() ) {
    maxDate.setTime( nowDate.getTime() );
}
// if date range over 12 hours, force reduce range in 12 hours.
if ( maxDate.getTime() - minDate.getTime() > twelveHours ) {
    minDate.setTime( maxDate.getTime() - twelveHours );
}

// override parameters
passParams.start = minDate.yymmddHHmm();
passParams.end = new Date((maxDate.getTime() + oneMinute)).yymmddHHmm();

var minDateTime = minDate.getTime();
var maxDateTime = maxDate.getTime();

// 1 mins for slider step
var unitStep = oneMinute;

var shiftBackDate = new Date( minDateTime - ( ( maxDateTime - minDateTime > twoHours ) ? oneHour : threeHours ) );
var shiftForwardDate = new Date( maxDateTime + oneHour );

var mapSurrounObjectController = {
    _map: null,
    _mapInfo: {},
    _config: {
        kilometer: 25
    },
    _objects: [],
    _filterd: [],
    _inBounds: [],
    _outBounds: [],
    _objKeyMap: {},
    _hiddenInDegree: 30,
    _updateMapInfo: function(){
        var self = this;
        var om = self._mapInfo;
        if ( self._map ) {
            var center = self._map.getCenter(),
                bounds = self._map.getBounds(),
                north = bounds.getNorth(),
                east = bounds.getEast();
            self._mapInfo = {
                center: [ center.lat, center.lng ],
                north: north,
                east: east,
                west: bounds.getWest(),
                south: bounds.getSouth(),
                cornerInfo: getTriangleInfo(center.lat, center.lng, north, east)
            }
        }
    },
    _defaultRenderer: function(obj){
        var wrap = document.createElement('div');
        wrap.classList.add("soc-wrap");

        var arrow = document.createElement('div');
        arrow.classList.add("soc-arrow");
        arrow.classList.add("fa");
        arrow.classList.add("fa-angle-up")

        var body = document.createElement('div');
        body.classList.add("soc-body");

        wrap.appendChild(arrow);
        wrap.appendChild(body);

        return wrap;
    },
    _defaultLayouter: function(objEl, objInfo, cornerInfo, body){
        if ( !objEl || !objInfo ) return;
        var socBody = objEl.children(".soc-body"),
            socArrow = objEl.children(".soc-arrow"),
            positiveDegree = objInfo.degree * objInfo.inverse,
            recoverdDegree = positiveDegree - objInfo.increment,
            isAnother = positiveDegree > cornerInfo.degree && positiveDegree < ( 180 - cornerInfo.degree );

        var mapContainer = this._map.getContainer();
        var mapWidth = $(mapContainer).width();
        var mapHeight = $(mapContainer).height();

        socBody.empty();
        socBody.append(body);

        var wrapWidth = objEl.outerWidth();
        var wrapHeight = objEl.outerHeight();
        var arrowWidth = socArrow.outerWidth();
        var arrowHeight = socArrow.outerHeight();

        var wrapPositions = {
            left: '', top: '', right: '', bottom: ''
        };
        var arrowPositions = {
            left: '', top: '', right: '', bottom: ''
        };

        var verticalProp = ( objInfo.increment == 0 ) ? "top" : "bottom";
        var horizontalProp = ( objInfo.inverse == 1 ) ? "right" : "left" ;

        var baseDegree, differentDegree;
        if ( isAnother ) {
            baseDegree = 90 - cornerInfo.degree;
            if ( objInfo.increment ) {
                differentDegree = baseDegree - recoverdDegree;
            } else {
                differentDegree = baseDegree - ( 90 - recoverdDegree );
            }
        } else {
            baseDegree = cornerInfo.degree;
            if ( objInfo.increment ) {
                differentDegree = baseDegree - ( 90 - recoverdDegree );
            } else {
                differentDegree = baseDegree - recoverdDegree;
            }
        }

        var positionRatio = differentDegree / baseDegree;

        var zeroProp = isAnother ? horizontalProp : verticalProp;
        var offsetProp = isAnother ? verticalProp : horizontalProp;

        var offsetMapBase = isAnother ? ( mapHeight / 2 ) : ( mapWidth / 2 );
        var offsetWrapBase = isAnother ? ( wrapHeight / 2 ) : ( wrapWidth / 2 );
        var offsetArrowBase = isAnother ? ( arrowHeight / 2 ) : ( arrowWidth / 2 );

        // wrap
        wrapPositions[zeroProp] = 0;
        wrapPositions[offsetProp] = Math.max( positionRatio * offsetMapBase - offsetWrapBase, 0);
        // arrow
        arrowPositions[zeroProp] = 0;
        arrowPositions[offsetProp] = Math.max( positionRatio * offsetWrapBase - offsetArrowBase, 0);

        objEl.css(wrapPositions);
        socArrow.css(arrowPositions);
    },
    _hideSingle: function(obj){
        if ( obj._el ) obj._el.hide();
    },
    _hideFilterd: function(){
        // old filterd
        this._filterd.forEach(this._hideSingle);
    },
    _renderFiltered: function(){
        var self = this;
        var mapContainer = self._map.getContainer();
        self._filterd.forEach(function(obj){
            if ( !obj._el ) {
                obj._el = self._defaultRenderer();
                mapContainer.appendChild(obj._el);
                obj._el = $(obj._el);
            }
        });
    },
    _calculateFiltered: function(){
        var self = this;
        if ( !self._map ) return;

        // update object according to the map
        if ( self._objects.length && self._mapInfo && self._mapInfo.center ) {
            var mapInfo = self._mapInfo;
            var center = mapInfo.center;
            self._objects.forEach(function(obj){
                obj._info = getTriangleInfo(center[0], center[1], obj.lat, obj.lng);
            });

            self._filterd = self._objects.filter(function(obj){
                return obj._info.hypotenuse < self._config.kilometer;
            });

            self._inBounds = self._filterd.filter(function(obj){
                var isInBound = obj.lat <= mapInfo.north && obj.lat >= mapInfo.south &&
                    obj.lng <= mapInfo.east && obj.lng >= mapInfo.west;
                obj._isInBound = isInBound;
                return isInBound;
            });

            self._outBounds = self._filterd.filter(function(obj){
                var isOutBound = self._inBounds.indexOf(obj) == -1;
                obj._isInBound = !isOutBound;
                obj._tempHidden = false;
                return isOutBound;
            });

            if ( self._hiddenInDegree ) {
                // sort by nearest
                self._outBounds.sort(function(a, b){
                    return a._info.hypotenuse < b._info.hypotenuse ? -1 : 1;
                });

                // find the items would not overlap
                var tempOutBounds = [];
                self._outBounds.forEach(function(obj){
                    if ( !tempOutBounds.length ) tempOutBounds.push(obj);
                    else {
                        var foundOverlap = tempOutBounds.filter(function(tempObj){
                            var absDiff = Math.abs( tempObj._info.degree - obj._info.degree );
                            return Math.min(absDiff, 360 - absDiff) < self._hiddenInDegree;
                        });
                        if ( !foundOverlap.length ) tempOutBounds.push(obj);
                        else obj._tempHidden = true;
                    }
                });

                self._outBounds = tempOutBounds.slice(0);
            }
        }
    },
    _layouts: function(){
        var self = this;
        var cornerInfo = self._mapInfo.cornerInfo;
        var cornerAdjacent = cornerInfo.adjacent;

        self._outBounds.forEach(function(obj){
            var objEl = obj._el,
                socBody = objEl.children(".soc-body"),
                socArrow = objEl.children(".soc-arrow"),
                objInfo = obj._info;

            var objRenderer = obj._outBoundRenderer;

            socArrow.css("transform", "rotate(" + objInfo.degree + "deg)");

            obj._kilometer = fixedFloat(objInfo.hypotenuse, 2);

            self._defaultLayouter(objEl, objInfo, cornerInfo, objRenderer.call(self, obj, obj._kilometer, obj._metadata ) );
        });

        self._inBounds.forEach(function(obj){
            var objInfo = obj._info;

            obj._kilometer = fixedFloat(objInfo.hypotenuse, 2);

            if ( obj._marker ) self._map.removeLayer(obj._marker);
            obj._marker = obj._inBoundRenderer.call(self, obj, obj._kilometer, obj._metadata);
        });
    },
    _showSingle: function(obj){
        if ( obj.hidden === true || obj._tempHidden === true ) {
            if ( obj._isInBound ) obj._marker && obj._marker.remove();
            else obj._el && obj._el.hide();
        } else {
            if ( obj._isInBound ) obj._marker && obj._marker.addTo(this._map);
            else obj._el && obj._el.show().css("display", "inline-block");
        }
    },
    _shows: function(){
        this._inBounds.forEach(this._showSingle.bind(this));
        this._outBounds.forEach(this._showSingle.bind(this));
    },
    bindMap: function(map){
        var self = this;
        self._map = map;

        function refreshAll(){
            self._updateMapInfo();
            self._hideFilterd();
            self._calculateFiltered();
            self._renderFiltered();
            self._layouts();
            self._shows();
        }

        // binding events
        self._map.on('zoomend', refreshAll);
        self._map.on('dragend', refreshAll);
        self._map.on('resize', function(){ setTimeout(refreshAll, 400);    });

        refreshAll();
    },
    addObject: function(point, options){
        var self = this, lat, lng;
        if ( Array.isArray(point) ) {
            lat = point[0];
            lng = point[1];
        } else {
            lat = point.lat;
            lng = point.lng;
        }

        var obj = { lat: lat, lng: lng };

        // default renderer
        obj._outBoundRenderer = function(target, kilometers, metadata){
            return kilometers + " km";
        };

        if ( options ) {
            if ( options.outBoundRenderer && typeof options.outBoundRenderer == "function" ) {
                obj._outBoundRenderer = options.outBoundRenderer;
            }
            if ( options.inBoundRenderer && typeof options.inBoundRenderer == "function") {
                obj._inBoundRenderer = options.inBoundRenderer;
            }
            if ( options.metadata ) {
                obj._metadata = options.metadata;
            }
        }

        self._objects.push(obj);

        self._objKeyMap[lat + "-" + lng] = obj;

        if ( self._map ) {
            self._calculateFiltered();
            self._renderFiltered();
            self._layouts();
            self._shows();
        }
    },
    forceUpdate: function(){
        var self = this;
        if ( self._map ) {
            self._hideFilterd();
            self._calculateFiltered();
            self._shows();
        }
    },
    updateMetadata: function(point, metadata){
        var self = this,
            obj = self._objKeyMap[point[0] + "-" + point[1]],
            body;
        if ( obj ) {
            obj._metadata = metadata;

            if ( obj._kilometer ) {
                obj.hidden = false;
                body = obj._outBoundRenderer.call(self, obj, obj._kilometer, obj._metadata );
            } else {
                obj.hidden = true;
            }

            self._defaultLayouter(
                obj._el,
                obj._info,
                self._mapInfo.cornerInfo,
                body
            );

            if ( obj._marker && self._map ) self._map.removeLayer(obj._marker);
            obj._marker = obj._inBoundRenderer.call(self, obj, obj._kilometer, obj._metadata);

            self._showSingle(obj);
        }
    },
    hide: function(point){
        this._hideSingle( this._objKeyMap[point[0] + "-" + point[1]] );
    }
};

var windPanel = {
    _previousData: null,
    _currentDatestr: "",
    _ranges: [11.25, 33.75, 56.25, 78.75, 101.25, 123.75, 146.25, 168.75, 191.25, 213.75, 236.25, 258.75, 281.25, 303.75, 326.25, 348.75],
    _targets: ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N'],
    isChange: function(data, datestr){
        var self = this;
        return !self._previousData || self._previousData.WD != data.WD || self._previousData.WS != data.WS || self._currentDatestr != datestr;
    },
    applyData: function(data, datestr){
        var self = this;
        if(!self._previousData) self._previousData = {};
        self._previousData.WD = data.WD; self._previousData.WS = data.WS;
        self._currentDatestr = datestr;
    },
    getShort: function(wd){
        var value = parseFloat(wd || 0);
        var ranges = this._ranges.slice(0);
        ranges.push(value);
        ranges.sort(function(a,b) { return a - b;});
        return this._targets[ranges.indexOf(value)];
    },
    getNearestWind: function(windList, current, datestr){
        if ( windList.length ) {
            var isNearNow = nowDate.getTime() - current.getTime() <= 2 * oneHour,    // define "near" is in 2 hours.
                nearedValidWinds = windList.filter(function(item){ return typeof item.WD == "number" && typeof item.WS == "number"; }),
                foundWinds = nearedValidWinds.filter( function(item){ return item.datetime == datestr; } );
            if ( foundWinds.length ) {
                var foundWind = foundWinds[0];
                return { WD: foundWind.WD, WS: foundWind.WS, station: foundWind.station, lat: foundWind.lat, lon: foundWind.lon };
            } else if ( isNearNow && nearedValidWinds.length ) {
                var nearedWind = nearedValidWinds[0];
                return { WD: nearedWind.WD, WS: nearedWind.WS, station: nearedWind.station, lat: nearedWind.lat, lon: nearedWind.lon };
            }
        }
        return null;
    },
    setWindByTime: function(timestamp){
        var self = this,
            current = new Date(timestamp),
            nonExistText = "無風向資料";

        current.setTime( current.getTime() + twentyNightMins );

        var datestr = current.yymmddHH() + ":00:00";

        // foundWindList has sorted by datetime desc
        var data = self.getNearestWind(foundWindList, current, datestr),
            isExist = !!data;

        data = data || {};

        if(self.isChange(data, datestr)){

            var dirNumberJq = $("#windDirNumber"),
                dirShortJq = $("#windDirShort"),
                speedJq = $("#windSpeed"),
                dirArrowJq = $("#windDirArrow"),
                barbJq = $("#windBarb");
                windInfosJq = $("#wind-direction > *:not(:first)");

            windInfosJq.show();
            windPanel.setTooltip('本風向資訊來自離目前中心最近的 ' + data.station + ' &#10;位置在 ' + data.lat + ', ' + data.lon);

            dirNumberJq.text(isExist? data.WD : nonExistText);

            if ( isExist ){
                dirShortJq.text("(" + self.getShort(data.WD) + ")").show();
            } else dirShortJq.hide();

            speedJq.text(isExist? data.WS : nonExistText);

            if ( isExist ) {
                dirArrowJq.css(
                    { transform: 'rotate(' + (data.WD > 180? (data.WD - 180) : (data.WD + 180)) + 'deg)' }
                ).show();
            } else dirArrowJq.hide();

            if ( isExist ) {
                var currentIcon = L.WindBarb.icon({
                    deg: data.WD,
                    fillColor: "#9fcb50",
                    speed: data.WS,
                    pointRadius: 8,
                    barbHeight: 15,
                    strokeWidth: 2,
                    forceDir: true
                });

                barbJq.empty();
                barbJq.append(currentIcon.createIcon());
                barbJq.append(currentIcon.createShadow());
                barbJq.show();
            } else barbJq.hide();

            // tune layout
            var shortPosition = dirShortJq.position();
            dirArrowJq.css("left", shortPosition.left + dirShortJq.width() + 5);

            // apply current
            self.applyData(data, datestr);

            Object.keys(latLngWindsMap).forEach(function(key){
                var points = key.split('-').map(function(v){ return parseFloat(v); });

                mapSurrounObjectController.hide(points);

                var foundData = self.getNearestWind(latLngWindsMap[key], current, datestr);
                if ( foundData ) {
                    mapSurrounObjectController.updateMetadata([foundData.lat, foundData.lon], {
                        WD: foundData.WD,
                        WS: foundData.WS,
                        name: foundData.station
                    });
                }
            });
        }
    },
    setTooltip: function(str){
        var windDataInfoJq = $("#windDataInfo");
        if ( windDataInfoJq.get(0) ) {
            windDataInfoJq.attr('title', str);
        } else {
            $("#windDataInfoWrap").append('<i id="windDataInfo" class="info fa fa-info-circle" title="' + str + '" data-toggle="tooltip" data-placement="right"></i>');
            // Wind source information
            $('#wind-direction').tooltip({
                selector: "#windDataInfo",
                container: "#show-layer"
            });
        }
    }
};

var chartCompares = {
    _compares: [],
    _el: $("#chart-compares"),
    _itemMinHeight: 110,
    _itemMaxHeight: 213,
    _isShow: false,
    add: function(idx, name, data, points){
        var self = this;
        var exist = self._compares.filter( function(item){ return item.id == "chart-compare-" + idx } ).length != 0;
        if ( !exist ) {
            var id = "chart-compare-" + idx;
            var chartWrap = $('<div class="chart-compare-item"><div class="flot-chart"><div class="flot-chart-content" id="' + id + '"></div></div><h5><span>設備編號：' + name + '</span><button type="button" class="btn btn-xs btn-link chart-compare-remove">&lt;&nbsp;取消比較</button></h5></div>');

            self.show();

            self._el.append(chartWrap);

            var plot = $.plot( $("#" + id), [{
                label: 'pm25',
                data: data
            }], plotOptions);

            var markerSize = stationMarkerOptions.radius * 5;

            var marker = L.marker(points, {
                    icon: L.divIcon({
                        className: '',
                        html: '<div class="chart-compare-maplabel"><span>#' + name + '</span></div>',
                        iconSize: [markerSize, markerSize]
                    })
                })
                .on('mouseover', function(){ self.markerFocus(id); })
                .on('mouseout', function(){ self.markerBlur(id); })
                .addTo(mainMap);

            // hook remove
            chartWrap.find("button.chart-compare-remove").on('click', function(){ self.remove(id); });

            // hook the event that can be reconized.
            chartWrap
                .on('mouseover', function(){ self.markerFocus(id); })
                .on('mouseout', function(){ self.markerBlur(id); })

            self._compares.push({
                id: id,
                el: chartWrap,
                plot: plot,
                marker: marker
            });

            self.rearrange();
        }
    },
    remove: function(id){
        var self = this;
        var isRemoved = false;
        for (var idx = self._compares.length; idx--; ) {
            var item = self._compares[idx];
            if ( item.id == id ) {
                item.el.remove();
                mainMap.removeLayer(item.marker);
                self._compares.splice(idx, 1);
                isRemoved = true;
            }
        }

        isRemoved && self.rearrange();
    },
    show: function(){
        if (!this._isShow) {
            $("#map").css("width", "calc(100% - 360px)");
            $("#chart-compares").show();
            mainMap.invalidateSize();
            this._isShow = true;
        }
    },
    hide: function(){
        if (this._isShow) {
            $("#map").css("width", "100%");
            $("#chart-compares").hide();
            mainMap.invalidateSize();
            this._isShow = false;
        }
    },
    markerFocus: function(id){
        var self = this;
        var founds = self._compares.filter(function(item){ return item.id == id; });
        if ( founds.length ) {
            var item = founds[0];
            var marker = item.marker.getElement();
            var chart = item.el;
            $(marker).children().addClass('focus');
            $(chart).addClass('focus');
        }
    },
    markerBlur: function(id){
        var self = this;
        var founds = self._compares.filter(function(item){ return item.id == id; });
        if ( founds.length ) {
            var item = founds[0];
            var marker = item.marker.getElement();
            var chart = item.el;
            $(marker).children().removeClass('focus');
            $(chart).removeClass('focus');
        }
    },
    rearrange: function(){
        var self = this;
        var height = self._el.height();

        if ( self._compares.length ) {
            var unitHeight = height / self._compares.length;

            unitHeight = Math.min( unitHeight, self._itemMaxHeight );
            unitHeight = Math.max( unitHeight, self._itemMinHeight );

            var heightSum = self._compares
                .map(function(item){ return item.el.outerHeight(); })
                .reduce( function(a, b){ return a+b; }, 0 );

            self._compares.forEach(function(item){
                var innerHeight = unitHeight - 15 - 8;    // margin-bottom  // padding
                item.el.height(innerHeight);
                item.el.children(".flot-chart").height(innerHeight - 18);    // label outer height
            });
        } else self.hide();
    }
};

// Make first tick contains scores.
// minDateTime = minDateTime + unitStep;

var getTickIndex = function(stamp){
    return Math.abs( Math.ceil( ( stamp - minDateTime ) / unitStep ) );
};

var forEachTick = function(handler){
    for( var tick = minDateTime, idx = 0; tick < maxDateTime; tick += unitStep, idx++ ) {
        handler(tick, idx);
    }
};

/*************************/
/*  顯示絕對數值 Switcher
/*************************/
var showSwitcherEl;
function initSwitcher(){
    showSwitcherEl = document.querySelector('#valueShowSwitch');
    var showSwitcherInstance = new Switchery(showSwitcherEl, { size: 'small' });
    var onShowSwitcherChange = function(){
        var method = showSwitcherEl.checked? 'openTooltip' : 'closeTooltip';
        if(allStations && allStations.length){
            allStations.forEach(function(marker){ marker[method](); });
        }
    };
    showSwitcherEl.addEventListener('change', onShowSwitcherChange);
}

/*************************/
/*  顯示擴散效果 Switcher
/*************************/
var diffusionSwitcherEl;
var eventFromSwitcher = false;
var diffusionFlags = { v1: false, v2: true };
function initDiffusionSwitcher(){

    // init idwLayer
    idwLayer = L.idwLayer([], {
        gradient: colorPicker.getDiffusionGradient(),
        opacity: 0.35,
        cellSize: 11, //height and width of each cell, 25 by default
        exp: 3, //exponent used for weighting, 1 by default
        max: colorPicker.getMaxPatternValue() //maximum point values, 1.0 by default
    });

    function buttonStyleToggle(){
        var jqSelf = $(this);
        jqSelf.parents("#diffusionButtons").find("button").removeClass("btn-success").addClass("btn-default");
        jqSelf.removeClass("btn-default").addClass("btn-success");
        Object.keys(diffusionFlags).forEach(function(name){ diffusionFlags[name] = false; });
    }

    Object.keys(diffusionFlags)
        .forEach(function(name){
            var b = document.createElement("button");

            $(b).text(name)
                .addClass("btn btn-xs " + ( diffusionFlags[name] ? "btn-success" : "btn-default") )
                .click(
                    (function(n){
                        return function(){
                            // buttonToggle.call(this);
                            if ( !diffusionFlags[n] ) {
                                buttonStyleToggle.call(this);
                                diffusionFlags[n] = true;
                                eventFromSwitcher = true;
                                slider.noUiSlider.set( Number(slider.noUiSlider.get()) );
                            }
                        };
                    })(name)
                );

            $("#diffusionButtons").append(b);
        });

    // add close button
    var closeBtn = $('<button class="btn btn-xs btn-default">關閉</button>');
    closeBtn.click(function(){
        buttonStyleToggle.call(this);
        eventFromSwitcher = true;
        slider.noUiSlider.set( Number(slider.noUiSlider.get()) );
    })
    $("#diffusionButtons").append(closeBtn);
}

/*************************/
/*  滑軌
/*************************/
var slider;
function initSlider(){
    // init slider for use in global
    slider = document.getElementById('slider');
    var playjq = $("#play");
    var pausejq = $("#pause");
    var forwardjq = $("#stepForward");
    var backwardjq = $("#stepBackward");
    var playTimer = null;

    function forwardNextTick(){
        var current = Number(slider.noUiSlider.get());
        if ( current == maxDateTime ) return;
        var value = current + unitStep;
        if (value > maxDateTime) value = maxDateTime;
        slider.noUiSlider.set(value);
    }

    //播放空汙動畫
    function playAnimate(){
        if (Number(slider.noUiSlider.get()) == maxDateTime) {    // loop
            slider.noUiSlider.set(minDateTime);
        } else {
            forwardNextTick();
        }
    }

    function stampsToDateStr(stamps){
        var d = new Date( parseInt(stamps) );
        return d.yymmddHHmm();
    }

    function onSliderSetHandler(formateds, handle, stamps){

        var mapIdx = getTickIndex(stamps[0]);

        if( allStations && allStations.length ) {
            var frontArrange = [];
            var idwDataArray = [];
            allStations.forEach(function(marker){
                var position = marker.getLatLng(),
                    key = position.lat + "-" + position.lng,
                    // startTick = mapIdx,
                    circleGroup = latLngDiffusionMap[key][mapIdx],
                    score = latLngScoreTickMap[key][mapIdx],
                    scoreChanged = marker._currentScore != score,
                    picked = latLngPickedTickMap[key] <= mapIdx;

                // update tooltip by each marker if score has changed.
                if ( scoreChanged ) {
                    marker._currentScore = score;
                    // marker.setStyle({ fillColor: colorPicker.getColorByValue(score) })
                    marker.setStyle(picked ?
                        { fillColor: colorPicker.getColorByValue(score), radius: 10, color: 'teal', weight: 5, opacity: 0.7, fillOpacity: 1 } :
                        { fillColor: colorPicker.getColorByValue(score),
                            radius: stationMarkerOptions.radius, color: stationMarkerOptions.color,
                            weight: 2
                        });
                    if ( showSwitcherEl.checked ) marker.openTooltip();
                }

                if ( scoreChanged || eventFromSwitcher ) {
                    // if has changed and previous remove
                    if ( latLngDiffusionPreviousMap[key] ) {
                        latLngDiffusionPreviousMap[key].forEach(function(circle){
                            circle.remove();
                        });
                    }

                    if ( typeof score == "number" && circleGroup && diffusionFlags.v2 ) {
                        latLngDiffusionPreviousMap[key] = circleGroup;

                        frontArrange.push({
                            score: score,
                            group: circleGroup
                        });
                    }
                }

                if ( typeof score == "number" && diffusionFlags.v1 ) {
                    idwDataArray.push( [ position.lat, position.lng, score ] );
                }
            });

            if ( diffusionFlags.v1 ) {
                if ( eventFromSwitcher ) idwLayer.addTo(mainMap);
                idwLayer.setLatLngs( idwDataArray );
            } else if ( eventFromSwitcher ) idwLayer.remove();

            if ( diffusionFlags.v2 ) {
                // for layers ordering
                frontArrange.sort( function(a, b){
                    return a.score < b.score ? -1 : 1;
                } );
                frontArrange.forEach(function(item){
                    item.group.forEach(function(circle){ circle.addTo(mainMap); });
                });
            }

            // station markers should be on top.
            allStations.forEach(function(marker){ marker.bringToFront(); });
        }

        eventFromSwitcher && ( eventFromSwitcher = false );

        windPanel.setWindByTime(stamps[0]);
    }

    noUiSlider.create(slider, {
        animate: false,

        start: minDateTime,

        // 3 mins
        step: unitStep,
        connect: true,
        tooltips: {
            to: function ( value ) {
                return stampsToDateStr(value);
            }
        },
        range: {
            'min': minDateTime,
            'max': maxDateTime
        }
    });

    slider.noUiSlider.on('set', onSliderSetHandler);

    playjq.click(function(){
        playjq.hide();
        pausejq.show();
        if ( !playTimer ) playTimer = setInterval(playAnimate, animateStepTime);
        forwardjq.addClass("deny");
        backwardjq.addClass("deny");
    });

    pausejq.click(function(){
        if (playTimer) {
            clearInterval(playTimer);
            playTimer = null;
        }
        pausejq.hide();
        playjq.show();
        forwardjq.removeClass("deny");
        backwardjq.removeClass("deny");
    });

    forwardjq.click(function(){
        if ( $(this).hasClass("deny") ) return;
        forwardNextTick();
    });

    backwardjq.click(function(){
        if ( $(this).hasClass("deny") ) return;
        var current = Number(slider.noUiSlider.get()),
            value = current - unitStep;
        if ( current == minDateTime ) return;
        // handle less than unitstep case
        if ( current == maxDateTime ) {
            value = minDateTime + getTickIndex(value) * unitStep;
        }
        if ( value < minDateTime ) value = minDateTime;
        slider.noUiSlider.set(value);
    });
}

function initControlBtns(){
    var colorMobileWrap = $(".color-mobile-wrap"),
        colorSamples = $("#color-samples");    // #color-samples

    var windMobileWrap = $(".wind-mobile-wrap"),
        windWrap = $(".wind-wrap"); // .wind-wrap

    colorMobileWrap.on('click', function(){
        colorMobileWrap._isShowInfo ? colorMobileWrap.removeClass("onFocus") : colorMobileWrap.addClass("onFocus");
        colorMobileWrap._isShowInfo ? colorSamples.fadeOut() : colorSamples.fadeIn();
        colorMobileWrap._isShowInfo = !colorMobileWrap._isShowInfo;
    });

    windMobileWrap.on('click', function(){
        windMobileWrap._isShowInfo ? windMobileWrap.removeClass("onFocus") : windMobileWrap.addClass("onFocus");
        windMobileWrap._isShowInfo ? windWrap.fadeOut() : windWrap.fadeIn();
        windMobileWrap._isShowInfo = !windMobileWrap._isShowInfo;
    });
}

L.mapbox.accessToken = 'pk.eyJ1IjoieWlrYWkiLCJhIjoiY2lvYTJ4b2pkMDM4dHZna3FqcGFjaHFnZiJ9.5ryPOdNr9TafMBk4AQcI6w';
mainMap = L.mapbox.map('map', 'mapbox.emerald', {
    center: initCenterPoints,
    zoom: initZoomLevel,
    closePopupOnClick: false
});

var dataFetchPromises = [];

// get all stations in range of start and end.
dataFetchPromises.push(
    Promise.resolve(
        $.getJSON(API_URLS.epa_station_rawdata + '?' + encodeParamPairs({
            fields: "wind_direct,wind_speed",
            start_time: shiftBackDate.yymmddHHmm(),
            end_time: shiftForwardDate.yymmddHHmm(),
            min_lat: parseFloat(passParams.start_lat) - latitudeDiffIn25km,
            max_lat: parseFloat(passParams.end_lat) + latitudeDiffIn25km,
            min_lon: parseFloat(passParams.start_lon) - longitudeDiffIn25km,
            max_lon: parseFloat(passParams.end_lon) + longitudeDiffIn25km
        }))
    )
    .then(function(result){

        // generate short name
        var shortNameRe = new RegExp("^.*-(.*)\\[.*$");

        result.data.forEach(function(item){
            var matches;
            if ( item.name && ( matches = item.name.match(shortNameRe) ) ) {
                item.short_name = matches[1];
            }
            item.WS = item.wind_speed;
            item.WD = item.wind_direct;
            item.datetime = item.time;
            item.station = item.short_name || item.name;
        });

        latLngWindsMap = arrayToObjectWithKey(
            result.data,
            function(item){
                if ( item['lat'] && item['lon'] ) return item['lat'] + "-" + item['lon'];
            },
            true
        );

        // sort all
        Object.keys(latLngWindsMap).forEach(function(key){
            // sort by datetime desc
            latLngWindsMap[key].sort(function(obj1, obj2){
                return (obj1.datetime > obj2.datetime) ? -1 : 1;
            });
        });

        var bounds = L.latLngBounds(
            [ parseFloat(passParams.end_lat), parseFloat(passParams.end_lon) ],
              [ parseFloat(passParams.start_lat), parseFloat(passParams.start_lon) ]
        );
        var centerPoints = bounds.getCenter();

        // distanceMeasure
        var measuredList = [];
        Object.keys(latLngWindsMap).map(function(key, kindex){
            var points = key.split('-').map(function(v){ return parseFloat(v); });

            measuredList.push({
                key: key,
                kilometers: distanceMeasure(points[0], points[1], centerPoints.lat, centerPoints.lng)
            });

            mapSurrounObjectController.addObject(points, {
                outBoundRenderer: function(target, kilometers, metadata){
                    if ( metadata.WD ) {

                        var wrap = $('<div class="wind-object-wrap"></div>');

                        var header = $('<div class="wind-object-header"></div>');

                        var center = this._mapInfo.center;

                        header.append('<img width="24" height="24" src="' + $("#windIconPreload").attr("src") + '"/> ' + metadata.name);

                        wrap.append(header);

                        wrap.append('<p>距離: ' + kilometers + ' km <i class="info fa fa-info-circle" title="此為' + metadata.name + '距離此圖中心（latitude：' + fixedFloat(center[0], 4) + ' , longitude：' + fixedFloat(center[1], 4) + '）之距離" data-toggle="tooltip" data-placement="right"></i></p>');
                        wrap.append("<p>風速: " + metadata.WS + "</p>");
                        wrap.append('<p>角度: <span class="wind-object-arrow" style="transform: rotate(' + (metadata.WD > 180? (metadata.WD - 180) : (metadata.WD + 180)) + 'deg);">↑<span></p>');

                        // Wind source information
                        wrap.tooltip({
                            selector: "[data-toggle=tooltip]",
                            container: "#show-layer"
                        });

                        target.hidden = false;

                        // mobile wrap
                        var mobileWrap = $('<div class="wind-object-mobile-wrap"></div>');
                        var tinyName = metadata.name.split("測站")[0];
                        mobileWrap.append('<span class="wind-object-mobile-text">' + tinyName + '</span><span class="wind-object-mobile-space"></span><span class="wind-object-mobile-arrow" style="transform: rotate(' + (metadata.WD > 180? (metadata.WD - 180) : (metadata.WD + 180)) + 'deg);">↑</span>');
                        mobileWrap.on('click', function(){
                            mobileWrap._isShowInfo ? mobileWrap.removeClass("onFocus") : mobileWrap.addClass("onFocus");
                            mobileWrap._isShowInfo ? wrap.fadeOut() : wrap.fadeIn();
                            mobileWrap._isShowInfo = !mobileWrap._isShowInfo;
                        });

                        if ( target._info && target._info.inverse == 1 ) {
                            // on right
                            mobileWrap.addClass("toRight");
                        }

                        if ( target._info && target._info.increment ) {
                            return [wrap, mobileWrap];
                        } else {
                            return [mobileWrap, wrap];
                        }
                    } else {
                        target.hidden = true;
                    }
                },
                inBoundRenderer: function(target, kilometers, metadata){
                    if ( metadata.WD ) {
                        target.hidden = false;

                        return L.marker([target.lat, target.lng], {
                                icon: L.divIcon({
                                    className: 'wind-icon-wrap',
                                    html: '<div class="wind-icon-inner" style="transform: rotate(' + (metadata.WD > 180? (metadata.WD - 180) : (metadata.WD + 180)) + 'deg);">↑</div>',
                                    iconSize: [40, 40]
                                })
                            })
                            .bindPopup( (function(latLng, n, url, k, wd, ws){
                                return L.popup({ maxWidth: 500, autoClose: false })
                                    .setLatLng(latLng)
                                    .setContent('<div class="wind-object-wrap wind-object-inpopup"><div class="wind-object-header"><img width="24" height="24" src="' + url + '"/> ' + n + '</div><p>距離: ' + k + ' km</p><p>風速: ' + ws + '</p><p>角度: <span class="wind-object-arrow" style="transform: rotate(' + (wd > 180? (wd - 180) : (wd + 180)) + 'deg);">↑<span></p></div>');
                            })([target.lat, target.lng], metadata.name, $("#windIconPreload").attr("src"), kilometers, metadata.WD, metadata.WS) );
                    } else {
                        target.hidden = true;
                    }
                },
                metadata: {}
            });
        });

        measuredList.sort( function(a, b){ return a.kilometers - b.kilometers; } );

        if ( measuredList.length ) {
            foundWindList = latLngWindsMap[measuredList[0].key].slice(0);

            if ( foundWindList.length ) {
                windPanel.setWindByTime(minDateTime);
            }
        }
    })
    .catch( function(err){ console.error(err); } )
);

// To fetch pm2.5 data and resample to 3min
var requestRawdataParam = {
    fields: "pm2_5",
    resample: "1min",
    min_lat: passParams.min_lat,
    max_lat: passParams.end_lat,
    min_lon: passParams.start_lon,
    max_lon: passParams.end_lon,
    start_time: passParams.start,
    end_time: passParams.end
};

// get raw data by input parameters.
var event = null
dataFetchPromises.push(
    Promise.resolve($.getJSON(`/api/v1/event/data/${passParams.event_id}`))
        .then( function(res){
            event = res
            event.start = new Date(event.start)
            event.end = new Date(event.end)
            event.nodes.forEach(function(node){ node.time = new Date(node.time) })
        } )
        .catch( function(err){
            console.error(err);
        } )
)

var fetchData = function(project) {
    return Promise.resolve($.getJSON(`/api/v1/data/${project}/pm2_5/${requestRawdataParam.start_time}/${requestRawdataParam.end_time}/0?deviceFields=lon,lat,name`))
        .then( function(res){
            // transform
            var data = []
            res.forEach(function(d) {
                d.pm2_5.forEach(function(pm25Data) {
                    data.push({
                        device_id: d._id,
                        lat: d.lat,
                        lon: d.lon,
                        name: d.name,
                        score: pm25Data.value,
                        datetime: new Date(pm25Data.time),
                        pm2_5: pm25Data.value,
                        time: new Date(pm25Data.time),
                    })
                })
            })

            var latLngMap = arrayToObjectWithKey(
                data,
                function(item){
                    if ( item['lat'] && item['lon'] ) return item['lat'] + "-" + item['lon'];
                },
                true
            );

            var deviceIdKeyMap = {}
            res.forEach(function(item) {
                if ( item['lat'] && item['lon'] ) deviceIdKeyMap[item._id] = item['lat'] + "-" + item['lon'];
            })

            var latLngChartDataMap = {};

            event.nodes.forEach(function(node){
                var key = deviceIdKeyMap[node.device]
                latLngPickedTickMap[key] = getTickIndex(node.time);
            })

            Object.keys(latLngMap).forEach(function(key){
                var points = key.split('-').map(function(v){ return parseFloat(v); });

                if ( !latLngScoreTickMap[key] ) latLngScoreTickMap[key] = [];
                if ( !latLngDiffusionMap[key] ) latLngDiffusionMap[key] = [];
                if ( !latLngChartDataMap[key] ) latLngChartDataMap[key] = [];

                latLngMap[key].forEach(function(item){
                    // item.datetime
                    // item.score
                    var datastamp = parseDateString(item.datetime).getTime();
                    var idx = getTickIndex(datastamp);

                    latLngScoreTickMap[key][idx] = item.score;

                    var diffusionCircles = [];
                    if ( typeof item.score == "number" ) {
                        // do not diffuse too much
                        var mutedStep = diffusionDefaultStep;
                        var stageScore = Math.min( colorPicker.getMaxPatternValue() + diffusionDefaultStep, item.score );
                        if ( diffusionDefaultStep * diffusionMaxCircles < stageScore ) {
                            mutedStep = stageScore / diffusionMaxCircles;
                        }
                        while( stageScore > 0 && diffusionMaxCircles > diffusionCircles.length ) {
                            diffusionCircles.push(
                                L.circleMarker( points, {
                                    radius: ( diffusionCircles.length + 1 ) * diffusionRadiusPixel,
                                    fillColor: colorPicker.getColorByValue(stageScore),
                                    fillOpacity: 0.3,
                                    stroke: false
                                })
                            );
                            stageScore -= mutedStep;
                        }
                    }
                    latLngDiffusionMap[key][idx] = diffusionCircles.reverse();
                });

                forEachTick(function(stamp, idx){
                    latLngChartDataMap[key].push( [ stamp, latLngScoreTickMap[key][idx] || null ] );
                });
                var value = null
                for(var i=0; i<latLngScoreTickMap[key].length; i++) {
                    if (latLngScoreTickMap[key][i]) {
                        value = latLngScoreTickMap[key][i]
                    } else {
                        latLngScoreTickMap[key][i] = value
                    }
                }
            });

            var closePopup = function(o) { o.target.closePopup() }

            allStations = Object.keys(latLngMap).map(function(key, kindex){
                var points = key.split('-').map(function(v){ return parseFloat(v); });
                return L.circleMarker(L.latLng(points[0], points[1]), stationMarkerOptions)
                    .bindPopup( (function(latLng, idx){
                        var innerItem = latLngMap[ latLng.join('-') ];
                        var deviceName = innerItem.length ? innerItem[0].name : "";
                        return L.popup({ maxWidth: 500, autoClose: false })
                            .setLatLng(latLng)
                            .setContent('<div class="flot-chart"><div class="flot-chart-content" id="flot-chart-' + idx + '"></div></div><h4><span>設備編號：' + deviceName + '</span><button type="button" class="btn btn-xs btn-link flot-chart-add">加入比較&nbsp;&gt;</button></h4>');
                    })(points, kindex) )
                    .bindTooltip(
                        function(o){
                            return typeof o._currentScore != "number" ? "N/A" : o._currentScore.toString();
                        },
                        {offset: L.point(8, 0), permanent: true, direction: 'right'}
                    )
                    .on('popupopen', (function(latLng, idx, data){
                        var innerItem = latLngMap[ latLng.join('-') ];
                        var deviceName = innerItem.length ? innerItem[0].name : "";
                        return function(){
                            var self = this;
                            var chartBody = $("#flot-chart-" + idx);
                            data = data.filter(function(d) { return !!d[1] })
                            $.plot( chartBody, [{
                                label: 'pm25',
                                data: data
                            }], plotOptions);

                            chartBody.parent().siblings()
                                .find("button.flot-chart-add")
                                .on("click", function(){
                                    chartCompares.add(idx, deviceName, data, latLng);
                                    self.closePopup();
                                });
                            this.on('click', closePopup)
                        };
                    })(points, kindex, latLngChartDataMap[key] ) )
                    .on('popupclose', (function(idx){
                        return function(){
                            var chartBody = $("#flot-chart-" + idx);
                            chartBody.empty();
                            chartBody.parent().siblings().find("button.flot-chart-add").off();
                            this.off('click', closePopup)
                        };
                    })(kindex) )
                    .on('mouseover', function(o){
                        if ( o.target && !showSwitcherEl.checked ) o.target.openTooltip();
                    })
                    .on('mouseout', function(o){
                        if ( o.target && !showSwitcherEl.checked ) o.target.closeTooltip();
                    })
                    .addTo(mainMap);
            });

            allStations.forEach(function(marker){ marker.closeTooltip(); });

        } )
        .catch( function(err){
            console.error(err);
        } )
};

// finally is not work in android webview, so change to then
Promise.all(dataFetchPromises).then(function() {
    Promise.all([fetchData(event.project)]).then(function () {
        slider.noUiSlider.set(minDateTime);
        loadingLayer.hide();
    })
});

// wait for the map rendered, otherwise would cause error.
setTimeout(function(){
    mainMap.fitBounds([
      [ parseFloat(passParams.end_lat), parseFloat(passParams.end_lon) ],
      [ parseFloat(passParams.start_lat), parseFloat(passParams.start_lon) ]
    ]);
    L.control.scale({
        maxWidth: 150,
        position: 'bottomright'
    }).addTo(mainMap);

    mapSurrounObjectController.bindMap(mainMap);
}, 1000);

initSlider();
initSwitcher();
initDiffusionSwitcher();
initControlBtns();
colorPicker.renderColorSamples(document.querySelector("#color-samples .color-list"));

