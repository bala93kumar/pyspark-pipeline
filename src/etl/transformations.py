from pyspark.sql import DataFrame
from pyspark.sql.functions import col, current_timestamp, trim, upper


def clean_marketing_campaigns(df: DataFrame) -> DataFrame:
    """Clean raw marketing campaigns for the silver layer."""
    return (
        df.filter(col("campaign_id").isNotNull() & (col("budget") > 0))
        .withColumn("campaign_name", upper(trim(col("campaign_name"))))
        .withColumn("processed_at", current_timestamp())
    )
