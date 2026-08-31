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
df["W"] = norm(df["dry_rain_mm"])        # dry-season rain = better (CORRECTED indicator)
df["N"] = norm(df["NDWI"])               # more surface water = better
df["E"] = norm_inv(df["elevation_m"])    # lower = nearer water table

# --- ALSO normalize ANNUAL rainfall, so the before/after inversion map can be built ---
# This reproduces the NAIVE indicator we later replaced. Not used in the final score;
# kept only to demonstrate the inversion in Figure (before/after).
if "rainfall_mm" in df.columns:
    df["W_annual"] = norm(df["rainfall_mm"])
    print("W_annual (naive annual-rainfall indicator) added for the before/after figure.")
else:
    print("[note] 'rainfall_mm' not found in indicators_raw.csv — before/after map "
          "cannot be built. Check that build_indicators.py merged village_rainfall_v2.csv.")

for c in ["R", "P", "W", "N", "E"]:
    df[c] = df[c].fillna(50)
if "W_annual" in df.columns:
    df["W_annual"] = df["W_annual"].fillna(50)

print("=== winsorized + log ===")
print(df[["R", "P", "W", "N", "E"]].describe().to_string())

print("\nIQR per indicator (higher = more discriminating):")
for c in ["R", "P", "W", "N", "E"]:
    print(f"  {c}: {df[c].quantile(.75) - df[c].quantile(.25):5.1f}")

print("\ncorrelation matrix:")
print(df[["R", "P", "W", "N", "E"]].corr().round(2).to_string())

# quick confirmation of the inversion the paper is built on
if "W_annual" in df.columns:
    print("\nannual vs dry-season rainfall indicator correlation:",
          round(df["W_annual"].corr(df["W"]), 2),
          "(negative/low = the two regimes diverge — the inversion mechanism)")

df.to_csv("indicators_normalized.csv", index=False)
print("\nSaved indicators_normalized.csv")