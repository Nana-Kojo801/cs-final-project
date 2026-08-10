# Data Integration Report
National Electricity Grid Network Analysis - Task 1.3

## 1. Loading cleaned data

- utilities: 10 rows
- substations: 44 rows
- lines: 55 rows (this is the join's base table - one row per line)
- Built lookup dicts: substation_by_id (44 entries), utility_by_id (10 entries)

## 2. Joining datasets

- Rows before join: 55
- Rows after join: 55
- Row count changed by join: no (expected for a left join with valid FKs)
- Lines that failed to match a source substation: 0
- Lines that failed to match a destination substation: 0
- Lines that failed to match a utility: 0
(Non-zero counts here would mean an orphaned foreign key slipped through Task 1 cleaning - see data_cleaning_report.md's foreign-key validation section.)

## 3. Lines by utility and source region

Utility Code        Source Region  Line Count
         GRD        Greater Accra           5
         NED        Greater Accra           4
         GRD                 Bono           3
         GRD              Eastern           3
         NED              Central           3
         GRD                Volta           3
         NED              Ashanti           3
         GRD              Western           3
         GRD              Ashanti           2
         CIE Cote d'Ivoire border           2

## 4. Output

Merged dataset written to integrated_data\merged_lines.csv (55 rows, 28 columns)