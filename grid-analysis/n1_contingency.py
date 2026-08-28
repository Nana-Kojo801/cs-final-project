"""
N-1 Contingency Analysis and Static Network Diagram
National Electricity Grid Network Analysis - Course Project (issue #3)

Builds the grid graph from the cleaned datasets, draws a static network diagram,
and runs a simplified N-1 contingency analysis: remove each important substation
(and each single line) and measure how the network fragments. A resilient
network tolerates the loss of one important component without splitting.

Outputs:
  charts/network_graph.png
  charts/n1_contingency_impact.png
  network_analysis/n1_contingency_report.md
  network_analysis/n1_substation_impact.csv
  network_analysis/n1_line_impact.csv
"""

import os
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = "cleaned_data"
CHART_DIR = "charts"
NET_DIR = "network_analysis"
for d in (CHART_DIR, NET_DIR):
    os.makedirs(d, exist_ok=True)

report = []


def log(m=""):
    print(m)
    report.append(m)


def section(t):
    log(f"\n## {t}\n")


# ---------------------------------------------------------------------------
section("1. Load data and build graph")
utilities = pd.read_csv(os.path.join(DATA_DIR, "utilities_clean.csv"))
substations = pd.read_csv(os.path.join(DATA_DIR, "substations_clean.csv"))
lines = pd.read_csv(os.path.join(DATA_DIR, "lines_clean.csv"))
util_alias = dict(zip(utilities["Utility ID"], utilities["Alias"]))

G = nx.Graph()
for _, r in substations.iterrows():
    G.add_node(r["Substation ID"], name=r["Short Name"], region=r["Region"],
               voltage=r["Voltage (kV)"], capacity=r["Capacity (MVA)"],
               lat=r["Latitude"], lon=r["Longitude"], status=r["Status"])
for _, r in lines.iterrows():
    G.add_edge(r["Source Substation ID"], r["Destination Substation ID"],
               length=r["Length (km)"], voltage=r["Voltage (kV)"],
               status=r["Status"], utility=util_alias.get(r["Utility ID"], "?"))

log(f"- nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
log(f"- connected components (baseline): {nx.number_connected_components(G)}")
name = nx.get_node_attributes(G, "name")
region = nx.get_node_attributes(G, "region")

# ---------------------------------------------------------------------------
section("2. Static network diagram")
pos = {n: (G.nodes[n]["lon"], G.nodes[n]["lat"]) for n in G.nodes}
regions = sorted(set(region.values()))
cmap = plt.cm.tab20
region_color = {rg: cmap(i / max(len(regions) - 1, 1)) for i, rg in enumerate(regions)}
node_colors = [region_color[region[n]] for n in G.nodes]
node_sizes = [40 + G.nodes[n]["capacity"] * 2 for n in G.nodes]

fig, ax = plt.subplots(figsize=(13, 12))
nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, width=1.0)
nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, alpha=0.9)
nx.draw_networkx_labels(G, pos, labels=name, ax=ax, font_size=6)
handles = [plt.Line2D([0], [0], marker="o", color="w", label=rg,
                      markerfacecolor=region_color[rg], markersize=8) for rg in regions]
