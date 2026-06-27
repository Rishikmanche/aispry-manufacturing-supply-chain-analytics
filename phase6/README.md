# Phase 6 — Orchestration & Scheduling

## Overview
Orchestrates Phase 4 and Phase 5 pipelines in a Databricks Workflow with a validation notebook. Scheduled daily at 2:00 AM IST with email failure notifications.

## Workflow
- **Name:** Procurement_Pipeline_Orchestration
- **Job ID:** 396138927034308
- **Schedule:** 0 0 2 * * ? (Quartz cron — 2:00 AM Asia/Calcutta)
- **Failure notification:** rishikmanche@gmail.com

## Tasks
| Task | Type | Depends On |
|------|------|------------|
| Bronze_to_Silver_DLT | Delta Live Tables pipeline | none |
| Silver_to_Gold_DLT | Delta Live Tables pipeline | Bronze_to_Silver_DLT (Success) |
| Validate_Gold | Notebook | Silver_to_Gold_DLT (Success) |

## Validation Checks
- fact_goods_receipts is not empty
- No NULL supplier_sk in fact table
- dim_material has at least one current row (__END_AT IS NULL)

## Screenshots
| File | Description |
|------|-------------|
| 01_workflow_dag.png | Workflow DAG — 3 tasks with dependency arrows |
| 02_successful_run.png | All 3 tasks green with timestamps |
| 03_failure_test.png | Validate_Gold red + failure email received |
| 04_schedule_settings.png | Cron expression and IST timezone visible |
