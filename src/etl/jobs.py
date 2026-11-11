"""ETL job orchestration."""
from pyspark.sql import SparkSession
import sys

from src.etl.bronze_loader import load_bronze_marketing
from src.etl.transformations import clean_marketing_campaigns
from src.etl.gold_layer import aggregate_campaign_performance


def run_bronze_to_silver_etl(spark: SparkSession, catalog: str = "hive_metastore") -> None:
    """Run the bronze to silver transformation pipeline."""
    # Read from bronze
    df_bronze = spark.sql(f"SELECT * FROM {catalog}.marketing.bronze_campaigns")

    # Transform to silver
    df_silver = clean_marketing_campaigns(df_bronze)

    # Write to silver
    df_silver.write.mode("overwrite").option("mergeSchema", "true").saveAsTable(
        f"{catalog}.marketing.silver_campaigns"
    )
    print(f"Transformed {df_silver.count()} records to silver layer")


def run_silver_to_gold_etl(spark: SparkSession, catalog: str = "hive_metastore") -> None:
    """Run the silver to gold aggregation pipeline."""
    # Read from silver
    df_silver = spark.sql(f"SELECT * FROM {catalog}.marketing.silver_campaigns")

    # Aggregate to gold
    df_gold = aggregate_campaign_performance(df_silver)

    # Write to gold
    df_gold.write.mode("overwrite").option("mergeSchema", "true").saveAsTable(
        f"{catalog}.marketing.gold_campaign_performance"
    )
    print(f"Aggregated {df_gold.count()} campaign records to gold layer")


def run_full_pipeline(spark: SparkSession, catalog: str = "hive_metastore") -> None:
    """Run the complete marketing pipeline."""
    run_bronze_to_silver_etl(spark, catalog)
    run_silver_to_gold_etl(spark, catalog)
    print("Pipeline execution completed successfully")


if __name__ == "__main__":
    # Get job name from command-line arguments (passed by Databricks)
    job_name = sys.argv[1] if len(sys.argv) > 1 else "full_pipeline"

    spark = SparkSession.builder.appName(f"marketing-{job_name}").getOrCreate()

    try:
        if job_name == "full_pipeline":
            run_full_pipeline(spark)
        elif job_name == "bronze_to_silver":
            run_bronze_to_silver_etl(spark)
        elif job_name == "silver_to_gold":
            run_silver_to_gold_etl(spark)
        else:
            raise ValueError(f"Unknown job name: {job_name}")

        print(f"✅ Job '{job_name}' completed successfully")

    except Exception as e:
        print(f"❌ Job '{job_name}' failed with error:")
        print(str(e))
        raise

    finally:
        spark.stop()

