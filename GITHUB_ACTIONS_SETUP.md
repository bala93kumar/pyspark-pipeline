"""
Instructions for setting up GitHub Actions secrets for Databricks CI/CD deployment.

This document provides step-by-step guidance for administrators to configure the
necessary secrets for automated deployment from GitHub Actions to Databricks.
"""

# GitHub Actions Secrets Setup Guide

## Overview

The CI/CD pipeline in `.github/workflows/deploy.yml` requires Azure service principal
credentials to authenticate with Databricks and deploy Databricks bundles.

These secrets are:
- `ARM_CLIENT_ID`: Azure Service Principal Client ID
- `ARM_CLIENT_SECRET`: Azure Service Principal Client Secret
- `ARM_TENANT_ID`: Azure Tenant ID

## Prerequisites

1. Access to GitHub repository settings (Repository Admin role required)
2. Azure service principal credentials (provided by platform team)
3. The credentials should already be created and stored in your platform repository

## Step-by-Step Configuration

### 1. Get Credentials from Platform Team

Contact the Databricks platform team to obtain:
- Client ID (Application/Service Principal ID)
- Client Secret (Service Principal secret)
- Tenant ID (Azure Tenant ID)

These should be securely stored in the platform repository (`Databricks_CI_CD_apps`).

### 2. Navigate to Repository Settings

In GitHub:
1. Go to the repository: `https://github.com/bala93kumar/pyspark-pipeline`
2. Click **Settings** (top right)
3. In the left sidebar, click **Secrets and variables**
4. Click **Actions**

### 3. Add Each Secret

Click **New repository secret** and add:

#### Secret 1: ARM_CLIENT_ID
- **Name**: `ARM_CLIENT_ID`
- **Value**: `<client-id-from-platform-team>`
- Click **Add secret**

#### Secret 2: ARM_CLIENT_SECRET
- **Name**: `ARM_CLIENT_SECRET`
- **Value**: `<client-secret-from-platform-team>`
- Click **Add secret**
- ⚠️ **IMPORTANT**: This is sensitive! Verify it's correct before saving.

#### Secret 3: ARM_TENANT_ID
- **Name**: `ARM_TENANT_ID`
- **Value**: `<tenant-id-from-platform-team>`
- Click **Add secret**

### 4. Verify Configuration

After adding secrets:
1. You should see all three secrets listed with masked values (●●●●●●●●)
2. Secrets are now available to GitHub Actions workflows
3. Once configured, GitHub Actions will use these credentials for deployment

## Security Best Practices

✅ **DO:**
- Store secrets only in GitHub Secrets (never in code or environment files)
- Rotate credentials periodically (coordinate with platform team)
- Use secrets with minimal required permissions
- Monitor GitHub Actions logs for failed authentication

❌ **DON'T:**
- Commit secrets to git repository
- Share credentials via email or chat
- Use personal credentials (use service principal)
- Store secrets in `.env` files or configuration files

## Testing the Setup

Once secrets are configured:

1. Push a commit to the `dev` branch (to test DEV deployment)
2. Go to **Actions** tab in GitHub
3. Click the latest workflow run (should be "Data Pipeline CI/CD")
4. Check that:
   - Tests pass (green ✅)
   - Deploy job completes (green ✅)
   - No authentication errors in logs

## Troubleshooting

### "Authentication failed" Error
- Verify secrets are spelled correctly (case-sensitive)
- Check that service principal still has valid credentials
- Ensure service principal has Databricks workspace permissions

### Job Deployment Fails
- Check the full workflow log in GitHub Actions
- Verify Azure service principal has permissions:
  - Databricks workspace access
  - Unity Catalog admin (if using UC)
- Contact platform team if permissions are missing

### Secrets Not Visible in Workflow
- Secrets take effect only on new workflow runs
- Try manually triggering a workflow with a new commit
- Check branch protection rules aren't blocking deployments

## Reference

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Databricks Bundle Deployment](https://docs.databricks.com/en/dev-tools/bundles/deploy.html)
- [Azure Service Principal for Databricks](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth#service-principal-authentication)
