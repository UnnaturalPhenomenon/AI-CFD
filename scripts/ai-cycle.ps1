[CmdletBinding()]
param(
    [ValidateSet('check', 'implement', 'review', 'fix', 'full')]
    [string]$Mode = 'check',
    [switch]$AllowApiKeys,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$taskPath = Join-Path $projectRoot '.ai\TASK.md'
$reviewPath = Join-Path $projectRoot '.ai\REVIEW.md'
$logDirectory = Join-Path $projectRoot '.ai\logs'
$environmentCheck = Join-Path $PSScriptRoot 'Test-AiEnvironment.ps1'

function Invoke-CheckedExternalCommand {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][scriptblock]$Command,
        [Parameter(Mandatory)][string]$LogPath
    )

    Write-Host "[$Name] starting..." -ForegroundColor Cyan

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'

        $output = & $Command 2>&1 |
            ForEach-Object { $_.ToString() } |
            Tee-Object -FilePath $LogPath

        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    if ($exitCode -ne 0) {
        throw "$Name failed with exit code $exitCode. See $LogPath"
    }

    return @($output)
}

function Assert-ReadyTask {
    if (-not (Test-Path -LiteralPath $taskPath)) {
        throw "Task file not found: $taskPath"
    }

    $taskText = Get-Content -LiteralPath $taskPath -Raw
    if ($taskText -notmatch '(?m)^STATUS:\s*READY\s*$') {
        if ($DryRun) {
            Write-Host '[DRY RUN] TASK.md is DRAFT; continuing without executing agents.' -ForegroundColor Yellow
            return
        }
        throw 'TASK.md is not ready. Complete it, then set STATUS: READY.'
    }
}

function Assert-ReviewAvailable {
    if (-not (Test-Path -LiteralPath $reviewPath)) {
        throw "Review file not found: $reviewPath"
    }

    $reviewText = Get-Content -LiteralPath $reviewPath -Raw
    if ([string]::IsNullOrWhiteSpace($reviewText) -or $reviewText.Trim() -eq 'NOT_RUN') {
        throw 'No review is available. Run review or full first.'
    }
}

function Test-ReviewPassed {
    $reviewText = (Get-Content -LiteralPath $reviewPath -Raw).Trim()
    return $reviewText -eq 'PASS'
}

function Invoke-CodexImplement {
    $prompt = @'
Read AGENTS.md and execute .ai/TASK.md from the current repository.
Make only scoped changes, run VERIFY, and stop when DONE is satisfied.
'@

    if ($DryRun) {
        Write-Host "[DRY RUN] codex exec --sandbox workspace-write --ephemeral <implementation prompt>"
        return
    }

    $logPath = Join-Path $logDirectory 'codex-implement.log'
    Invoke-CheckedExternalCommand -Name 'Codex implementation' -LogPath $logPath -Command {
        & codex exec --sandbox workspace-write --ephemeral $prompt
    } | Out-Null
}

function Invoke-ClaudeReview {
    $prompt = @'
Review the current git diff against .ai/TASK.md. Do not edit files.

Check only:
1. correctness
2. regressions
3. requirement violations
4. missing or invalid verification
5. unsafe resource/session cleanup

If there are no actionable issues, output exactly:
PASS

Otherwise output at most 5 findings in this exact form:
1. BLOCKER|BUG|RISK path:line
   problem: concise explanation
   fix: smallest required correction

Output findings only. Do not include a preamble, recap, praise, or code rewrite.
'@

    if ($DryRun) {
        Write-Host "[DRY RUN] claude -p <review prompt> --model sonnet --effort low --permission-mode plan --output-format text --no-session-persistence --max-turns 8"
        return
    }

    $logPath = Join-Path $logDirectory 'claude-review.log'
    $reviewOutput = Invoke-CheckedExternalCommand -Name 'Claude review' -LogPath $logPath -Command {
        & claude -p $prompt --model sonnet --effort low --permission-mode plan --output-format text --no-session-persistence --max-turns 8
    }

    $reviewText = ($reviewOutput -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($reviewText)) {
        throw 'Claude returned an empty review.'
    }

    Set-Content -LiteralPath $reviewPath -Value $reviewText -Encoding utf8
    Write-Host "[Claude review] saved to $reviewPath" -ForegroundColor Green
}

function Invoke-CodexFix {
    $prompt = @'
Read AGENTS.md, .ai/TASK.md, and .ai/REVIEW.md.
Validate each review finding against the repository. Fix only valid findings.
Do not refactor. Run VERIFY and stop. Do not invoke another reviewer.
'@

    if ($DryRun) {
        Write-Host "[DRY RUN] codex exec --sandbox workspace-write --ephemeral <fix prompt>"
        return
    }

    $logPath = Join-Path $logDirectory 'codex-fix.log'
    Invoke-CheckedExternalCommand -Name 'Codex correction' -LogPath $logPath -Command {
        & codex exec --sandbox workspace-write --ephemeral $prompt
    } | Out-Null
}

Push-Location $projectRoot
try {
    & $environmentCheck -AllowApiKeys:$AllowApiKeys

    if ($Mode -eq 'check') {
        return
    }

    Assert-ReadyTask
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

    switch ($Mode) {
        'implement' {
            Invoke-CodexImplement
        }
        'review' {
            Invoke-ClaudeReview
        }
        'fix' {
            Assert-ReviewAvailable
            if (Test-ReviewPassed) {
                Write-Host '[Codex correction] skipped because review is PASS.' -ForegroundColor Green
            } else {
                Invoke-CodexFix
            }
        }
        'full' {
            Invoke-CodexImplement
            Invoke-ClaudeReview
            if ($DryRun) {
                Write-Host '[DRY RUN] a correction runs only when REVIEW.md is not PASS.'
            } elseif (Test-ReviewPassed) {
                Write-Host '[Cycle complete] Claude review: PASS' -ForegroundColor Green
            } else {
                Invoke-CodexFix
                Write-Host '[Cycle complete] One correction pass completed. Review again manually if needed.' -ForegroundColor Yellow
            }
        }
    }
} finally {
    Pop-Location
}

