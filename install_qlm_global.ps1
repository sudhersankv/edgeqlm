# PowerShell script to install qlm command globally on Windows
# Run this as Administrator

param(
    [switch]$Uninstall
)

$projectPath = $PSScriptRoot
$qlmPyPath = Join-Path $projectPath "qlm.py"
$systemPath = "$env:WINDIR\System32"
$userPath = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"

# Choose installation path (prefer user path to avoid admin requirements)
$installPath = $userPath
if (-not (Test-Path $installPath)) {
    New-Item -ItemType Directory -Path $installPath -Force
}

$batchFile = Join-Path $installPath "qlm.bat"

if ($Uninstall) {
    # Uninstall
    if (Test-Path $batchFile) {
        Remove-Item $batchFile -Force
        Write-Host "✅ qlm command removed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️ qlm command not found" -ForegroundColor Yellow
    }
    exit
}

# Install
if (-not (Test-Path $qlmPyPath)) {
    Write-Host "❌ qlm.py not found in $projectPath" -ForegroundColor Red
    exit 1
}

# Create batch file
$batchContent = @"
@echo off
python "$qlmPyPath" %*
"@

$batchContent | Out-File -FilePath $batchFile -Encoding ASCII

Write-Host "✅ qlm command installed successfully!" -ForegroundColor Green
Write-Host "📍 Location: $batchFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "  qlm compile verilog testbench tb_axi" -ForegroundColor White
Write-Host "  qlm -c run regression for uart flow" -ForegroundColor White
Write-Host "  qlm --list-sessions" -ForegroundColor White
Write-Host ""
Write-Host "Note: You may need to restart PowerShell for the command to be available." -ForegroundColor Gray 