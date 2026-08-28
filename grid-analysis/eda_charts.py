"""
Task 3: Exploratory Data Analysis and Saved Charts
National Electricity Grid Network Analysis - Course Project

Reads the cleaned datasets, answers the EDA questions from the project brief,
and saves publication-quality charts as PNG files in charts/.

Outputs:
  charts/eda_substations_by_region.png
  charts/eda_voltage_levels.png
  charts/eda_lines_per_utility.png
  charts/eda_capacity_distribution.png
  charts/eda_infrastructure_age_by_region.png
  charts/eda_line_status.png
  charts/eda_top_connected_substations.png
  charts/eda_capacity_vs_voltage.png
  charts/eda_report.md
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless / no display needed
import matplotlib.pyplot as plt

try:
    import seaborn as sns
    sns.set_theme(style="whitegrid")
    HAVE_SNS = True
except ImportError:  # seaborn is optional - fall back to matplotlib styling
    plt.style.use("ggplot")
    HAVE_SNS = False

DATA_DIR = "cleaned_data"
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

report_lines = []


def log(msg=""):
    print(msg)
    report_lines.append(msg)


def section(title):
    log(f"\n## {title}\n")


def save(fig, name):
    path = os.path.join(CHART_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    log(f"- saved `{path}`")


# ---------------------------------------------------------------------------
section("1. Load cleaned data")
utilities = pd.read_csv(os.path.join(DATA_DIR, "utilities_clean.csv"))
substations = pd.read_csv(os.path.join(DATA_DIR, "substations_clean.csv"))
lines = pd.read_csv(os.path.join(DATA_DIR, "lines_clean.csv"))
utility_name = dict(zip(utilities["Utility ID"], utilities["Alias"]))
log(f"- utilities: {len(utilities)}, substations: {len(substations)}, lines: {len(lines)}")

# ---------------------------------------------------------------------------
section("2. Descriptive statistics (numeric columns)")
log("**Substations**\n")
log(substations[["Latitude", "Longitude", "Voltage (kV)", "Capacity (MVA)",
                 "Commissioning Year"]].describe().round(2).to_string())
log("\n**Lines**\n")
log(lines[["Voltage (kV)", "Length (km)", "Capacity (MVA)"]].describe().round(2).to_string())

# ---------------------------------------------------------------------------
section("3. Q: Which regions have the most substations?")
by_region = substations["Region"].value_counts()
log(by_region.to_string())
fig, ax = plt.subplots(figsize=(10, 5))
by_region.plot(kind="bar", ax=ax, color="#2b6cb0")
ax.set_title("Substations by Region")
ax.set_xlabel("Region")
ax.set_ylabel("Number of substations")
save(fig, "eda_substations_by_region.png")

# ---------------------------------------------------------------------------
section("4. Q: Which voltage levels are most common?")
volts = substations["Voltage (kV)"].value_counts().sort_index()
log(volts.to_string())
fig, ax = plt.subplots(figsize=(8, 5))
volts.plot(kind="bar", ax=ax, color="#805ad5")
ax.set_title("Substation Count by Nominal Voltage Level")
ax.set_xlabel("Voltage (kV)")
ax.set_ylabel("Number of substations")
save(fig, "eda_voltage_levels.png")

# ---------------------------------------------------------------------------
section("5. Q: Which utility operates the most lines?")
lines_per_util = lines["Utility ID"].map(utility_name).value_counts()
log(lines_per_util.to_string())
fig, ax = plt.subplots(figsize=(8, 5))
lines_per_util.plot(kind="bar", ax=ax, color="#dd6b20")
ax.set_title("Lines Operated per Utility")
ax.set_xlabel("Utility")
ax.set_ylabel("Number of lines")
save(fig, "eda_lines_per_utility.png")

# ---------------------------------------------------------------------------
section("6. Q: What is the distribution of substation capacities?")
log(substations["Capacity (MVA)"].describe().round(2).to_string())
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(substations["Capacity (MVA)"], bins=15, color="#38a169", edgecolor="white")
ax.set_title("Distribution of Substation Rated Capacity")
ax.set_xlabel("Capacity (MVA)")
ax.set_ylabel("Number of substations")
save(fig, "eda_capacity_distribution.png")

# ---------------------------------------------------------------------------
section("7. Q: Which regions contain the oldest infrastructure?")
age = substations.groupby("Region")["Commissioning Year"].agg(["min", "median", "max"]).sort_values("min")
log(age.to_string())
fig, ax = plt.subplots(figsize=(10, 5))
age["min"].plot(kind="bar", ax=ax, color="#718096")
ax.set_title("Oldest Substation (min commissioning year) by Region")
ax.set_xlabel("Region")
ax.set_ylabel("Earliest commissioning year")
save(fig, "eda_infrastructure_age_by_region.png")

# ---------------------------------------------------------------------------
section("8. Q: What proportion of lines are active vs under maintenance?")
status = lines["Status"].value_counts()
status_pct = (status / status.sum() * 100).round(1)
log(status_pct.astype(str).add(" %").to_string())
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(status, labels=status.index, autopct="%1.1f%%",
       colors=["#3182ce", "#e53e3e"], startangle=90)
ax.set_title("Line Operational Status")
save(fig, "eda_line_status.png")

# ---------------------------------------------------------------------------
section("9. Q: Which substations have the most connections?")
conn = pd.concat([lines["Source Substation ID"], lines["Destination Substation ID"]]).value_counts()
name_by_id = dict(zip(substations["Substation ID"], substations["Short Name"]))
conn_named = conn.head(10).rename(index=name_by_id)
log(conn_named.to_string())
fig, ax = plt.subplots(figsize=(10, 5))
conn_named[::-1].plot(kind="barh", ax=ax, color="#d53f8c")
ax.set_title("Top 10 Substations by Number of Connecting Lines")
ax.set_xlabel("Number of lines")
save(fig, "eda_top_connected_substations.png")

# ---------------------------------------------------------------------------
section("10. Q: How are high-capacity substations distributed by voltage?")
fig, ax = plt.subplots(figsize=(9, 5))
for v in sorted(substations["Voltage (kV)"].unique()):
    sub = substations[substations["Voltage (kV)"] == v]
    ax.scatter(sub["Voltage (kV)"], sub["Capacity (MVA)"], label=f"{v} kV", alpha=0.7)
ax.set_title("Substation Capacity vs Voltage Level")
ax.set_xlabel("Voltage (kV)")
ax.set_ylabel("Capacity (MVA)")
ax.legend()
save(fig, "eda_capacity_vs_voltage.png")

# ---------------------------------------------------------------------------
section("11. Key findings")
log(f"- **{by_region.index[0]}** has the most substations ({by_region.iloc[0]}).")
log(f"- **{volts.idxmax()} kV** is the most common substation voltage level.")
log(f"- **{lines_per_util.index[0]}** operates the most lines ({lines_per_util.iloc[0]}).")
log(f"- Median substation capacity is **{substations['Capacity (MVA)'].median():.1f} MVA**; "
    f"the distribution is right-skewed (a few large transmission substations).")
log(f"- The oldest infrastructure sits in **{age.index[0]}** "
    f"(commissioned {int(age['min'].iloc[0])}).")
log(f"- **{status_pct.iloc[0]}%** of lines are `{status_pct.index[0]}`; "
    f"the rest are under maintenance.")
log(f"- **{conn_named.index[0]}** is the most-connected substation "
    f"({int(conn_named.iloc[0])} lines).")
log("\n*All figures come from the seeded synthetic dataset (`random.seed(42)`) "
    "and are illustrative, not official grid measurements.*")

with open(os.path.join(CHART_DIR, "eda_report.md"), "w", encoding="utf-8") as f:
    f.write("# Exploratory Data Analysis Report\n")
    f.write("National Electricity Grid Network Analysis - Task 3\n")
    f.write("\n".join(report_lines))

print(f"\nEDA report written to {os.path.join(CHART_DIR, 'eda_report.md')}")
