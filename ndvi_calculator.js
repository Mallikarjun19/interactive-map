// Load the Google Earth Engine API
var ee = require('google-earth-engine');

// Initialize the Earth Engine API
ee.initialize();

// Function to calculate the NDVI value
function calculateNdvi(polygonCoords, callback) {
  // Create a new Earth Engine geometry from the polygon coordinates
  var geometry = ee.Geometry.Polygon(polygonCoords.map(function (coord) {
    return [coord.lng, coord.lat];
  }));

  // Load the Sentinel-2 satellite imagery data
  var sentinel2 = ee.ImageCollection('COPERNICUS/S2')
    .filterDate('2020-01-01', '2020-12-31')
    .filterBounds(geometry);

  // Calculate the NDVI value using the NIR and Red bands
  var ndvi = sentinel2.map(function (image) {
    var nir = image.select('B8'); // NIR band
    var red = image.select('B4'); // Red band
    return nir.subtract(red).divide(nir.add(red)).rename('NDVI');
  });

  // Calculate the mean NDVI value for the polygon
  var meanNdvi = ndvi.mean().clip(geometry).reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: geometry,
    scale: 10,
    maxPixels: 1e9
  });

  // Get the mean NDVI value as a number
  meanNdvi.evaluate(function (result) {
    var ndviValue = result.NDVI;

    // Return the NDVI value via callback
    callback(ndviValue);
  });
}

// Export the calculateNdvi function
export { calculateNdvi };
