$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Invoke-ReadOnlyStatusStep {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,

        [Parameter(Mandatory = $true)]
        [scriptblock] $Command
    )

    Write-Host "[project-status] $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Project status step failed: $Name"
    }
}

Push-Location $RepoRoot
try {
    Write-Host "[project-status] Phase 10.3 guardrails are read-only/dry-run/debug-only"
    Write-Host "[project-status] Guardrails are regression protection only; real desktop actions remain disabled"

    Invoke-ReadOnlyStatusStep "git status --short" {
        git status --short
    }

    Invoke-ReadOnlyStatusStep "git log -n 5 --oneline" {
        git log -n 5 --oneline
    }

    Invoke-ReadOnlyStatusStep "python -m unittest discover -s tests" {
        python -m unittest discover -s tests
    }

    Invoke-ReadOnlyStatusStep "python scripts/safety_scan.py" {
        python scripts/safety_scan.py
    }

    Invoke-ReadOnlyStatusStep "node --check ui/app.js" {
        node --check ui/app.js
    }

    Invoke-ReadOnlyStatusStep "git diff --check" {
        git diff --check
    }

    Write-Host "[project-status] OK"
} finally {
    Pop-Location
}
