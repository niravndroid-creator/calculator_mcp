# Quick Start: Deploy to Azure Functions

## 📦 Package Already Created!

The deployment package `calculator-mcp-function.zip` has been created and is ready to upload.

## 🚀 Quick Upload Steps

### Option 1: Azure Portal (Easiest)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Function App
3. Click **Deployment Center** (left menu)
4. Click **ZIP Deploy** tab
5. Click **Browse** and select `calculator-mcp-function.zip`
6. Click **Upload**
7. Wait for deployment to complete (check notification bell icon)

### Option 2: Azure CLI (Fastest)

```powershell
# Login to Azure
az login

# Set variables (replace with your values)
$RESOURCE_GROUP = "your-resource-group"
$FUNCTION_APP_NAME = "your-function-app-name"

# Deploy
az functionapp deployment source config-zip `
  --resource-group $RESOURCE_GROUP `
  --name $FUNCTION_APP_NAME `
  --src calculator-mcp-function.zip
```

### Option 3: PowerShell with REST API

```powershell
# Set variables
$functionAppName = "your-function-app-name"
$resourceGroup = "your-resource-group"

# Get publishing credentials
$creds = az functionapp deployment list-publishing-credentials `
  --name $functionAppName `
  --resource-group $resourceGroup | ConvertFrom-Json

# Create auth header
$username = $creds.publishingUserName
$password = $creds.publishingPassword
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${username}:${password}"))

# Upload ZIP
$apiUrl = "https://$functionAppName.scm.azurewebsites.net/api/zipdeploy"
Invoke-RestMethod -Uri $apiUrl `
  -Headers @{Authorization="Basic $base64AuthInfo"} `
  -Method POST `
  -InFile "calculator-mcp-function.zip" `
  -ContentType "application/octet-stream"
```

## ✅ Post-Deployment: Test Your Function

### Get Function URL

```powershell
# Get function key
$functionKey = az functionapp keys list `
  --name $FUNCTION_APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --query "functionKeys.default" -o tsv

# Your function URL
$functionUrl = "https://$FUNCTION_APP_NAME.azurewebsites.net/api/calculator"
Write-Host "Function URL: $functionUrl`?code=$functionKey"
```

### Test with PowerShell

```powershell
# Test addition
$body = @{
    a = 5
    b = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "$functionUrl/add?code=$functionKey" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

### Test with curl

```bash
# Test addition
curl -X POST "https://$FUNCTION_APP_NAME.azurewebsites.net/api/calculator/add?code=$functionKey" \
  -H "Content-Type: application/json" \
  -d '{"a":5,"b":3}'

# Test multiplication
curl -X POST "https://$FUNCTION_APP_NAME.azurewebsites.net/api/calculator/multiply?code=$functionKey" \
  -H "Content-Type: application/json" \
  -d '{"a":4,"b":7}'
```

## 🔧 Configuration

Set environment variables in Azure:

```powershell
az functionapp config appsettings set `
  --name $FUNCTION_APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --settings "CALCULATOR_DATA_TYPES=both"
```

## 📊 Monitor Logs

```powershell
# Stream logs
az webapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Or view in Azure Portal:
# Function App > Monitor > Logs
```

## 🔄 Re-deploy After Changes

If you make code changes:

1. Run: `.\create-deployment-package.ps1`
2. Upload new `calculator-mcp-function.zip` using any method above

## 📚 Full Documentation

See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for complete documentation.

## 🆘 Troubleshooting

**Issue:** Function not responding
- **Solution:** Check logs in Azure Portal or use `az webapp log tail`

**Issue:** Module not found
- **Solution:** Verify `requirements.txt` includes all dependencies

**Issue:** Configuration not loading  
- **Solution:** Set `CALCULATOR_DATA_TYPES` in Application Settings

**Issue:** Authentication errors
- **Solution:** Check function key is correct and not expired
