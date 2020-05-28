

(function(scope){

	var _replaceAndLabel = function(v){
		var replaced = v.replace("T", " ");
		var splits = replaced.split(' ');
		// just only HH:mm
		var hourMin = splits[1].split(':').slice(0, 2).join(':');
		return '<span class="label label-default">' + splits[0] + '</span>&nbsp;&nbsp;&nbsp;' + hourMin;
	};

	var _levelToConfigs = {
		"高": {
			case: 'danger',
			text: 'IoT 發生相對異常之次數超過 15 次，並且持續超過 15 分鐘'
		},
		"中": {
			case: 'warning',
			text: 'IoT 發生相對異常之次數超過 10 次，並且持續超過 10 分鐘'
		},
		"低": {
			case: 'default',
			text: 'IoT 發生相對異常之次數超過 5 次，並且持續超過 5 分鐘'
		}
	};

	function EventTable(options){
		var self = this;

		appendTo = options.appendTo || "";
		defaultSearch = options.defaultSearch || [];

		if ( !appendTo ) throw new Error("EventTable: 'appendTo' parameter is required.");

		$(appendTo).append('<div class="table-responsive"><div class="loading-layer"><div class="loader"></div></div><table class="table table-striped table-bordered table-hover dataTables-example"></table></div>');

		self._el = $(appendTo).children(".table-responsive");
		self._loader = self._el.children(".loading-layer");

		// search text
		self._searchText = Array.isArray(defaultSearch) ? defaultSearch.slice(0) : [defaultSearch.toString()];

		self._tableWrap = self._el.find('.dataTables-example').DataTable({
			data: [],
			columns: [
				{ data: 7, title: "污染事件編號", orderable: false, width: 70, className: 'dt-center',
					render: function ( data, type, row, meta ) {
						return data || "";
					}
				},
				{ data: 2, title: "污染等級", orderable: false, width: 65, className: 'dt-center',
					render: function ( data, type, row, meta ) {
						var strLevel = getRiskLevel(data, row[5]);
						var configs = _levelToConfigs[strLevel];
						if (configs) return '<span class="label label-' + configs.case + '">' + strLevel + '污染</span>&nbsp;&nbsp;<i class="info fa fa-exclamation-circle" title="' + configs.text + '" data-toggle="tooltip" data-placement="right"></i>';
						else return '';
					}
				},
				{ data: 8, title: "污染分數", className: 'dt-center', width: 80 },
				{ data: 3, title: "開始時間", className: 'dt-center', render: _replaceAndLabel },
				{ data: 4, title: "結束時間", className: 'dt-center', render: _replaceAndLabel },
				{ data: 5, title: "歷時(分)", className: 'dt-center', width: 60 },
				{ data: 0, title: "區域", className: 'dt-center', width: 100 },
				{ data: 1, title: "關聯 IoT 數量", className: 'dt-center', width: 80,
					render: function ( data, type, row, meta ) {
						var names = data.map(function(item){return item.device_id + " (" + item.name + ")";});
						return '<span>' + data.length + '</span>&nbsp;&nbsp;' + '<i class="info fa fa-info-circle" title="' + names.join("&#10;") + '" data-toggle="tooltip" data-placement="right"></i>';
					}
				},
				// For CSV download
				{ data: 1, title: "關聯 IoT 設備", className: 'dt-center', visible: false,
					render: function ( data, type, row, meta ) {
						var names = data.map(function(item){return item.device_id + "(" + item.name + ")";});
						return names.join("\n");
					}
				},
				// For CSV download
				{ data: 6, title: "動畫網址參數", className: 'dt-center', visible: false },
				{ data: 6, title: "", orderable: false, searchable: false, className: 'dt-center',
					render: function ( data, type, row, meta ) {
						//TODO: Need to pass CAMEO_SUB_PATH here
						return '<a href="/web/iot/history/animation?'+ data +'" class="btn btn-sm btn-primary" target="_blank">播放</a>';
					}
				}
			],
			pageLength: 10,
			responsive: true,
			order: [[3, 'desc']],
			drawCallback: function(){
				self._el.find('.dataTables-example').tooltip({
					selector: "[data-toggle=tooltip]",
					container: ".ibox"
				});
			}
		});

		self._searchFn = function( settings, data, dataIndex ) {
			if ( self._tableWrap && self._searchText.length && self._tableWrap.table().container() == settings.nTableWrapper ) {
				var reducedStr = data[1];
				if ( reducedStr && ( reducedStr = reducedStr.trim() ) && self._searchText.indexOf(reducedStr) != -1 ) return true;
				else return false;
			}
			return true;
		};

		$.fn.dataTable.ext.search.push(self._searchFn);
	}

	EventTable.prototype.addSearch = function(word){
		var self = this;
		self._searchText.push(word);
		self._searchText = self._searchText.unique();
		self._tableWrap && self._tableWrap.draw();
	};	

	EventTable.prototype.removeSearch = function(word){
		var self = this, 
			idx = self._searchText.indexOf(word);
		if ( idx != -1 ) {
			self._searchText.splice(idx, 1);
			self._tableWrap && self._tableWrap.draw();
		}
	};

	EventTable.prototype.loadData = function(area, start, end, level){
		var self = this,
			passParams = {};

		if (area) passParams.area = area;
		if (start) passParams.start_time = start;
		if (end) passParams.end_time = end;

		// loading state
		self._loader.show();
		self._el.addClass("loading");

		Promise.resolve($.getJSON(API_URLS.iot_events + '?' + encodeParamPairs(passParams)))
			.then(function(res){
				var resolveDataSet = [],
					areaMeta = areaMetaMap[area],
					areaBounds = areaMeta ? areaMeta.bounds : [];

				res.data && res.data.forEach(function(item){
					
					var strParameter = "";
					if ( areaBounds.length ) {
						strParameter = encodeParamPairs({
							start: item.start_time,
							end: item.end_time,
							start_lon: areaBounds[0],
							end_lon: areaBounds[1],
							start_lat: areaBounds[2],
							end_lat: areaBounds[3]
						});
					}

					resolveDataSet.push(
						[ item.area, item.device_list, item.event_count,
						item.start_time, item.end_time, item.duration, strParameter, item.uid, item.score ]
					);
				});

				// renew
				self._tableWrap.clear();
				self._tableWrap.rows.add(resolveDataSet);
				if ( level ) {
					self._searchText.push(level);
					self._searchText = self._searchText.unique();
				}
				self._tableWrap.draw();
				
				// back to normal state
				self._loader.hide();
				self._el.removeClass("loading");
			})
			.catch( function(err){
				console.error(err);
		    });
	};

	EventTable.prototype.destroy = function(){
		var self = this,
			idx = $.fn.dataTable.ext.search.indexOf(self._searchFn);
		if ( idx != -1 ) $.fn.dataTable.ext.search.splice(idx, 1);
	};
	
	scope.EventTable = EventTable;
})(window);
