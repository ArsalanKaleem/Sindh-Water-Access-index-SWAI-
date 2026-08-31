"""
SWAI — export everything needed to sanity-check the paper, into one zip.

Bundles: key CSVs, all figures, and a computed sanity-check report that
recomputes every headline number in the paper straight from the data, so
they can be verified against what the manuscript claims.

Run from C:\Projects\SWAI. Produces: swai_review_bundle.zip
"""
import pandas as pd, numpy as np, zipfile, os, io, json
from scipy.stats import spearmanr, pearsonr

OUT = "swai_review_bundle.zip"
report = []
def log(s=""):
    report.append(str(s)); print(s)

log("="*60)
log("SWAI SANITY-CHECK REPORT")
log("="*60)

# ---------- load ----------
def try_read(path):
    try: return pd.read_csv(path)
    except Exception as e:
        log(f"[missing] {path}: {e}"); return None

final = try_read("swai_final.csv")
wd    = try_read("swai_with_district.csv")
ind   = try_read("indicators_normalized.csv")
raw   = try_read("indicators_raw.csv")

# ---------- headline recomputations ----------
if final is not None:
    sc = final["water_access_score"] if "water_access_score" in final else final.filter(like="score").iloc[:,0]
    log(f"\n[villages] n = {len(final)}")
    log(f"[score] mean={sc.mean():.1f} sd={sc.std():.1f} min={sc.min():.1f} max={sc.max():.1f}")
    log(f"         median={sc.median():.1f}  IQR={sc.quantile(.75)-sc.quantile(.25):.1f}")

if ind is not None:
    log("\n[indicator IQRs]")
    for c in ["R","P","W","N","E"]:
        if c in ind: log(f"   {c}: {ind[c].quantile(.75)-ind[c].quantile(.25):5.1f}")
    log("\n[indicator correlation matrix]  (reviewer asked for this)")
    cols=[c for c in ["R","P","W","N","E"] if c in ind]
    log(ind[cols].corr().round(3).to_string())
    if "W_annual" in ind and "W" in ind:
        log(f"\n[inversion] corr(W_annual, W) = {ind['W_annual'].corr(ind['W']):+.3f}")
    if "P" in ind:
        # P inertness: corr of P with composite
        if "water_access_score" in (final.columns if final is not None else []):
            m = ind.merge(final[["village_id","water_access_score"]], on="village_id", how="left")
            log(f"[P inertness] corr(P, score) = {m['P'].corr(m['water_access_score']):+.3f}")

# ---------- canal dependency ----------
for cand in ["swai_final.csv","swai_with_district.csv","village_water_distance.csv"]:
    d = try_read(cand)
    if d is not None and any("canal" in c.lower() or "nearest_type" in c.lower() for c in d.columns):
        tcol=[c for c in d.columns if "canal" in c.lower() or "nearest_type" in c.lower()][0]
        vc=d[tcol].value_counts()
        log(f"\n[canal dependency] from {cand}::{tcol}\n{vc.to_string()}")
        break

# ---------- district means ----------
if wd is not None and "district" in wd and "water_access_score" in wd:
    dm = wd.groupby("district")["water_access_score"].agg(["mean","count"]).round(1).sort_values("mean")
    log("\n[district means] (ascending)\n"+dm.to_string())

# ---------- MICS division validation recompute ----------
mics = {"Hyderabad":94.8,"Karachi":98.9,"Larkana":99.3,"Mirpur Khas":78.0,
        "Shaheed Benazir Abad":97.8,"Sukkur":98.4}
d2d = try_read("mics_validation.csv")
if d2d is not None and {"swai_mean","mics_improved_pct"}.issubset(d2d.columns):
    rho,ps=spearmanr(d2d["swai_mean"],d2d["mics_improved_pct"])
    r,pp=pearsonr(d2d["swai_mean"],d2d["mics_improved_pct"])
    log(f"\n[MICS validation] Spearman={rho:+.2f}(p={ps:.3f}) Pearson={r:+.2f}(p={pp:.3f}) n={len(d2d)}")

# ---------- Thatta 21-point ----------
tv = try_read("thatta_validation_points.csv")
if tv is not None:
    log(f"\n[Thatta points] n={len(tv)}  TDS range {tv['tds_mgl'].min()}-{tv['tds_mgl'].max()}  "
        f"all>WHO500: {(tv['tds_mgl']>500).all()}")

report_txt = "\n".join(report)

# ---------- write zip ----------
DATA = ["swai_final.csv","swai_with_district.csv","indicators_normalized.csv",
        "indicators_raw.csv","district_summary.csv","district_validation.csv",
        "weight_bootstrap.csv","mics_validation.csv","census_validation.csv",
        "thatta_validation_points.csv"]
FIGS = [f for f in os.listdir(".") if f.lower().endswith(".png")]

with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr("SANITY_REPORT.txt", report_txt)
    for f in DATA+FIGS:
        if os.path.exists(f): z.write(f, arcname=f)
        elif f in DATA: log(f"[note] {f} not found, skipped")

log(f"\nWrote {OUT}  ({os.path.getsize(OUT)/1e6:.1f} MB)")
log("Upload that zip in the chat and I'll verify every paper number against it.")
print("\nDONE.")
