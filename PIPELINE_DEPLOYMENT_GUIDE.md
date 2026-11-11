# Pipeline Deployment Guide: Azure SP, Admin Repo & Serverless Databricks Job

This guide provides complete, step-by-step instructions to create a dedicated least-privilege Service Principal (`marketing-pipeline-sp`), onboard it via the Admin Repo (`Databricks_CI_CD_apps`), configure GitHub Secrets, and run the Serverless Medallion ETL pipeline (`Bronze → Silver → Gold`).

---

## Architecture Overview

```text
1. Azure Entra ID        ──> Creates identity `marketing-pipeline-sp` (0 Azure IAM roles)
2. Admin Repo (Terraform)──> Adds SP to DEV/PROD Databricks & grants marketing_* schema access
3. Pipeline Repo (GitHub)──> Uses SP secrets in GitHub Actions to deploy Serverless DABs
4. Databricks Workspace  ──> Runs Serverless Job: Bronze -> Silver -> Gold in ~30 seconds
```

---

## Part A: Create `marketing-pipeline-sp` in Azure Portal

### Step 1: Go to App Registrations
1. Log into the **[Azure Portal](https://portal.azure.com)**.
2. In the top search bar, search for **`Microsoft Entra ID`** and open it.
3. In the left sidebar under **Manage**, click **App registrations**.
4. Click **+ New registration**.

### Step 2: Register the Application
1. **Name:** `marketing-pipeline-sp`
2. **Supported account types:** Select **Accounts in this organizational directory only (Single tenant)**.
3. **Redirect URI:** Leave completely blank.
4. Click **Register**.

### Step 3: Save the IDs
On the **Overview** page of `marketing-pipeline-sp`, copy and save:
- **Application (client) ID** *(format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)*
- **Directory (tenant) ID** *(format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)*

### Step 4: Create the Client Secret
1. In the left sidebar of your app, click **Certificates & secrets**.
2. Go to the **Client secrets** tab and click **+ New client secret**.
3. **Description:** `github-actions-pyspark-pipeline`
4. **Expires:** Choose **180 days (6 months)** or **365 days (12 months)**.
5. Click **Add**.
6. **CRITICAL:** Immediately copy the **Value** column (not the Secret ID) and store it securely for Step 8. Once you leave this page, Azure masks the secret value permanently.

### Step 5: Verify Zero Azure IAM Roles
- **Do NOT** assign any IAM roles (no Contributor, no Owner, no Reader) on your Azure Subscription or Resource Group.
- Keeping zero Azure cloud permissions ensures this SP can never modify or delete Azure infrastructure.

---

## Part B: Onboard the SP in the Admin Repo (`Databricks_CI_CD_apps`)

### Step 6: Update `terraform/governance.tf`
In your **`Databricks_CI_CD_apps`** repository, update `terraform/governance.tf` using the declarative `locals` + `for_each` pattern. Replace `<PASTE_CLIENT_ID_HERE>` with the **Application (client) ID** from Step 3:

```hcl
# Inside existing locals {} block:
  pipeline_service_principals = [
    {
      display_name   = "marketing-pipeline-sp"
      application_id = "<PASTE_CLIENT_ID_HERE>"
      schemas        = ["marketing_bronze", "marketing_silver", "marketing_gold"]
    }
  ]
```

```hcl
# ======================================================================
# PIPELINE SERVICE PRINCIPALS (CI/CD Deployment & Serverless Execution)
# ======================================================================

resource "databricks_service_principal" "dev_pipeline_sp" {
  for_each             = { for sp in local.pipeline_service_principals : sp.display_name => sp }
  provider             = databricks.dev
  application_id       = each.value.application_id
  display_name         = each.value.display_name
  workspace_access     = true
  allow_cluster_create = false
}

resource "databricks_service_principal" "prod_pipeline_sp" {
  for_each             = { for sp in local.pipeline_service_principals : sp.display_name => sp }
  provider             = databricks.prod
  application_id       = each.value.application_id
  display_name         = each.value.display_name
  workspace_access     = true
  allow_cluster_create = false
}

locals {
  sp_schema_pairs = flatten([
    for sp in local.pipeline_service_principals : [
      for schema_name in sp.schemas : {
        key            = "${sp.display_name}.${schema_name}"
        application_id = sp.application_id
        schema_name    = schema_name
      }
    ]
  ])
}

resource "databricks_grant" "dev_sp_grants" {
  for_each   = { for p in local.sp_schema_pairs : p.key => p }
  provider   = databricks.dev
  schema     = "${data.databricks_catalog.dev_workspace_catalog.name}.${each.value.schema_name}"
  principal  = each.value.application_id
  privileges = ["USE_SCHEMA", "SELECT", "MODIFY", "CREATE_TABLE"]
  depends_on = [databricks_service_principal.dev_pipeline_sp, databricks_schema.dev_schemas]
}

resource "databricks_grant" "prod_sp_grants" {
  for_each   = { for p in local.sp_schema_pairs : p.key => p }
  provider   = databricks.prod
  schema     = "${data.databricks_catalog.prod_workspace_catalog.name}.${each.value.schema_name}"
  principal  = each.value.application_id
  privileges = ["USE_SCHEMA", "SELECT", "MODIFY", "CREATE_TABLE"]
  depends_on = [databricks_service_principal.prod_pipeline_sp, databricks_schema.prod_schemas]
}
```

### Step 7: Apply Terraform (DEV & PROD)
1. Commit and push the update to the `dev` branch in `Databricks_CI_CD_apps` (or run `terraform apply`).
2. Open a Pull Request from `dev` → `main` in `Databricks_CI_CD_apps` and merge it so PROD receives the exact same grants.
3. **Verify:** In Databricks DEV UI (**Settings → Identity and access → Service principals**), confirm `marketing-pipeline-sp` appears.

---

## Part C: Configure Secrets & Deploy in `pyspark-pipeline`

### Step 8: Add GitHub Secrets
1. Open **`https://github.com/bala93kumar/pyspark-pipeline`**.
2. Go to **Settings → Secrets and variables → Actions**.
3. Click **New repository secret** and add these 3 secrets from **Steps 3 & 4**:

| Secret Name | Value |
| :--- | :--- |
| **`ARM_CLIENT_ID`** | Application (client) ID of `marketing-pipeline-sp` |
| **`ARM_CLIENT_SECRET`** | Client Secret **Value** of `marketing-pipeline-sp` |
| **`ARM_TENANT_ID`** | Directory (tenant) ID |

*(You do not need `DATABRICKS_TOKEN` or `DATABRICKS_HOST` — Databricks CLI uses OAuth via the Service Principal and reads hosts from `databricks.yml`.)*

### Step 9: Push Code & Merge to `dev`
In your local `pyspark-pipeline` VS Code terminal:
```bash
git add .
git commit -m "Add serverless medallion ETL pipeline and bronze seeder"
git push -u origin feature/pipeline1
```

1. Open a Pull Request on GitHub from **`feature/pipeline1` → `dev`**.
2. Wait for the **`Unit Tests (pytest)`** GitHub Actions check to pass.
3. Merge the Pull Request into `dev`.
4. GitHub Actions will automatically run **`Deploy to DEV Databricks`** using `marketing-pipeline-sp`.

---

## Part D: Run & Verify in Databricks DEV

### Step 10: Execute the Serverless Job
1. Log into your DEV Databricks workspace:
   `https://adb-7405605201845024.4.azuredatabricks.net`
2. Go to **Workflows → Jobs**.
3. Select **`[dev] Marketing Medallion ETL (Bronze -> Silver -> Gold)`**.
   - Verify the **Compute** section displays **Serverless**.
4. Click **Run now**.
5. Wait ~30 seconds for completion. On its first run, `src/etl/run_pipeline.py` automatically seeds dummy records if the bronze table doesn't exist yet, then executes the full medallion transformations:
   - **Bronze:** `dbx_demo_dev_ws_7405605201845024.marketing_bronze.raw_campaigns`
   - **Silver:** `dbx_demo_dev_ws_7405605201845024.marketing_silver.cleaned_campaigns`
   - **Gold:** `dbx_demo_dev_ws_7405605201845024.marketing_gold.campaign_roi_summary`
6. Go to **Catalog** in the left sidebar and inspect the generated Delta tables and sample data.

---

## Part E: Promote to PROD

### Step 11: Deploy to Production
1. Open a Pull Request on GitHub from **`dev` → `main`** in `pyspark-pipeline`.
2. Review changes and merge into `main`.
3. GitHub Actions deploys the bundle to PROD (`https://adb-7405618385351801.1.azuredatabricks.net`) targeting catalog `dbx_demo_prod_ws_7405618385351801`.
4. Log into PROD Databricks (**Workflows → Jobs**) to view or run **`[prod] Marketing Medallion ETL (Bronze -> Silver -> Gold)`**.
