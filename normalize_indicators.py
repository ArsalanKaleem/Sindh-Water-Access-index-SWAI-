import pandas as pd
import numpy as np

df = pd.read_csv("indicators_raw.csv")

def winsorize(s, lo=0.01, hi=0.99):
    return s.clip(s.quantile(lo), s.quantile(hi))

def norm(s):
    s = winsorize(s)
    return 100 * (s - s.min()) / (s.max() - s.min())

def norm_inv(s):
    return 100 - norm(s)

# log-transform the multiplicatively skewed variables
df["log_pop"]  = np.log1p(df["pop_sum"])
df["log_dist"] = np.log1p(df["river_distance_km"])

# normalize: 100 always = good for water access
df["R"] = norm_inv(df["log_dist"])       # closer to perennial water = better
df["P"] = norm_inv(df["log_pop"])        # fewer people competing = better
df["W"] = norm(df["dry_rain_mm"])        # dry-season rain = better
df["N"] = norm(df["NDWI"])               # more surface water = better
df["E"] = norm_inv(df["elevation_m"])    # lower = nearer water table

for c in ["R", "P", "W", "N", "E"]:
    df[c] = df[c].fillna(50)

print("=== winsorized + log ===")
print(df[["R", "P", "W", "N", "E"]].describe().to_string())

print("\nIQR per indicator (higher = more discriminating):")
for c in ["R", "P", "W", "N", "E"]:
    print(f"  {c}: {df[c].quantile(.75) - df[c].quantile(.25):5.1f}")

print("\ncorrelation matrix:")
print(df[["R", "P", "W", "N", "E"]].corr().round(2).to_string())

df.to_csv("indicators_normalized.csv", index=False)
print("\nSaved indicators_normalized.csv")