"""
Task 2: Network Modelling with NetworkX
National Electricity Grid Network Analysis - Course Project

Loads the cleaned grid datasets, runs exploratory data analysis, builds a
NetworkX graph of the grid (substations = nodes, lines = edges), computes
network metrics, and writes:
  - network_analysis/network_metrics.csv   (per-node metrics)
  - network_analysis/network_analysis_report.md
  - network_analysis/n1_contingency_results.csv
  - network_analysis/n1_contingency_report.md
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
# STEP 5: N-1 CONTINGENCY ANALYSIS
# ---------------------------------------------------------------------------
section("5. N-1 contingency analysis")

# The graph may already contain isolated or separate components. To keep the
# comparison fair, every scenario uses the same whole-graph measures and
# computes average shortest path length within that scenario's largest
# connected component.
def summarize_topology(graph):
    components = list(nx.connected_components(graph))
    largest_component = max(components, key=len) if components else set()
    largest_subgraph = graph.subgraph(largest_component)
    avg_path = (
        nx.average_shortest_path_length(largest_subgraph, weight='length_km')
        if len(largest_component) > 1
        else 0.0
    )
    return {
        'connected_components': len(components),
        'largest_component_size': len(largest_component),
        'isolated_nodes': sum(1 for component in components if len(component) == 1),
        # NetworkX global_efficiency uses unweighted reachability; the
        # length-weighted metric is reported separately below.
        'global_efficiency': nx.global_efficiency(graph),
        'avg_shortest_path_km': avg_path,
        'bridge_count': len(list(nx.bridges(graph))),
    }


def pct_change(before, after):
    if before == 0:
        return 0.0
    return ((after - before) / before) * 100


baseline_topology = summarize_topology(G)
node_candidates = metrics.head(3)['Substation ID'].tolist()
edge_betweenness = nx.edge_betweenness_centrality(G, weight='length_km')
edge_candidates = sorted(
    edge_betweenness,
    key=edge_betweenness.get,
    reverse=True,
)[:3]

contingency_rows = [{
    'Scenario': 'Baseline',
    'Failure Type': 'None',
    'Failed Asset ID': '',
    'Failed Asset': 'All assets available',
    'Connected Components': baseline_topology['connected_components'],
    'Largest Component Size': baseline_topology['largest_component_size'],
    'Isolated Nodes': baseline_topology['isolated_nodes'],
    'Global Efficiency': round(baseline_topology['global_efficiency'], 6),
    'Average Shortest Path (km)': round(baseline_topology['avg_shortest_path_km'], 4),
    'Bridge Count': baseline_topology['bridge_count'],
    'Efficiency Change (%)': 0.0,
    'Average Path Change (%)': 0.0,
}]

for node in node_candidates:
    scenario_graph = G.copy()
    scenario_graph.remove_node(node)
    after = summarize_topology(scenario_graph)
    contingency_rows.append({
        'Scenario': f'Remove substation {node}',
        'Failure Type': 'Substation removal',
        'Failed Asset ID': node,
        'Failed Asset': G.nodes[node]['name'],
        'Connected Components': after['connected_components'],
        'Largest Component Size': after['largest_component_size'],
        'Isolated Nodes': after['isolated_nodes'],
        'Global Efficiency': round(after['global_efficiency'], 6),
        'Average Shortest Path (km)': round(after['avg_shortest_path_km'], 4),
        'Bridge Count': after['bridge_count'],
        'Efficiency Change (%)': round(pct_change(
            baseline_topology['global_efficiency'],
            after['global_efficiency'],
        ), 2),
        'Average Path Change (%)': round(pct_change(
            baseline_topology['avg_shortest_path_km'],
            after['avg_shortest_path_km'],
        ), 2),
    })

for source, destination in edge_candidates:
    edge_data = G[source][destination]
    scenario_graph = G.copy()
    scenario_graph.remove_edge(source, destination)
    after = summarize_topology(scenario_graph)
    contingency_rows.append({
        'Scenario': f"Remove line {edge_data['line_id']}",
        'Failure Type': 'Line removal',
        'Failed Asset ID': edge_data['line_id'],
        'Failed Asset': (
            f"{G.nodes[source]['name']} <-> {G.nodes[destination]['name']}"
        ),
        'Connected Components': after['connected_components'],
        'Largest Component Size': after['largest_component_size'],
        'Isolated Nodes': after['isolated_nodes'],
        'Global Efficiency': round(after['global_efficiency'], 6),
        'Average Shortest Path (km)': round(after['avg_shortest_path_km'], 4),
        'Bridge Count': after['bridge_count'],
        'Efficiency Change (%)': round(pct_change(
            baseline_topology['global_efficiency'],
            after['global_efficiency'],
        ), 2),
        'Average Path Change (%)': round(pct_change(
            baseline_topology['avg_shortest_path_km'],
            after['avg_shortest_path_km'],
        ), 2),
    })

contingency_results = pd.DataFrame(contingency_rows)
contingency_results_path = os.path.join(OUTPUT_DIR, 'n1_contingency_results.csv')
contingency_results.to_csv(contingency_results_path, index=False)
log(f"- N-1 comparison written to {contingency_results_path}")
log("\n**N-1 before/after comparison**\n")
log(contingency_results.to_string(index=False))

n1_report_path = os.path.join(OUTPUT_DIR, 'n1_contingency_report.md')
with open(n1_report_path, 'w', encoding='utf-8') as f:
    f.write('# N-1 Contingency Analysis Report\n')
    f.write('National Electricity Grid Network Analysis - Issue #3\n\n')
    f.write('## Method\n\n')
    f.write(
        'Candidate substations were selected from the three highest '
        'betweenness-centrality scores in the network metrics. Candidate '
        'lines were selected from the three highest weighted edge '
        'betweenness-centrality scores. Each candidate was removed from a '
        'copy of the graph, then connected components, largest component '
        'size, isolated nodes, global efficiency, bridge count, and average '
        'shortest path within the largest connected component were recomputed.\n\n'
    )
    f.write('## Before/after results\n\n')
    f.write(contingency_results.to_markdown(index=False))
    f.write('\n\n## Interpretation\n\n')
    f.write(
        'The comparison shows how structurally important assets affect the '
        'resilience of this graph. The global efficiency value is the '
        'unweighted NetworkX reachability measure. A decrease in global '
        'efficiency indicates '
        'that remaining substations become less reachable on average. An '
        'increase in connected components or isolated nodes indicates '
        'fragmentation, while a smaller largest component indicates that a '
        'larger share of the network has been separated from the main group. '
        'The results should be read alongside the candidate centrality '
        'scores rather than treated as a prediction of electrical service '
        'loss.\n\n'
    )
    f.write(
        '> This is a graph-based educational approximation. It is not a '
        'substitute for real power-flow, transient-stability, or '
        'protection-coordination studies.\n'
    )
log(f"- Dedicated N-1 report written to {n1_report_path}")

# ---------------------------------------------------------------------------
# STEP 6: INTERPRETATION
# ---------------------------------------------------------------------------
section("6. Interpretation")

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
