# Phase 4 — Bronze to Silver

## Overview
Reads raw procurement data (purchase orders + goods receipts) from ADLS Bronze container using Auto Loader. Applies DLT expectations for data quality, cleanses and type-casts fields, writes to Silver Delta tables in Unity Catalog (procurement_db.silver).

## Pipeline
- **Name:** Procurement_Bronze_to_Silver
- **Notebook:** 04_bronze_to_silver.py
- **Catalog:** procurement_db | **Schema:** silver

## Tables Produced
| Table | Rows | Key Expectations |
|-------|------|-----------------|
| silver_purchase_orders | see screenshot | valid_po_id, valid_supplier, positive_quantity |
| silver_goods_receipts | see screenshot | valid_gr_id, valid_supplier, positive_quantity_received |

## Screenshots
| File | Description |
|------|-------------|
| 01_pipeline_dag_green.png | DLT pipeline DAG — all nodes green |
| 02_row_counts.png | Row count for each Silver table |
| 03_event_log.png | Event log showing rows_written and rows_dropped |
| 04_data_explorer_schema.png | Silver table schema in Data Explorer |
