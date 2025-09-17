# Alembic CLI helper for PowerShell
# Usage: .\alembic_tasks.ps1 upgrade|downgrade|revision|current [args]
param(
    [Parameter(Mandatory=$true)][string]$cmd,
    [string[]]$args
)

$env:PYTHONPATH = ".."
$alembic = "alembic -c alembic.ini"

switch ($cmd) {
    "upgrade"   { iex "$alembic upgrade $($args -join ' ')" }
    "downgrade" { iex "$alembic downgrade $($args -join ' ')" }
    "revision"  { iex "$alembic revision $($args -join ' ')" }
    "current"   { iex "$alembic current $($args -join ' ')" }
    default     { Write-Host "Unknown command. Use upgrade|downgrade|revision|current" }
}