ax.legend(handles=handles, title="Region", loc="lower left", fontsize=7)
ax.set_title("National Grid Substation Network (geographic layout, node size ~ capacity)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "network_graph.png"), dpi=130)
plt.close(fig)
log(f"- saved `{os.path.join(CHART_DIR, 'network_graph.png')}`")

# ---------------------------------------------------------------------------
section("3. Centrality shortlist")
deg = dict(G.degree())
btw = nx.betweenness_centrality(G, weight="length")
by_btw = sorted(btw, key=btw.get, reverse=True)[:8]
by_deg = sorted(deg, key=deg.get, reverse=True)[:8]
log("**Top by degree**: " + ", ".join(f"{name[n]}({deg[n]})" for n in by_deg))
log("**Top by betweenness**: " + ", ".join(f"{name[n]}({btw[n]:.3f})" for n in by_btw))

bridges = list(nx.bridges(G))
log(f"\n**Bridge lines** ({len(bridges)}): " +
    ("; ".join(f"{name[u]}<->{name[v]}" for u, v in bridges) if bridges else "none"))

# ---------------------------------------------------------------------------
section("4. N-1 contingency analysis - remove one substation")
log("For each candidate substation we delete the node (and its incident lines) "
    "and record how the network fragments.\n")

base_components = nx.number_connected_components(G)
base_largest = len(max(nx.connected_components(G), key=len))
candidates = list(dict.fromkeys(by_btw + by_deg))
rows = []
for n in candidates:
    H = G.copy()
    H.remove_node(n)
    comps = nx.number_connected_components(H)
    largest = len(max(nx.connected_components(H), key=len)) if H.number_of_nodes() else 0
    rows.append({
        "Substation": name[n], "Region": region[n], "Degree": deg[n],
        "Betweenness": round(btw[n], 3),
        "Components after": comps, "Largest component after": largest,
        "Extra fragments": max(comps - base_components, 0),
        "Nodes cut from giant component": max(base_largest - 1 - largest, 0),
    })
n1_sub = pd.DataFrame(rows).sort_values(
    ["Extra fragments", "Nodes cut from giant component"], ascending=False)
log(n1_sub.to_string(index=False))

# ---------------------------------------------------------------------------
section("5. N-1 contingency analysis - remove one line")
rows = []
for u, v in list(G.edges()):
    H = G.copy()
    H.remove_edge(u, v)
    comps = nx.number_connected_components(H)
    rows.append({
        "Line": f"{name[u]} <-> {name[v]}",
        "Is bridge": (u, v) in bridges or (v, u) in bridges,
        "Components after": comps,
        "Splits network": comps > base_components,
    })
n1_line = pd.DataFrame(rows).sort_values("Splits network", ascending=False)
splitters = n1_line[n1_line["Splits network"]]
log(f"- lines whose loss splits the network: {len(splitters)} of {G.number_of_edges()}")
log(splitters.to_string(index=False) if len(splitters)
    else "- none: every single line loss leaves the grid connected")

# ---------------------------------------------------------------------------
section("6. Contingency impact chart")
fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(n1_sub["Substation"], n1_sub["Nodes cut from giant component"],
       color="#e53e3e", label="Nodes cut from giant component")
ax.bar(n1_sub["Substation"], n1_sub["Extra fragments"],
       bottom=n1_sub["Nodes cut from giant component"],
       color="#dd6b20", label="Extra fragments created")
ax.set_title("N-1 Contingency: Impact of Removing Each Candidate Substation")
ax.set_ylabel("Impact (node count / fragment count)")
plt.xticks(rotation=55, ha="right")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "n1_contingency_impact.png"), dpi=120)
plt.close(fig)
log(f"- saved `{os.path.join(CHART_DIR, 'n1_contingency_impact.png')}`")

# ---------------------------------------------------------------------------
section("7. Interpretation")
worst = n1_sub.iloc[0]
if worst["Extra fragments"] == 0 and worst["Nodes cut from giant component"] == 0:
    log("In this seeded dataset the regional network is well meshed: removing any "
        "single high-centrality substation does not fragment the grid.")
else:
    log(f"The most damaging single-substation loss is **{worst['Substation']}** "
        f"({worst['Region']}): it creates {int(worst['Extra fragments'])} extra "
        f"fragment(s) and cuts {int(worst['Nodes cut from giant component'])} "
        f"substation(s) from the main connected grid.")
log(f"\n{len(splitters)} individual line(s) are single points of failure. These map "
    "onto the bridge edges and are the lines a real operator would be most cautious "
    "about de-energising for maintenance.")
log("\n*This is a graph-topology approximation of N-1 analysis. It ignores load flow, "
    "thermal limits, voltage stability, and protection behaviour - a real contingency "
    "study models all of those.*")

with open(os.path.join(NET_DIR, "n1_contingency_report.md"), "w", encoding="utf-8") as f:
    f.write("# N-1 Contingency Analysis Report\n")
    f.write("National Electricity Grid Network Analysis - issue #3\n")
    f.write("\n".join(report))
n1_sub.to_csv(os.path.join(NET_DIR, "n1_substation_impact.csv"), index=False)
n1_line.to_csv(os.path.join(NET_DIR, "n1_line_impact.csv"), index=False)
print("\nN-1 contingency analysis complete.")
