# Merge and Advanced Analysis Report
National Electricity Grid Network Analysis - Task 4

## 1. Load cleaned data

- utilities 10, substations 44, lines 55

## 2. Build the master line-level table

- rows after merge: 55 (expected 55)
- lines with unmatched source substation: 0
- lines with unmatched destination substation: 0
- lines with unmatched utility: 0
- master table written to `integrated_data\master_lines.csv` (33 columns)

## 3. Q: Which utility operates the most lines, by source region?

 Alias           Region_src  Line Count
GRIDCo        Greater Accra           5
 NEDCo        Greater Accra           4
GRIDCo                 Bono           3
GRIDCo              Eastern           3
 NEDCo              Central           3
GRIDCo                Volta           3
 NEDCo              Ashanti           3
GRIDCo              Western           3
GRIDCo              Ashanti           2
   CIE Cote d'Ivoire border           2
   CEB          Togo border           2
GRIDCo           Upper East           2
- saved `charts\merge_utility_region.png`

## 4. Q: How much capacity does each utility carry?

         Lines  Total_Capacity_MVA  Avg_Length_km
Alias                                            
GRIDCo      24              6037.1          117.9
NEDCo       14              2746.9           62.4
ECG         10              1672.7           59.2
CEB          3               857.9          103.9
CIE          2               469.6          188.2
SONABEL      2               447.8          239.5

## 5. Q: Which region pairs are connected by inter-regional lines?

- inter-regional lines: 16 of 55
Pair
Ashanti <-> Greater Accra                 1
Ashanti <-> Western                       1
Central <-> Western                       1
Central <-> Eastern                       1
Eastern <-> Volta                         1
Bono <-> Volta                            1
Bono <-> Northern                         1
Northern <-> Upper East                   1
Upper East <-> Upper West                 1
Burkina Faso border <-> Upper East        1
Burkina Faso <-> Burkina Faso border      1
Ashanti <-> Cote d'Ivoire border          1
Cote d'Ivoire <-> Cote d'Ivoire border    1
Greater Accra <-> Togo border             1
Togo <-> Togo border                      1
Benin <-> Togo                            1
- saved `charts\merge_interregional_lines.png`

## 6. Q: Which cross-border interconnections exist (WAPP-style)?

  Alias     Source Substation Country_src     Destination Substation Country_dst  Voltage (kV)  Length (km)
SONABEL Bolgatanga Substation       Ghana Bolgatanga Interconnection     Burkina           330         53.0
    CIE  Elubo Border Station        Cote  Kumasi Central Substation       Ghana           330        235.2
    CEB  Aflao Border Station        Togo            Tema Substation       Ghana           330        157.9
    CEB Lome Transmission Hub        Togo   Cotonou Transmission Hub       Benin           330        150.0

## 7. Findings

- **GRIDCo** dominates in **Greater Accra** (5 lines from that region).
- **GRIDCo** carries the most rated transfer capacity (6,037 MVA across 24 lines) - consistent with its role as the transmission operator.
- The busiest inter-regional corridor is **Ashanti <-> Greater Accra** (1 lines).
- 4 cross-border line(s) model Ghana's WAPP interconnections; all are synthetic stand-ins, not survey data.
- Merge caused **no data loss**: 0 orphaned foreign keys across 55 lines.