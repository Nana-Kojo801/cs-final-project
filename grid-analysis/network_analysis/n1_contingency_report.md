# N-1 Contingency Analysis Report
National Electricity Grid Network Analysis - Issue #3

## Method

Candidate substations were selected from the three highest betweenness-centrality scores in the network metrics. Candidate lines were selected from the three highest weighted edge betweenness-centrality scores. Each candidate was removed from a copy of the graph, then connected components, largest component size, isolated nodes, global efficiency, bridge count, and average shortest path within the largest connected component were recomputed.

## Before/after results

| Scenario             | Failure Type       |   Failed Asset ID | Failed Asset                                      |   Connected Components |   Largest Component Size |   Isolated Nodes |   Global Efficiency |   Average Shortest Path (km) |   Bridge Count |   Efficiency Change (%) |   Average Path Change (%) |
|:---------------------|:-------------------|------------------:|:--------------------------------------------------|-----------------------:|-------------------------:|-----------------:|--------------------:|-----------------------------:|---------------:|------------------------:|--------------------------:|
| Baseline             | None               |                   | All assets available                              |                      3 |                       42 |                2 |            0.244048 |                      818.845 |             21 |                    0    |                      0    |
| Remove substation 16 | Substation removal |                16 | Cape Coast Substation                             |                      5 |                       20 |                2 |            0.151732 |                      368.363 |             21 |                  -37.83 |                    -55.01 |
| Remove substation 12 | Substation removal |                12 | Takoradi Substation                               |                      5 |                       22 |                2 |            0.152711 |                      702.882 |             19 |                  -37.43 |                    -14.16 |
| Remove substation 7  | Substation removal |                 7 | Kumasi Central Substation                         |                      6 |                       26 |                2 |            0.149914 |                      699.801 |             19 |                  -38.57 |                    -14.54 |
| Remove line 42       | Line removal       |                42 | Takoradi Substation <-> Cape Coast Substation     |                      4 |                       22 |                2 |            0.167337 |                      702.882 |             20 |                  -31.43 |                    -14.16 |
| Remove line 43       | Line removal       |                43 | Cape Coast Substation <-> Koforidua Substation    |                      4 |                       24 |                2 |            0.16992  |                      406.38  |             20 |                  -30.37 |                    -50.37 |
| Remove line 41       | Line removal       |                41 | Kumasi Central Substation <-> Takoradi Substation |                      4 |                       26 |                2 |            0.169645 |                      699.801 |             20 |                  -30.49 |                    -14.54 |

## Interpretation

The comparison shows how structurally important assets affect the resilience of this graph. The global efficiency value is the unweighted NetworkX reachability measure. A decrease in global efficiency indicates that remaining substations become less reachable on average. An increase in connected components or isolated nodes indicates fragmentation, while a smaller largest component indicates that a larger share of the network has been separated from the main group. The results should be read alongside the candidate centrality scores rather than treated as a prediction of electrical service loss.

> This is a graph-based educational approximation. It is not a substitute for real power-flow, transient-stability, or protection-coordination studies.
