import pandas as pd, folium

df = pd.read_csv("swai_final.csv")

colors = {"Good": "#2a9d5c", "Moderate": "#edae49", "Poor": "#d1495b"}

m = folium.Map(location=[25.9, 68.5], zoom_start=7, tiles="cartodbpositron")

for _, r in df.iterrows():
    folium.CircleMarker(
        location=[r["Y"], r["X"]],
        radius=3,
        color=colors.get(r["band"], "gray"),
        fill=True,
        fill_opacity=0.75,
        weight=0,
        popup=folium.Popup(
            f"<b>{r['name']}</b><br>"
            f"Score: {r['water_access_score']} ({r['band']})<br>"
            f"Water: {r['river_distance_km']:.1f} km<br>"
            f"Rain: {r['rainfall_mm']:.0f} mm",
            max_width=250),
    ).add_to(m)

m.save("swai_map.html")
print("Saved swai_map.html — open it in your browser")