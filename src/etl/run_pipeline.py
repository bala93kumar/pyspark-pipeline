"""Medallion Pipeline Runner: Bronze -> Silver -> Gold (Serverless Optimized)."""

import argparse
import sys
from pyspark.sql import SparkSession
from src.etl.transformations import aggregate_campaign_kpis, clean_marketing_campaigns

DEFAULT_CATALOG = "dbx_demo_dev_ws_7405605201845024"


def run_pipeline(catalog: str):
    spark = SparkSession.builder.appName("marketing_medallion_etl").getOrCreate()

    bronze_table = f"`{catalog}`.marketing_bronze.raw_campaigns"
    silver_table = f"`{catalog}`.marketing_silver.cleaned_campaigns"
    gold_table = f"`{catalog}`.marketing_gold.campaign_roi_summary"

    print(f"=== Starting Marketing Medallion Pipeline for Catalog: {catalog} ===")

    # 1. READ BRONZE (Auto-seed if table doesn't exist yet)
    unquoted_table = bronze_table.replace("`", "")
    if not spark.catalog.tableExists(unquoted_table):
        print(f"Table {bronze_table} not found. Seeding initial dummy bronze data...")
        from src.etl.seed_bronze import seed_bronze

        seed_bronze(catalog)

    print(f"[1/3] Reading raw data from bronze: {bronze_table}...")
    bronze_df = spark.read.table(bronze_table)
    bronze_count = bronze_df.count()
    print(f"      Loaded {bronze_count} bronze records.")

    # 2. TRANSFORM & WRITE SILVER
    print(f"[2/3] Cleaning and transforming data to silver...")
    silver_df = clean_marketing_campaigns(bronze_df)
    silver_df.write.format("delta").mode("overwrite").saveAsTable(silver_table)
    silver_count = spark.read.table(silver_table).count()
    print(f"      Saved {silver_count} cleaned records to {silver_table}.")

    # 3. AGGREGATE & WRITE GOLD
    print(f"[3/3] Aggregating KPIs to gold...")
    gold_df = aggregate_campaign_kpis(silver_df)
    gold_df.write.format("delta").mode("overwrite").saveAsTable(gold_table)
    gold_count = spark.read.table(gold_table).count()
    print(f"      Saved {gold_count} KPI records to {gold_table}.")

    print("=== Pipeline completed successfully! ===")


def main():
    parser = argparse.ArgumentParser(description="Run marketing bronze to gold pipeline")
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG,
        help=f"Target Unity Catalog (default: {DEFAULT_CATALOG})",
    )
    args, unknown = parser.parse_known_args()

    # Support positional argument if supplied by Databricks task parameters
    catalog = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else args.catalog
    run_pipeline(catalog)


if __name__ == "__main__":
    main()
