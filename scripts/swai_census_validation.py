"""
SWAI external validation against MICS Sindh 2018-19 improved-water-source data.

The MICS district table is only published at DIVISION level for Sindh (6 divisions),
so this validates SWAI aggregated to division level: an independent, single-
definition external check. n=6 is small - report it honestly alongside the
district-scale descriptive comparison (Table 3).

Run from C:\Projects\SWAI  (needs swai_with_district.csv).
"""
import pandas as pd
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt

# --- MICS 2018-19: % using improved drinking-water source, by division ---
mics_division = {
    "Hyderabad":            94.8,
    "Karachi":              98.9,
    "Larkana":              99.3,
    "Mirpur Khas":          78.0,
    "Shaheed Benazir Abad": 97.8,
    "Sukkur":               98.4,
}

# --- Map each GADM district (as spelled in swai_with_district.csv) to its division ---
# EDIT if any spelling doesn't match your file; the script prints unmatched ones.
district_to_division = {
    # Hyderabad division
    "Hyderabad":"Hyderabad","Badin":"Hyderabad","Dadu":"Hyderabad",
    "Jamshoro":"Hyderabad","Matiari":"Hyderabad","Tando Allahyar":"Hyderabad",
    "Tando M. Khan":"Hyderabad","Tando Muhammad Khan":"Hyderabad","Thatta":"Hyderabad",
    "Sujawal":"Hyderabad",
    # Karachi division
    "Karachi East":"Karachi","Karachi West":"Karachi","Karachi Central":"Karachi",
    "Karachi South":"Karachi","Malir":"Karachi","Korangi":"Karachi",
    "Karachi west":"Karachi","Karachi east":"Karachi",
    # Larkana division
    "Larkana":"Larkana","Kambar Shahdadkot":"Larkana","Qambar Shahdadkot":"Larkana",
    "Shikarpur":"Larkana","Jacobabad":"Larkana","Jakobabad":"Larkana","Kashmore":"Larkana",
    # Mirpur Khas division
    "Mirphurkhas":"Mirpur Khas","Mirpur Khas":"Mirpur Khas","Umerkot":"Mirpur Khas",
    "Tharparkar":"Mirpur Khas","Mithi":"Mirpur Khas","Rann of Kutch":"Mirpur Khas",
    # Shaheed Benazir Abad division
    "Nawab Shah":"Shaheed Benazir Abad","Nawabshah":"Shaheed Benazir Abad",
    "Shaheed Benazirabad":"Shaheed Benazir Abad","Naushahro Firoz":"Shaheed Benazir Abad",
    "Sanghar":"Shaheed Benazir Abad",
    # Sukkur division
    "Sukkur":"Sukkur","Khairpur":"Sukkur","Ghotki":"Sukkur",
}

df = pd.read_csv("swai_with_district.csv")
df["division"] = df["district"].map(district_to_division)

unmatched = sorted(df.loc[df["division"].isna(), "district"].unique())
if unmatched:
    print("[warn] districts not mapped to a division (edit district_to_division):")
    for u in unmatched: print("   ", repr(u))

div_mean = df.groupby("division")["water_access_score"].mean()

rows = []
for div, mics in mics_division.items():
    if div in div_mean.index:
        rows.append({"division": div, "swai_mean": round(div_mean[div],1),
                     "mics_improved_pct": mics,
                     "n_villages": int((df["division"]==div).sum())})
v = pd.DataFrame(rows).sort_values("swai_mean", ascending=False)

print("\n=== SWAI (division mean) vs MICS % improved water source ===")
print(v.to_string(index=False))

rho, ps = spearmanr(v["swai_mean"], v["mics_improved_pct"])
r, pp   = pearsonr(v["swai_mean"], v["mics_improved_pct"])
print(f"\nSpearman rho = {rho:+.2f} (p={ps:.3f}) | Pearson r = {r:+.2f} (p={pp:.3f}) | n={len(v)}")
print("\nPositive = SWAI accessibility tracks independent WASH access (validation).")
print("Near-zero/negative = honest divergence; report it. Watch Mirpur Khas (78%, lowest).")

fig, ax = plt.subplots(figsize=(6.5,5))
ax.scatter(v["swai_mean"], v["mics_improved_pct"], s=55, color="#2f7fb5")
for _,row in v.iterrows():
    ax.annotate(row["division"], (row["swai_mean"], row["mics_improved_pct"]),
                fontsize=8, xytext=(4,4), textcoords="offset points")
ax.set_xlabel("Division-mean SWAI score")
ax.set_ylabel("MICS 2018-19 % improved water source")
ax.set_title(f"External validation vs MICS (division level)\nSpearman rho = {rho:+.2f}, n = {len(v)}")
fig.savefig("fig6_mics_validation.png", dpi=200, bbox_inches="tight")
v.to_csv("mics_validation.csv", index=False)
print("\nSaved fig6_mics_validation.png and mics_validation.csv")