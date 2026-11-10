# pyspark-pipeline

PySpark transformations and Databricks Asset Bundle deployment for the
marketing campaign pipeline.

## Local development

Use Python 3.10 and install the project dependencies:

```bash
python -m pip install -r requirements.txt
pytest tests/
```

The unit tests create a local Spark session; they do not require a Databricks
workspace or cloud credentials.

## Databricks deployment

The bundle defines `dev` and `prod` targets in `databricks.yml`. Deployments are
triggered only by pushes to the corresponding branches, after the test job
passes. Pull requests run tests but do not deploy.

Configure these repository Actions secrets for Azure service principal
authentication:

- `ARM_CLIENT_ID`
- `ARM_CLIENT_SECRET`
- `ARM_TENANT_ID`

The configured service principal must already have the required workspace and
Unity Catalog permissions. Manage those permissions in the platform
administration repository rather than in this pipeline repository.
