# Phase 5 — Silver to Gold (Star Schema & SCD Type 2)

## Overview
Transforms Silver tables into a Gold Star Schema using DLT apply_changes(). Builds a SCD Type 1 supplier dimension, SCD Type 2 material dimension (full history preserved), and an incremental fact table with surrogate key joins.

## Pipeline
- **Name:** Procurement_Silver_to_Gold
- **Pipeline ID:** 263afc34-6c40-4296-826a-865b19b045d8
- **Notebook:** 05_silver_to_gold.py
- **Catalog:** procurement_db | **Schema:** gold

## Tables Produced
| Table | SCD Type | Key |
|-------|----------|-----|
| dim_supplier | SCD Type 1 | supplier_id |
| dim_material | SCD Type 2 | material_id |
| fact_goods_receipts | Incremental fact | gr_id |

## Key Design Decisions
- Both dimensions sourced from silver_goods_receipts to ensure material_id coverage → NULL SK = 0
- Surrogate keys generated using abs(hash(natural_key)).cast(long) — deterministic, no sequence needed
- dim_material filtered on __END_AT IS NULL in fact join to use only current version

## Business Query
```sql
SELECT
  d_sup.supplier_id,
  d_mat.material_id,
  COUNT(f.gr_id) AS total_receipts,
  ROUND(SUM(f.quantity_received), 2) AS total_qty_received,
  ROUND(SUM(f.total_value), 2) AS total_value
FROM procurement_db.gold.fact_goods_receipts f
JOIN procurement_db.gold.dim_supplier d_sup
  ON f.supplier_sk = abs(hash(d_sup.supplier_id))
JOIN procurement_db.gold.dim_material d_mat
  ON f.material_sk = abs(hash(d_mat.material_id))
WHERE d_mat.__END_AT IS NULL
GROUP BY d_sup.supplier_id, d_mat.material_id
ORDER BY total_value DESC
LIMIT 10;
```

## Screenshots
| File | Description |
|------|-------------|
| 01_pipeline_dag_green.png | DLT pipeline DAG — all nodes green |
| 02_scd2_proof.png | dim_material showing expired + current row for same material_id |
| 03_null_sk_audit.png | NULL SK audit — result = 0 |
| 04_business_query.png | Business query joining fact + 2 dims |
| 05_erd.png | Star schema ERD |
