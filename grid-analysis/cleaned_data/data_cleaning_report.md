# Data Cleaning and Validation Report
National Electricity Grid Network Analysis — Task 1

## 1. Loading the raw data

- utilities.csv: 10 rows x 7 columns
- substations.csv: 44 rows x 12 columns
- lines.csv: 55 rows x 11 columns

## 2. Initial inspection (before cleaning)


**utilities** dtypes:
Utility ID    int64
Name            str
Alias           str
Code            str
Type            str
Country         str
Active          str

**utilities** missing values (raw):
  none found
**utilities** fully duplicated rows: 0

**substations** dtypes:
Substation ID           int64
Name                      str
Short Name                str
Region                    str
Country                   str
Latitude              float64
Longitude             float64
Voltage (kV)            int64
Capacity (MVA)        float64
Commissioning Year      int64
Type                      str
Status                    str

**substations** missing values (raw):
  none found
**substations** fully duplicated rows: 0

**lines** dtypes:
Line ID                        int64
Utility ID                     int64
Source Substation ID           int64
Source Substation                str
Destination Substation ID      int64
Destination Substation           str
Voltage (kV)                   int64
Length (km)                  float64
Capacity (MVA)               float64
Status                           str
Line Type                        str

**lines** missing values (raw):
  none found
**lines** fully duplicated rows: 0

## 3. Checking for placeholder-style missing values

- utilities: no placeholder-missing values found in text columns
- substations: no placeholder-missing values found in text columns
- lines: no placeholder-missing values found in text columns

## 4. Duplicate primary-key checks

- Duplicate Utility IDs: 0
- Duplicate Substation IDs: 0
- Duplicate Line IDs: 0
- Duplicate Source/Destination substation pairs (possible double-logged lines): 0

## 5. Data-type coercion

Numeric columns coerced with pd.to_numeric(errors='coerce'); resulting NaN counts (non-zero would indicate a value that could not be parsed as numeric):
  - substations.Latitude: 0
  - substations.Longitude: 0
  - substations.Voltage (kV): 0
  - substations.Capacity (MVA): 0
  - substations.Commissioning Year: 0
  - lines.Voltage (kV): 0
  - lines.Length (km): 0
  - lines.Capacity (MVA): 0

All text columns stripped of leading/trailing whitespace.

## 6. Categorical value consistency checks

utilities.Type values: Distribution, Generation, Transmission
utilities.Active values: N, Y
substations.Type values: Bulk Supply Point, Distribution, Transmission
substations.Status values: Active, Inactive
substations.Voltage (kV) values: 11, 33, 69, 161, 330
lines.Status values: Active, Under Maintenance
lines.Line Type values: Overhead, Underground

No unexpected categorical values found — all fields match the documented domain.

## 7. Foreign-key / relationship validation

- Lines with a Source Substation ID not present in substations.csv: 0
- Lines with a Destination Substation ID not present in substations.csv: 0
- Lines with a Utility ID not present in utilities.csv: 0
- Self-loop lines (source == destination): 0
- Lines where Source Substation name doesn't match the ID's record in substations.csv: 0
- Lines where Destination Substation name doesn't match the ID's record in substations.csv: 0

## 8. Geographic coordinate validation (plausible West African bounds)

- Bounding box used: latitude [3.0, 15.5], longitude [-15.5, 5.5]
- Substations outside plausible bounds: 0
- Substations with missing/unparseable coordinates: 0

## 9. Value-range sanity checks

- Substations with an implausible Commissioning Year (<1900 or >2026): 0
- Substations with non-positive Capacity (MVA): 0
- Lines with non-positive Capacity (MVA): 0
- Lines with non-positive Length (km): 0

## 10. Duplicate removal

- Row counts before dedup: utilities=10, substations=44, lines=55
- Row counts after dedup:  utilities=10, substations=44, lines=55

## 11. Summary statistics (post-cleaning)

**utilities** — Type / Active breakdown:
Type
Distribution    6
Transmission    2
Generation      2

Active
Y    8
N    2

**substations** — numeric summary:
        Latitude  Longitude  Voltage (kV)  Capacity (MVA)  Commissioning Year
count  44.000000  44.000000     44.000000       44.000000                44.0
mean    6.898402  -1.194868    134.545455      157.865909         1996.295455
std     1.879404   2.314917    120.399810      139.923148           16.112366
min     4.874700 -13.580000     11.000000        6.400000              1967.0
25%     5.586350  -1.760000     33.000000       43.825000             1982.25
50%     6.184400  -0.800700     69.000000      108.550000              1999.5
75%     7.364200  -0.170900    161.000000      254.350000             2009.25
max    11.200000   2.430000    330.000000      487.600000              2022.0

**substations** — Status counts:
Status
Active      43
Inactive     1

**substations** — Region counts:
Region
Greater Accra           6
Ashanti                 5
Western                 4
Central                 4
Eastern                 4
Volta                   4
Bono                    3
Northern                3
Upper East              2
Upper West              1
Burkina Faso border     1
Cote d'Ivoire border    1
Togo border             1
Togo                    1
Benin                   1
Cote d'Ivoire           1
Burkina Faso            1
Guinea                  1

**lines** — numeric summary:
       Voltage (kV)  Length (km)  Capacity (MVA)
count     55.000000    55.000000       55.000000
mean     141.381818    99.312727      222.400000
std      135.169097    90.275104      109.181765
min       11.000000     3.800000       32.900000
25%       22.000000    42.900000      134.550000
50%       69.000000    75.900000      229.900000
75%      330.000000   129.600000      292.100000
max      330.000000   426.000000      506.300000

**lines** — Status counts:
Status
Active               53
Under Maintenance     2

**lines** — Line Type counts:
Line Type
Overhead       40
Underground    15

## 12. Output

Cleaned files written to cleaned_data/: utilities_clean.csv, substations_clean.csv, lines_clean.csv