"""Seed small sample dummy data into the marketing_bronze schema."""

import argparse
import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

DEFAULT_CATALOG = "dbx_demo_dev_ws_7405605201845024"


def get_dummy_data(spark: SparkSession):
    schema = StructType(
        [
            StructField("campaign_id", StringType(), True),
            StructField("campaign_name", StringType(), True),
            StructField("channel", StringType(), True),
            StructField("budget", DoubleType(), True),
            StructField("clicks", DoubleType(), True),
            StructField("conversions", DoubleType(), True),
        ]
    )

    data = [
        ("C101", "  summer_sale_search  ", "Search", 5000.0, 12000.0, 480.0),
        ("C102", "facebook_retargeting", "Social", 3500.0, 9500.0, 290.0),
        ("C103", "newsletter_blast_q3", "Email", 800.0, 4100.0, 310.0),
        ("C104", "invalid_campaign_zero_budget", "Social", 0.0, 0.0, 0.0),
        ("C105", "negative_budget_error", "Display", -250.0, 100.0, 0.0),
        (None, "missing_id_campaign", "Search", 1200.0, 300.0, 12.0),
        ("C106", "  holiday_deals_google  ", "Search", 8500.0, 22000.0, 1100.0),
        ("C107", "instagram_influencer_q4", "Social", 4200.0, 11200.0, 390.0),
    ]

    return spark.createDataFrame(data, schema)


def seed_bronze(catalog: str):
    spark = SparkSession.builder.appName("seed_marketing_bronze").getOrCreate()

    target_table = f"`{catalog}`.marketing_bronze.raw_campaigns"
    print(f"Preparing dummy data for {target_table}...")

    df = get_dummy_data(spark)
    total_count = df.count()
    print(f"Generated {total_count} sample records.")

    print(f"Writing to Delta table {target_table}...")
    df.write.format("delta").mode("overwrite").saveAsTable(target_table)
    print("Successfully seeded bronze table.")


def main():
    parser = argparse.ArgumentParser(description="Seed dummy marketing bronze data")
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG,
        help=f"Target Unity Catalog (default: {DEFAULT_CATALOG})",
    )
    args, unknown = parser.parse_known_args()

    # Also support positional argument if passed from Databricks CLI / job
    catalog = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else args.catalog
    seed_bronze(catalog)


if __name__ == "__main__":
    main()
