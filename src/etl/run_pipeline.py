"""Medallion Pipeline Runner: Bronze -> Silver -> Gold (Serverless Optimized)."""

import argparse
import os
import sys


def _ensure_repo_root_on_path() -> None:
    """Add bundle/repo root to sys.path so `from src.etl...` works in Serverless."""
    candidates = []

    # 1. Explicit --bundle-root parameter if passed by Databricks Asset Bundles
    for i, arg in enumerate(sys.argv):
        if arg == "--bundle-root" and i + 1 < len(sys.argv):
            candidates.append(sys.argv[i + 1])
        elif arg.startswith("--bundle-root="):
            candidates.append(arg.split("=", 1)[1])

    # 2. Script file location (__file__ or ipykernel's filename variable)
    script_path = globals().get("__file__") or globals().get("filename")
    if script_path:
        candidates.append(os.path.abspath(os.path.join(os.path.dirname(script_path), "..", "..")))

    # 3. Walk up from current working directory until a 'src' directory is found
    cwd = os.getcwd()
    while cwd != os.path.dirname(cwd):
        if os.path.isdir(os.path.join(cwd, "src")):
            candidates.append(cwd)
            break
        cwd = os.path.dirname(cwd)

    for path in candidates:
        if path and os.path.isdir(path) and path not in sys.path:
            sys.path.insert(0, path)


_ensure_repo_root_on_path()

from pyspark.sql import SparkSession  # noqa: E402
from src.etl.transformations import (  # noqa: E402
    aggregate_campaign_kpis,
    clean_marketing_campaigns,
)

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
    print("[2/3] Cleaning and transforming data to silver...")
    silver_df = clean_marketing_campaigns(bronze_df)
    silver_df.write.format("delta").mode("overwrite").saveAsTable(silver_table)
    silver_count = spark.read.table(silver_table).count()
    print(f"      Saved {silver_count} cleaned records to {silver_table}.")

    # 3. AGGREGATE & WRITE GOLD
    print("[3/3] Aggregating KPIs to gold...")
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
    parser.add_argument(
        "--bundle-root",
        default=None,
        help="Optional bundle files root path",
    )
    args, unknown = parser.parse_known_args()

    # Support positional argument if supplied by Databricks task parameters
    catalog = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else args.catalog
    run_pipeline(catalog)


if __name__ == "__main__":
    main()
