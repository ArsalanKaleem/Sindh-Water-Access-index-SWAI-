import pandas as pd
from scipy.stats import spearmanr

df = pd.read_csv("swai_with_district.csv")

def score(d, w):
    S = d[["R", "W"]].max(axis=1)
    return (w["S"]*S + w["P"]*d["P"] + w["N"]*d["N"] + w["E"]*d["E"])

variants = {
    "baseline":      {"S": .45, "P": .20, "N": .20, "E": .15},
    "supply_heavy":  {"S": .60, "P": .15, "N": .15, "E": .10},
    "supply_light":  {"S": .30, "P": .25, "N": .25, "E": .20},
    "no_elevation":  {"S": .50, "P": .25, "N": .25, "E": .00},
    "equal_weights": {"S": .25, "P": .25, "N": .25, "E": .25},
    "P_flipped":     {"S": .45, "P": .20, "N": .20, "E": .15},   # P direction reversed below
}

out = {}
for name, w in variants.items():
    d = df.copy()
    if name == "P_flipped":
        d["P"] = 100 - d["P"]        # test: larger settlements = BETTER access
    out[name] = score(d, w)

res = pd.DataFrame(out)
res["district"] = df["district"]

dist_means = res.groupby("district").mean()

print("=== district ranks under each weighting ===")
ranks = dist_means.rank(ascending=False).astype(int)
print(ranks.sort_values("baseline").to_string())

print("\n=== rank correlation vs baseline (Spearman) ===")
for c in dist_means.columns:
    if c != "baseline":
        rho, p = spearmanr(dist_means["baseline"], dist_means[c])
        print(f"  {c:15s} rho = {rho:.3f}")

print("\n=== Mithi's rank under each variant (1 = best access) ===")
print(ranks.loc["Mithi"].to_string())