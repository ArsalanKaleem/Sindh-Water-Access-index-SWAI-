import geopandas as gpd
import rasterio
from rasterstats import zonal_stats

buf = gpd.read_file("villages_buffer2km.gpkg")
print("buffers:", len(buf), "| CRS:", buf.crs)

with rasterio.open("population_utm.tif") as src:
    print("raster CRS:", src.crs)

# 1. drop the NULL / empty geometry rows
buf = buf[buf.geometry.notna() & ~buf.geometry.is_empty].copy()
print("after dropping empty geometries:", len(buf))

# 2. force the CRS if it went missing
if buf.crs is None:
    buf = buf.set_crs("EPSG:32642")
    print("CRS was missing — set to EPSG:32642")

stats = zonal_stats(buf, "population_utm.tif", stats=["sum"])
buf["pop_sum"] = [s["sum"] if s["sum"] is not None else 0 for s in stats]

buf[["village_id", "pop_sum"]].to_csv("village_population.csv", index=False)

print(buf["pop_sum"].describe())
print("Saved village_population.csv")