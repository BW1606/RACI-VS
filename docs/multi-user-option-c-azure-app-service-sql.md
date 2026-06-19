# Option C — Azure App Service + Azure SQL (full cloud stack)

## Summary

Deploy the app to Azure App Service and replace SQLite with Azure SQL Server. The `feature/azure-sql-backend` branch already implements the database layer change. This is the most scalable and "enterprise" approach.

## When to use this

- Team works remotely and can't use a VPN
- You want a proper cloud database (no file system concerns)
- You expect growth in users or data volume
- You have an Azure subscription

## Estimated cost

- App Service B1 plan: ~€13/month
- Azure SQL Database (Basic, 2 GB): ~€5/month
- **Total: ~€18/month** (Basic tier, suitable for small teams)

## Branches

- **`feature/azure-sql-backend`** — already implements the SQLAlchemy + pyodbc Azure SQL connection
- **`master`** — base app code (merge azure-sql-backend into a new deployment branch)

## Setup steps

### 1. Create Azure resources

```bash
# Resource group
az group create --name raci-vs-rg --location germanywestcentral

# App Service
az appservice plan create --name raci-vs-plan --resource-group raci-vs-rg --sku B1 --is-linux
az webapp create --name raci-vs --resource-group raci-vs-rg --plan raci-vs-plan --runtime "PYTHON:3.11"

# Azure SQL Server + Database
az sql server create --name raci-vs-sql --resource-group raci-vs-rg \
  --location germanywestcentral --admin-user sqladmin --admin-password <strong-password>

az sql db create --server raci-vs-sql --resource-group raci-vs-rg \
  --name racivisdb --service-objective Basic

# Allow Azure services to reach SQL Server
az sql server firewall-rule create --server raci-vs-sql --resource-group raci-vs-rg \
  --name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
```

### 2. Configure the connection string

Get the connection string from the Azure Portal (SQL Database → Connection strings → ODBC). Set it as an app setting:

```bash
az webapp config appsettings set --name raci-vs --resource-group raci-vs-rg \
  --settings DATABASE_URL="mssql+pyodbc://sqladmin:<password>@raci-vs-sql.database.windows.net/racivisdb?driver=ODBC+Driver+18+for+SQL+Server"
```

The `feature/azure-sql-backend` branch reads `DATABASE_URL` from environment (via `.env` locally, App Service settings in the cloud) — no code change needed beyond using that branch.

### 3. Install ODBC driver on App Service

Add a startup script that installs the ODBC driver (Linux App Service):

```bash
# startup.sh
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18
uvicorn main:app --host 0.0.0.0 --port 8000
```

Set as startup command:
```bash
az webapp config set --name raci-vs --resource-group raci-vs-rg --startup-file "bash startup.sh"
```

### 4. Deploy via GitHub Actions

Same workflow as Option B, but deploy from the `feature/azure-sql-backend` branch (or a merged branch):

```yaml
name: Deploy to Azure

on:
  push:
    branches: [feature/azure-sql-backend]

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

### 5. Migrate existing data (if needed)

If you have existing data in a local SQLite file, export it via the app's built-in organisation export (JSON) and re-import it after deploying to the cloud.

### 6. Access the app

After deployment: `https://raci-vs.azurewebsites.net`

## Advantages over Option B

- No Azure Files latency — Azure SQL is a proper network database
- No SQLite concurrent-write limitations
- Automated backups included with Azure SQL
- Can scale the SQL tier independently of the app tier
