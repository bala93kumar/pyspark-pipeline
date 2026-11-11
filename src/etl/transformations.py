from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    avg,
    col,
    count,
    current_timestamp,
    round,
    sum as _sum,
    trim,
    upper,
    when,
)


def clean_marketing_campaigns(df: DataFrame) -> DataFrame:
    """Clean raw marketing campaigns for the silver layer.

    - Filters out rows with null campaign_id or budget <= 0.
    - Normalizes campaign_name and channel to trimmed uppercase.
    - Adds a processed_at timestamp.
    """
    cleaned = df.filter(col("campaign_id").isNotNull() & (col("budget") > 0))
    cleaned = cleaned.withColumn("campaign_name", upper(trim(col("campaign_name"))))
    if "channel" in df.columns:
        cleaned = cleaned.withColumn("channel", upper(trim(col("channel"))))
    return cleaned.withColumn("processed_at", current_timestamp())


def aggregate_campaign_kpis(silver_df: DataFrame) -> DataFrame:
    """Aggregate cleaned silver campaigns into gold layer KPIs grouped by channel."""
    has_clicks_and_conversions = (
        "clicks" in silver_df.columns and "conversions" in silver_df.columns
    )

    agg_exprs = [
        count("campaign_id").alias("total_campaigns"),
        round(_sum("budget"), 2).alias("total_budget"),
        round(avg("budget"), 2).alias("avg_budget"),
    ]

    if has_clicks_and_conversions:
        agg_exprs.extend(
            [
                _sum("clicks").alias("total_clicks"),
                _sum("conversions").alias("total_conversions"),
                round(
                    when(
                        _sum("clicks") > 0,
                        (_sum("conversions") / _sum("clicks")) * 100,
                    ).otherwise(0.0),
                    2,
                ).alias("conversion_rate_pct"),
            ]
        )

    group_col = "channel" if "channel" in silver_df.columns else "campaign_name"
    return (
        silver_df.groupBy(group_col)
        .agg(*agg_exprs)
        .withColumn("updated_at", current_timestamp())
    )
