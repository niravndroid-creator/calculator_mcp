# PowerShell script to create deployment package for Azure Functions

Write-Host "Creating Azure Functions deployment package..." -ForegroundColor Green

# Set variables
$projectRoot = $PSScriptRoot
$deployDir = Join-Path $projectRoot "deploy_package"
$zipFile = Join-Path $projectRoot "calculator-mcp-function.zip"

# Clean up old deployment folder and zip
if (Test-Path $deployDir) {
    Remove-Item -Path $deployDir -Recurse -Force
}
if (Test-Path $zipFile) {
    Remove-Item -Path $zipFile -Force
}

# Create deployment folder
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

# Copy necessary files
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item -Path (Join-Path $projectRoot "server.py") -Destination $deployDir
Copy-Item -Path (Join-Path $projectRoot "pyproject.toml") -Destination $deployDir
Copy-Item -Path (Join-Path $projectRoot "requirements.txt") -Destination $deployDir
Copy-Item -Path (Join-Path $projectRoot "host.json") -Destination $deployDir
Copy-Item -Path (Join-Path $projectRoot "CalculatorMCP") -Destination $deployDir -Recurse

# Optional: Copy .gitignore patterns
$gitignorePath = Join-Path $projectRoot ".gitignore"
if (Test-Path $gitignorePath) {
    Copy-Item -Path $gitignorePath -Destination $deployDir
}

# Create ZIP file
Write-Host "Creating ZIP package..." -ForegroundColor Yellow
Compress-Archive -Path (Join-Path $deployDir "*") -DestinationPath $zipFile -Force

# Get ZIP file size
$zipSize = (Get-Item $zipFile).Length / 1MB
Write-Host "Package created successfully!" -ForegroundColor Green
Write-Host "File: $zipFile" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan

# Cleanup
Remove-Item -Path $deployDir -Recurse -Force
Write-Host "Temporary files cleaned up." -ForegroundColor Yellow

Write-Host "`nNext steps:" -ForegroundColor Magenta
Write-Host "1. Upload calculator-mcp-function.zip to Azure Function App" -ForegroundColor White
Write-Host "2. Use Azure CLI: az functionapp deployment source config-zip ..." -ForegroundColor White
Write-Host "3. Or upload via Azure Portal > Deployment Center > ZIP Deploy" -ForegroundColor White
Write-Host "`nSee AZURE_DEPLOYMENT.md for detailed instructions." -ForegroundColor Cyan
