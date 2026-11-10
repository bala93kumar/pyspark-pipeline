from pyspark.sql.types import DoubleType, StringType, StructField, StructType

from src.etl.transformations import clean_marketing_campaigns


def test_clean_marketing_campaigns(spark):
    schema = StructType(
        [
            StructField("campaign_id", StringType(), True),
            StructField("campaign_name", StringType(), True),
            StructField("budget", DoubleType(), True),
        ]
    )
    test_data = [
        ("C1", "  summer_sale  ", 5000.0),
        ("C2", "winter_promo", -100.0),
        (None, "invalid_id", 2000.0),
    ]

    result = clean_marketing_campaigns(spark.createDataFrame(test_data, schema))

    assert result.count() == 1
    row = result.first()
    assert row["campaign_name"] == "SUMMER_SALE"
    assert row["budget"] == 5000.0
    assert row["processed_at"] is not None
