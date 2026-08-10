"""
Task 1: Data Cleaning and Preprocessing / Validation
National Electricity Grid Network Analysis - Course Project

Loads utilities.csv, substations.csv, lines.csv, inspects them, cleans them,
validates relationships and geographic bounds, and writes:
  - cleaned CSVs (utilities_clean.csv, substations_clean.csv, lines_clean.csv)
  - a markdown data-cleaning / validation report
"""

import os
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 140)

DATA_DIR = 'Datasets'
OUTPUT_DIR = 'cleaned_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

report_lines = []


def log(msg=""):
    print(msg)
    report_lines.append(msg)


def section(title):
    log(f"\n## {title}\n")


# ---------------------------------------------------------------------------
# STEP 1: LOAD
# ---------------------------------------------------------------------------
section("1. Loading the raw data")

utilities = pd.read_csv(os.path.join(DATA_DIR, 'utilities.csv'))
substations = pd.read_csv(os.path.join(DATA_DIR, 'substations.csv'))
lines = pd.read_csv(os.path.join(DATA_DIR, 'lines.csv'))

log(f"- utilities.csv: {utilities.shape[0]} rows x {utilities.shape[1]} columns")
log(f"- substations.csv: {substations.shape[0]} rows x {substations.shape[1]} columns")
log(f"- lines.csv: {lines.shape[0]} rows x {lines.shape[1]} columns")

# ---------------------------------------------------------------------------
# STEP 2: INITIAL INSPECTION (dtypes, missing values, duplicates)
# ---------------------------------------------------------------------------
section("2. Initial inspection (before cleaning)")

for name, df in [("utilities", utilities), ("substations", substations), ("lines", lines)]:
    log(f"\n**{name}** dtypes:")
    log(df.dtypes.to_string())
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    log(f"\n**{name}** missing values (raw):")
    log(missing.to_string() if len(missing) else "  none found")
    dup_rows = df.duplicated().sum()
    log(f"**{name}** fully duplicated rows: {dup_rows}")

# Also check blank-string / placeholder "missing" indicators, since real asset
# registers often encode missingness as '', ' ', 'NULL', 'N/A', '\\N' rather than
# a true NaN.
placeholder_missing = ['\\N', 'NULL', 'null', 'N/A', 'n/a', '', ' ', 'NA', '-']

section("3. Checking for placeholder-style missing values")
for name, df in [("utilities", utilities), ("substations", substations), ("lines", lines)]:
    obj_cols = df.select_dtypes(include='object').columns
    found_any = False
    for c in obj_cols:
        hits = df[c].astype(str).str.strip().isin(placeholder_missing).sum()
        if hits:
            found_any = True
            log(f"- {name}.{c}: {hits} placeholder-missing values")
    if not found_any:
        log(f"- {name}: no placeholder-missing values found in text columns")

# ---------------------------------------------------------------------------
# STEP 3: DUPLICATE PRIMARY KEYS
# ---------------------------------------------------------------------------
section("4. Duplicate primary-key checks")

dup_util_id = utilities['Utility ID'].duplicated().sum()
dup_sub_id = substations['Substation ID'].duplicated().sum()
dup_line_id = lines['Line ID'].duplicated().sum()
log(f"- Duplicate Utility IDs: {dup_util_id}")
log(f"- Duplicate Substation IDs: {dup_sub_id}")
log(f"- Duplicate Line IDs: {dup_line_id}")

# Duplicate line pairs (same source+destination regardless of Line ID) - could
# indicate an accidental double-entry of the same physical line.
pair_key = lines.apply(
    lambda r: tuple(sorted((r['Source Substation ID'], r['Destination Substation ID']))), axis=1
)
dup_pairs = pair_key.duplicated().sum()
log(f"- Duplicate Source/Destination substation pairs (possible double-logged lines): {dup_pairs}")

# ---------------------------------------------------------------------------
# STEP 4: TYPE COERCION
# ---------------------------------------------------------------------------
section("5. Data-type coercion")

numeric_casts = {
    'substations': {
        'Latitude': substations['Latitude'].dtype,
        'Longitude': substations['Longitude'].dtype,
        'Voltage (kV)': substations['Voltage (kV)'].dtype,
        'Capacity (MVA)': substations['Capacity (MVA)'].dtype,
        'Commissioning Year': substations['Commissioning Year'].dtype,
    },
    'lines': {
        'Voltage (kV)': lines['Voltage (kV)'].dtype,
        'Length (km)': lines['Length (km)'].dtype,
        'Capacity (MVA)': lines['Capacity (MVA)'].dtype,
    }
}

substations['Latitude'] = pd.to_numeric(substations['Latitude'], errors='coerce')
substations['Longitude'] = pd.to_numeric(substations['Longitude'], errors='coerce')
substations['Voltage (kV)'] = pd.to_numeric(substations['Voltage (kV)'], errors='coerce')
substations['Capacity (MVA)'] = pd.to_numeric(substations['Capacity (MVA)'], errors='coerce')
substations['Commissioning Year'] = pd.to_numeric(substations['Commissioning Year'], errors='coerce').astype('Int64')

