# PySpark Marketing Pipeline - Developer Guide

## Overview

This repository contains the data transformation pipelines for the marketing analytics system. It implements the medallion architecture (bronze → silver → gold) using PySpark on Databricks.

**Repository Branch Structure:**
- `dev` branch → automatically deploys to DEV Databricks workspace
- `main` branch → automatically deploys to PROD Databricks workspace
- Feature branches → run tests only, no deployment

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Git
- Access to the Databricks workspace (onboarded via the platform repo)
- GitHub account with push access to this repository

### 2. Local Development Setup

```bash
# Clone the repository
git clone https://github.com/bala93kumar/pyspark-pipeline.git
cd pyspark-pipeline

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# Or macOS/Linux
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Running Local Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_transformations.py
```

Tests use a local Spark session and don't require Databricks credentials.

## Development Workflow

### For Feature Development

1. **Create a feature branch** from `dev`:
   ```bash
   git checkout -b feature/my-new-transformation dev
   ```

2. **Write transformation code** in `src/etl/`:
   - Add your transformation function
   - Add corresponding unit tests in `tests/`
   - Run `pytest tests/` locally to verify

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add new transformation for XYZ metric"
   git push origin feature/my-new-transformation
   ```

4. **Create Pull Request** to `dev` branch:
   - GitHub Actions automatically runs tests
   - Once approved, merge to `dev`
   - Deployment to DEV Databricks happens automatically

5. **Validate in DEV** Databricks workspace:
   - Check the job output in the Databricks workspace
   - Verify data in the marketing schema tables

6. **Create PR to main** when ready for production:
   - PR from `dev` → `main`
   - Once approved and merged, automatic deployment to PROD

### GitHub Actions CI/CD Pipeline

**On Every Push:**
- ✅ Run unit tests (pytest)

**On Push to `dev` Branch (after tests pass):**
- 🚀 Deploy to DEV Databricks workspace

**On Push to `main` Branch (after tests pass):**
- 🚀 Deploy to PROD Databricks workspace

## Data Architecture

### Medallion Schema Structure

**Bronze Layer** (`marketing.bronze_campaigns`)
- Raw ingestion table
- Minimal transformation
- Contains all source data including invalid records
- Source: External data sources, APIs, uploaded files

**Silver Layer** (`marketing.silver_campaigns`)
- Cleaned and validated data
- Data quality checks applied
- Invalid records filtered out
- Transformations:
  - Remove null campaign IDs
  - Remove negative budgets
  - Normalize campaign names (uppercase, trim whitespace)
  - Add processing timestamp

**Gold Layer** (`marketing.gold_campaign_performance`)
- Business-ready aggregated metrics
- Campaign-level performance analytics
- Metrics:
  - Total budget and spend
  - Impressions and clicks
  - Conversion metrics
  - ROI (Return on Investment)
  - CTR (Click-Through Rate)
  - Conversion Rate

### Example Schema

```
marketing.bronze_campaigns
├── campaign_id (STRING)
├── campaign_name (STRING)
├── channel (STRING) - email, social, display, search
├── budget (DOUBLE)
├── spend (DOUBLE)
├── impressions (INTEGER)
├── clicks (INTEGER)
├── conversions (INTEGER)
└── loaded_at (TIMESTAMP)

marketing.silver_campaigns
├── [same as bronze, plus processed_at]

marketing.gold_campaign_performance
├── campaign_id (STRING)
├── campaign_name (STRING)
├── channel (STRING)
├── total_budget (DOUBLE)
├── total_spend (DOUBLE)
├── total_impressions (INTEGER)
├── total_clicks (INTEGER)
├── total_conversions (INTEGER)
├── roi (DOUBLE)
├── ctr (DOUBLE)
└── conversion_rate (DOUBLE)
```

## Code Structure

```
src/
├── etl/
│   ├── __init__.py
│   ├── bronze_loader.py       # Sample data generation & bronze load
│   ├── transformations.py     # Silver layer transformations
│   ├── gold_layer.py          # Gold layer aggregations
│   └── jobs.py                # Job orchestration
└── __init__.py

