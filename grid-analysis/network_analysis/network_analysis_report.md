# Network Modelling and Analysis Report
National Electricity Grid Network Analysis - Task 2

## 1. Loading cleaned data

- utilities: 10 rows
- substations: 44 rows
- lines: 55 rows

## 2. Exploratory data analysis

**Substations per region**

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

**Most common voltage levels (substations)**

Voltage (kV)
330    10
161    11
69      8
33      6
11      9

**Lines operated per utility**

Utility ID
Ghana Grid Company                           24
Northern Electricity Distribution Company    14
Electricity Company of Ghana                 10
Communaute Electrique du Benin                3
Sonabel                                       2
Compagnie Ivoirienne d'Electricite            2

**Substation capacity distribution (MVA)**

count     44.000000
mean     157.865909
std      139.923148
min        6.400000
25%       43.825000
50%      108.550000
75%      254.350000
max      487.600000

**Oldest infrastructure by region (min commissioning year)**

Region
Western                 1967
Northern                1969
Greater Accra           1970
Central                 1970
Upper East              1971
Eastern                 1975
Upper West              1977
Volta                   1980
Burkina Faso            1983
Cote d'Ivoire border    1984
Ashanti                 1989
Burkina Faso border     1991
Benin                   1995
Bono                    1999
Guinea                  2004
Cote d'Ivoire           2010
Togo                    2014
Togo border             2015

**Line status proportions**

Status
Active               96.4 %
Under Maintenance     3.6 %

**Most-connected substations (by raw line count, pre-graph)**

                                    Name  Line Count
Substation ID                                       
3                      Mallam Substation           5
7              Kumasi Central Substation           5
16                 Cape Coast Substation           5
1                    Achimota Substation           4
2                        Tema Substation           4
4                       Legon Substation           4
12                   Takoradi Substation           4
20                  Koforidua Substation           4
24                         Ho Substation           4
34                 Bolgatanga Substation           4

## 3. Building the graph

- Nodes (substations): 44
- Edges (lines): 55
- Isolated substations (no lines): [33, 44]

## 4. Network metrics

- Per-node metrics written to network_analysis\network_metrics.csv

**Top 10 substations by betweenness centrality**

 Substation ID                      Name        Region  Degree  Degree Centrality  Betweenness Centrality  Closeness Centrality  PageRank  Clustering Coefficient
            16     Cape Coast Substation       Central       5             0.1163                  0.5260                0.2641    0.0489                  0.2000
            12       Takoradi Substation       Western       4             0.0930                  0.5161                0.2606    0.0316                  0.1667
             7 Kumasi Central Substation       Ashanti       5             0.1163                  0.5006                0.2443    0.0451                  0.1000
            20      Koforidua Substation       Eastern       4             0.0930                  0.4983                0.2539    0.0456                  0.1667
            24             Ho Substation         Volta       4             0.0930                  0.4363                0.2327    0.0445                  0.1667
            28        Sunyani Substation          Bono       3             0.0698                  0.3344                0.2058    0.0438                  0.0000
             1       Achimota Substation Greater Accra       4             0.0930                  0.2968                0.2125    0.0287                  0.3333
            31         Tamale Substation      Northern       3             0.0698                  0.2381                0.1793    0.0377                  0.0000
            34     Bolgatanga Substation    Upper East       4             0.0930                  0.1694                0.1564    0.0435                  0.0000
             2           Tema Substation Greater Accra       4             0.0930                  0.1262                0.1827    0.0237                  0.3333

**Top 10 substations by PageRank**

 Substation ID                      Name        Region  Degree  Degree Centrality  Betweenness Centrality  Closeness Centrality  PageRank  Clustering Coefficient
            16     Cape Coast Substation       Central       5             0.1163                  0.5260                0.2641    0.0489                  0.2000
            20      Koforidua Substation       Eastern       4             0.0930                  0.4983                0.2539    0.0456                  0.1667
             7 Kumasi Central Substation       Ashanti       5             0.1163                  0.5006                0.2443    0.0451                  0.1000
            24             Ho Substation         Volta       4             0.0930                  0.4363                0.2327    0.0445                  0.1667
            28        Sunyani Substation          Bono       3             0.0698                  0.3344                0.2058    0.0438                  0.0000
            34     Bolgatanga Substation    Upper East       4             0.0930                  0.1694                0.1564    0.0435                  0.0000
            31         Tamale Substation      Northern       3             0.0698                  0.2381                0.1793    0.0377                  0.0000
            12       Takoradi Substation       Western       4             0.0930                  0.5161                0.2606    0.0316                  0.1667
             4          Legon Substation Greater Accra       4             0.0930                  0.0432                0.1570    0.0305                  0.5000
             1       Achimota Substation Greater Accra       4             0.0930                  0.2968                0.2125    0.0287                  0.3333

