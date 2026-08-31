import pandas as pd

# ---- 1. base table ----
villages = pd.read_csv("Village.csv")[["village_id", "X", "Y", "name"]]
villages = villages[villages["X"] != 0].copy()
print("villages after dropping phantom row:", len(villages))

# ---- 2. water distance: dedupe ties, convert m -> km ----
rivers = pd.read_csv("village_water_distance.csv")[["village_id", "distance", "layer"]]
rivers["distance"] = pd.to_numeric(rivers["distance"], errors="coerce")
print("water rows before dedupe:", len(rivers))

rivers = rivers.sort_values("distance").drop_duplicates("village_id", keep="first")
rivers["river_distance_km"] = rivers["distance"] / 1000

print("\nnearest water source type:")
print(rivers["layer"].value_counts())

rivers = rivers[["village_id", "river_distance_km"]]
print("\nwater rows after dedupe:", len(rivers))

# ---- 3. the rest ----
pop     = pd.read_csv("village_population.csv")[["village_id", "pop_sum"]]
rain    = pd.read_csv("village_rainfall_v2.csv")[["village_id", "rainfall_mm"]]
dryrain = pd.read_csv("village_dryrain.csv")[["village_id", "dry_rain_mm"]]
ndwi    = pd.read_csv("village_ndwi.csv")[["village_id", "NDWI", "NDVI"]]
elev    = pd.read_csv("village_elevation_v2.csv")[["village_id", "elevation_m"]]

# ---- 4. merge everything on village_id ----
df = (villages
      .merge(rivers,  on="village_id", how="left")
      .merge(pop,     on="village_id", how="left")
      .merge(rain,    on="village_id", how="left")
      .merge(dryrain, on="village_id", how="left")
      .merge(ndwi,    on="village_id", how="left")
      .merge(elev,    on="village_id", how="left"))

df.to_csv("indicators_raw.csv", index=False)

# ---- 5. diagnostics ----
print("\n=== merged table:", len(df), "rows ===")
print("\nmissing values per column:")
print(df.isna().sum())

print("\nranges:")
cols = ["river_distance_km", "pop_sum", "rainfall_mm", "dry_rain_mm", "NDWI", "elevation_m"]
print(df[cols].describe().to_string())

print("\ndry season as % of annual rainfall:")
pct = (df["dry_rain_mm"] / df["rainfall_mm"] * 100)
print(pct.describe().round(1).to_string())

print("\nSaved indicators_raw.csv")