"""Load sample marketing data into the bronze layer."""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType, TimestampType
from datetime import datetime


def create_sample_marketing_data(spark: SparkSession) -> DataFrame:
    """Generate sample marketing campaign data for the bronze layer."""
    schema = StructType(
        [
            StructField("campaign_id", StringType(), False),
            StructField("campaign_name", StringType(), False),
            StructField("channel", StringType(), False),
            StructField("budget", DoubleType(), False),
            StructField("spend", DoubleType(), False),
            StructField("impressions", IntegerType(), False),
            StructField("clicks", IntegerType(), False),
            StructField("conversions", IntegerType(), False),
            StructField("loaded_at", TimestampType(), False),
        ]
    )

    data = [
        ("C001", "  Summer Sale 2024  ", "email", 5000.0, 4200.0, 50000, 1200, 45, datetime.now()),
        ("C002", "Winter Promo", "social", 3000.0, 2800.0, 75000, 2100, 120, datetime.now()),
        ("C003", "Black Friday", "display", 8000.0, 7900.0, 200000, 5500, 450, datetime.now()),
        ("C004", "Spring Launch", "search", 4500.0, 4100.0, 100000, 3200, 280, datetime.now()),
        ("C005", "Q4 Clearance", "email", 6000.0, 5800.0, 120000, 2800, 95, datetime.now()),
        (None, "Invalid Campaign", "social", 1000.0, 900.0, 10000, 100, 5, datetime.now()),
        ("C006", "Back to School", "display", -500.0, 450.0, 80000, 2000, 150, datetime.now()),
    ]

    return spark.createDataFrame(data, schema)


def load_bronze_marketing(spark: SparkSession, table_path: str) -> None:
    """Load sample data into the marketing.bronze_campaigns table."""
    df = create_sample_marketing_data(spark)
    df.write.mode("overwrite").option("mergeSchema", "true").saveAsTable(
        "marketing.bronze_campaigns", path=table_path
    )
    print(f"Loaded {df.count()} records into marketing.bronze_campaigns")
