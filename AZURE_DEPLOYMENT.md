# Azure Functions Deployment Guide

## Prerequisites

1. **Azure CLI** installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. **Azure Functions Core Tools** installed: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local
3. **Azure subscription** and resource group
4. **Python 3.10 or 3.11** installed

## Option 1: Deploy Using Azure CLI (Recommended)

### Step 1: Login to Azure

```bash
az login
```

### Step 2: Create Azure Function App (if not exists)

```bash
# Set variables
$RESOURCE_GROUP="calculator-mcp-rg"
$LOCATION="eastus"
$STORAGE_ACCOUNT="calculatormcpstorage"
$FUNCTION_APP_NAME="calculator-mcp-function"
$PYTHON_VERSION="3.11"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --location $LOCATION --sku Standard_LRS

# Create Function App
az functionapp create --resource-group $RESOURCE_GROUP --consumption-plan-location $LOCATION --runtime python --runtime-version $PYTHON_VERSION --functions-version 4 --name $FUNCTION_APP_NAME --storage-account $STORAGE_ACCOUNT --os-type Linux
```

### Step 3: Configure Application Settings

```bash
# Set configuration
az functionapp config appsettings set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --settings "CALCULATOR_DATA_TYPES=both"
```

### Step 4: Deploy from Local Directory

```bash
# Navigate to project directory
cd C:\MCP_Calculator\calculator_mcp

# Deploy using func CLI
func azure functionapp publish $FUNCTION_APP_NAME
```

## Option 2: Deploy Using ZIP Package

### Step 1: Prepare Azure Functions Structure

Create the following structure:

```
calculator_mcp/
├── CalculatorMCP/
│   ├── __init__.py
│   └── function.json
├── host.json
├── requirements.txt
├── server.py
└── pyproject.toml
```

### Step 2: Create host.json

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "logging": {
    "logLevel": {
      "default": "Information"
    }
  }
}
```

### Step 3: Create Function Directory and function.json

Create directory: `CalculatorMCP/`

Create `CalculatorMCP/function.json`:

```json
{
  "scriptFile": "../server.py",
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get", "post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

### Step 4: Create __init__.py wrapper

Create `CalculatorMCP/__init__.py`:

```python
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Your MCP server logic here
        return func.HttpResponse(
            json.dumps({"status": "success"}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
```

### Step 5: Update requirements.txt for Azure

```
azure-functions>=1.18.0
mcp>=1.0.0
tomli>=2.0.0; python_version < "3.11"
```

### Step 6: Create ZIP Package

**Using PowerShell:**

```powershell
# Navigate to project directory
cd C:\MCP_Calculator\calculator_mcp

# Create a temporary deployment folder
$deployDir = "deploy_package"
New-Item -ItemType Directory -Path $deployDir -Force

# Copy necessary files
Copy-Item -Path "server.py" -Destination $deployDir
Copy-Item -Path "pyproject.toml" -Destination $deployDir
Copy-Item -Path "requirements.txt" -Destination $deployDir
Copy-Item -Path "host.json" -Destination $deployDir
Copy-Item -Path "CalculatorMCP" -Destination $deployDir -Recurse

# Create ZIP file
Compress-Archive -Path "$deployDir\*" -DestinationPath "calculator-mcp-function.zip" -Force

# Cleanup
Remove-Item -Path $deployDir -Recurse -Force

Write-Host "Package created: calculator-mcp-function.zip"
```

**Using Command Prompt:**

```cmd
cd C:\MCP_Calculator\calculator_mcp
powershell -Command "Compress-Archive -Path server.py,pyproject.toml,requirements.txt,host.json,CalculatorMCP -DestinationPath calculator-mcp-function.zip -Force"
```

### Step 7: Upload ZIP to Azure Function App

**Method A: Using Azure CLI**

```bash
az functionapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $FUNCTION_APP_NAME --src calculator-mcp-function.zip
```

**Method B: Using Azure Portal**

1. Go to Azure Portal (https://portal.azure.com)
2. Navigate to your Function App
3. Go to **Deployment Center**
4. Select **ZIP Deploy**
5. Upload `calculator-mcp-function.zip`
6. Wait for deployment to complete

**Method C: Using REST API with PowerShell**

```powershell
$functionAppName = "calculator-mcp-function"
$resourceGroup = "calculator-mcp-rg"

# Get publishing credentials
$creds = az functionapp deployment list-publishing-credentials --name $functionAppName --resource-group $resourceGroup | ConvertFrom-Json

# Create basic auth header
$username = $creds.publishingUserName
$password = $creds.publishingPassword
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $username, $password)))

# Upload ZIP
$apiUrl = "https://$functionAppName.scm.azurewebsites.net/api/zipdeploy"
Invoke-RestMethod -Uri $apiUrl -Headers @{Authorization=("Basic {0}" -f $base64AuthInfo)} -Method POST -InFile "calculator-mcp-function.zip" -ContentType "multipart/form-data"
```

## Option 3: Deploy Using VS Code

1. Install **Azure Functions** extension in VS Code
2. Open project folder in VS Code
3. Click Azure icon in sidebar
4. Right-click on Function App → **Deploy to Function App**
5. Select subscription and function app
6. Confirm deployment

## Post-Deployment Steps

### 1. Verify Deployment

```bash
# Check function app status
az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Get function URL
az functionapp function show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --function-name CalculatorMCP
```

### 2. Test the Function

```bash
# Get function key
$functionKey = az functionapp keys list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --query "functionKeys.default" -o tsv

# Test with curl
curl "https://$FUNCTION_APP_NAME.azurewebsites.net/api/CalculatorMCP?code=$functionKey" -d '{"operation":"add","a":5,"b":3}'
```

### 3. View Logs

```bash
# Stream logs
az webapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Or view in Azure Portal
# Go to Function App → Monitor → Logs
```

## Troubleshooting

### Issue: Module not found

**Solution:** Ensure all dependencies are in `requirements.txt` and reinstall:

```bash
az functionapp deployment source sync --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP
```

### Issue: Configuration not loading

**Solution:** Set application settings:

```bash
az functionapp config appsettings set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --settings "CALCULATOR_DATA_TYPES=both" "PYTHONPATH=/home/site/wwwroot"
```

### Issue: Timeout errors

**Solution:** Increase timeout (default is 5 minutes for Consumption plan):

```bash
az functionapp config set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --timeout 00:10:00
```

## Important Notes

1. **MCP over HTTP**: Azure Functions uses HTTP triggers, not stdio. You'll need to adapt the MCP server for HTTP transport.
2. **Cold Start**: Consumption plan has cold start delays. Consider Premium plan for production.
3. **Authentication**: Use function keys or Azure AD authentication for security.
4. **Costs**: Monitor usage to avoid unexpected charges.

## Alternative: MCP Server is Not Ideal for Azure Functions

**Note:** MCP servers typically use stdio or SSE transport, which don't map well to Azure Functions' HTTP trigger model. Consider these alternatives:

1. **Azure Container Instances** - Run the MCP server as a container
2. **Azure App Service** - Deploy as a web app with SSE support
3. **Azure VM** - Full control over the environment

Would you like help adapting the MCP server for one of these alternatives?