tests/
├── __init__.py
├── conftest.py                # Pytest fixtures (Spark session)
└── test_transformations.py    # All transformation tests
```

## Writing Transformations

### Template for New Transformations

```python
# src/etl/my_transformation.py
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, sum as spark_sum

def transform_marketing_data(df: DataFrame) -> DataFrame:
    """
    Transform raw marketing data.
    
    Args:
        df: Input DataFrame from previous layer
        
    Returns:
        Transformed DataFrame ready for next layer
    """
    return (
        df
        .filter(col("campaign_id").isNotNull())
        .withColumn("new_metric", ...)
    )
```

### Add Tests

```python
# tests/test_my_transformation.py
from src.etl.my_transformation import transform_marketing_data

def test_transform_marketing_data(spark):
    schema = StructType([...])
    test_data = [...]
    df = spark.createDataFrame(test_data, schema)
    
    result = transform_marketing_data(df)
    
    assert result.count() > 0
    assert "new_metric" in result.columns
```

## Setting Up GitHub Actions Secrets (Admin Only)

The CI/CD pipeline requires Azure service principal credentials for Databricks authentication. These must be configured as GitHub repository secrets.

### Steps to Configure Secrets

1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**

2. Add three secrets (obtained from platform team):
   - `ARM_CLIENT_ID`: Azure service principal client ID
   - `ARM_CLIENT_SECRET`: Azure service principal secret
   - `ARM_TENANT_ID`: Azure tenant ID

3. **Important**: These credentials should already be securely stored in the platform repository. Never commit them to this repository.

## Running Pipelines in Databricks

### Deploy to DEV

```bash
# Merge to dev branch via pull request
# GitHub Actions will automatically:
# 1. Run tests
# 2. Deploy to DEV workspace
# 3. Run the job
```

### Deploy to PROD

```bash
# Merge to main branch via pull request
# GitHub Actions will automatically:
# 1. Run tests
# 2. Deploy to PROD workspace
# 3. Run the job
```

### Manual Deployment (if needed)

```bash
# Deploy to DEV
databricks bundle deploy -t dev

# Deploy to PROD
databricks bundle deploy -t prod

# Run a job
databricks jobs run-now --job-id <job_id>
```

## Debugging & Troubleshooting

### Local Tests Fail

```bash
# Ensure Python 3.10+
python --version

# Reinstall dependencies in clean environment
pip install --upgrade pip
pip install -r requirements.txt

# Run with verbose output
pytest -v tests/
```

### Deployment Fails in GitHub Actions

1. Check GitHub Actions logs in **Actions** tab
2. Common issues:
   - Missing or expired Azure credentials (check secrets)
   - Databricks workspace unreachable
   - Python syntax errors (would fail local tests first)

### Data Issues in Databricks

1. Check if tables exist:
   ```sql
   SHOW TABLES IN marketing;
   ```

2. Query table contents:
   ```sql
   SELECT COUNT(*) FROM marketing.bronze_campaigns;
   SELECT * FROM marketing.silver_campaigns LIMIT 5;
   ```

3. Check job logs in Databricks workspace

## Best Practices

### Code Quality
- Write tests for all transformations
- Use type hints in functions
- Keep transformations focused and reusable
- Document complex business logic

### Performance
- Filter early to reduce data volume
- Use partitioning for large tables
- Avoid unnecessary transformations
- Test with realistic data volumes

### Git Workflow
- Use descriptive branch names: `feature/`, `bugfix/`, `hotfix/`
- Write clear commit messages
- Keep PRs focused on single features
- Request review before merging to `dev` or `main`

### Data Quality
- Validate data in silver layer
- Handle nulls explicitly
- Document data contracts between layers
- Monitor data lineage

## Need Help?

- **Code issues**: Create GitHub issues in this repository
- **Access issues**: Contact platform team in the Databricks_CI_CD_apps repository
- **Databricks workspace questions**: Refer to [Databricks Documentation](https://docs.databricks.com)

## Related Repositories

- **Platform Management**: https://github.com/bala93kumar/Databricks_CI_CD_apps
  - Infrastructure setup
  - User access management
  - Workspace configuration
  - Unity Catalog administration
