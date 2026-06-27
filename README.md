# Manufacturing Supply Chain Analytics

End-to-end data engineering pipeline on **Azure Databricks** — ingesting raw procurement data from ADLS Gen2, transforming it through a medallion architecture, and delivering a production-grade star schema with SCD Type 2 history tracking.

- **Domain:** Procurement — Purchase Orders & Goods Receipts
- **Volume:** 10,000+ records
- **Catalog:** `procurement_db` · schemas: `bronze` · `silver` · `gold`

## Architecture

```mermaid
graph LR
    subgraph Source
        A[(ADLS Gen2 - Bronze)]
    end

    subgraph Phase 4 - Bronze to Silver
        A -->|Auto Loader| B[bronze_purchase_orders]
        A -->|Auto Loader| C[bronze_goods_receipts]
        B -->|DLT Expectations| D[silver_purchase_orders]
        C -->|DLT Expectations| E[silver_goods_receipts]
    end

    subgraph Phase 5 - Silver to Gold
        D --> F["dim_supplier - SCD1"]
        E --> F
        D --> G["dim_material - SCD2"]
        E --> G
        D --> H[fact_goods_receipts]
        E --> H
        F -->|supplier_sk| H
        G -->|material_sk| H
    end

    subgraph Phase 6 - Orchestration
        I[Databricks Workflow] -->|Task 1| J[Bronze to Silver DLT]
        J -->|on success| K[Silver to Gold DLT]
        K -->|on success| L[Validate Gold Notebook]
        L -->|on failure| M[Email Alert]
    end

    subgraph Phase 7 - Observability
        N[Unity Catalog Lineage]
        O[Delta Time Travel]
        P[DLT Event Log]
        Q[SQL Alerts]
    end
```

## Star Schema - Gold Layer

```mermaid
erDiagram
    dim_supplier ||--o{ fact_goods_receipts : "supplier_sk"
    dim_material ||--o{ fact_goods_receipts : "material_sk"

    dim_supplier {
        string supplier_id PK
        string po_id
        string plant_id
        string unit_of_measure
        double unit_price
        timestamp _silver_ts
        timestamp _gold_ts
    }

    fact_goods_receipts {
        long gr_sk PK
        string gr_id
        string po_id
        long supplier_sk FK
        long material_sk FK
        double quantity_received
        double quantity_rejected
        double quantity_accepted
        double unit_price
        double total_value
        date receipt_date
        timestamp _gold_ts
    }

    dim_material {
        string material_id PK
        string unit_of_measure
        double unit_price
        timestamp __START_AT
        timestamp __END_AT
        timestamp _silver_ts
        timestamp _gold_ts
    }
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

## Phases

| Phase | Focus | Notebook |
|-------|-------|----------|
| 4 | Bronze → Silver ingestion + cleansing | `04_bronze_to_silver.py` |
| 5 | Silver → Gold star schema + SCD | `05_silver_to_gold.py` |
| 6 | Workflow orchestration + scheduling | `06_validate_gold.py` |
| 7 | Lineage, time travel, observability | — |

---

*Built as part of the AiSPRY Data Engineering Program.*
