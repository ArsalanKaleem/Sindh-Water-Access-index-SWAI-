"""
SWAI point-level validation against 21 georeferenced Thatta groundwater samples
(Zenodo record 15033704). Produces the numbers and Figure 5 for Section 4.4
of the paper.

Run from C:\Projects\SWAI  (needs swai_final.csv there, and
thatta_validation_points.csv copied into the same folder).
"""
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

swai = pd.read_csv("swai_final.csv")
pts  = pd.read_csv("thatta_validation_points.csv")

# nearest SWAI village to each sample (rough metric degrees -> km)
def nearest_village(lat, lon):
    d = np.sqrt(((swai["Y"] - lat) * 111)**2 + ((swai["X"] - lon) * 101)**2)
    i = d.idxmin()
    return pd.Series({"village_id": swai.loc[i, "village_id"],
                      "village": swai.loc[i, "name"],
                      "score": swai.loc[i, "water_access_score"],
                      "band": swai.loc[i, "band"],
                      "km_to_village": d.min()})

pts = pts.join(pts.apply(lambda r: nearest_village(r["lat"], r["lon"]), axis=1))

print("=== sample -> nearest village ===")
print(pts[["sample_code","locality","tds_mgl","chloride_mgl","village","score","band","km_to_village"]]
      .to_string(index=False))

print(f"\nmean SWAI score of villages nearest the samples: {pts['score'].mean():.1f}")
print(f"Sindh-wide mean score:                           {swai['water_access_score'].mean():.1f}")
print(f"samples whose nearest village is 'Good' band:    {(pts['band']=='Good').sum()} of {len(pts)}")

for var in ["tds_mgl", "chloride_mgl"]:
    rho, pval = spearmanr(pts["score"], pts[var])
    print(f"Spearman rho (score vs {var}): {rho:+.2f}  (p = {pval:.3f})")

# Figure 5: scatter
fig, ax = plt.subplots(figsize=(6,5))
ax.scatter(pts["score"], pts["tds_mgl"], s=45, color="#2f7fb5", label="TDS")
ax.axhline(500, color="red", ls="--", lw=1, label="WHO TDS limit (500 mg/L)")
ax.set_xlabel("SWAI score of nearest village")
ax.set_ylabel("Measured TDS (mg/L)")
ax.set_title("Accessibility score vs. measured groundwater TDS\n(21 samples, Thatta; Zenodo 15033704)")
ax.legend()
fig.savefig("fig5_validation_scatter.png", dpi=200, bbox_inches="tight")
print("\nSaved fig5_validation_scatter.png")
print("\nCAVEAT to state in the paper: samples cluster within ~30 km of Thatta town;")
print("report as point-anchored evidence, not a district-wide correlation.")
