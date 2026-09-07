<#
  Prepares Windows to run Docker Desktop (WSL 2 backend).
  Enables "Virtual Machine Platform" + WSL. Requires administrator rights.
  Run this ONCE. Afterwards you must REBOOT the PC.

  Normal usage: double-click setup-requirements.bat
#>

# --- Self-elevate to administrator ----------------------------------------
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Requesting administrator rights..." -ForegroundColor Yellow
    Start-Process powershell.exe -Verb RunAs -ArgumentList `
        "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

$ErrorActionPreference = 'Continue'

Write-Host "=== 1/3  Enabling Windows features ===" -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host ""
Write-Host "=== 2/3  Installing the WSL 2 core (no Linux distribution) ===" -ForegroundColor Cyan
# Docker Desktop ships its own distro; Ubuntu is not needed.
wsl.exe --install --no-distribution
if ($LASTEXITCODE -ne 0) {
    Write-Host "  (a failure here is fine: it completes after the reboot with 'wsl --update')" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== 3/3  Final settings ===" -ForegroundColor Cyan
wsl.exe --set-default-version 2 2>&1 | Out-Null

Write-Host ""
Write-Host "-------------------------------------------------------------" -ForegroundColor Green
Write-Host "  DONE. Now:" -ForegroundColor Green
Write-Host "   1) REBOOT the computer." -ForegroundColor Green
Write-Host "   2) Open Docker Desktop and wait for 'Engine running'." -ForegroundColor Green
Write-Host "   3) In the project folder:  .\run.ps1 start" -ForegroundColor Green
Write-Host "-------------------------------------------------------------" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
