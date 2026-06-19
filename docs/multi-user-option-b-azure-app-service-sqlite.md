# Option B — Azure App Service + Azure Files (cloud, SQLite stays)

## Summary

Deploy the app to Azure App Service. Store the SQLite database on an Azure Files share (persistent cloud storage) so it survives restarts. Users access a permanent HTTPS URL from anywhere — no VPN needed.

## When to use this

- Team works remotely or from home and can't use a VPN
- You want a permanent, stable HTTPS URL
- You have (or can create) an Azure subscription
- You want to keep SQLite rather than migrating to a full SQL database

## Estimated cost

- App Service B1 plan: ~€13/month
- Azure Files (5 GB): ~€1/month
- **Total: ~€14/month**

## Setup steps

### 1. Create Azure resources (Azure Portal or Azure CLI)

```bash
# Create resource group
az group create --name raci-vs-rg --location germanywestcentral

# Create App Service plan (Linux, B1)
az appservice plan create --name raci-vs-plan --resource-group raci-vs-rg --sku B1 --is-linux

# Create web app (Python 3.11)
az webapp create --name raci-vs --resource-group raci-vs-rg --plan raci-vs-plan --runtime "PYTHON:3.11"

# Create storage account + file share for the database
az storage account create --name racivsstorage --resource-group raci-vs-rg --sku Standard_LRS
az storage share create --name raci-vs-db --account-name racivsstorage

# Mount the file share to the web app at /home/raci_vs
az webapp config storage-account add \
  --name raci-vs --resource-group raci-vs-rg \
  --custom-id raci-vs-db \
  --storage-type AzureFiles \
  --account-name racivsstorage \
  --share-name raci-vs-db \
  --mount-path /home/raci_vs
```

### 2. Update database.py (one line change)

In `database.py`, change the database path so it writes to the mounted Azure Files share when running in the cloud:

```python
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "raci_vs.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"
```

Then set the `DB_PATH` environment variable on the App Service:

```bash
az webapp config appsettings set --name raci-vs --resource-group raci-vs-rg \
  --settings DB_PATH=/home/raci_vs/raci_vs.db
```

### 3. Add a startup command

In the Azure Portal, go to **Configuration → General settings → Startup Command**:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or via CLI:
```bash
az webapp config set --name raci-vs --resource-group raci-vs-rg \
  --startup-file "uvicorn main:app --host 0.0.0.0 --port 8000"
```

### 4. Deploy via GitHub Actions

Add a workflow to `.github/workflows/deploy.yml`. Get the publish profile from the Azure Portal (App Service → Overview → Get publish profile) and add it as a GitHub secret named `AZURE_WEBAPP_PUBLISH_PROFILE`.

```yaml
name: Deploy to Azure

on:
  push:
    branches: [master]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - uses: azure/webapps-deploy@v3
        with:
          app-name: raci-vs
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

### 5. Access the app

After deployment: `https://raci-vs.azurewebsites.net`

## Limitations

- Azure Files has slightly higher latency than a local disk — acceptable for this app's workload
- SQLite is not ideal for very high concurrent writes (100+ simultaneous users), but fine for a small company team
- Requires ongoing Azure subscription
