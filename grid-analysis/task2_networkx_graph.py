"""
Task 2: Network Modelling with NetworkX
National Electricity Grid Network Analysis - Course Project

Loads the cleaned grid datasets, runs exploratory data analysis, builds a
NetworkX graph of the grid (substations = nodes, lines = edges), computes
network metrics, and writes:
  - network_analysis/network_metrics.csv   (per-node metrics)
  - network_analysis/network_analysis_report.md
"""

import os
import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 140)

DATA_DIR = 'cleaned_data'
OUTPUT_DIR = 'network_analysis'
os.makedirs(OUTPUT_DIR, exist_ok=True)

report_lines = []


def log(msg=""):
    print(msg)
    report_lines.append(msg)


def section(title):
    log(f"\n## {title}\n")


# ---------------------------------------------------------------------------
# STEP 1: LOAD CLEANED DATA
# ---------------------------------------------------------------------------
section("1. Loading cleaned data")

utilities = pd.read_csv(os.path.join(DATA_DIR, 'utilities_clean.csv'))
substations = pd.read_csv(os.path.join(DATA_DIR, 'substations_clean.csv'))
lines = pd.read_csv(os.path.join(DATA_DIR, 'lines_clean.csv'))

log(f"- utilities: {len(utilities)} rows")
log(f"- substations: {len(substations)} rows")
log(f"- lines: {len(lines)} rows")

utility_name_by_id = dict(zip(utilities['Utility ID'], utilities['Name']))

# ---------------------------------------------------------------------------
# STEP 2: EXPLORATORY DATA ANALYSIS (pre-graph)
# ---------------------------------------------------------------------------
section("2. Exploratory data analysis")

log("**Substations per region**\n")
log(substations['Region'].value_counts().to_string())

log("\n**Most common voltage levels (substations)**\n")
log(substations['Voltage (kV)'].value_counts().sort_index(ascending=False).to_string())

log("\n**Lines operated per utility**\n")
lines_per_utility = lines['Utility ID'].map(utility_name_by_id).value_counts()
log(lines_per_utility.to_string())

log("\n**Substation capacity distribution (MVA)**\n")
log(substations['Capacity (MVA)'].describe().to_string())

log("\n**Oldest infrastructure by region (min commissioning year)**\n")
log(substations.groupby('Region')['Commissioning Year'].min().sort_values().to_string())

log("\n**Line status proportions**\n")
line_status_pct = (lines['Status'].value_counts(normalize=True) * 100).round(1)
log(line_status_pct.astype(str).add(' %').to_string())

log("\n**Most-connected substations (by raw line count, pre-graph)**\n")
line_counts = pd.concat([
    lines['Source Substation ID'],
    lines['Destination Substation ID']
]).value_counts().head(10)
line_counts.index.name = 'Substation ID'
name_by_id = dict(zip(substations['Substation ID'], substations['Name']))
top_connected = line_counts.rename('Line Count').to_frame()
top_connected['Name'] = top_connected.index.map(name_by_id)
log(top_connected[['Name', 'Line Count']].to_string())

# ---------------------------------------------------------------------------
# STEP 3: BUILD THE GRAPH
# ---------------------------------------------------------------------------
section("3. Building the graph")

G = nx.Graph()

for _, row in substations.iterrows():
    G.add_node(
        row['Substation ID'],
        name=row['Name'],
        region=row['Region'],
        voltage_kv=row['Voltage (kV)'],
        capacity_mva=row['Capacity (MVA)'],
        status=row['Status'],
        type=row['Type'],
    )

# Substations don't carry a utility column directly - ownership is inferred
# from which utilities operate lines that touch each substation.
utilities_by_substation = {sid: set() for sid in G.nodes}

for _, row in lines.iterrows():
    src, dst = row['Source Substation ID'], row['Destination Substation ID']
    utility_name = utility_name_by_id.get(row['Utility ID'], 'Unknown')
    utilities_by_substation[src].add(utility_name)
    utilities_by_substation[dst].add(utility_name)
    G.add_edge(
        src, dst,
        line_id=row['Line ID'],
        length_km=row['Length (km)'],
        capacity_mva=row['Capacity (MVA)'],
        voltage_kv=row['Voltage (kV)'],
        status=row['Status'],
        line_type=row['Line Type'],
        utility=utility_name,
    )

for sid, utils in utilities_by_substation.items():
    G.nodes[sid]['utilities'] = ', '.join(sorted(utils)) if utils else 'None'

log(f"- Nodes (substations): {G.number_of_nodes()}")
log(f"- Edges (lines): {G.number_of_edges()}")
log(f"- Isolated substations (no lines): {list(nx.isolates(G))}")

