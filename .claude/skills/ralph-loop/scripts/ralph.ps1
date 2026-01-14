# Ralph Wiggum Loop - Windows PowerShell Version
# Autonomous task completion for Personal AI Employee
# Usage: .\ralph.ps1 [-MaxIterations 10] [-RalphDir "path"]

param(
    [int]$MaxIterations = 10,
    [string]$RalphDir = "AI_Employee_Vault\Ralph",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-RalphInfo { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-RalphSuccess { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-RalphWarning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-RalphError { param($Message) Write-Host $Message -ForegroundColor Red }

# Get script directory and vault root
$ScriptDir = Split-Path -Parent $PSCommandPath
$VaultRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir))
$RalphPath = Join-Path $VaultRoot $RalphDir

# File paths
$PrdFile = Join-Path $RalphPath "prd.json"
$ProgressFile = Join-Path $RalphPath "progress.txt"
$PromptFile = Join-Path $RalphPath "prompt.md"
$ArchiveDir = Join-Path $RalphPath "archive"
$LastBranchFile = Join-Path $RalphPath ".last-branch"
$LastOutputFile = Join-Path $RalphPath ".last-output.txt"

Write-RalphInfo "═══════════════════════════════════════════════════════"
Write-RalphInfo "  Ralph Wiggum Loop - Personal AI Employee"
Write-RalphInfo "  Max Iterations: $MaxIterations"
Write-RalphInfo "  Ralph Directory: $RalphPath"
Write-RalphInfo "═══════════════════════════════════════════════════════"
Write-Host ""

# Create Ralph directory if it doesn't exist
if (!(Test-Path $RalphPath)) {
    Write-RalphInfo "Creating Ralph directory: $RalphPath"
    New-Item -ItemType Directory -Path $RalphPath -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $RalphPath "tasks") -Force | Out-Null
    New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
}

# Check if prd.json exists
if (!(Test-Path $PrdFile)) {
    Write-RalphError "ERROR: prd.json not found at: $PrdFile"
    Write-Host ""
    Write-RalphWarning "To create a PRD:"
    Write-Host "  1. Use /prd skill to generate a PRD"
    Write-Host "  2. Use /ralph-converter to convert it to prd.json"
    Write-Host ""
    exit 1
}

# Archive previous run if branch changed
if ((Test-Path $PrdFile) -and (Test-Path $LastBranchFile)) {
    $PrdContent = Get-Content $PrdFile -Raw | ConvertFrom-Json
    $CurrentBranch = $PrdContent.branchName
    $LastBranch = Get-Content $LastBranchFile -Raw

    if ($CurrentBranch -and $LastBranch -and ($CurrentBranch -ne $LastBranch.Trim())) {
        $Date = Get-Date -Format "yyyy-MM-dd"
        $FolderName = $LastBranch.Trim() -replace '^ralph/', ''
        $ArchiveFolder = Join-Path $ArchiveDir "$Date-$FolderName"

        Write-RalphInfo "Archiving previous run: $LastBranch"
        New-Item -ItemType Directory -Path $ArchiveFolder -Force | Out-Null
        Copy-Item $PrdFile $ArchiveFolder -Force
        if (Test-Path $ProgressFile) {
            Copy-Item $ProgressFile $ArchiveFolder -Force
        }
        Write-RalphSuccess "   Archived to: $ArchiveFolder"

        # Reset progress file
        @"
# Ralph Progress Log
Started: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
---
"@ | Out-File $ProgressFile -Encoding UTF8
    }
}

# Track current branch
if (Test-Path $PrdFile) {
    $PrdContent = Get-Content $PrdFile -Raw | ConvertFrom-Json
    if ($PrdContent.branchName) {
        $PrdContent.branchName | Out-File $LastBranchFile -Encoding UTF8 -NoNewline
    }
}

# Initialize progress file if it doesn't exist
if (!(Test-Path $ProgressFile)) {
    @"
# Ralph Progress Log
Started: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
---
"@ | Out-File $ProgressFile -Encoding UTF8
}

# Copy prompt template if it doesn't exist
if (!(Test-Path $PromptFile)) {
    $PromptTemplate = Join-Path $ScriptDir "prompt.md"
    if (Test-Path $PromptTemplate) {
        Copy-Item $PromptTemplate $PromptFile -Force
        Write-RalphInfo "Created prompt.md from template"
    }
}

# Main loop
Write-Host ""
Write-RalphSuccess "Starting Ralph loop..."
Write-Host ""

$Completed = $false

for ($i = 1; $i -le $MaxIterations; $i++) {
    Write-Host ""
    Write-RalphInfo "═══════════════════════════════════════════════════════"
    Write-RalphInfo "  Ralph Iteration $i of $MaxIterations"
    Write-RalphInfo "═══════════════════════════════════════════════════════"
    Write-Host ""

    # Read the prompt
    if (!(Test-Path $PromptFile)) {
        Write-RalphError "ERROR: prompt.md not found at: $PromptFile"
        exit 1
    }

    $Prompt = Get-Content $PromptFile -Raw

    # Run Claude Code with the prompt
    try {
        # Change to vault root for Claude context
        Push-Location $VaultRoot

        # Run Claude and capture output
        $Output = ""

        if ($Verbose) {
            Write-RalphInfo "Running: claude with ralph prompt"
        }

        # Use a temporary file for the prompt
        $TempPromptFile = [System.IO.Path]::GetTempFileName()
        $Prompt | Out-File $TempPromptFile -Encoding UTF8

        # Run Claude Code
        $Output = & claude --prompt-file $TempPromptFile 2>&1 | Tee-Object -Variable claudeOutput | Out-String

        # Save output
        $Output | Out-File $LastOutputFile -Encoding UTF8

        # Clean up temp file
        Remove-Item $TempPromptFile -Force -ErrorAction SilentlyContinue

        Pop-Location

    } catch {
        Write-RalphError "ERROR running Claude Code: $_"
        Pop-Location
        exit 1
    }

    # Check for completion signal
    if ($Output -match "<promise>COMPLETE</promise>") {
        Write-Host ""
        Write-RalphSuccess "═══════════════════════════════════════════════════════"
        Write-RalphSuccess "  Ralph completed all tasks!"
        Write-RalphSuccess "  Completed at iteration $i of $MaxIterations"
        Write-RalphSuccess "═══════════════════════════════════════════════════════"
        Write-Host ""
        $Completed = $true
        break
    }

    Write-RalphInfo "Iteration $i complete. Continuing..."
    Start-Sleep -Seconds 2
}

Write-Host ""

if ($Completed) {
    Write-RalphSuccess "All tasks completed successfully!"
    Write-Host ""
    Write-Host "Check results:"
    Write-Host "  - Progress: $ProgressFile"
    Write-Host "  - Task list: $PrdFile"
    Write-Host "  - Last output: $LastOutputFile"
    Write-Host ""
    exit 0
} else {
    Write-RalphWarning "Ralph reached max iterations ($MaxIterations) without completing all tasks."
    Write-Host ""
    Write-Host "Check status:"
    Write-Host "  - Progress: $ProgressFile"
    Write-Host "  - Task list: $PrdFile"
    Write-Host "  - Last output: $LastOutputFile"
    Write-Host ""
    Write-RalphWarning "Consider:"
    Write-Host "  - Increasing max iterations"
    Write-Host "  - Splitting large tasks into smaller ones"
    Write-Host "  - Checking for errors in progress.txt"
    Write-Host ""
    exit 1
}
