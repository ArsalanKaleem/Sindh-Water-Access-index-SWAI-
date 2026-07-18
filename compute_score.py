import pandas as pd

df = pd.read_csv("indicators_normalized.csv")

# R and W are substitutable water sources -> take the better one
df["S"] = df[["R", "W"]].max(axis=1)

df["water_access_score"] = (
    0.45*df["S"] + 0.20*df["P"] + 0.20*df["N"] + 0.15*df["E"]
).round(1)

df["band"] = pd.qcut(df["water_access_score"], [0, .2, .8, 1.0],
                     labels=["Poor", "Moderate", "Good"])

df.to_csv("swai_final.csv", index=False)

print("=== score distribution ===")
print(df["water_access_score"].describe().to_string())

print("\n=== bands ===")
print(df["band"].value_counts())

print("\ncorrelation with final score:")
for c in ["S", "P", "N", "E"]:
    print(f"  {c}: {df[c].corr(df['water_access_score']):.2f}")

print("\n=== 10 lowest ===")
print(df.nsmallest(10, "water_access_score")[
    ["name", "water_access_score", "river_distance_km", "dry_rain_mm"]].to_string(index=False))

print("\nSaved swai_final.csv")