lines['Voltage (kV)'] = pd.to_numeric(lines['Voltage (kV)'], errors='coerce')
lines['Length (km)'] = pd.to_numeric(lines['Length (km)'], errors='coerce')
lines['Capacity (MVA)'] = pd.to_numeric(lines['Capacity (MVA)'], errors='coerce')

new_nans = {
    'substations.Latitude': substations['Latitude'].isnull().sum(),
    'substations.Longitude': substations['Longitude'].isnull().sum(),
    'substations.Voltage (kV)': substations['Voltage (kV)'].isnull().sum(),
    'substations.Capacity (MVA)': substations['Capacity (MVA)'].isnull().sum(),
    'substations.Commissioning Year': substations['Commissioning Year'].isnull().sum(),
    'lines.Voltage (kV)': lines['Voltage (kV)'].isnull().sum(),
    'lines.Length (km)': lines['Length (km)'].isnull().sum(),
    'lines.Capacity (MVA)': lines['Capacity (MVA)'].isnull().sum(),
}
log("Numeric columns coerced with pd.to_numeric(errors='coerce'); resulting NaN counts "
    "(non-zero would indicate a value that could not be parsed as numeric):")
for k, v in new_nans.items():
    log(f"  - {k}: {v}")

# String/categorical columns: strip whitespace, standardise case where useful
for df in (utilities, substations, lines):
    for c in df.select_dtypes(include='object').columns:
        df[c] = df[c].astype(str).str.strip()

log("\nAll text columns stripped of leading/trailing whitespace.")

# ---------------------------------------------------------------------------
# STEP 5: CATEGORICAL VALUE CONSISTENCY
# ---------------------------------------------------------------------------
section("6. Categorical value consistency checks")

log("utilities.Type values: " + ", ".join(sorted(utilities['Type'].unique())))
log("utilities.Active values: " + ", ".join(sorted(utilities['Active'].unique())))
log("substations.Type values: " + ", ".join(sorted(substations['Type'].unique())))
log("substations.Status values: " + ", ".join(sorted(substations['Status'].unique())))
log("substations.Voltage (kV) values: " + ", ".join(str(v) for v in sorted(substations['Voltage (kV)'].unique())))
log("lines.Status values: " + ", ".join(sorted(lines['Status'].unique())))
log("lines.Line Type values: " + ", ".join(sorted(lines['Line Type'].unique())))

expected_sub_types = {"Distribution", "Bulk Supply Point", "Transmission"}
expected_sub_status = {"Active", "Inactive"}
expected_line_status = {"Active", "Under Maintenance"}
expected_line_type = {"Overhead", "Underground"}
expected_voltages = {11, 33, 69, 161, 330}

unexpected = []
bad = set(substations['Type'].unique()) - expected_sub_types
if bad:
    unexpected.append(f"substations.Type has unexpected values: {bad}")
bad = set(substations['Status'].unique()) - expected_sub_status
if bad:
    unexpected.append(f"substations.Status has unexpected values: {bad}")
bad = set(lines['Status'].unique()) - expected_line_status
if bad:
    unexpected.append(f"lines.Status has unexpected values: {bad}")
bad = set(lines['Line Type'].unique()) - expected_line_type
if bad:
    unexpected.append(f"lines.Line Type has unexpected values: {bad}")
bad = set(substations['Voltage (kV)'].dropna().unique()) - expected_voltages
if bad:
    unexpected.append(f"substations.Voltage (kV) has unexpected values: {bad}")

log("\nUnexpected categorical values found:" if unexpected else "\nNo unexpected categorical values found — all fields match the documented domain.")
for u in unexpected:
    log(f"  - {u}")

# ---------------------------------------------------------------------------
# STEP 6: RELATIONSHIP / FOREIGN-KEY VALIDATION
# ---------------------------------------------------------------------------
section("7. Foreign-key / relationship validation")

valid_sub_ids = set(substations['Substation ID'])
valid_util_ids = set(utilities['Utility ID'])

orphan_source = lines[~lines['Source Substation ID'].isin(valid_sub_ids)]
orphan_dest = lines[~lines['Destination Substation ID'].isin(valid_sub_ids)]
orphan_util = lines[~lines['Utility ID'].isin(valid_util_ids)]

log(f"- Lines with a Source Substation ID not present in substations.csv: {len(orphan_source)}")
log(f"- Lines with a Destination Substation ID not present in substations.csv: {len(orphan_dest)}")
log(f"- Lines with a Utility ID not present in utilities.csv: {len(orphan_util)}")

self_loops = lines[lines['Source Substation ID'] == lines['Destination Substation ID']]
log(f"- Self-loop lines (source == destination): {len(self_loops)}")

# Cross-check that the *name* columns in lines.csv agree with the substations table
sub_lookup = substations.set_index('Substation ID')['Name']
name_mismatch_src = lines[lines.apply(
    lambda r: sub_lookup.get(r['Source Substation ID']) != r['Source Substation'], axis=1)]
name_mismatch_dst = lines[lines.apply(
    lambda r: sub_lookup.get(r['Destination Substation ID']) != r['Destination Substation'], axis=1)]
