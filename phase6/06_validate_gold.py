# 06_validate_gold.py — Validation Notebook
checks = {
    'fact_not_empty': spark.table('procurement_db.gold.fact_goods_receipts').count() > 0,
    'no_null_supplier_sk': spark.sql('SELECT COUNT(*) FROM procurement_db.gold.fact_goods_receipts WHERE supplier_sk IS NULL').collect()[0][0] == 0,
    'dim_has_current_material': spark.sql('SELECT COUNT(*) FROM procurement_db.gold.dim_material WHERE __END_AT IS NULL').collect()[0][0] > 0,
}
failed = [k for k, v in checks.items() if not v]
if failed:
    raise Exception(f'Validation FAILED: {failed}')
print('All checks passed')
dbutils.notebook.exit('OK')
