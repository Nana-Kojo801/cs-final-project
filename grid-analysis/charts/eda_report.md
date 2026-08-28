# Exploratory Data Analysis Report
National Electricity Grid Network Analysis - Task 3

## 1. Load cleaned data

- utilities: 10, substations: 44, lines: 55

## 2. Descriptive statistics (numeric columns)

**Substations**

       Latitude  Longitude  Voltage (kV)  Capacity (MVA)  Commissioning Year
count     44.00      44.00         44.00           44.00               44.00
mean       6.90      -1.19        134.55          157.87             1996.30
std        1.88       2.31        120.40          139.92               16.11
min        4.87     -13.58         11.00            6.40             1967.00
25%        5.59      -1.76         33.00           43.82             1982.25
50%        6.18      -0.80         69.00          108.55             1999.50
75%        7.36      -0.17        161.00          254.35             2009.25
max       11.20       2.43        330.00          487.60             2022.00

**Lines**

       Voltage (kV)  Length (km)  Capacity (MVA)
count         55.00        55.00           55.00
mean         141.38        99.31          222.40
std          135.17        90.28          109.18
min           11.00         3.80           32.90
25%           22.00        42.90          134.55
50%           69.00        75.90          229.90
75%          330.00       129.60          292.10
max          330.00       426.00          506.30

## 3. Q: Which regions have the most substations?

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
- saved `charts\eda_substations_by_region.png`

## 4. Q: Which voltage levels are most common?

Voltage (kV)
11      9
33      6
69      8
161    11
330    10
- saved `charts\eda_voltage_levels.png`

## 5. Q: Which utility operates the most lines?

Utility ID
GRIDCo     24
NEDCo      14
ECG        10
CEB         3
SONABEL     2
CIE         2
- saved `charts\eda_lines_per_utility.png`

## 6. Q: What is the distribution of substation capacities?

count     44.00
mean     157.87
std      139.92
min        6.40
25%       43.82
50%      108.55
75%      254.35
max      487.60
- saved `charts\eda_capacity_distribution.png`

## 7. Q: Which regions contain the oldest infrastructure?

                       min  median   max
Region                                  
Western               1967  1987.0  2010
Northern              1969  1978.0  2015
Greater Accra         1970  2002.5  2011
Central               1970  1996.0  2003
Upper East            1971  1981.5  1992
Eastern               1975  2009.5  2021
Upper West            1977  1977.0  1977
Volta                 1980  1998.0  2017
Burkina Faso          1983  1983.0  1983
Cote d'Ivoire border  1984  1984.0  1984
Ashanti               1989  2007.0  2018
Burkina Faso border   1991  1991.0  1991
Benin                 1995  1995.0  1995
Bono                  1999  2000.0  2022
Guinea                2004  2004.0  2004
Cote d'Ivoire         2010  2010.0  2010
Togo                  2014  2014.0  2014
Togo border           2015  2015.0  2015
- saved `charts\eda_infrastructure_age_by_region.png`

## 8. Q: What proportion of lines are active vs under maintenance?

Status
Active               96.4 %
Under Maintenance     3.6 %
- saved `charts\eda_line_status.png`

## 9. Q: Which substations have the most connections?

Mallam            5
Kumasi Central    5
Cape Coast        5
Achimota          4
Tema              4
Legon             4
Takoradi          4
Koforidua         4
Ho                4
Bolgatanga        4
- saved `charts\eda_top_connected_substations.png`

## 10. Q: How are high-capacity substations distributed by voltage?

- saved `charts\eda_capacity_vs_voltage.png`

## 11. Key findings

- **Greater Accra** has the most substations (6).
- **161 kV** is the most common substation voltage level.
- **GRIDCo** operates the most lines (24).
- Median substation capacity is **108.6 MVA**; the distribution is right-skewed (a few large transmission substations).
- The oldest infrastructure sits in **Western** (commissioned 1967).
- **96.4%** of lines are `Active`; the rest are under maintenance.
- **Mallam** is the most-connected substation (5 lines).

*All figures come from the seeded synthetic dataset (`random.seed(42)`) and are illustrative, not official grid measurements.*