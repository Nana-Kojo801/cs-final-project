"""
Interactive Grid Maps (Folium + Plotly)
National Electricity Grid Network Analysis - Course Project (issue #4)

Exports interactive maps of the substation network from the cleaned datasets:
a layered Folium map (substations + lines, voltage colour-coding, maintenance
highlighting) and a Plotly scatter-geo map.

Outputs:
  maps/grid_interactive_map.html
  maps/substation_map_plotly.html
"""

import os
import pandas as pd

DATA_DIR = "cleaned_data"
MAP_DIR = "maps"
os.makedirs(MAP_DIR, exist_ok=True)


def section(t):
    print(f"\n## {t}\n")


section("1. Load cleaned data")
substations = pd.read_csv(os.path.join(DATA_DIR, "substations_clean.csv"))
lines = pd.read_csv(os.path.join(DATA_DIR, "lines_clean.csv"))
print(f"- substations: {len(substations)}, lines: {len(lines)}")

# ---------------------------------------------------------------------------
section("2. Interactive Folium map")
import folium

center = [substations["Latitude"].mean(), substations["Longitude"].mean()]
fmap = folium.Map(location=center, zoom_start=7, tiles="cartodbpositron")

volt_color = {11: "#8c9eff", 33: "#00bcd4", 69: "#4caf50", 161: "#ff9800", 330: "#e53935"}
sub_layer = folium.FeatureGroup(name="Substations")
for _, r in substations.iterrows():
    folium.CircleMarker(
        location=[r["Latitude"], r["Longitude"]],
        radius=4 + r["Capacity (MVA)"] / 60,
        color=volt_color.get(r["Voltage (kV)"], "#777"),
        fill=True, fill_opacity=0.85,
        popup=folium.Popup(
            f"<b>{r['Name']}</b><br>Region: {r['Region']}<br>"
            f"Voltage: {r['Voltage (kV)']} kV<br>Capacity: {r['Capacity (MVA)']} MVA<br>"
            f"Commissioned: {r['Commissioning Year']}<br>Status: {r['Status']}",
            max_width=260),
    ).add_to(sub_layer)
sub_layer.add_to(fmap)

sub_ll = substations.set_index("Substation ID")[["Latitude", "Longitude"]].to_dict("index")
line_layer = folium.FeatureGroup(name="Lines")
for _, r in lines.iterrows():
    a = sub_ll.get(r["Source Substation ID"])
    b = sub_ll.get(r["Destination Substation ID"])
    if not a or not b:
        continue
    folium.PolyLine(
        [[a["Latitude"], a["Longitude"]], [b["Latitude"], b["Longitude"]]],
        color="#999" if r["Status"] == "Active" else "#c0392b",
        weight=2 if r["Voltage (kV)"] < 161 else 3.5,
        opacity=0.7, dash_array=None if r["Status"] == "Active" else "6",
        popup=f"{r['Source Substation']} -> {r['Destination Substation']} "
              f"({r['Voltage (kV)']} kV, {r['Length (km)']} km, {r['Status']})",
    ).add_to(line_layer)
line_layer.add_to(fmap)

legend = """
<div style="position: fixed; bottom: 24px; left: 24px; z-index: 9999;
background: white; padding: 10px 12px; border: 1px solid #bbb; font: 12px sans-serif;">
<b>Voltage (kV)</b><br>
<span style="color:#8c9eff">&#9679;</span> 11 &nbsp;
<span style="color:#00bcd4">&#9679;</span> 33 &nbsp;
<span style="color:#4caf50">&#9679;</span> 69<br>
<span style="color:#ff9800">&#9679;</span> 161 &nbsp;
<span style="color:#e53935">&#9679;</span> 330<br>
Dashed red line = under maintenance
</div>"""
fmap.get_root().html.add_child(folium.Element(legend))
folium.LayerControl().add_to(fmap)
fmap.save(os.path.join(MAP_DIR, "grid_interactive_map.html"))
print(f"- saved `{os.path.join(MAP_DIR, 'grid_interactive_map.html')}`")

# ---------------------------------------------------------------------------
section("3. Plotly scatter-geo map")
import plotly.express as px

pfig = px.scatter_geo(
    substations, lat="Latitude", lon="Longitude", color="Region",
    size="Capacity (MVA)", hover_name="Name",
    hover_data={"Voltage (kV)": True, "Commissioning Year": True, "Status": True},
    title="National Grid Substations (seeded synthetic dataset)", scope="africa")
pfig.update_geos(center=dict(lat=8.0, lon=-1.0), projection_scale=6, showcountries=True)
pfig.write_html(os.path.join(MAP_DIR, "substation_map_plotly.html"))
print(f"- saved `{os.path.join(MAP_DIR, 'substation_map_plotly.html')}`")

print("\nInteractive maps written to maps/.")
