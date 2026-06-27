# Phase 7 — Data Lineage & Observability

## Overview
Demonstrates production observability using Unity Catalog lineage, Delta time travel, DLT event log, job run history monitoring, and an automated SQL alert.

## Key Results
| Check | Result |
|-------|--------|
| fact_goods_receipts VERSION AS OF 36 | 10,259 rows |
| fact_goods_receipts VERSION AS OF 10 | 10,898 rows |
| DESCRIBE HISTORY rows | 37 versions |
| SQL Alert trigger | total_receipts < 1 |
| Alert email | rishikmanche@gmail.com |

## Event Log Query (Pipeline ID: 263afc34-6c40-4296-826a-865b19b045d8)
```sql
SELECT details
FROM event_log('263afc34-6c40-4296-826a-865b19b045d8')
WHERE event_type = 'flow_progress'
AND details:flow_progress:status = 'COMPLETED'
LIMIT 5;
```

## Time Travel Queries
```sql
SELECT COUNT(*) FROM procurement_db.gold.fact_goods_receipts VERSION AS OF 36;
SELECT COUNT(*) FROM procurement_db.gold.fact_goods_receipts VERSION AS OF 10;
```

## Screenshots
| File | Description |
|------|-------------|
| 01_lineage_graph.png | Unity Catalog table lineage graph for fact_goods_receipts |
| 02_column_lineage.png | Column list with lineage icons |
| 03_describe_history.png | DESCRIBE HISTORY — 37 rows |
| 04_time_travel.png | Two time travel queries at different versions |
| 05_event_log.png | Event log showing status=COMPLETED |
| 06_job_run_history.png | Job run history from Workflows UI |
| 07_sql_alert.png | SQL Alert — condition + email configured |
