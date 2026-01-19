# Add Windows Defender Exceptions for Playwright
# Run this script as Administrator

Write-Host "Adding Windows Defender Exceptions for Playwright..." -ForegroundColor Green
Write-Host ""

# Paths to exclude
$paths = @(
    "$env:LOCALAPPDATA\ms-playwright",
    "$env:USERPROFILE\Desktop\My Vault\watchers\whatsapp_session"
)

foreach ($path in $paths) {
    Write-Host "Adding exclusion for: $path" -ForegroundColor Yellow

    try {
        Add-MpPreference -ExclusionPath $path -ErrorAction Stop
        Write-Host "  [OK] Successfully added exclusion" -ForegroundColor Green
    }
    catch {
        Write-Host "  [ERROR] Failed to add exclusion: $_" -ForegroundColor Red
        Write-Host "  Please run this script as Administrator" -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host "Checking current exclusions..." -ForegroundColor Cyan
$prefs = Get-MpPreference
Write-Host ""
Write-Host "Current Exclusion Paths:" -ForegroundColor Cyan
$prefs.ExclusionPath | ForEach-Object { Write-Host "  - $_" }

Write-Host ""
Write-Host "Done! Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
