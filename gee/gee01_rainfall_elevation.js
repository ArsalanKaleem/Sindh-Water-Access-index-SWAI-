/**
 * SWAI — Script 1: Annual rainfall + elevation
 *
 * Produces two indicators:
 *   - rainfall_mm  : mean annual precipitation, CHIRPS daily 2020-2024 (~5.5 km)
 *   - elevation_m  : SRTM 1 Arc-Second (30 m)
 *
 * NOTE: annual rainfall is NOT used as the W indicator in the final model —
 * it inverts the district ranking (see README). It is retained because
 * figures.py compares it against dry-season rainfall (fig3_seasonality.png).
 *
 * Exports -> Google Drive:
 *   village_rainfall_v2.csv   [village_id, rainfall_mm]
 *   village_elevation_v2.csv  [village_id, elevation_m]
 *
 * Replace the asset path below with your own uploaded villages asset.
 */

var villages = ee.FeatureCollection(
  'projects/my-project-earth-engine-502320/assets/sindh_villages');
Map.centerObject(villages, 7);

// --- Rainfall: CHIRPS daily, summed over 5 years, divided to annual mean ---
var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
  .filterDate('2020-01-01', '2025-01-01')
  .select('precipitation');

var annualRain = chirps.sum().divide(5).rename('rainfall_mm');

// --- Elevation: SRTM ---
var elevation = ee.Image('USGS/SRTMGL1_003')
  .select('elevation').rename('elevation_m');

// --- Visual check ---
Map.addLayer(annualRain.clip(villages.geometry().bounds()),
  {min: 50, max: 400, palette: ['white', 'lightblue', 'blue']}, 'Annual rainfall');
Map.addLayer(villages, {color: 'red'}, 'Villages');

// --- Sample each at its NATIVE scale ---
// setOutputs() is required: reduceRegions names the output column after the
// reducer ('first') rather than the band unless told otherwise.
var rainSampled = annualRain.reduceRegions({
  collection: villages,
  reducer: ee.Reducer.first().setOutputs(['rainfall_mm']),
  scale: 5566
});

Export.table.toDrive({
  collection: rainSampled,
  description: 'village_rainfall_v2',
  fileFormat: 'CSV',
  selectors: ['village_id', 'rainfall_mm']
});

var elevSampled = elevation.reduceRegions({
  collection: villages,
  reducer: ee.Reducer.first().setOutputs(['elevation_m']),
  scale: 30
});

Export.table.toDrive({
  collection: elevSampled,
  description: 'village_elevation_v2',
  fileFormat: 'CSV',
  selectors: ['village_id', 'elevation_m']
});