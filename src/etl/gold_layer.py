"""Gold layer aggregations and reporting tables."""
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, round as spark_round, sum as spark_sum


def aggregate_campaign_performance(df: DataFrame) -> DataFrame:
    """Aggregate campaign performance metrics for reporting."""
    return (
        df.filter(col("campaign_id").isNotNull())
        .groupBy("campaign_id", "campaign_name", "channel")
        .agg(
            spark_sum("budget").alias("total_budget"),
            spark_sum("spend").alias("total_spend"),
            spark_sum("impressions").alias("total_impressions"),
            spark_sum("clicks").alias("total_clicks"),
            spark_sum("conversions").alias("total_conversions"),
        )
        .withColumn("roi", spark_round((col("total_spend") - col("total_budget")) / col("total_budget") * 100, 2))
        .withColumn("ctr", spark_round(col("total_clicks") / col("total_impressions") * 100, 4))
        .withColumn("conversion_rate", spark_round(col("total_conversions") / col("total_clicks") * 100, 4))
    )
