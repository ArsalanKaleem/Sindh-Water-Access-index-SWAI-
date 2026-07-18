import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("swai_with_district.csv")

# Fig 1: score distribution
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(df["water_access_score"], bins=40, color="#2f7fb5", edgecolor="white")
ax.set_xlabel("Water Access Score")
ax.set_ylabel("Number of villages")
ax.set_title("Distribution of SWAI scores across Sindh (n=5,159)")
fig.savefig("fig1_distribution.png", dpi=200, bbox_inches="tight")

# Fig 2: district ranking
d = df.groupby("district")["water_access_score"].agg(["mean", "count"])
d = d[d["count"] >= 20].sort_values("mean")

fig, ax = plt.subplots(figsize=(7, 8))
ax.barh(d.index, d["mean"], color="#2f7fb5")
ax.set_xlabel("Mean Water Access Score")
ax.set_title("District ranking (districts with ≥20 villages)")
fig.savefig("fig2_districts.png", dpi=200, bbox_inches="tight")

# Fig 3: the diagnostic that matters — annual vs dry-season rainfall
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(df["rainfall_mm"], df["dry_rain_mm"], s=4, alpha=.3, color="#2f7fb5")
ax.set_xlabel("Annual rainfall (mm)")
ax.set_ylabel("Dry-season rainfall, Nov–May (mm)")
ax.set_title("Why annual rainfall misleads: Thar's rain is monsoon-only")
fig.savefig("fig3_seasonality.png", dpi=200, bbox_inches="tight")

print("Saved fig1_distribution.png, fig2_districts.png, fig3_seasonality.png")