# ---------------------------------------------------------------------------
# STEP 4: NETWORK METRICS
# ---------------------------------------------------------------------------
section("4. Network metrics")

degree = dict(G.degree())
degree_centrality = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(G, weight='length_km')
closeness = nx.closeness_centrality(G)
pagerank = nx.pagerank(G, weight='capacity_mva')
clustering = nx.clustering(G)

metrics = pd.DataFrame({
    'Substation ID': list(G.nodes),
    'Name': [G.nodes[n]['name'] for n in G.nodes],
    'Region': [G.nodes[n]['region'] for n in G.nodes],
    'Degree': [degree[n] for n in G.nodes],
    'Degree Centrality': [round(degree_centrality[n], 4) for n in G.nodes],
    'Betweenness Centrality': [round(betweenness[n], 4) for n in G.nodes],
    'Closeness Centrality': [round(closeness[n], 4) for n in G.nodes],
    'PageRank': [round(pagerank[n], 4) for n in G.nodes],
    'Clustering Coefficient': [round(clustering[n], 4) for n in G.nodes], # type: ignore
}).sort_values('Betweenness Centrality', ascending=False)

metrics_path = os.path.join(OUTPUT_DIR, 'network_metrics.csv')
metrics.to_csv(metrics_path, index=False)
log(f"- Per-node metrics written to {metrics_path}")

log("\n**Top 10 substations by betweenness centrality**\n")
log(metrics.head(10).to_string(index=False))

log("\n**Top 10 substations by PageRank**\n")
log(metrics.sort_values('PageRank', ascending=False).head(10).to_string(index=False))

# Connectivity / topology
components = list(nx.connected_components(G))
largest_cc = max(components, key=len)
bridges = list(nx.bridges(G))
efficiency = nx.global_efficiency(G)

log(f"\n**Connected components**: {len(components)}")
log(f"- Largest component size: {len(largest_cc)} / {G.number_of_nodes()} substations")
if len(components) > 1:
    small = [c for c in components if c != largest_cc]
    log(f"- Smaller components: {[sorted(c) for c in small]}")

log(f"\n**Bridges** (single lines whose removal disconnects the network): {len(bridges)}")
if bridges:
    bridge_rows = []
    for u, v in bridges:
        bridge_rows.append(f"  - {G.nodes[u]['name']} <-> {G.nodes[v]['name']}")
    log("\n".join(bridge_rows))

log(f"\n**Global efficiency**: {round(efficiency, 4)}")

# Shortest paths - average shortest path length within the largest component
subgraph = G.subgraph(largest_cc)
avg_shortest_path = nx.average_shortest_path_length(subgraph, weight='length_km')
log(f"**Average shortest path length** (largest component, weighted by line length km): {round(avg_shortest_path, 2)}")

# Communities
communities = greedy_modularity_communities(G, weight='capacity_mva')
log(f"\n**Communities detected** (greedy modularity): {len(communities)}")
for i, c in enumerate(communities, start=1):
    names = sorted(G.nodes[n]['name'] for n in c)
    log(f"- Community {i} ({len(c)} substations): {', '.join(names)}")

# ---------------------------------------------------------------------------
# STEP 5: INTERPRETATION
# ---------------------------------------------------------------------------
section("5. Interpretation")

log(
    "The metrics above are **structural observations about the graph topology "
    "of a synthetically generated dataset** (`random.seed(42)`), not measurements "
    "of real electrical load, voltage stability, or power flow. High betweenness "
    "or PageRank identifies substations that sit on many shortest connection "
    "paths or are linked to well-connected neighbors - i.e. structurally central "
    "positions in the network graph. In a real grid this would be one input "
    "among many (alongside load-flow studies, protection schemes, and asset "
    "condition) for prioritizing reliability investment, not a standalone answer.\n"
)

top_betweenness = metrics.iloc[0]
log(
    f"The substation with the highest betweenness centrality in this dataset is "
    f"**{top_betweenness['Name']}** ({top_betweenness['Region']}) - flagged here purely "
    f"as a graph-structural reliability proxy: many shortest paths between other "
    f"substation pairs pass through it, so its removal would be expected to lengthen "
    f"or break more routes than removing a peripheral substation. See the N-1 "
    f"contingency analysis task for a direct test of that expectation."
)

if bridges:
    log(
        f"\nThe {len(bridges)} bridge edge(s) identified above are single points of "
        f"failure in this graph: removing any one of them would split the network "
        f"into more components. They are natural candidates to examine first in the "
        f"N-1 contingency analysis."
    )

report_path = os.path.join(OUTPUT_DIR, 'network_analysis_report.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# Network Modelling and Analysis Report\n")
    f.write("National Electricity Grid Network Analysis - Task 2\n")
    f.write("\n".join(report_lines))

print(f"\nReport written to {report_path}")
