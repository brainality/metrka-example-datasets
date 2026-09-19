param(
    [switch]$UseComposeDatabase
)

$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

$env:METRKA_ENV = "development"
$env:METRKA_WORKSPACES_CONFIG_PATH = Join-Path $repositoryRoot "workspaces.example.yaml"

if ($UseComposeDatabase) {
    $env:METRKA_MIGRATION_DSN = `
        "postgresql://metrka_migrator:metrka_migrator_local@127.0.0.1:55432/metrka"
    $env:METRKA_METADATA_DSN = `
        "postgresql://metrka_etl:metrka_etl_local@127.0.0.1:55432/metrka"
    $env:METRKA_OPERATIONS_DSN = `
        "postgresql://metrka_operator:metrka_operator_local@127.0.0.1:55432/metrka"

    Write-Host "Database: local Docker Compose PostgreSQL on port 55432"
} else {
    Write-Host "Database: existing Metrka PostgreSQL configuration was preserved"
}

Write-Host "Configured the local Metrka example environment."
Write-Host "Workspaces config: $env:METRKA_WORKSPACES_CONFIG_PATH"
