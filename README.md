# metrka-example-datasets

A minimal, public, end-to-end example for `metrka-core` 1.0.0.

The repository uses only the stable `metrka` command and declarative YAML. It
does not import private modules from the private `metrka-datasets` repository
and does not register custom Python actions.

## What the example proves

One pipeline command executes the complete data-processing path:

```text
pinned HTTP source
  -> immutable source capture
  -> Bronze preservation and checksum evidence
  -> quality gates
  -> contract-driven Silver transformation
  -> CSV and Parquet Silver artifacts
  -> publication candidate and audit records in PostgreSQL
```

Publication is deliberately a separate operator decision. The quick start
below continues from the candidate through approval, publication,
reconciliation, and a second idempotent pipeline run.

The source is the stable Gapminder teaching table: 1,704 country/year rows with
country, continent, year, life expectancy, population, and GDP per capita. The
URL is pinned to an exact upstream Git commit. See `NOTICE.md` for attribution
and licensing.

## Prerequisites

- Git
- Python 3.12 or newer
- PostgreSQL 17, either an existing Metrka database or Docker Compose
- the `metrka-core` 1.0.0 wheel published in the corresponding GitHub Release

The included PostgreSQL credentials are intentionally public development-only
values. Never reuse them outside this local example.

Run the pipeline from a committed, clean checkout. Metrka records the exact
Git revision of this repository and deliberately rejects uncommitted dataset
configuration changes.

## Run on Windows PowerShell

Clone the repository and enter its root:

```powershell
git clone https://github.com/brainality/metrka-example-datasets.git
Set-Location .\metrka-example-datasets
```

Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
metrka --version
```

Until the public `metrka-core` 1.0.0 Release asset exists, developers can test
against a clean local core checkout instead:

```powershell
python -m pip install -e "C:\path\to\metrka-core"
python -m pip install pytest ruff mypy
python -m pip install -e . --no-deps
```

This local override is for development only. The committed dependency remains
the immutable release wheel used by public installations and CI.

### Option A: use Docker Compose

Start the disposable local database, select its connection, and apply migrations:

```powershell
docker compose up -d --wait
. .\scripts\set-local-env.ps1 -UseComposeDatabase
python -m metrka_core.metadata.migrations upgrade head
python -m metrka_core.metadata.migrations check
```

### Option B: use an existing Metrka PostgreSQL database

Keep your existing `METRKA_METADATA_DSN`, `METRKA_MIGRATION_DSN`, or
`METRKA_METADATA_CONFIG_PATH` configuration and set only the workspace placement:

```powershell
. .\scripts\set-local-env.ps1
python -m metrka_core.metadata.migrations upgrade head
python -m metrka_core.metadata.migrations check
```

Without `-UseComposeDatabase`, the script never changes database credentials.
If the existing database is already on the migration head, `upgrade head` is
idempotent.

Run the pipeline:

```powershell
metrka workspace validate gapminder
metrka run gapminder
```

`workspace validate` checks the placement, actions, quality gates, Silver task,
and contract without connecting to PostgreSQL or downloading data. The run
prints the pipeline run ID. The prepared files appear below:

```text
datasets/gapminder/data/files/silver/tables/gapminder/
```

Audit, quality, lineage, catalog, and publication-candidate records are stored
in PostgreSQL. The first development run may use a candidate Silver engine;
production mode always requires an approved engine release.

## Run on Linux or macOS

```bash
git clone https://github.com/brainality/metrka-example-datasets.git
cd metrka-example-datasets
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
metrka --version
docker compose up -d --wait
source scripts/set-local-env.sh --compose-database
python -m metrka_core.metadata.migrations upgrade head
python -m metrka_core.metadata.migrations check
metrka workspace validate gapminder
metrka run gapminder
```

## Approve and publish the Silver output

The pipeline stops at an auditable publication candidate. List candidates and
copy the candidate ID shown in the first column:

```powershell
metrka operations publication-candidates list `
    --dataset-id gapminder.development
```

On Windows PowerShell, enter that ID and record your operator identity:

```powershell
$candidateId = Read-Host "Candidate ID"
$operatorName = if ($env:USERNAME) { $env:USERNAME } else { "local-example-operator" }

metrka operations publication-candidates approve $candidateId `
    --approved-by $operatorName
metrka operations publication-candidates publish $candidateId `
    --workspace gapminder
metrka operations reconcile-publications `
    --workspace gapminder `
    --dataset-id gapminder.development
```

On Linux or macOS:

```bash
metrka operations publication-candidates list \
    --dataset-id gapminder.development
read -r -p "Candidate ID: " candidate_id
operator_name="${USER:-local-example-operator}"

metrka operations publication-candidates approve "$candidate_id" \
    --approved-by "$operator_name"
metrka operations publication-candidates publish "$candidate_id" \
    --workspace gapminder
metrka operations reconcile-publications \
    --workspace gapminder \
    --dataset-id gapminder.development
```

A successful reconciliation exits with code `0` and reports no integrity,
manifest, projection, or orphan-build failures. Run the pipeline once more to
exercise the normal idempotent path:

```powershell
metrka run gapminder
```

The unchanged source and configuration must not create another Silver build or
publication candidate.

## Inspect configuration without running PostgreSQL

```powershell
python -m pytest -q
```

These tests validate the explicit portable workspace placement, pipeline actions, quality gates,
Silver contract, output formats, immutable source URL, and the exact
`metrka-core` release dependency.

## Stop the local database

Preserve the database volume:

```powershell
docker compose down
```

Delete the disposable example database as well:

```powershell
docker compose down --volumes
```

The second command permanently removes the local example metadata database.

## Why the dataset repository is separate

`metrka-core` owns the execution engine, ports, adapters, composition, and
stable CLI. This repository owns one source definition, its transformation
contract, quality policy, and local filesystem workspace. Keeping those two
responsibilities separate demonstrates that the public core package can run a
dataset repository that was developed independently.
