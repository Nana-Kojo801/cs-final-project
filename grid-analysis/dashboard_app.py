"""
Grid Analysis Interactive Dashboard (Streamlit)
National Electricity Grid Network Analysis - Course Project, Task 3.1

Run:  streamlit run dashboard_app.py
(from the grid-analysis/ folder, after task1..task5 have generated cleaned_data/,
integrated_data/, network_analysis/ and maps/)

Tabs: Overview | Network | Geography | Reliability | Search
"""

import os
import pandas as pd
import networkx as nx
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

DATA_DIR = "cleaned_data"
NET_DIR = "network_analysis"
MAP_DIR = "maps"

st.set_page_config(page_title="National Grid Analysis", layout="wide")


@st.cache_data
def load():
    u = pd.read_csv(os.path.join(DATA_DIR, "utilities_clean.csv"))
    s = pd.read_csv(os.path.join(DATA_DIR, "substations_clean.csv"))
    ln = pd.read_csv(os.path.join(DATA_DIR, "lines_clean.csv"))
    metrics_path = os.path.join(NET_DIR, "network_metrics.csv")
    m = pd.read_csv(metrics_path) if os.path.exists(metrics_path) else None
    return u, s, ln, m


utilities, substations, lines, metrics = load()
alias = dict(zip(utilities["Utility ID"], utilities["Alias"]))

st.title("National Electricity Grid Network Analysis")
st.caption("Seeded synthetic dataset (random.seed(42)) - illustrative, not official grid data.")

# sidebar filters
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", sorted(substations["Region"].unique()),
                                 default=list(sorted(substations["Region"].unique())))
volts = st.sidebar.multiselect("Voltage (kV)", sorted(substations["Voltage (kV)"].unique()),
                               default=list(sorted(substations["Voltage (kV)"].unique())))
sub_f = substations[substations["Region"].isin(regions) & substations["Voltage (kV)"].isin(volts)]
ids = set(sub_f["Substation ID"])
line_f = lines[lines["Source Substation ID"].isin(ids) | lines["Destination Substation ID"].isin(ids)]

tab_over, tab_net, tab_geo, tab_rel, tab_search = st.tabs(
    ["Overview", "Network", "Geography", "Reliability", "Search"])

with tab_over:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Substations", len(sub_f))
    c2.metric("Lines", len(line_f))
    c3.metric("Utilities", utilities["Active"].eq("Y").sum())
    c4.metric("Total capacity (MVA)", f"{sub_f['Capacity (MVA)'].sum():,.0f}")
    c5, c6 = st.columns(2)
    c5.plotly_chart(px.bar(sub_f["Region"].value_counts().sort_values(),
                           orientation="h", title="Substations by region"),
                    use_container_width=True)
    c6.plotly_chart(px.histogram(sub_f, x="Capacity (MVA)", nbins=15,
                                 title="Substation capacity distribution"),
                    use_container_width=True)

with tab_net:
    G = nx.Graph()
    for _, r in sub_f.iterrows():
        G.add_node(r["Substation ID"], name=r["Short Name"])
    for _, r in line_f.iterrows():
        if r["Source Substation ID"] in G and r["Destination Substation ID"] in G:
            G.add_edge(r["Source Substation ID"], r["Destination Substation ID"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Graph nodes", G.number_of_nodes())
    c2.metric("Graph edges", G.number_of_edges())
    c3.metric("Connected components", nx.number_connected_components(G) if G.number_of_nodes() else 0)
    if metrics is not None:
        st.subheader("Per-substation network metrics")
        st.dataframe(metrics[metrics["Substation ID"].isin(ids)], use_container_width=True)
    n1 = os.path.join(NET_DIR, "n1_substation_impact.csv")
    if os.path.exists(n1):
        st.subheader("N-1 contingency (substation removal)")
        st.dataframe(pd.read_csv(n1), use_container_width=True)

with tab_geo:
    fig = px.scatter_geo(sub_f, lat="Latitude", lon="Longitude", color="Region",
                         size="Capacity (MVA)", hover_name="Name", scope="africa")
    fig.update_geos(center=dict(lat=8, lon=-1), projection_scale=6, showcountries=True)
    st.plotly_chart(fig, use_container_width=True)
    html_map = os.path.join(MAP_DIR, "grid_interactive_map.html")
    if os.path.exists(html_map):
        with open(html_map, encoding="utf-8") as f:
            components.html(f.read(), height=600, scrolling=True)

with tab_rel:
    line_f = line_f.copy()
    line_f["Utility"] = line_f["Utility ID"].map(alias)
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.pie(line_f, names="Status", title="Line status"),
                    use_container_width=True)
    c2.plotly_chart(px.bar(line_f.groupby("Utility")["Capacity (MVA)"].sum().sort_values(),
                           orientation="h", title="Rated capacity carried per utility"),
                    use_container_width=True)
    st.plotly_chart(px.box(sub_f, x="Region", y="Commissioning Year",
                           title="Asset age by region"), use_container_width=True)

with tab_search:
    q = st.text_input("Search substation name")
    res = sub_f[sub_f["Name"].str.contains(q, case=False, na=False)] if q else sub_f
    st.dataframe(res, use_container_width=True)
    u1, u2 = st.columns(2)
    a = u1.selectbox("Utility A", utilities["Alias"])
    b = u2.selectbox("Utility B", utilities["Alias"], index=min(2, len(utilities) - 1))
    comp = []
    for name in (a, b):
        uid = utilities.loc[utilities["Alias"] == name, "Utility ID"].iloc[0]
        ul = lines[lines["Utility ID"] == uid]
        comp.append({"Utility": name, "Lines": len(ul),
                     "Capacity (MVA)": ul["Capacity (MVA)"].sum(),
                     "Avg length (km)": round(ul["Length (km)"].mean(), 1) if len(ul) else 0})
    st.table(pd.DataFrame(comp))
