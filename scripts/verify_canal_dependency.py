"""
Re-verify the 88.6% canal-dependency figure.

Pipeline layers are stored in EPSG:32642 (UTM 42N) but some lost their CRS
label on save. We assign 32642 where missing (the data is already in metres,
confirmed by bounds ~270000-703000 E / 2.65M-3.15M N) and do NOT reproject.

Run from C:\Projects\SWAI.
"""
import geopandas as gpd
import numpy as np

def load_utm(path):
    g = gpd.read_file(path)
    if g.crs is None:
        # data is already metric UTM 42N; just label it, don't transform
        g = g.set_crs(32642, allow_override=True)
    else:
        g = g.to_crs(32642)
    return g

villages = load_utm("villages_utm.gpkg")
rivers   = load_utm("rivers_perennial.gpkg")
print(f"villages: {len(villages)} | perennial river features: {len(rivers)}")

canal_path = None
for cand in ["canals_utm.gpkg", "water_lines_utm.gpkg"]:
    try:
        canals = load_utm(cand); canal_path = cand; break
    except Exception as e:
        print(f"  ({cand} not usable: {e})")
if canal_path is None:
    raise SystemExit("No canal layer found.")
print(f"canal features: {len(canals)}  (from {canal_path})")

# sanity: all three should share the same bounds ballpark now
print("village bounds:", np.round(villages.total_bounds))
print("river bounds:  ", np.round(rivers.total_bounds))
print("canal bounds:  ", np.round(canals.total_bounds))

rivers_u = rivers.union_all() if hasattr(rivers,"union_all") else rivers.unary_union
canals_u = canals.union_all() if hasattr(canals,"union_all") else canals.unary_union

vg = villages.geometry
d_river = vg.distance(rivers_u)
d_canal = vg.distance(canals_u)

nearer_canal = int((d_canal < d_river).sum())
pct = 100 * nearer_canal / len(villages)

print("\n=== CANAL DEPENDENCY RECOMPUTED ===")
print(f"nearer a CANAL: {nearer_canal} of {len(villages)} = {pct:.1f}%")
print(f"paper claims:   4,573 of 5,159 = 88.6%")
print(f"MATCH: {abs(pct-88.6)<1.5}" + ("" if abs(pct-88.6)<1.5 else "  <-- investigate"))
print(f"median dist to nearest supply: {np.minimum(d_river,d_canal).median()/1000:.2f} km")