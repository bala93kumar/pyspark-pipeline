"""
Complete Developer Workflow Guide for Marketing Pipeline

This document provides an end-to-end walkthrough of how developers interact with
this repository from day 1 to production deployment.
"""

# Complete Developer Workflow Guide

## Pre-Requisites

Before starting, ensure you have:

1. **Databricks Access**
   - You've been onboarded by the platform team
   - You can access both DEV and PROD Databricks workspaces
   - You have write access to DEV and read-only access to PROD

2. **GitHub Access**
   - You have a GitHub account with push access to this repository
   - You've configured SSH keys or personal access tokens for git

3. **Local Development**
   - Python 3.10+ installed
   - Git installed and configured
   - A code editor (VS Code, PyCharm, etc.)

4. **Infrastructure Ready**
   - The `marketing` schema exists in Databricks
   - Bronze, silver, and gold tables are created
   - (If not, ask platform team to run `scripts/init_schema.sql`)

---

## Workflow: End-to-End Example

### Scenario
You need to add a new feature to filter out low-ROI campaigns in the gold layer.

### Step 1: Prepare Your Local Environment

```bash
# Navigate to repo directory
cd ~/projects/pyspark-pipeline

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Pull latest changes from dev
git fetch origin
git checkout dev
git pull origin dev

# Verify you're on dev branch
git status
# Should show: On branch dev
```

### Step 2: Create Feature Branch

```bash
# Create a new branch from dev
git checkout -b feature/filter-low-roi-campaigns dev

# Verify branch was created
git branch
# Should show: * feature/filter-low-roi-campaigns
```

### Step 3: Implement Your Feature

**File: `src/etl/gold_layer.py`**

Add a new function:

```python
def filter_high_roi_campaigns(df: DataFrame, min_roi: float = 10.0) -> DataFrame:
    """Filter campaigns with ROI above threshold for executive reporting."""
    return df.filter(col("roi") >= min_roi)
```

### Step 4: Write Tests

**File: `tests/test_transformations.py`**

Add a test function:

```python
def test_filter_high_roi_campaigns(spark):
    """Test filtering by ROI threshold."""
    schema = StructType([
        StructField("campaign_id", StringType(), False),
        StructField("roi", DoubleType(), False),
    ])
    
    data = [
        ("C1", 15.0),  # Include
        ("C2", 5.0),   # Filter out
        ("C3", 20.0),  # Include
    ]
    
    df = spark.createDataFrame(data, schema)
    result = filter_high_roi_campaigns(df, min_roi=10.0)
    
    assert result.count() == 2
    assert result.where(col("campaign_id") == "C2").count() == 0
```

### Step 5: Run Local Tests

```bash
# Run all tests
pytest tests/ -v

# Or run just your new test
pytest tests/test_transformations.py::test_filter_high_roi_campaigns -v

# Check test coverage
pytest --cov=src tests/

# Expected output:
# test_filter_high_roi_campaigns PASSED
# ✅ All tests pass
```

### Step 6: Review Your Changes

```bash
# See what you changed
git status
# Shows modified/untracked files

# Review specific changes
git diff src/etl/gold_layer.py

# See all changes
git diff
```

### Step 7: Commit Your Changes

```bash
# Stage your changes
git add src/etl/gold_layer.py tests/test_transformations.py

# Verify what's staged
git status
# Should show green "Changes to be committed:"

# Commit with descriptive message
git commit -m "Add high-ROI campaign filter for executive reporting

- Filter campaigns with ROI >= threshold
- Enables executive-focused analytics view
- Min ROI threshold configurable (default 10%)

Tests added for threshold filtering logic"

# Verify commit was created
git log --oneline -1
```

### Step 8: Push to GitHub

```bash
# Push your feature branch to GitHub
git push origin feature/filter-low-roi-campaigns

# Output should show:
# remote: Create a pull request for 'feature/filter-low-roi-campaigns' on GitHub
```

### Step 9: Create Pull Request

**In GitHub Web UI:**

1. Go to repository: https://github.com/bala93kumar/pyspark-pipeline
2. You'll see a banner: "Compare & pull request" - click it
3. Or go to **Pull requests** tab → **New pull request**
4. Configure:
   - **Base**: `dev` (where it will merge)
   - **Compare**: `feature/filter-low-roi-campaigns` (your branch)
5. Click "Create pull request"
6. Fill in PR template:
   - Title: "Add high-ROI campaign filter for executive reporting"
   - Description: Link to feature design, testing notes, etc.
7. Click "Create pull request"

### Step 10: GitHub Actions Runs Automatically

