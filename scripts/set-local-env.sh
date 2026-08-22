#!/usr/bin/env bash

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export METRKA_ENV="development"
export METRKA_WORKSPACES_CONFIG_PATH="$repository_root/workspaces.example.yaml"

if [[ "${1:-}" == "--compose-database" ]]; then
  export METRKA_MIGRATION_DSN="postgresql://metrka_migrator:metrka_migrator_local@127.0.0.1:55432/metrka"
  export METRKA_METADATA_DSN="postgresql://metrka_etl:metrka_etl_local@127.0.0.1:55432/metrka"
  echo "Database: local Docker Compose PostgreSQL on port 55432"
elif [[ -n "${1:-}" ]]; then
  echo "Unknown option: $1" >&2
  return 2
else
  echo "Database: existing Metrka PostgreSQL configuration was preserved"
fi

echo "Configured the local Metrka example environment."
echo "Workspaces config: $METRKA_WORKSPACES_CONFIG_PATH"
