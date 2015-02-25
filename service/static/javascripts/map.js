window.onload = function() {
  if ((indexData) &&
    (indexData.geometry) &&
    (indexData.geometry.coordinates && indexData.geometry.coordinates.length > 0)) {
    //Define coordinate system using PROJ4 standards
    var bng = new L.Proj.CRS('EPSG:27700',
      '+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000' +
      ' +ellps=airy +datum=OSGB36 +units=m +no_defs',
      {
        resolutions: [2500, 1000, 500, 200, 100, 50, 25, 10, 5, 2.5, 1],
        bounds: L.bounds([1300000,0],[700000,0])
      }
    );

    /*
    var latlon = new L.Proj.CRS('EPSG:3857',
      '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6378137' +
      ' +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
    );
    */

    // var latlon = new L.Proj.CRS('EPSG:3857', proj4.defs('EPSG:3857'));

    proj4.defs("urn:ogc:def:crs:EPSG:27700", "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +datum=OSGB36 +units=m +no_defs");
    //proj4.defs('EPSG:3857');

    // set up control and options
    options = {
      // crs: latlon,
      continuousWorld: true,
      worldCopyJump: false,
      minZoom: 15,
      maxZoom: 19,

      // controls
      dragging: false,
      touchZoom: false,
      doubleClickZoom: false,
      scrollWheelZoom: false,
      boxZoom: false,
      keyboard: false,
      tap: false,
      zoomControl: true,
      attributionControl: false
    };

    // set up the map
    var map = new L.Map('map', options);

    // create the tile layer with correct attribution
    var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var osm = new L.TileLayer(osmUrl);
    map.addLayer(osm);

    //Add a scale control to the map
    L.control.scale().addTo(map);

  /*
    //Extent style
    var extentStyle = {
      color: 'red',
      fillOpacity: 0.0,
      opacity: 1
    };
  */

    //Index stlye
    var indexStyle = {
      fillcolor: 'blue',
      fillOpacity: 0.5,
      opacity: 0
    };

  /*
    //Create the extent layer
    var extentGeoJson = L.Proj.geoJson(extentData, {
      style: extentStyle
    });
  */

    //Create the index layer
    var indexGeoJson = L.Proj.geoJson(indexData, {
      style: indexStyle
    });

    //extentGeoJson.addTo(map);
    indexGeoJson.addTo(map);

    //Center map view on geojson polygon
    var bounds = indexGeoJson.getBounds();
    var center = bounds.getCenter();

  /*
    markerOptions = {
      clickable: false,
      draggable: false,
      keyboard: false,
      riseOnHover: false
    };

    L.marker(center, markerOptions).addTo(map);
  */

    //map.setView(center, 18);
    map.fitBounds(bounds, {maxZoom: 18, animate: false});
  } else {
    document.getElementById('map').innerText = 'No map information available';
  }
};
