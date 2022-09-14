var aspect_ratio;
var map;
var geocoder;
var lng;
var lat;

// Function referenced in picture_view.html
// Switches between showing the map of the image location (if present)
// and the picture itself
function toggleMapFunction() {
	if( $('#map-container').is(':hidden') ) {
		$("#map-container").css("display", "initial");
		$("#img-container").css("display", "none");
		$('#map-toggle').html("Hide Map");
	} else {
		$("#map-container").css("display", "none");
		$("#img-container").css("display", "initial");
		$('#map-toggle').html("Show Map");
	}
}

$(document).ready(function(){
	if ($('#map-container').attr('data-show-location') == "true") {
		// Displays a map in the picture view showing the image location of a picture
		// The div containing the map is resized to be just as large as the picture
		aspect_ratio = $('#picture_image').height() / $('#picture_image').width();
		$('#comment_column').height($('#center-column').width() * aspect_ratio);
		$('#map-container').append("<div id='map' style='width: " + $('#center-column').width() + "px; height: " + $('#center-column').width() * aspect_ratio + "px;'>");
		
		lng = $('#map-toggle').attr('data-longitude');
		lat = $('#map-toggle').attr('data-latitude');
		mapboxgl.accessToken = 'pk.eyJ1IjoiMjQ2OTgxMWIiLCJhIjoiY2ttdWtuZ2RjMHZ5MzJ3bXc3b3J4N29ieSJ9.rR1dAX-utT26r3bIQRbcjA';
		map = new mapboxgl.Map({
			container: 'map', // container ID
			style: 'mapbox://styles/mapbox/streets-v11', // style URL
			center: [lng, lat], // starting position [lng, lat]
			zoom: 9 // starting zoom
		});
		$("#map-container").css("display", "none");
		var picture_location_marker = new mapboxgl.Marker()
			.setLngLat([lng, lat])
			.addTo(map);
	}
	if ($('#map-container').attr('data-set-location') == "true") {
		// Displays a map when uploading a picture to set the image location
		$('#map-checkbox').click(function() {
			if ( $('#map-checkbox').is(':checked') ) {
				$("#map-container").css("display", "initial");
			} else {
				$("#map-container").css("display", "none");
			}
		});
		$('#map-container').append("<div id='map' style='width: " + 400 + "px; height: " + 300 + "px;'>");
		mapboxgl.accessToken = 'pk.eyJ1IjoiMjQ2OTgxMWIiLCJhIjoiY2ttdWtuZ2RjMHZ5MzJ3bXc3b3J4N29ieSJ9.rR1dAX-utT26r3bIQRbcjA';
		map = new mapboxgl.Map({
			container: 'map', // container ID
			style: 'mapbox://styles/mapbox/streets-v11', // style URL
			center: [0, 0], // starting position [lng, lat]
			zoom: 0 // starting zoom
		});
		geocoder = new MapboxGeocoder({
			accessToken: mapboxgl.accessToken,
			marker: {color: 'orange'},
			mapboxgl: mapboxgl
		});
		map.addControl(geocoder);
		geocoder.on('result', function() {
			try {
				lng_lat = geocoder.mapMarker.getLngLat();
				lng = lng_lat.lng;
				lat = lng_lat.lat;
			} catch(err) {
				lng = "";
				lat = "";
			} finally {
				$("#lng-input").attr('value', lng);
				$("#lat-input").attr('value', lat);
			}
		});
		$("#map-container").css("display", "none");
	}
});