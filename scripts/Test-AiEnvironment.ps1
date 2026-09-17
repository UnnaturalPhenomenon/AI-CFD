[CmdletBinding()]
param(
    [switch]$AllowApiKeys
)

$ErrorActionPreference = 'Stop'

function Test-Executable {
    param([Parameter(Mandatory)][string]$Name)

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        Write-Host "[MISSING] $Name" -ForegroundColor Red
        return $false
    }

    Write-Host "[OK]      $Name -> $($command.Source)" -ForegroundColor Green
    return $true
}

$ok = $true
foreach ($name in @('git', 'codex', 'claude')) {
    if (-not (Test-Executable -Name $name)) {
        $ok = $false
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot '..\.git'))) {
    Write-Host '[MISSING] Git repository. Run: git init' -ForegroundColor Red
    $ok = $false
} else {
    Write-Host '[OK]      Git repository detected' -ForegroundColor Green
}

$presentApiKeys = @()
foreach ($name in @('OPENAI_API_KEY', 'ANTHROPIC_API_KEY')) {
    $value = [Environment]::GetEnvironmentVariable($name)
    if (-not [string]::IsNullOrWhiteSpace($value)) {
        $presentApiKeys += $name
    }
}

if ($presentApiKeys.Count -gt 0 -and -not $AllowApiKeys) {
    Write-Host "[BLOCKED] API key environment variable(s): $($presentApiKeys -join ', ')" -ForegroundColor Red
    Write-Host '          They can route CLI usage to separately billed API access.' -ForegroundColor Yellow
    Write-Host '          Remove them for this shell, or pass -AllowApiKeys intentionally.' -ForegroundColor Yellow
    $ok = $false
} elseif ($presentApiKeys.Count -gt 0) {
    Write-Host "[WARNING] API key use explicitly allowed: $($presentApiKeys -join ', ')" -ForegroundColor Yellow
} else {
    Write-Host '[OK]      No OpenAI/Anthropic API key found in this process' -ForegroundColor Green
}

if (-not $ok) {
    throw 'Environment checks failed.'
}

Write-Host '[READY]   Environment checks passed.' -ForegroundColor Cyan
