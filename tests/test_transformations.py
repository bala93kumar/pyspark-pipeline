from pyspark.sql.types import DoubleType, StringType, StructField, StructType

from src.etl.transformations import aggregate_campaign_kpis, clean_marketing_campaigns


def test_clean_marketing_campaigns(spark):
    schema = StructType(
        [
            StructField("campaign_id", StringType(), True),
            StructField("campaign_name", StringType(), True),
            StructField("channel", StringType(), True),
            StructField("budget", DoubleType(), True),
        ]
    )
    test_data = [
        ("C1", "  summer_sale  ", "search", 5000.0),
        ("C2", "winter_promo", "social", -100.0),      # Invalid budget <= 0
        ("C3", "zero_promo", "email", 0.0),            # Invalid budget == 0
        (None, "invalid_id", "search", 2000.0),        # Invalid null ID
    ]

    result = clean_marketing_campaigns(spark.createDataFrame(test_data, schema))

    assert result.count() == 1
    row = result.first()
    assert row["campaign_name"] == "SUMMER_SALE"
    assert row["channel"] == "SEARCH"
    assert row["budget"] == 5000.0
    assert row["processed_at"] is not None


def test_aggregate_campaign_kpis(spark):
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
    test_data = [
        ("C1", "CAMP_1", "SEARCH", 1000.0, 500.0, 50.0),
        ("C2", "CAMP_2", "SEARCH", 2000.0, 1500.0, 150.0),
        ("C3", "CAMP_3", "SOCIAL", 1500.0, 800.0, 40.0),
    ]

    silver_df = spark.createDataFrame(test_data, schema)
    gold_df = aggregate_campaign_kpis(silver_df)

    results = {row["channel"]: row for row in gold_df.collect()}

    assert len(results) == 2
    assert "SEARCH" in results
    assert "SOCIAL" in results

    search_row = results["SEARCH"]
    assert search_row["total_campaigns"] == 2
    assert search_row["total_budget"] == 3000.0
    assert search_row["avg_budget"] == 1500.0
    assert search_row["total_clicks"] == 2000.0
    assert search_row["total_conversions"] == 200.0
    assert search_row["conversion_rate_pct"] == 10.0  # (200 / 2000) * 100
    assert search_row["updated_at"] is not None