**Connected components**: 3
- Largest component size: 42 / 44 substations
- Smaller components: [[33], [44]]

**Bridges** (single lines whose removal disconnects the network): 21
  - Achimota Substation <-> Kumasi Central Substation
  - Tema Substation <-> Aflao Border Station
  - Kumasi Central Substation <-> Takoradi Substation
  - Kumasi Central Substation <-> Elubo Border Station
  - Takoradi Substation <-> Cape Coast Substation
  - Cape Coast Substation <-> Koforidua Substation
  - Koforidua Substation <-> Ho Substation
  - Ho Substation <-> Sunyani Substation
  - Hohoe Substation <-> Sogakope Substation
  - Sunyani Substation <-> Techiman Substation
  - Sunyani Substation <-> Tamale Substation
  - Techiman Substation <-> Berekum Substation
  - Tamale Substation <-> Yendi Substation
  - Tamale Substation <-> Bolgatanga Substation
  - Bolgatanga Substation <-> Bawku Substation
  - Bolgatanga Substation <-> Wa Substation
  - Bolgatanga Substation <-> Bolgatanga Interconnection
  - Bolgatanga Interconnection <-> Bobo-Dioulasso Hub
  - Elubo Border Station <-> Abidjan Transmission Hub
  - Aflao Border Station <-> Lome Transmission Hub
  - Lome Transmission Hub <-> Cotonou Transmission Hub

**Global efficiency**: 0.244
**Average shortest path length** (largest component, weighted by line length km): 818.85

**Communities detected** (greedy modularity): 10
- Community 1 (9 substations): Akosombo Substation, Assin Fosu Substation, Cape Coast Substation, Kasoa Substation, Koforidua Substation, Nkawkaw Substation, Suhum Substation, Takoradi Substation, Winneba Substation
- Community 2 (9 substations): Berekum Substation, Ho Substation, Hohoe Substation, Kpong Substation, Sogakope Substation, Sunyani Substation, Tamale Substation, Techiman Substation, Yendi Substation
- Community 3 (5 substations): Abidjan Transmission Hub, Achimota Substation, Elubo Border Station, Kumasi Central Substation, Mampong Substation
- Community 4 (5 substations): Bawku Substation, Bobo-Dioulasso Hub, Bolgatanga Interconnection, Bolgatanga Substation, Wa Substation
- Community 5 (4 substations): Aboadze Junction Substation, Kaneshie Substation, Legon Substation, Mallam Substation
- Community 6 (4 substations): Aflao Border Station, Cotonou Transmission Hub, Lome Transmission Hub, Tema Substation
- Community 7 (3 substations): Ejisu Substation, Konongo Substation, Obuasi Substation
- Community 8 (3 substations): Aboadze Substation, Axim Substation, Tarkwa Substation
- Community 9 (1 substations): Savelugu Substation
- Community 10 (1 substations): Conakry Transmission Hub

## 5. Interpretation

The metrics above are **structural observations about the graph topology of a synthetically generated dataset** (`random.seed(42)`), not measurements of real electrical load, voltage stability, or power flow. High betweenness or PageRank identifies substations that sit on many shortest connection paths or are linked to well-connected neighbors - i.e. structurally central positions in the network graph. In a real grid this would be one input among many (alongside load-flow studies, protection schemes, and asset condition) for prioritizing reliability investment, not a standalone answer.

The substation with the highest betweenness centrality in this dataset is **Cape Coast Substation** (Central) - flagged here purely as a graph-structural reliability proxy: many shortest paths between other substation pairs pass through it, so its removal would be expected to lengthen or break more routes than removing a peripheral substation. See the N-1 contingency analysis task for a direct test of that expectation.

The 21 bridge edge(s) identified above are single points of failure in this graph: removing any one of them would split the network into more components. They are natural candidates to examine first in the N-1 contingency analysis.