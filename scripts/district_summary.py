import pandas as pd
import geopandas as gpd

df = pd.read_csv("swai_final.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.X, df.Y), crs="EPSG:4326")

# GADM level 3 = districts for Pakistan
dist = gpd.read_file("C:/Users/Abbasi/Desktop/gadm41_PAK_shp/gadm41_PAK_3.shp")
dist = dist[dist["NAME_1"] == "Sindh"][["NAME_3", "geometry"]]

joined = gpd.sjoin(gdf, dist, how="left", predicate="within")
joined = joined.rename(columns={"NAME_3": "district"})
joined.drop(columns="geometry").to_csv("swai_with_district.csv", index=False)

summary = (joined.groupby("district")["water_access_score"]
                 .agg(["mean", "median", "count"])
                 .sort_values("mean")
                 .round(1))
summary.to_csv("district_summary.csv")

print("=== districts ranked by mean water access score ===")
print(summary.to_string())

print("\n=== the reality check ===")
for d in ["Mithi", "Umerkot", "Thatta", "Badin", "Sukkur", "Larkana"]:
    if d in summary.index:
        print(f"  {d:12s} {summary.loc[d, 'mean']:5.1f}   (n={int(summary.loc[d, 'count'])})")
        