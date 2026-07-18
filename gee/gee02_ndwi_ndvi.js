/**
 * SWAI — Script 2: Sentinel-2 composite, NDWI & NDVI
 *
 * Builds a cloud-masked annual median composite for 2023, computes:
 *   - NDWI = (B3 - B8) / (B3 + B8)   surface water index
 *   - NDVI = (B8 - B4) / (B8 + B4)   vegetation index
 * and samples the mean of each within a 1 km buffer of every village.
 *
 * NDWI is the N indicator in the final model. NDVI is retained for context
 * but is not currently scored.
 *
 * LIMITATION: an annual median composite averages monsoon and dry season,
 * smoothing out seasonal water bodies. A dry-season-only composite would
 * better represent water available in April. See README future work.
 *
 * Exports -> Google Drive:
 *   village_ndwi.csv  [village_id, NDWI, NDVI]
 */

var villages = ee.FeatureCollection(
  'projects/my-project-earth-engine-502320/assets/sindh_villages');
var sindh = villages.geometry().bounds();
Map.centerObject(villages, 7);

// --- Sentinel-2 surface reflectance, low cloud only ---
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(sindh)
  .filterDate('2023-01-01', '2024-01-01')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

// --- Cloud mask via Scene Classification band ---
// drops: 3 = cloud shadow, 8 = cloud medium prob,
//        9 = cloud high prob, 10 = cirrus
function maskClouds(img) {
  var scl = img.select('SCL');
  var clear = scl.neq(3).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10));
  return img.updateMask(clear);
}

var composite = s2.map(maskClouds).median().clip(sindh);

// --- Indices ---
var ndwi = composite.normalizedDifference(['B3', 'B8']).rename('NDWI');
var ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI');

// --- Visual check: the Indus and canal network should light up in NDWI ---
Map.addLayer(composite, {bands: ['B4','B3','B2'], min: 0, max: 3000}, 'True colour');
Map.addLayer(ndwi, {min: -0.3, max: 0.5, palette: ['white','blue']}, 'NDWI (water)');
Map.addLayer(ndvi, {min: 0, max: 0.8, palette: ['white','green']}, 'NDVI (vegetation)');
Map.addLayer(villages, {color: 'red'}, 'Villages');

// --- Sample mean NDWI/NDVI within 1 km of each village ---
// The buffer represents "water near the village", i.e. accessibility rather
// than water at the exact point. Buffer radius is a modelling choice.
var buffered = villages.map(function(f) { return f.buffer(1000); });

var sampled = ndwi.addBands(ndvi).reduceRegions({
  collection: buffered,
  reducer: ee.Reducer.mean(),
  scale: 20
});

Export.table.toDrive({
  collection: sampled,
  description: 'village_ndwi',
  fileFormat: 'CSV',
  selectors: ['village_id', 'NDWI', 'NDVI']
});