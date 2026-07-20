import pandas as pd, numpy as np

df = pd.read_csv("swai_with_district.csv")
thatta = df[df["district"] == "Thatta"]

# distance from Keti Bandar (24.14 N, 67.45 E) in rough km
d = np.sqrt(((thatta["Y"] - 24.14)*111)**2 + ((thatta["X"] - 67.45)*101)**2)
near = thatta.assign(km_from_keti=d).nsmallest(10, "km_from_keti")

print(near[["name","water_access_score","band","km_from_keti",
            "river_distance_km","NDWI"]].to_string(index=False))
print("\nThatta mean:", round(thatta["water_access_score"].mean(),1))
print("Sindh mean: ", round(df["water_access_score"].mean(),1))