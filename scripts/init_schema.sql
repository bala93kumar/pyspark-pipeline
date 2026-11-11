-- Initialize marketing schema and tables in Databricks
-- Run this in a Databricks notebook or SQL cell to set up the medallion architecture

-- Create catalog if needed (only works if user has CREATE CATALOG privilege)
-- CREATE CATALOG IF NOT EXISTS hive_metastore;

-- Create schema for marketing data
CREATE SCHEMA IF NOT EXISTS hive_metastore.marketing
COMMENT "Marketing analytics medallion architecture (bronze, silver, gold layers)";

-- Bronze Layer: Raw ingestion table
CREATE TABLE IF NOT EXISTS hive_metastore.marketing.bronze_campaigns (
    campaign_id STRING COMMENT "Unique campaign identifier",
    campaign_name STRING COMMENT "Campaign name from source system",
    channel STRING COMMENT "Marketing channel (email, social, display, search)",
    budget DOUBLE COMMENT "Allocated budget in dollars",
    spend DOUBLE COMMENT "Actual spend in dollars",
    impressions INT COMMENT "Number of impressions",
    clicks INT COMMENT "Number of clicks",
    conversions INT COMMENT "Number of conversions",
    loaded_at TIMESTAMP COMMENT "Timestamp when record was loaded"
)
COMMENT "Raw marketing campaign data from source systems"
TBLPROPERTIES (
    "delta.dataChangeFile" = "true",
    "delta.enableDeletionVectors" = "true"
);

-- Silver Layer: Cleaned and validated data
CREATE TABLE IF NOT EXISTS hive_metastore.marketing.silver_campaigns (
    campaign_id STRING COMMENT "Unique campaign identifier",
    campaign_name STRING COMMENT "Normalized campaign name",
    channel STRING COMMENT "Marketing channel",
    budget DOUBLE COMMENT "Budget (only positive values)",
    spend DOUBLE COMMENT "Actual spend",
    impressions INT COMMENT "Number of impressions",
    clicks INT COMMENT "Number of clicks",
    conversions INT COMMENT "Number of conversions",
    loaded_at TIMESTAMP COMMENT "Original load timestamp",
    processed_at TIMESTAMP COMMENT "Timestamp when record was processed to silver"
)
COMMENT "Cleaned and validated marketing campaign data"
TBLPROPERTIES (
    "delta.dataChangeFile" = "true",
    "delta.enableDeletionVectors" = "true"
);

-- Gold Layer: Aggregated business-ready metrics
CREATE TABLE IF NOT EXISTS hive_metastore.marketing.gold_campaign_performance (
    campaign_id STRING COMMENT "Unique campaign identifier",
    campaign_name STRING COMMENT "Campaign name",
    channel STRING COMMENT "Marketing channel",
    total_budget DOUBLE COMMENT "Total allocated budget",
    total_spend DOUBLE COMMENT "Total actual spend",
    total_impressions INT COMMENT "Total impressions",
    total_clicks INT COMMENT "Total clicks",
    total_conversions INT COMMENT "Total conversions",
    roi DOUBLE COMMENT "Return on Investment percentage",
    ctr DOUBLE COMMENT "Click-Through Rate percentage",
    conversion_rate DOUBLE COMMENT "Conversion rate percentage"
)
COMMENT "Campaign performance metrics for reporting and analytics"
TBLPROPERTIES (
    "delta.dataChangeFile" = "true",
    "delta.enableDeletionVectors" = "true"
);

-- Set data quality expectations
ALTER TABLE hive_metastore.marketing.silver_campaigns
SET TBLPROPERTIES (
    'quality_checks' = 'campaign_id NOT NULL, budget > 0'
);

-- Create external location (optional, if using external storage)
-- CREATE EXTERNAL LOCATION IF NOT EXISTS marketing_data_location
--   URL 's3://my-bucket/marketing/'
--   WITH (CREDENTIAL 'credential-name');

SHOW TABLES IN hive_metastore.marketing;