log(f"- Lines where Source Substation name doesn't match the ID's record in substations.csv: {len(name_mismatch_src)}")
log(f"- Lines where Destination Substation name doesn't match the ID's record in substations.csv: {len(name_mismatch_dst)}")

# ---------------------------------------------------------------------------
# STEP 7: GEOGRAPHIC BOUNDS VALIDATION
# ---------------------------------------------------------------------------
section("8. Geographic coordinate validation (plausible West African bounds)")

# Generous bounding box covering Ghana plus the WAPP cross-border points used
# in the generator (Guinea in the west to roughly the Nigeria/Benin area east,
# Burkina Faso to the north, Gulf of Guinea coast to the south).
LAT_MIN, LAT_MAX = 3.0, 15.5
LON_MIN, LON_MAX = -15.5, 5.5

out_of_bounds = substations[
    (substations['Latitude'] < LAT_MIN) | (substations['Latitude'] > LAT_MAX) |
    (substations['Longitude'] < LON_MIN) | (substations['Longitude'] > LON_MAX)
]
log(f"- Bounding box used: latitude [{LAT_MIN}, {LAT_MAX}], longitude [{LON_MIN}, {LON_MAX}]")
log(f"- Substations outside plausible bounds: {len(out_of_bounds)}")
if len(out_of_bounds):
    log(out_of_bounds[['Substation ID', 'Name', 'Latitude', 'Longitude']].to_string(index=False))

null_coords = substations[substations['Latitude'].isnull() | substations['Longitude'].isnull()]
log(f"- Substations with missing/unparseable coordinates: {len(null_coords)}")

# ---------------------------------------------------------------------------
# STEP 8: VALUE-RANGE / SANITY CHECKS
# ---------------------------------------------------------------------------
section("9. Value-range sanity checks")

bad_year = substations[
    (substations['Commissioning Year'] < 1900) | (substations['Commissioning Year'] > 2026)
]
log(f"- Substations with an implausible Commissioning Year (<1900 or >2026): {len(bad_year)}")

neg_capacity_sub = substations[substations['Capacity (MVA)'] <= 0]
neg_capacity_line = lines[lines['Capacity (MVA)'] <= 0]
log(f"- Substations with non-positive Capacity (MVA): {len(neg_capacity_sub)}")
log(f"- Lines with non-positive Capacity (MVA): {len(neg_capacity_line)}")

neg_length = lines[lines['Length (km)'] <= 0]
log(f"- Lines with non-positive Length (km): {len(neg_length)}")

# ---------------------------------------------------------------------------
# STEP 9: DROP DUPLICATES (defensive — none expected, but per task instructions)
# ---------------------------------------------------------------------------
section("10. Duplicate removal")

before = (len(utilities), len(substations), len(lines))
utilities = utilities.drop_duplicates()
substations = substations.drop_duplicates()
lines = lines.drop_duplicates()
after = (len(utilities), len(substations), len(lines))
log(f"- Row counts before dedup: utilities={before[0]}, substations={before[1]}, lines={before[2]}")
log(f"- Row counts after dedup:  utilities={after[0]}, substations={after[1]}, lines={after[2]}")

# ---------------------------------------------------------------------------
# STEP 10: SUMMARY STATISTICS
# ---------------------------------------------------------------------------
section("11. Summary statistics (post-cleaning)")

log("**utilities** — Type / Active breakdown:")
log(utilities['Type'].value_counts().to_string())
log("")
log(utilities['Active'].value_counts().to_string())

log("\n**substations** — numeric summary:")
log(substations[['Latitude', 'Longitude', 'Voltage (kV)', 'Capacity (MVA)', 'Commissioning Year']].describe().to_string())

log("\n**substations** — Status counts:")
log(substations['Status'].value_counts().to_string())

log("\n**substations** — Region counts:")
log(substations['Region'].value_counts().to_string())

log("\n**lines** — numeric summary:")
log(lines[['Voltage (kV)', 'Length (km)', 'Capacity (MVA)']].describe().to_string())

log("\n**lines** — Status counts:")
log(lines['Status'].value_counts().to_string())

log("\n**lines** — Line Type counts:")
log(lines['Line Type'].value_counts().to_string())

# ---------------------------------------------------------------------------
# STEP 11: SAVE CLEANED FILES
# ---------------------------------------------------------------------------
utilities.to_csv(os.path.join(OUTPUT_DIR, 'utilities_clean.csv'), index=False)
substations.to_csv(os.path.join(OUTPUT_DIR, 'substations_clean.csv'), index=False)
lines.to_csv(os.path.join(OUTPUT_DIR, 'lines_clean.csv'), index=False)

section("12. Output")
log(f"Cleaned files written to {OUTPUT_DIR}/: utilities_clean.csv, substations_clean.csv, lines_clean.csv")

with open(os.path.join(OUTPUT_DIR, 'data_cleaning_report.md'), 'w') as f:
    f.write("# Data Cleaning and Validation Report\n")
    f.write("National Electricity Grid Network Analysis — Task 1\n")
    f.write("\n".join(report_lines))

print("\nDONE")