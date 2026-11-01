"""Build the data files for the SWAI district explorer (docs/).

Reads the published CSVs in data/ and writes compact JSON to docs/data/:
  villages.json    one row per village: score, naive score, indicators, raw values
  samples.json     the 21 Thatta groundwater samples used for validation
  validation.json  district-level published percent-unsafe figures
  meta.json        counts, band cut-offs and build date

The naive score repeats swai_paper_extras.py: the same formula with
annual rainfall (W_annual) in place of dry-season rainfall (W).

Run from anywhere:  python scripts/build_web.py
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "docs" / "data"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA / "swai_with_district.csv")
ind = pd.read_csv(DATA / "indicators_normalized.csv", usecols=["village_id", "W_annual"])
df = df.merge(ind, on="village_id", how="left")
df["naive"] = (0.45 * df[["R", "W_annual"]].max(axis=1)
               + 0.20 * df["P"] + 0.20 * df["N"] + 0.15 * df["E"])


def num(x, nd):
    if pd.isna(x):
        return None
    return int(round(float(x))) if nd == 0 else round(float(x), nd)


fields = ["id", "name", "district", "lon", "lat", "score", "naive",
          "R", "P", "W", "Wa", "N", "E",
          "dist_km", "dry_mm", "rain_mm", "elev_m", "ndwi", "pop2km"]
rows = []
for r in df.itertuples(index=False):
    rows.append([
        int(r.village_id),
        None if pd.isna(r.name) else str(r.name),
        r.district,
        num(r.X, 4), num(r.Y, 4),
        num(r.water_access_score, 1), num(r.naive, 1),
        num(r.R, 0), num(r.P, 0), num(r.W, 0), num(r.W_annual, 0), num(r.N, 0), num(r.E, 0),
        num(r.river_distance_km, 2), num(r.dry_rain_mm, 1), num(r.rainfall_mm, 0),
        num(r.elevation_m, 0), num(r.NDWI, 3),
        None if pd.isna(r.pop_sum) else int(round(r.pop_sum)),
    ])
(OUT / "villages.json").write_text(
    json.dumps({"fields": fields, "rows": rows}, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8")

s = pd.read_csv(DATA / "thatta_validation_points.csv")
samples = [{"code": r.sample_code, "place": r.locality, "lat": r.lat, "lon": r.lon,
            "tds": r.tds_mgl, "cl": r.chloride_mgl, "taste": r.taste, "bact": r.bacterial}
           for r in s.itertuples(index=False)]
(OUT / "samples.json").write_text(json.dumps(samples, ensure_ascii=False), encoding="utf-8")

v = pd.read_csv(DATA / "district_validation.csv")
validation = {r.district: {"score": r.swai_mean_score, "unsafe": r.published_pct_unsafe}
              for r in v.itertuples(index=False)}
(OUT / "validation.json").write_text(json.dumps(validation), encoding="utf-8")

# band edges as published: Poor = bottom 20%, Good = top 20% (compute_score.py)
score = df["water_access_score"]
meta = {
    "villages": int(len(df)),
    "districts": int(df["district"].nunique()),
    "poor_max": float(df.loc[df["band"] == "Poor", "water_access_score"].max()),
    "good_min": float(df.loc[df["band"] == "Good", "water_access_score"].min()),
    "median": float(score.median()),
    "mean": round(float(score.mean()), 1),
    "generated": date.today().isoformat(),
}
(OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

print(f"villages: {len(rows)} -> {OUT / 'villages.json'}")
print(f"samples: {len(samples)}, validation districts: {len(validation)}")
print("meta:", meta)
