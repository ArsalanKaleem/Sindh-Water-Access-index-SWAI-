/**
 * SWAI — Script 3: Dry-season rainfall  [THE KEY CORRECTION]
 *
 * Computes mean rainfall for the NON-monsoon months only (November-May),
 * CHIRPS daily 2020-2024.
 *
 * WHY THIS EXISTS:
 * Using annual rainfall inverts the district ranking — it scores Tharparkar,
 * Pakistan's driest district, as the best-served in Sindh. Sindh has two
 * rainfall regimes: the southeast/coast is monsoon-dominated (~600 mm/yr but
 * ~10 mm across Nov-May), while western Sindh gets ~150 mm/yr with 30-65 mm
 * spread through the dry months from westerly disturbances. Annual totals
 * therefore rank the province backwards for drinking-water availability.
 *
 * Substituting this indicator moves Mithi from rank 1 (best) to rank 25
 * (worst), matching known drought conditions.
 *
 * Dry-season rain averages 14.5% of the annual total (range 0.6-39.6%).
 *
 * Exports -> Google Drive:
 *   village_dryrain.csv  [village_id, dry_rain_mm]
 */

var villages = ee.FeatureCollection(
  'projects/my-project-earth-engine-502320/assets/sindh_villages');
Map.centerObject(villages, 7);

// calendarRange(11, 5, 'month') wraps across the year boundary:
// Nov, Dec, Jan, Feb, Mar, Apr, May
var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
  .filterDate('2020-01-01', '2025-01-01')
  .select('precipitation')
  .filter(ee.Filter.calendarRange(11, 5, 'month'));

// Sanity check — should print a few thousand images, NOT zero.
// If zero, the calendarRange wrap failed and the correction is inert.
print('images in dry season:', chirps.size());

var dryRain = chirps.sum().divide(5).rename('dry_rain_mm');

Map.addLayer(dryRain.clip(villages.geometry().bounds()),
  {min: 0, max: 70, palette: ['white', 'lightblue', 'blue']}, 'Dry-season rainfall');
Map.addLayer(villages, {color: 'red'}, 'Villages');

var sampled = dryRain.reduceRegions({
  collection: villages,
  reducer: ee.Reducer.first().setOutputs(['dry_rain_mm']),
  scale: 5566
});

Export.table.toDrive({
  collection: sampled,
  description: 'village_dryrain',
  fileFormat: 'CSV',
  selectors: ['village_id', 'dry_rain_mm']
});