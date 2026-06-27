# 04_bronze_to_silver.py — DLT Pipeline Notebook
import dlt
from pyspark.sql import functions as F

BRONZE_PATH = "abfss://bronze@rishikphase3storage.dfs.core.windows.net/"

@dlt.table(name="bronze_purchase_orders", comment="Raw purchase orders from ADLS")
def bronze_purchase_orders():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "parquet")
            .option("cloudFiles.schemaLocation", BRONZE_PATH + "_schemas/purchase_orders")
            .load(BRONZE_PATH + "purchase_orders/"))

@dlt.table(name="bronze_goods_receipts", comment="Raw goods receipts from ADLS")
def bronze_goods_receipts():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "parquet")
            .option("cloudFiles.schemaLocation", BRONZE_PATH + "_schemas/goods_receipts")
            .load(BRONZE_PATH + "goods_receipts/"))

@dlt.table(
    name="silver_purchase_orders",
    comment="Cleansed purchase orders",
    table_properties={"quality": "silver", "delta.enableChangeDataFeed": "true"}
)
@dlt.expect_or_drop("valid_po_id", "po_id IS NOT NULL")
@dlt.expect_or_drop("valid_supplier", "supplier_id IS NOT NULL")
@dlt.expect("positive_quantity", "quantity_ordered > 0")
def silver_purchase_orders():
    return (dlt.read_stream("bronze_purchase_orders")
            .withColumn("po_id", F.col("po_id").cast("string"))
            .withColumn("supplier_id", F.trim(F.col("supplier_id")))
            .withColumn("material_id", F.trim(F.col("material_id")))
            .withColumn("quantity_ordered", F.col("quantity_ordered").cast("double"))
            .withColumn("unit_price", F.col("unit_price").cast("double"))
            .withColumn("total_value", F.col("total_value").cast("double"))
            .withColumn("order_date", F.to_date(F.col("order_date")))
            .withColumn("_silver_ts", F.current_timestamp()))

@dlt.table(
    name="silver_goods_receipts",
    comment="Cleansed goods receipts",
    table_properties={"quality": "silver", "delta.enableChangeDataFeed": "true"}
)
@dlt.expect_or_drop("valid_gr_id", "gr_id IS NOT NULL")
@dlt.expect_or_drop("valid_supplier", "supplier_id IS NOT NULL")
@dlt.expect_or_drop("positive_quantity_received", "quantity_received > 0")
def silver_goods_receipts():
    return (dlt.read_stream("bronze_goods_receipts")
            .withColumn("gr_id", F.col("gr_id").cast("string"))
            .withColumn("supplier_id", F.trim(F.col("supplier_id")))
            .withColumn("material_id", F.trim(F.col("material_id")))
            .withColumn("quantity_received", F.col("quantity_received").cast("double"))
            .withColumn("quantity_rejected", F.col("quantity_rejected").cast("double"))
            .withColumn("quantity_accepted", F.col("quantity_accepted").cast("double"))
            .withColumn("unit_price", F.col("unit_price").cast("double"))
            .withColumn("total_value", F.col("total_value").cast("double"))
            .withColumn("receipt_date", F.to_date(F.col("receipt_date")))
            .withColumn("_silver_ts", F.current_timestamp()))
