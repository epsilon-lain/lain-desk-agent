$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,

        [Parameter(Mandatory = $true)]
        [scriptblock] $Command
    )

    Write-Host "[verify] $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Verification step failed: $Name"
    }
}

Push-Location $RepoRoot
try {
    Invoke-Step "python -m compileall src tests" {
        python -m compileall src tests
    }

    Invoke-Step "python -m unittest discover -s tests" {
        python -m unittest discover -s tests
    }

    Invoke-Step "node --check ui/app.js" {
        node --check ui/app.js
    }

    Invoke-Step "python scripts/safety_scan.py" {
        python scripts/safety_scan.py
    }

    Invoke-Step "git diff --check" {
        git diff --check
    }

    Write-Host "[verify] OK"
} finally {
    Pop-Location
}
