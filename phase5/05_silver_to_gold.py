# 05_silver_to_gold.py — DLT Pipeline Notebook
import dlt
from pyspark.sql import functions as F

@dlt.table(name="src_silver_purchase_orders", comment="Silver PO pass-through")
def src_silver_purchase_orders():
    return spark.readStream.table("procurement_db.silver.silver_purchase_orders")

@dlt.table(name="src_silver_goods_receipts", comment="Silver GR pass-through")
def src_silver_goods_receipts():
    return spark.readStream.table("procurement_db.silver.silver_goods_receipts")

# DIM_SUPPLIER — SCD Type 1
dlt.create_streaming_table(
    name="dim_supplier",
    comment="Supplier dimension — SCD Type 1",
    table_properties={"quality": "gold"}
)

dlt.apply_changes(
    target="dim_supplier",
    source="src_silver_goods_receipts",
    keys=["supplier_id"],
    sequence_by=F.col("_silver_ts"),
    stored_as_scd_type=1
)

# DIM_MATERIAL — SCD Type 2
dlt.create_streaming_table(
    name="dim_material",
    comment="Material dimension — SCD Type 2 history preserved",
    table_properties={"quality": "gold", "delta.enableChangeDataFeed": "true"}
)

dlt.apply_changes(
    target="dim_material",
    source="src_silver_goods_receipts",
    keys=["material_id"],
    sequence_by=F.col("_silver_ts"),
    stored_as_scd_type=2,
    track_history_column_list=["unit_of_measure", "unit_price"]
)

# FACT_GOODS_RECEIPTS
@dlt.table(
    name="fact_goods_receipts",
    comment="Goods receipts fact table — incremental",
    table_properties={"quality": "gold"}
)
@dlt.expect_or_drop("valid_gr_id", "gr_id IS NOT NULL")
@dlt.expect_or_drop("positive_quantity", "quantity_received > 0")
def fact_goods_receipts():
    gr = (dlt.read_stream("src_silver_goods_receipts")
          .filter(F.col("supplier_id").isNotNull())
          .filter(F.col("material_id").isNotNull()))

    dim_sup = (dlt.read("dim_supplier")
               .select("supplier_id",
                       F.abs(F.hash(F.col("supplier_id"))).cast("long").alias("supplier_sk")))

    dim_mat = (dlt.read("dim_material")
               .filter(F.col("__END_AT").isNull())
               .select("material_id",
                       F.abs(F.hash(F.col("material_id"))).cast("long").alias("material_sk")))

    return (gr
            .join(dim_sup, "supplier_id", "left")
            .join(dim_mat, "material_id", "left")
            .withColumn("gr_sk", F.abs(F.hash(F.col("gr_id"))).cast("long"))
            .withColumn("_gold_ts", F.current_timestamp())
            .select("gr_sk", "gr_id", "po_id",
                    "supplier_sk", "material_sk",
                    "quantity_received", "quantity_rejected", "quantity_accepted",
                    "unit_price", "total_value", "receipt_date", "_gold_ts"))
