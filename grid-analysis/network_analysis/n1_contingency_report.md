# N-1 Contingency Analysis Report
National Electricity Grid Network Analysis - issue #3

## 1. Load data and build graph

- nodes: 44, edges: 55
- connected components (baseline): 3

## 2. Static network diagram

- saved `charts\network_graph.png`

## 3. Centrality shortlist

**Top by degree**: Mallam(5), Kumasi Central(5), Cape Coast(5), Achimota(4), Tema(4), Legon(4), Konongo(4), Takoradi(4)
**Top by betweenness**: Cape Coast(0.526), Takoradi(0.516), Kumasi Central(0.501), Koforidua(0.498), Ho(0.436), Sunyani(0.334), Achimota(0.297), Tamale(0.238)

**Bridge lines** (21): Achimota<->Kumasi Central; Tema<->Aflao Border Station; Kumasi Central<->Takoradi; Kumasi Central<->Elubo Border Station; Takoradi<->Cape Coast; Cape Coast<->Koforidua; Koforidua<->Ho; Ho<->Sunyani; Hohoe<->Sogakope; Sunyani<->Techiman; Sunyani<->Tamale; Techiman<->Berekum; Tamale<->Yendi; Tamale<->Bolgatanga; Bolgatanga<->Bawku; Bolgatanga<->Wa; Bolgatanga<->Bolgatanga Interconnection; Bolgatanga Interconnection<->Bobo-Dioulasso Hub; Elubo Border Station<->Abidjan Transmission Hub; Aflao Border Station<->Lome Transmission Hub; Lome Transmission Hub<->Cotonou Transmission Hub

## 4. N-1 contingency analysis - remove one substation

For each candidate substation we delete the node (and its incident lines) and record how the network fragments.

    Substation        Region  Degree  Betweenness  Components after  Largest component after  Extra fragments  Nodes cut from giant component
Kumasi Central       Ashanti       5        0.501                 6                       26                3                              15
    Cape Coast       Central       5        0.526                 5                       20                2                              21
      Takoradi       Western       4        0.516                 5                       22                2                              19
     Koforidua       Eastern       4        0.498                 5                       24                2                              17
            Ho         Volta       4        0.436                 5                       28                2                              13
       Sunyani          Bono       3        0.334                 5                       32                2                               9
        Tamale      Northern       3        0.238                 5                       35                2                               6
      Achimota Greater Accra       4        0.297                 4                       33                1                               8
          Tema Greater Accra       4        0.126                 4                       38                1                               3
       Konongo       Ashanti       4        0.086                 4                       39                1                               2
        Mallam Greater Accra       5        0.000                 3                       41                0                               0
         Legon Greater Accra       4        0.043                 3                       41                0                               0

## 5. N-1 contingency analysis - remove one line

- lines whose loss splits the network: 21 of 55
                                              Line  Is bridge  Components after  Splits network
Lome Transmission Hub <-> Cotonou Transmission Hub       True                 4            True
                                  Tamale <-> Yendi       True                 4            True
                                  Koforidua <-> Ho       True                 4            True
                           Takoradi <-> Cape Coast       True                 4            True
                                    Ho <-> Sunyani       True                 4            True
                                Hohoe <-> Sogakope       True                 4            True
                              Sunyani <-> Techiman       True                 4            True
                       Kumasi Central <-> Takoradi       True                 4            True
                                Sunyani <-> Tamale       True                 4            True
                              Techiman <-> Berekum       True                 4            True
           Kumasi Central <-> Elubo Border Station       True                 4            True
                             Tamale <-> Bolgatanga       True                 4            True
 Bolgatanga Interconnection <-> Bobo-Dioulasso Hub       True                 4            True
    Aflao Border Station <-> Lome Transmission Hub       True                 4            True
                       Achimota <-> Kumasi Central       True                 4            True
                              Bolgatanga <-> Bawku       True                 4            True
 Elubo Border Station <-> Abidjan Transmission Hub       True                 4            True
                          Cape Coast <-> Koforidua       True                 4            True
                     Tema <-> Aflao Border Station       True                 4            True
         Bolgatanga <-> Bolgatanga Interconnection       True                 4            True
                                 Bolgatanga <-> Wa       True                 4            True

## 6. Contingency impact chart

- saved `charts\n1_contingency_impact.png`

## 7. Interpretation

The most damaging single-substation loss is **Kumasi Central** (Ashanti): it creates 3 extra fragment(s) and cuts 15 substation(s) from the main connected grid.

21 individual line(s) are single points of failure. These map onto the bridge edges and are the lines a real operator would be most cautious about de-energising for maintenance.

*This is a graph-topology approximation of N-1 analysis. It ignores load flow, thermal limits, voltage stability, and protection behaviour - a real contingency study models all of those.*