# AICC — Generate random secrets for .env
# Run from the aicc/ directory: .\scripts\generate-secrets.ps1

Write-Host ""
Write-Host "AICC Secret Generator" -ForegroundColor Cyan
Write-Host "Copy these values into your .env file" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray

function New-RandomHex {
    param([int]$bytes = 32)
    $randomBytes = New-Object byte[] $bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($randomBytes)
    return [System.BitConverter]::ToString($randomBytes).Replace("-", "").ToLower()
}

$jwtSecret = New-RandomHex -bytes 64
$secretKeyBase = New-RandomHex -bytes 64
$n8nEncryptionKey = New-RandomHex -bytes 32
$postgresPassword = "AICC_" + (New-RandomHex -bytes 16)

Write-Host ""
Write-Host "POSTGRES_PASSWORD=$postgresPassword" -ForegroundColor Green
Write-Host "JWT_SECRET=$jwtSecret" -ForegroundColor Green
Write-Host "SECRET_KEY_BASE=$secretKeyBase" -ForegroundColor Green
Write-Host "N8N_ENCRYPTION_KEY=$n8nEncryptionKey" -ForegroundColor Green
Write-Host ""
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "Paste the above into your .env file." -ForegroundColor Yellow
Write-Host "Keep these secret. Never commit .env to git." -ForegroundColor Yellow