**What happens:**
- ✅ GitHub Actions automatically runs tests (you'll see status checks)
- ✅ Tests must pass before you can merge
- ❌ If tests fail, click details to see error logs

**If tests fail:**
1. Scroll down in the PR to see which test failed
2. Click "Details" next to the failed test
3. Read the error message
4. Fix the bug locally:
   ```bash
   git checkout feature/filter-low-roi-campaigns
   # Fix the code
   pytest tests/ -v  # Verify it's fixed
   git add .
   git commit -m "Fix test for ROI filter"
   git push origin feature/filter-low-roi-campaigns
   ```
5. The PR automatically re-runs tests with your new commit

### Step 11: Request Code Review

In the GitHub PR:
1. On the right side under "Reviewers", click the icon
2. Select a team member to review your code
3. Leave a comment: "Ready for review 🚀"

### Step 12: Address Review Comments (if any)

When reviewers suggest changes:
1. Make the changes locally
2. Run tests: `pytest tests/ -v`
3. Commit: `git commit -m "Address review: clarify ROI filtering logic"`
4. Push: `git push origin feature/filter-low-roi-campaigns`
5. Reply in the GitHub PR thread: "Done, pushed new commits"

### Step 13: Merge to Dev

Once approved (green ✅):
1. In the GitHub PR, click "Merge pull request"
2. Choose merge strategy (suggest "Squash and merge")
3. Click "Confirm merge"
4. Delete the feature branch (GitHub will offer this)

### Step 14: Automatic Deployment to DEV

**What GitHub Actions does automatically:**
1. Pulls latest `dev` branch
2. Runs all tests
3. Deploys to DEV Databricks workspace (1-3 minutes)
4. You'll see workflow completion in the "Actions" tab

### Step 15: Validate in DEV Workspace

Go to Databricks DEV workspace:

1. Click **Workflows** → **Jobs**
2. Find "[dev] Marketing ETL Pipeline"
3. Click "Run now" to execute the pipeline
4. Monitor the run in the **Runs** tab
5. Once complete, query the data:

```sql
-- Verify gold layer has your new filtered view
SELECT campaign_id, roi FROM marketing.gold_campaign_performance;

-- Test your filter function would work
SELECT * FROM marketing.gold_campaign_performance WHERE roi >= 10.0;
```

### Step 16: Promote to Production

Once you're satisfied with DEV testing:

1. Go to GitHub → **Pull requests** → **New pull request**
2. Configure:
   - Base: `main`
   - Compare: `dev`
3. Title: "Promote dev to main - high ROI campaign filter"
4. Add description with testing notes
5. Get approval from tech lead
6. Merge to `main`

### Step 17: Automatic Deployment to PROD

**What happens automatically:**
1. GitHub Actions runs tests on `main`
2. Deploys to PROD workspace
3. Job executes automatically

**Verify PROD deployment:**
```bash
# In Databricks PROD workspace
SELECT * FROM marketing.gold_campaign_performance WHERE roi >= 10.0;
```

---

## Common Workflow Shortcuts

### Quick Test Fix During Code Review

```bash
# You're on feature branch with code review comments

# Make your fix
# ... edit files ...

# Test it
pytest tests/ -v

# Commit and push (new commit, don't amend)
git add .
git commit -m "Address review: [specific comment]"
git push origin feature/filter-low-roi-campaigns

# GitHub PR auto-updates with new commit
```

### Sync Your Branch with Latest Dev

```bash
# Get latest changes
git fetch origin

# Rebase your branch on top of latest dev
git rebase origin/dev

# If there are conflicts, resolve them, then:
git add .
git rebase --continue

# Force push your branch (rebase changes history)
git push origin feature/filter-low-roi-campaigns --force
```

### Revert a Merge

If something breaks production:

```bash
# Create new branch from main
git checkout -b hotfix/revert-bad-merge main

# Find the commit hash of the merge
git log --oneline | head -5

# Revert it
git revert -m 1 <merge-commit-hash>

# Push and create PR to main
git push origin hotfix/revert-bad-merge
# Then create PR to main
```

---

## Troubleshooting Common Issues

### "Tests pass locally but fail in GitHub Actions"

This usually means a dependency issue.

```bash
# Reinstall dependencies fresh
rm -rf venv
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate
pip install -r requirements.txt

# Run tests again
pytest tests/ -v
```

### "Can't push to GitHub"

```bash
# Verify you're on your branch
git status

# Pull latest in case branch updated elsewhere
git pull origin feature/filter-low-roi-campaigns

# Try push again
git push origin feature/filter-low-roi-campaigns

# If still fails, check git credentials are configured
git config user.name
git config user.email
```

### "Databricks job fails after deployment"

1. Go to DEV Databricks workspace
2. Click **Workflows** → **Jobs** → "[dev] Marketing ETL Pipeline"
3. Click the failed **Run**
4. Click the failed **Task** to see logs
5. Common issues:
   - Table not found → Run `init_schema.sql`
   - Permission denied → Contact platform team
   - Data quality issue → Check transformation filters

### "I accidentally committed sensitive data"

**Immediately:**
1. Don't push yet!
2. Undo the commit: `git reset HEAD~1`
3. Remove the file: `git rm --cached <sensitive-file>`
4. Update `.gitignore`
5. Make a new clean commit

**If already pushed:**
1. Contact repository admin immediately
2. They'll need to force-push to rewrite history

---

## Best Practices Summary

✅ **DO:**
- Create descriptive branch names: `feature/`, `bugfix/`, `hotfix/`
- Write tests for all new code
- Run tests locally before pushing
- Keep PRs focused on single features
- Write clear commit messages
- Request code review before merging to `dev`
- Test in DEV before promoting to PROD

❌ **DON'T:**
- Commit secrets or credentials
- Push directly to `dev` or `main` (use PRs)
- Skip tests to "save time"
- Force-push to shared branches
- Merge without approval
- Mix multiple features in one PR

---

## Quick Reference

| Task | Command |
|------|---------|
| Create feature branch | `git checkout -b feature/name dev` |
| Run tests | `pytest tests/ -v` |
| See changes | `git diff` |
| Stage changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin branch-name` |
| Pull latest dev | `git pull origin dev` |
| Create PR | Go to GitHub → Pull requests |
| Merge PR | Click "Merge pull request" in GitHub |

---

## Support & Resources

- **Questions about code**: Ask in #data-engineering Slack
- **Access issues**: @platform-team
- **Databricks help**: [Databricks Docs](https://docs.databricks.com)
- **GitHub help**: [GitHub Docs](https://docs.github.com)
- **PySpark reference**: [PySpark API](https://spark.apache.org/docs/latest/api/python/)

---

**Happy coding! 🚀**

Now that you understand the complete workflow, go create your first feature in `feature/your-feature-name` branch!
