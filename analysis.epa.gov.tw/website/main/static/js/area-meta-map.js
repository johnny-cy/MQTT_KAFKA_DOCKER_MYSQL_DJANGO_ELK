
/*
 * "Area" as key and mapping to the object of properties.
 *   bounds: [min_lon, max_lon, min_lat, max_lat]
 *   centerPoints: [ lat, lon ]		// Used in circle view
 *   zoomLevel: Number				// Used in circle view
 *   squareRadius: Number			// Used in circle view
 *   showText: String				// Used in circle view
 */

var areaMetaMap = {
	"觀音": {
		bounds: [121.1, 121.145, 25.04, 25.07],
		centerPoints: [25.0534222,121.1252922],
		zoomLevel: 14,
		squareRadius: 85,
		showText: "觀音工業區"
	},
	"鶯歌": {
		bounds: [121.324, 121.362, 24.945, 24.98],
		centerPoints: [24.9615336,121.3448217],
		zoomLevel: 14,
		squareRadius: 95,
		showText: "鶯歌工業區"
	},
	"大林蒲": {
		bounds: [120.3348, 120.3686, 22.5053, 22.5301],
		centerPoints: [22.5195552,120.3486075],
		zoomLevel: 14,
		squareRadius: 70,
		showText: "大林蒲工業區"
	},
	"台中港": {
		bounds: [120.5024, 120.5432, 24.1748, 24.2863],
		centerPoints: [24.22732919353378, 120.52395701408388],
		zoomLevel: 13,
		squareRadius: 140
	},
	"台中工業區": {
		bounds: [120.5742, 120.6305, 24.1331, 24.1932],
		centerPoints: [24.163153535405236, 120.60234999999999],
		zoomLevel: 13,
		squareRadius: 80
	},
	"大甲幼獅工業區": {
		bounds: [120.6124, 120.7052, 24.3663, 24.4214],
		centerPoints: [24.393853003716966, 120.6588],
		zoomLevel: 13,
		squareRadius: 80
	},
	"后里豐原": {
		bounds: [120.6517, 120.7889, 24.2432, 24.3498],
		centerPoints: [24.296649327733626, 120.72034835815431],
		zoomLevel: 13,
		squareRadius: 80
	}
};


