"""
Generate the data + figures the reviewer asked for:
  #1  district-level validation table (SWAI district means vs published exceedance)
  #2  choropleth-style village map + before/after inversion district maps
  #4  bootstrap of the weights -> confidence on district ranks

Run from C:\Projects\SWAI  (needs swai_with_district.csv, indicators_normalized.csv).
Outputs go to the same folder.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

df = pd.read_csv("swai_with_district.csv")

# ======================================================================
# #1  DISTRICT-LEVEL VALIDATION
# ----------------------------------------------------------------------
# Published exceedance / unsafe rates you already cite. EDIT / EXTEND this
# dict as you confirm more districts from PCRWR (2021) and the WQI papers.
# Values = % of samples unsafe / unfit for drinking (higher = worse quality).
published_unsafe = {
    "Thatta":      100,   # Solangi 2017: 100% exceed WHO chloride
    "Badin":        92,   # PCRWR 2021
    "Mirphurkhas": 100,   # PCRWR 2021 (note GADM spelling)
    "Sujawal":      36,   # Mahar 2019 (~unsuitable). VERIFY exact figure
    "Hyderabad":    80,   # PCRWR 2021  [VERIFY]
    "Karachi East": 93,   # PCRWR 2021 Karachi  [VERIFY / map to your Karachi units]
    "Sukkur":       67,   # PCRWR 2021  [VERIFY]
}

dmean = df.groupby("district")["water_access_score"].mean().round(1)

rows = []
for dist, unsafe in published_unsafe.items():
    if dist in dmean.index:
        rows.append({"district": dist,
                     "swai_mean_score": dmean[dist],
                     "published_pct_unsafe": unsafe})
val = pd.DataFrame(rows).sort_values("swai_mean_score", ascending=False)
val.to_csv("district_validation.csv", index=False)

print("=== #1 DISTRICT-LEVEL VALIDATION ===")
print(val.to_string(index=False))
if len(val) >= 3:
    rho, p = spearmanr(val["swai_mean_score"], val["published_pct_unsafe"])
    print(f"\nSpearman rho (SWAI accessibility vs % unsafe): {rho:+.2f}  (p = {p:.3f})")
    print("Expected: a POSITIVE or near-zero rho = accessibility does NOT track safety;")
    print("high-accessibility districts are among the least safe = decoupling at district scale.")

# ======================================================================
# #2  MAPS
# ----------------------------------------------------------------------
# (a) village choropleth-style scatter (no shapefile needed)
fig, ax = plt.subplots(figsize=(7, 8))
sc = ax.scatter(df["X"], df["Y"], c=df["water_access_score"],
                cmap="RdYlGn", s=6, vmin=df["water_access_score"].quantile(.05),
                vmax=df["water_access_score"].quantile(.95))
ax.set_aspect("equal"); ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
ax.set_title("SWAI score by village (n=5,159)")
plt.colorbar(sc, ax=ax, label="Water Access Score", shrink=0.6)
fig.savefig("fig_map_villages.png", dpi=200, bbox_inches="tight")
print("\nSaved fig_map_villages.png")

# (b) before/after inversion — district means, annual vs dry-season rainfall.
# Recompute an 'annual-rainfall' score using the raw annual W if available.
try:
    ind = pd.read_csv("indicators_normalized.csv")
    # need a village_id link; merge district onto indicators
    link = df[["village_id", "district"]]
    ind = ind.merge(link, on="village_id", how="left")

    def score_with(Wcol):
        S = ind[["R", Wcol]].max(axis=1)
        return 0.45*S + 0.20*ind["P"] + 0.20*ind["N"] + 0.15*ind["E"]

    # 'W' is dry-season (current). If you kept an annual-normalized column,
    # name it here; else this block just uses W and you can skip panel (b).
    have_annual = "W_annual" in ind.columns
    ind["score_dry"] = score_with("W")
    if have_annual:
        ind["score_annual"] = score_with("W_annual")
        d_annual = ind.groupby("district")["score_annual"].mean().sort_values()
        d_dry    = ind.groupby("district")["score_dry"].mean()

        order_annual = d_annual.index.tolist()
        fig, axes = plt.subplots(1, 2, figsize=(11, 8), sharey=True)
        axes[0].barh(order_annual, d_annual.values, color="#c0708a")
        axes[0].set_title("Ranked by ANNUAL rainfall\n(Mithi ranks BEST — wrong)")
        axes[1].barh(order_annual, d_dry.reindex(order_annual).values, color="#2f7fb5")
        axes[1].set_title("Ranked by DRY-SEASON rainfall\n(Mithi ranks WORST — correct)")
        for a in axes: a.set_xlabel("Mean score")
        fig.tight_layout()
        fig.savefig("fig_before_after_inversion.png", dpi=200, bbox_inches="tight")
        print("Saved fig_before_after_inversion.png")
    else:
        print("\n[note] No 'W_annual' column in indicators_normalized.csv.")
        print("      To build the before/after map, re-run normalize with annual")
        print("      rainfall saved as W_annual, OR tell me and I'll adjust.")
except Exception as e:
    print("\n[before/after map skipped]:", e)

# ======================================================================
# #4  BOOTSTRAP THE WEIGHTS
# ----------------------------------------------------------------------
print("\n=== #4 WEIGHT BOOTSTRAP ===")
ind = pd.read_csv("indicators_normalized.csv")
link = df[["village_id", "district"]]
ind = ind.merge(link, on="village_id", how="left")

base_w = {"S": 0.45, "P": 0.20, "N": 0.20, "E": 0.15}
def dist_ranks(w):
    S = ind[["R", "W"]].max(axis=1)
    sc = w["S"]*S + w["P"]*ind["P"] + w["N"]*ind["N"] + w["E"]*ind["E"]
    return sc.groupby(ind["district"]).mean().rank(ascending=False)

base_rank = dist_ranks(base_w)
N = 500
rng = np.random.default_rng(42)
rank_samples = {d: [] for d in base_rank.index}
for _ in range(N):
    w = {k: v * rng.uniform(0.8, 1.2) for k, v in base_w.items()}  # ±20%
    tot = sum(w.values()); w = {k: v/tot for k, v in w.items()}
    r = dist_ranks(w)
    for d in r.index:
        rank_samples[d].append(r[d])

summary = pd.DataFrame({
    "district": list(rank_samples.keys()),
    "base_rank": [int(base_rank[d]) for d in rank_samples],
    "rank_p05": [int(np.percentile(v, 5)) for v in rank_samples.values()],
    "rank_p95": [int(np.percentile(v, 95)) for v in rank_samples.values()],
}).sort_values("base_rank")
summary["rank_range"] = summary["rank_p95"] - summary["rank_p05"]
summary.to_csv("weight_bootstrap.csv", index=False)
print(summary.to_string(index=False))
print(f"\nMean 90% rank interval width: {summary['rank_range'].mean():.1f} positions")
print("Narrow intervals (esp. for top/bottom districts) = ranking is stable under ±20% weight noise.")
print("\nSaved district_validation.csv, weight_bootstrap.csv + figures.")