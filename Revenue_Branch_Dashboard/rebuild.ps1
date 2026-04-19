Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ESIC Dashboard - EXE Builder Tool   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ask for HTML source file path
$src = Read-Host "Enter full path of your HTML file (e.g. C:\Projects\ESIC_Dashboard_V2.0.html)"
$src = $src.Trim('"')

# Ask for NW.js folder path
$nwDir = Read-Host "Enter full path of your NW.js folder (e.g. C:\Downloads\nwjs-v0.89.0-win-x64)"
$nwDir = $nwDir.Trim('"')

# Validate HTML file exists
if (-not (Test-Path $src)) {
    Write-Host "ERROR: HTML file not found at: $src" -ForegroundColor Red
    Pause
    exit
}

# Validate NW.js folder exists
if (-not (Test-Path $nwDir)) {
    Write-Host "ERROR: NW.js folder not found at: $nwDir" -ForegroundColor Red
    Pause
    exit
}

# Get just the filename from the path
$htmlFileName = Split-Path $src -Leaf

Write-Host ""
Write-Host "Updating package.json with new filename..." -ForegroundColor Yellow

# Update package.json automatically with correct HTML filename
$packageJson = @"
{
  "name": "esic-dashboard",
  "version": "1.0.0",
  "main": "$htmlFileName",
  "window": {
    "title": "ESIC Dashboard",
    "width": 1400,
    "height": 900,
    "min_width": 1024,
    "min_height": 600,
    "resizable": true,
    "toolbar": false
  },
  "chromium-args": "--disable-web-security"
}
"@
$packageJson | Out-File -FilePath "$nwDir\package.nw\package.json" -Encoding utf8

Write-Host "Copying updated HTML to package.nw..." -ForegroundColor Yellow
Copy-Item $src "$nwDir\package.nw\" -Force

Write-Host "Building EXE..." -ForegroundColor Yellow
cmd /c "copy /b `"$nwDir\nw.exe`" + `"$nwDir\package.nw`" `"$nwDir\ESIC_Dashboard.exe`""

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " BUILD COMPLETE!" -ForegroundColor Green
Write-Host " EXE Location: $nwDir\ESIC_Dashboard.exe" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Pause