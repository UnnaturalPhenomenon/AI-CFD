[CmdletBinding()]
param(
    [ValidateSet('check', 'implement', 'review', 'fix', 'full')]
    [string]$Mode = 'check',
    [switch]$AllowApiKeys,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$runner = Join-Path $PSScriptRoot 'scripts\ai-cycle.ps1'

if (-not (Test-Path -LiteralPath $runner)) {
    throw "Runner not found: $runner"
}

& $runner -Mode $Mode -AllowApiKeys:$AllowApiKeys -DryRun:$DryRun
