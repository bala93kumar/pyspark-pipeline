"""
Quick Start Guide for Marketing Pipeline Developers

This guide provides a checklist for developers who are new to this repository.
"""

# Developer Quick Start Checklist

## Week 1: Onboarding

- [ ] **Request Access**
  - Get Databricks workspace access from platform team
  - You should be onboarded to both DEV and PROD workspaces
  - Verify you have write access to DEV, read-only to PROD

- [ ] **Clone Repository**
  ```bash
  git clone https://github.com/bala93kumar/pyspark-pipeline.git
  cd pyspark-pipeline
  ```

- [ ] **Set Up Local Environment**
  ```bash
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

- [ ] **Run Local Tests** (verify setup works)
  ```bash
  pytest tests/ -v
  ```

- [ ] **Explore the Code**
  - Read `README.md` for full documentation
  - Check `src/etl/transformations.py` to see silver layer logic
  - Check `src/etl/gold_layer.py` for aggregation logic

## Your First Feature

- [ ] **Create Feature Branch**
  ```bash
  git checkout -b feature/my-feature dev
  ```

- [ ] **Add Your Transformation**
  - Add function to `src/etl/transformations.py` or `src/etl/gold_layer.py`
  - Example:
    ```python
    def my_new_transformation(df: DataFrame) -> DataFrame:
        return df.filter(col("value") > 0)
    ```

- [ ] **Write Tests**
  - Add tests to `tests/test_transformations.py`
  - Run locally: `pytest tests/ -v`
  - Aim for 80%+ code coverage

- [ ] **Commit and Push**
  ```bash
  git add src/ tests/
  git commit -m "Add new transformation for XYZ"
  git push origin feature/my-feature
  ```

- [ ] **Create Pull Request**
  - Go to GitHub → Pull Requests → New Pull Request
  - Base: `dev` | Compare: `feature/my-feature`
  - Wait for tests to pass (green checkmark ✅)
  - Request review from team

- [ ] **Merge to Dev**
  - Once approved, click "Squash and merge" or "Create a merge commit"
  - This triggers automatic deployment to DEV workspace

- [ ] **Test in DEV Workspace**
  - Go to Databricks DEV workspace
  - Find the "Marketing ETL Pipeline" job
  - Check job run output
  - Query the tables:
    ```sql
    SELECT COUNT(*) FROM marketing.silver_campaigns;
    SELECT * FROM marketing.gold_campaign_performance LIMIT 5;
    ```

- [ ] **Promote to Production** (when ready)
  - Create PR from `dev` → `main`
  - Get approval
  - Merge to trigger PROD deployment

## Common Tasks

### Query Data in Databricks

```sql
-- Check raw data
SELECT * FROM marketing.bronze_campaigns LIMIT 5;

-- Check cleaned data
SELECT COUNT(*) FROM marketing.silver_campaigns;
SELECT * FROM marketing.silver_campaigns WHERE campaign_id = 'C001';

-- Check aggregations
SELECT * FROM marketing.gold_campaign_performance;

-- Check data quality
SELECT campaign_id, COUNT(*) as count 
FROM marketing.silver_campaigns 
GROUP BY campaign_id;
```

### Run a Specific Job

In Databricks workspace:
1. Click **Workflows** → **Jobs**
2. Find "[dev] Marketing ETL Pipeline" or "[prod] Marketing ETL Pipeline"
3. Click **Run Now**
4. Monitor execution in **Runs** tab

### Debug a Failed Job

1. Go to Databricks workspace → **Workflows** → **Jobs**
2. Click the failed run
3. Click **run_full_pipeline** task
4. Scroll to bottom to see error message
5. Common errors:
   - `Table not found`: Schema not initialized, run `scripts/init_schema.sql`
   - `Permission denied`: Contact platform team for access
   - `Data quality error`: Check filters in transformation code

### View Logs

**GitHub Actions logs:**
1. Go to GitHub repository
2. Click **Actions** tab
3. Click the workflow run
4. Click job name to see full log
5. Look for error messages in red

**Databricks job logs:**
1. Go to Databricks workspace
2. Click **Workflows** → **Jobs**
3. Click job name
4. Click recent run
5. Expand task to see logs

## Useful Commands

```bash
# Run tests locally
pytest tests/ -v

# Run specific test
pytest tests/test_transformations.py::test_aggregate_campaign_performance -v

# Run with coverage
pytest --cov=src tests/

# Format code (if using black)
black src/ tests/

# Check types (if using mypy)
mypy src/

# List git branches
git branch -a

# Switch branch
git checkout dev

# Create and switch branch
git checkout -b feature/my-feature dev

# See uncommitted changes
git status

# See what changed in a file
git diff src/etl/transformations.py

# Revert a file (discard local changes)
git checkout -- src/etl/transformations.py
```

## When Things Go Wrong

| Problem | Solution |
|---------|----------|
| Tests fail locally | Run `pip install -r requirements.txt` again to refresh dependencies |
| Can't push to GitHub | Check you have write access; verify branch name is correct |
| Job fails in Databricks | Check error logs in job run details; verify schema exists with `init_schema.sql` |
| Merge conflicts | Pull latest dev: `git pull origin dev` then resolve conflicts |
| Accidentally broke main | Contact platform team; they have backups |
| Need to rollback deployment | Create new PR reverting the change; merge to same branch |

## Getting Help

1. **Code Questions**: Post in #data-engineering Slack channel
2. **Access Issues**: Contact @platform-team
3. **Databricks Questions**: Check [Databricks Docs](https://docs.databricks.com)
4. **Git Issues**: Ask a senior developer

## Resources

- 📖 [README.md](README.md) - Full documentation
- 🔐 [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - CI/CD secrets setup
- 🗄️ [scripts/init_schema.sql](scripts/init_schema.sql) - Schema initialization
- 🏗️ [Databricks CI/CD Platform Repo](https://github.com/bala93kumar/Databricks_CI_CD_apps) - Infrastructure setup

---

**You're all set!** 🚀 Create your first feature branch and start building.
