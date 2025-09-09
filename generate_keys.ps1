# generate_keys.ps1 - Generate secure API keys and JWT secrets
# Run this script to generate cryptographically secure keys for your BrainDrive Document AI

param(
    [switch]$ApiKey,
    [switch]$JwtSecret,
    [switch]$Both,
    [int]$Length = 64,
    [string]$EnvFile = ".env"
)

# Function to generate a cryptographically secure random string
function Generate-SecureKey {
    param (
        [int]$Length = 64,
        [string]$Prefix = ""
    )
    
    # Use cryptographically secure random number generator
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $bytes = New-Object byte[] $Length
    $rng.GetBytes($bytes)
    $rng.Dispose()
    
    # Convert to base64 and clean up
    $key = [Convert]::ToBase64String($bytes)
    $key = $key -replace '[+/=]', ''  # Remove special characters
    $key = $key.Substring(0, [Math]::Min($Length, $key.Length))
    
    if ($Prefix) {
        return "$Prefix-$key"
    }
    return $key
}

# Function to append to .env file safely
function Add-ToEnvFile {
    param (
        [string]$Key,
        [string]$Value,
        [string]$FilePath,
        [string]$Comment = ""
    )
    
    $envLine = "$Key=$Value"
    
    if ($Comment) {
        $envLine = "# $Comment`n$envLine"
    }
    
    # Check if key already exists in file
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath
        $existingLine = $content | Where-Object { $_ -match "^$Key=" }
        
        if ($existingLine) {
            Write-Warning "Key '$Key' already exists in $FilePath"
            $overwrite = Read-Host "Overwrite existing value? (y/N)"
            if ($overwrite -ne 'y' -and $overwrite -ne 'Y') {
                Write-Host "Skipping $Key" -ForegroundColor Yellow
                return
            }
            
            # Replace existing line
            $newContent = $content | ForEach-Object {
                if ($_ -match "^$Key=") { $envLine } else { $_ }
            }
            $newContent | Set-Content $FilePath
            Write-Host "Updated $Key in $FilePath" -ForegroundColor Green
            return
        }
    }
    
    # Append new line
    Add-Content $FilePath "`n$envLine"
    Write-Host "Added $Key to $FilePath" -ForegroundColor Green
}

# Main script logic
Write-Host "🔐 BrainDrive Document AI - Key Generator" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

if (-not $ApiKey -and -not $JwtSecret -and -not $Both) {
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\generate_keys.ps1 -ApiKey          # Generate API key only"
    Write-Host "  .\generate_keys.ps1 -JwtSecret       # Generate JWT secret only"
    Write-Host "  .\generate_keys.ps1 -Both            # Generate both keys"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Length <int>       # Key length (default: 64)"
    Write-Host "  -EnvFile <string>   # .env file path (default: .env)"
    Write-Host ""
    
    $choice = Read-Host "What would you like to generate? (1=API Key, 2=JWT Secret, 3=Both)"
    switch ($choice) {
        "1" { $ApiKey = $true }
        "2" { $JwtSecret = $true }
        "3" { $Both = $true }
        default { 
            Write-Host "Invalid choice. Exiting." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""

# Generate API Key
if ($ApiKey -or $Both) {
    Write-Host "Generating API Key..." -ForegroundColor Yellow
    $generatedApiKey = Generate-SecureKey -Length $Length -Prefix "sk"
    
    Write-Host "✅ API Key generated:" -ForegroundColor Green
    Write-Host "  $generatedApiKey" -ForegroundColor White
    Write-Host ""
    
    # Option to save to .env file
    $save = Read-Host "Save AUTH_API_KEY to $EnvFile? (y/N)"
    if ($save -eq 'y' -or $save -eq 'Y') {
        Add-ToEnvFile -Key "AUTH_API_KEY" -Value $generatedApiKey -FilePath $EnvFile -Comment "Generated API key for BrainDrive Document AI"
    }
    
    Write-Host ""
    Write-Host "🔧 Usage example:" -ForegroundColor Cyan
    Write-Host "curl -X POST http://localhost:8000/documents/upload \" -ForegroundColor Gray
    Write-Host "  -H `"X-API-Key: $generatedApiKey`" \" -ForegroundColor Gray
    Write-Host "  -F `"file=@document.pdf`"" -ForegroundColor Gray
    Write-Host ""
}

# Generate JWT Secret
if ($JwtSecret -or $Both) {
    Write-Host "Generating JWT Secret..." -ForegroundColor Yellow
    $generatedJwtSecret = Generate-SecureKey -Length $Length
    
    Write-Host "✅ JWT Secret generated:" -ForegroundColor Green
    Write-Host "  $generatedJwtSecret" -ForegroundColor White
    Write-Host ""
    
    # Option to save to .env file
    $save = Read-Host "Save JWT_SECRET to $EnvFile? (y/N)"
    if ($save -eq 'y' -or $save -eq 'Y') {
        Add-ToEnvFile -Key "JWT_SECRET" -Value $generatedJwtSecret -FilePath $EnvFile -Comment "Generated JWT secret for BrainDrive Document AI"
    }
    
    Write-Host ""
    Write-Host "🔧 JWT Token Generation (Python):" -ForegroundColor Cyan
    Write-Host "import jwt" -ForegroundColor Gray
    Write-Host "from datetime import datetime, timedelta" -ForegroundColor Gray
    Write-Host ""
    Write-Host "token = jwt.encode({" -ForegroundColor Gray
    Write-Host "    'sub': 'user123'," -ForegroundColor Gray
    Write-Host "    'exp': datetime.utcnow() + timedelta(hours=1)" -ForegroundColor Gray
    Write-Host "}, '$generatedJwtSecret', algorithm='HS256')" -ForegroundColor Gray
    Write-Host ""
}

# Security recommendations
Write-Host ""
Write-Host "🛡️  Security Recommendations:" -ForegroundColor Cyan
Write-Host "  • Store keys in environment variables, not in code" -ForegroundColor White
Write-Host "  • Use different keys for development and production" -ForegroundColor White
Write-Host "  • Rotate keys periodically" -ForegroundColor White
Write-Host "  • Never commit .env files to version control" -ForegroundColor White
Write-Host "  • Set DISABLE_AUTH=false in production" -ForegroundColor White
Write-Host ""

# .env file reminder
if (Test-Path $EnvFile) {
    Write-Host "📝 Your $EnvFile file now contains:" -ForegroundColor Cyan
    Write-Host ""
    Get-Content $EnvFile | Where-Object { $_ -match "AUTH_API_KEY|JWT_SECRET|AUTH|DISABLE" } | ForEach-Object {
        if ($_ -match "^#") {
            Write-Host "  $_" -ForegroundColor Gray
        } else {
            Write-Host "  $_" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

Write-Host "✨ Key generation complete!" -ForegroundColor Green
