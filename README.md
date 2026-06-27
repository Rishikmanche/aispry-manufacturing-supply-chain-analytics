# Manufacturing Supply Chain Analytics

End-to-end data engineering pipeline on **Azure Databricks** — ingesting raw procurement data from ADLS Gen2, transforming it through a medallion architecture, and delivering a production-grade star schema with SCD Type 2 history tracking.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AZURE DATABRICKS WORKSPACE                         │
│                                                                           │
│  ┌──────────┐    Delta Live Tables     ┌──────────┐    Delta Live Tables  │
│  │  ADLS    │    ┌───────────────┐     │  SILVER  │    ┌──────────────┐   │
│  │  Gen2    │───▶│  Auto Loader  │────▶│  Layer   │───▶│ apply_changes│   │
│  │ (Bronze) │    │  + DLT        │     │          │    │ + SCD Type 2 │   │
│  └──────────┘    │  Expectations │     └──────────┘    └──────┬───────┘   │
│                  └───────────────┘                            │           │
│   Phase 4                                Phase 5             ▼           │
│   ─ bronze_purchase_orders               ─ dim_supplier    ┌──────────┐  │
│   ─ bronze_goods_receipts                  (SCD Type 1)    │   GOLD   │  │
│   ─ silver_purchase_orders               ─ dim_material    │  Star    │  │
│   ─ silver_goods_receipts                  (SCD Type 2)    │  Schema  │  │
│                                          ─ fact_goods_     └──────────┘  │
│                                            receipts                      │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 6: Orchestration          │ Phase 7: Observability          │   │
│  │ ─ 3-task Workflow (DAG)         │ ─ Unity Catalog Lineage         │   │
│  │ ─ Cron: 2:00 AM IST daily      │ ─ Delta Time Travel             │   │
│  │ ─ Email alerts on failure       │ ─ DLT Event Log                 │   │
│  │ ─ Validation notebook gate      │ ─ SQL Alerts                    │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Star Schema (Gold Layer)

```
  ┌───────────────────┐          ┌───────────────────────────┐          ┌───────────────────┐
  │   dim_supplier    │          │    fact_goods_receipts     │          │   dim_material     │
  │   (SCD Type 1)    │          │                           │          │   (SCD Type 2)     │
  ├───────────────────┤          ├───────────────────────────┤          ├───────────────────┤
  │ supplier_id  (PK) │◀─────── │ supplier_sk  (FK)         │ ───────▶│ material_id  (PK) │
  │ po_id              │          │ material_sk  (FK)         │          │ unit_of_measure    │
  │ plant_id           │          │ gr_sk  (PK)               │          │ unit_price         │
  │ unit_of_measure    │          │ gr_id                     │          │ __START_AT         │
  │ unit_price         │          │ po_id                     │          │ __END_AT           │
  │ _silver_ts         │          │ quantity_received         │          │ _silver_ts         │
  │ _gold_ts           │          │ quantity_rejected         │          │ _gold_ts           │
  └───────────────────┘          │ quantity_accepted         │          └───────────────────┘
                                  │ unit_price                │
                                  │ total_value               │
                                  │ receipt_date              │
                                  │ _gold_ts                  │
                                  └───────────────────────────┘
```

## Project Structure

```
├── phase4/                         # Bronze → Silver (DLT)
│   ├── 04_bronze_to_silver.py      # Auto Loader + quality expectations
│   └── screenshots/
├── phase5/                         # Silver → Gold (Star Schema)
│   ├── 05_silver_to_gold.py        # SCD Type 1/2 + fact table
│   └── screenshots/
├── phase6/                         # Orchestration & Scheduling
│   ├── 06_validate_gold.py         # Post-pipeline validation gate
│   └── screenshots/
└── phase7/                         # Lineage & Observability
    └── screenshots/
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Cloud | Microsoft Azure |
| Storage | ADLS Gen2 (Bronze container) |
| Compute | Azure Databricks |
| Ingestion | Auto Loader (cloudFiles) |
| Transformation | Delta Live Tables (DLT) |
| Data Quality | DLT Expectations (expect, expect_or_drop) |
| SCD Handling | `dlt.apply_changes()` — Type 1 & Type 2 |
| Catalog | Unity Catalog (procurement_db) |
| Orchestration | Databricks Workflows (3-task DAG) |
| Scheduling | Quartz Cron — daily 2:00 AM IST |
| Alerting | SQL Alerts + email notifications |
| Governance | Column-level lineage, Delta time travel |

## Key Highlights

- **22K+ goods receipts** and **28K+ purchase orders** processed through quality gates
- **SCD Type 2** on `dim_material` — full history with `__START_AT` / `__END_AT` versioning
- **Zero NULL surrogate keys** — validated via automated checks
- **37 Delta versions** tracked with time travel capability
- **Automated failure detection** — validation notebook blocks bad data from reaching Gold

## Phases Breakdown

| Phase | Focus | Notebook |
|-------|-------|----------|
| 4 | Bronze → Silver ingestion + cleansing | `04_bronze_to_silver.py` |
| 5 | Silver → Gold star schema + SCD | `05_silver_to_gold.py` |
| 6 | Workflow orchestration + scheduling | `06_validate_gold.py` |
| 7 | Lineage, time travel, observability | — |

---

*Built as part of the AiSPRY Data Engineering Program.*
