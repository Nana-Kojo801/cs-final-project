"""
Task 1.3: Data Integration and Relationship Mapping
National Electricity Grid Network Analysis - Course Project

Joins the three cleaned grid datasets (utilities, substations, lines) into a
single master dataset keyed on Line ID, using Utility ID / Substation ID as
foreign keys, validates the join for data loss, and writes:
  - integrated_data/merged_lines.csv   (one row per line, with source/destination
    substation details and operating-utility details attached)
  - integrated_data/integration_report.md
"""

import os
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 140)

DATA_DIR = 'cleaned_data'
OUTPUT_DIR = 'integrated_data'
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
log(f"- lines: {len(lines)} rows (this is the join's base table - one row per line)")

# Lookup dictionaries, built once, for O(1) access when the DataFrame merges
# below aren't the right tool (e.g. building the NetworkX graph in task 2).
substation_by_id = substations.set_index('Substation ID').to_dict(orient='index')
utility_by_id = utilities.set_index('Utility ID').to_dict(orient='index')
log(f"- Built lookup dicts: substation_by_id ({len(substation_by_id)} entries), "
    f"utility_by_id ({len(utility_by_id)} entries)")

# ---------------------------------------------------------------------------
# STEP 2: JOIN LINES -> SOURCE SUBSTATION -> DESTINATION SUBSTATION -> UTILITY
# ---------------------------------------------------------------------------
section("2. Joining datasets")

sub_cols = ['Substation ID', 'Name', 'Region', 'Country', 'Voltage (kV)', 'Capacity (MVA)', 'Status']

before_rows = len(lines)

merged = lines.merge(
    substations[sub_cols].add_prefix('Source '), left_on='Source Substation ID',
    right_on='Source Substation ID', how='left'
)
merged = merged.merge(
    substations[sub_cols].add_prefix('Destination '), left_on='Destination Substation ID',
    right_on='Destination Substation ID', how='left'
)
merged = merged.merge(
    utilities[['Utility ID', 'Name', 'Alias', 'Code', 'Type', 'Country']].add_prefix('Utility '),
    left_on='Utility ID', right_on='Utility Utility ID', how='left'
).drop(columns='Utility Utility ID')

after_rows = len(merged)
log(f"- Rows before join: {before_rows}")
log(f"- Rows after join: {after_rows}")
log(f"- Row count changed by join: {'yes - investigate' if after_rows != before_rows else 'no (expected for a left join with valid FKs)'}")

missing_source = merged['Source Name'].isnull().sum()
missing_dest = merged['Destination Name'].isnull().sum()
missing_utility = merged['Utility Name'].isnull().sum()
log(f"- Lines that failed to match a source substation: {missing_source}")
log(f"- Lines that failed to match a destination substation: {missing_dest}")
log(f"- Lines that failed to match a utility: {missing_utility}")
log("(Non-zero counts here would mean an orphaned foreign key slipped through "
    "Task 1 cleaning - see data_cleaning_report.md's foreign-key validation section.)")

# ---------------------------------------------------------------------------
# STEP 3: A DERIVED QUESTION THE MERGE MAKES EASY TO ANSWER
# ---------------------------------------------------------------------------
section("3. Lines by utility and source region")

lines_by_utility_region = (
    merged.groupby(['Utility Code', 'Source Region']).size().reset_index(name='Line Count')
    .sort_values('Line Count', ascending=False)
)
log(lines_by_utility_region.head(10).to_string(index=False))

# ---------------------------------------------------------------------------
# STEP 4: WRITE MERGED DATASET
# ---------------------------------------------------------------------------
merged_path = os.path.join(OUTPUT_DIR, 'merged_lines.csv')
merged.to_csv(merged_path, index=False)

section("4. Output")
log(f"Merged dataset written to {merged_path} ({len(merged)} rows, {len(merged.columns)} columns)")

report_path = os.path.join(OUTPUT_DIR, 'integration_report.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# Data Integration Report\n")
    f.write("National Electricity Grid Network Analysis - Task 1.3\n")
    f.write("\n".join(report_lines))

print(f"\nReport written to {report_path}")
