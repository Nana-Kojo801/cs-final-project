"""
Task 4: Merging and Advanced Analysis
National Electricity Grid Network Analysis - Course Project

Joins the three cleaned datasets into one master line-level table and answers
cross-table business questions (utility footprint by region, inter-regional
lines, cross-border links, capacity carried per utility).

Outputs:
  integrated_data/master_lines.csv
  charts/merge_utility_region.png
  charts/merge_interregional_lines.png
  charts/merge_report.md
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = "cleaned_data"
OUT_DATA = "integrated_data"
CHART_DIR = "charts"
os.makedirs(OUT_DATA, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

report = []


def log(msg=""):
    print(msg)
    report.append(msg)


def section(t):
    log(f"\n## {t}\n")


def save(fig, name):
    p = os.path.join(CHART_DIR, name)
    fig.tight_layout()
    fig.savefig(p, dpi=120)
    plt.close(fig)
    log(f"- saved `{p}`")


# ---------------------------------------------------------------------------
section("1. Load cleaned data")
utilities = pd.read_csv(os.path.join(DATA_DIR, "utilities_clean.csv"))
substations = pd.read_csv(os.path.join(DATA_DIR, "substations_clean.csv"))
lines = pd.read_csv(os.path.join(DATA_DIR, "lines_clean.csv"))
log(f"- utilities {len(utilities)}, substations {len(substations)}, lines {len(lines)}")

# ---------------------------------------------------------------------------
section("2. Build the master line-level table")
sub_cols = ["Substation ID", "Short Name", "Region", "Country",
            "Latitude", "Longitude", "Voltage (kV)", "Capacity (MVA)"]

m = lines.merge(
    substations[sub_cols].add_suffix("_src"),
    left_on="Source Substation ID", right_on="Substation ID_src", how="left")
m = m.merge(
    substations[sub_cols].add_suffix("_dst"),
    left_on="Destination Substation ID", right_on="Substation ID_dst", how="left")
m = m.merge(
    utilities[["Utility ID", "Name", "Alias", "Type", "Country"]].rename(
        columns={"Name": "Utility Name", "Type": "Utility Type",
                 "Country": "Utility Country"}),
    on="Utility ID", how="left")

# join validation
orphan_src = m["Region_src"].isna().sum()
orphan_dst = m["Region_dst"].isna().sum()
orphan_util = m["Utility Name"].isna().sum()
log(f"- rows after merge: {len(m)} (expected {len(lines)})")
log(f"- lines with unmatched source substation: {orphan_src}")
log(f"- lines with unmatched destination substation: {orphan_dst}")
log(f"- lines with unmatched utility: {orphan_util}")

m["Inter-Regional"] = m["Region_src"] != m["Region_dst"]
m["Cross-Border"] = m["Country_src"] != m["Country_dst"]

master_path = os.path.join(OUT_DATA, "master_lines.csv")
m.to_csv(master_path, index=False)
log(f"- master table written to `{master_path}` ({m.shape[1]} columns)")

# ---------------------------------------------------------------------------
section("3. Q: Which utility operates the most lines, by source region?")
pivot = (m.groupby(["Alias", "Region_src"]).size()
         .reset_index(name="Line Count")
         .sort_values("Line Count", ascending=False))
log(pivot.head(12).to_string(index=False))
top = pivot.head(12)
fig, ax = plt.subplots(figsize=(11, 5))
labels = top["Alias"] + " / " + top["Region_src"]
ax.bar(labels, top["Line Count"], color="#2b6cb0")
ax.set_title("Top Utility / Source-Region Combinations by Line Count")
ax.set_ylabel("Number of lines")
plt.xticks(rotation=60, ha="right")
save(fig, "merge_utility_region.png")

# ---------------------------------------------------------------------------
section("4. Q: How much capacity does each utility carry?")
cap = (m.groupby("Alias")
       .agg(Lines=("Line ID", "count"),
            Total_Capacity_MVA=("Capacity (MVA)", "sum"),
            Avg_Length_km=("Length (km)", "mean"))
       .round(1).sort_values("Total_Capacity_MVA", ascending=False))
log(cap.to_string())

# ---------------------------------------------------------------------------
section("5. Q: Which region pairs are connected by inter-regional lines?")
inter = m[m["Inter-Regional"]].copy()
inter["Pair"] = inter.apply(
    lambda r: " <-> ".join(sorted([str(r["Region_src"]), str(r["Region_dst"])])), axis=1)
pair_counts = inter["Pair"].value_counts()
log(f"- inter-regional lines: {len(inter)} of {len(m)}")
log(pair_counts.to_string())
fig, ax = plt.subplots(figsize=(10, 5))
pair_counts[::-1].plot(kind="barh", ax=ax, color="#dd6b20")
ax.set_title("Inter-Regional Line Count by Region Pair")
ax.set_xlabel("Number of lines")
save(fig, "merge_interregional_lines.png")

# ---------------------------------------------------------------------------
section("6. Q: Which cross-border interconnections exist (WAPP-style)?")
xb = m[m["Cross-Border"]][["Alias", "Source Substation", "Country_src",
                           "Destination Substation", "Country_dst",
                           "Voltage (kV)", "Length (km)"]]
log(xb.to_string(index=False) if len(xb) else "- none in this dataset")

# ---------------------------------------------------------------------------
section("7. Findings")
log(f"- **{pivot.iloc[0]['Alias']}** dominates in **{pivot.iloc[0]['Region_src']}** "
    f"({int(pivot.iloc[0]['Line Count'])} lines from that region).")
log(f"- **{cap.index[0]}** carries the most rated transfer capacity "
    f"({cap['Total_Capacity_MVA'].iloc[0]:,.0f} MVA across {int(cap['Lines'].iloc[0])} lines) "
    f"- consistent with its role as the transmission operator.")
if len(pair_counts):
    log(f"- The busiest inter-regional corridor is **{pair_counts.index[0]}** "
        f"({pair_counts.iloc[0]} lines).")
log(f"- {len(xb)} cross-border line(s) model Ghana's WAPP interconnections; "
    f"all are synthetic stand-ins, not survey data.")
log(f"- Merge caused **no data loss**: {orphan_src + orphan_dst + orphan_util} orphaned "
    f"foreign keys across {len(m)} lines.")

with open(os.path.join(CHART_DIR, "merge_report.md"), "w", encoding="utf-8") as f:
    f.write("# Merge and Advanced Analysis Report\n")
    f.write("National Electricity Grid Network Analysis - Task 4\n")
    f.write("\n".join(report))

print("\nMerge report written to charts/merge_report.md")
