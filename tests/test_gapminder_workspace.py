"""Contract tests for the public Gapminder example workspace."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import yaml
from metrka_core.datasets.source_config import load_source_config
from metrka_core.pipeline.models import parse_pipeline_spec
from metrka_core.pipeline.silver.task_factory import build_silver_tasks
from metrka_core.quality.config import load_quality_config
from metrka_core.quality.models import QualityGate
from metrka_core.quality.registry import create_default_quality_registry
from metrka_core.transform.validation import validate_contract_file

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPOSITORY_ROOT / "datasets" / "gapminder"
CONFIG_ROOT = WORKSPACE_ROOT / "conf"
PINNED_SOURCE_PATTERN = re.compile(
    r"https://raw\.githubusercontent\.com/jennybc/gapminder/"
    r"[0-9a-f]{40}/inst/extdata/gapminder\.tsv\Z"
)


def test_workspace_registry_resolves_gapminder() -> None:
    placement_config = yaml.safe_load(
        (REPOSITORY_ROOT / "workspaces.example.yaml").read_text(encoding="utf-8")
    )

    assert placement_config == {
        "schema_version": 1,
        "workspaces": {
            "gapminder": {"placement": "portable", "workspace_root": "datasets/gapminder"}
        },
    }
    assert WORKSPACE_ROOT.is_dir()


def test_pipeline_uses_only_standard_core_actions() -> None:
    source_config = load_source_config(CONFIG_ROOT / "main.yaml", expected_ws_name="gapminder")
    pipeline = parse_pipeline_spec(source_config.pipeline)

    assert pipeline.acquisition.extractor == "http.files"
    assert [step.action for step in pipeline.steps] == ["bronze.ingest", "silver.process"]


def test_source_url_is_pinned_to_an_immutable_git_revision() -> None:
    source_config = load_source_config(CONFIG_ROOT / "main.yaml", expected_ws_name="gapminder")
    source_url = source_config.streams["development"].extra["download_url"]

    assert isinstance(source_url, str)
    assert PINNED_SOURCE_PATTERN.fullmatch(source_url) is not None


def test_silver_contract_and_task_are_valid() -> None:
    source_config = load_source_config(CONFIG_ROOT / "main.yaml", expected_ws_name="gapminder")
    contract = validate_contract_file(CONFIG_ROOT / "gapminder.yaml")
    tasks = build_silver_tasks(source_config=source_config)
    source_table_key = Path(source_config.streams["development"].official_filename).stem

    assert set(contract["tables"]) == {"gapminder"}
    assert source_table_key in contract["tables"]
    assert len(tasks) == 1
    assert tasks[0].dataset_id == "gapminder.development"
    assert tasks[0].input_format == "tsv"
    assert tasks[0].output_formats == ["parquet", "csv"]


def test_quality_config_covers_every_gate() -> None:
    quality = load_quality_config(CONFIG_ROOT / "quality.yaml")
    create_default_quality_registry().validate_specs(quality.checks)

    assert {check.gate for check in quality.checks} == set(QualityGate)


def test_example_depends_on_the_verified_core_release_wheel() -> None:
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    assert project["version"] == "1.1.0"
    assert project["dependencies"] == [
        "metrka-core @ https://github.com/brainality/metrka-core/releases/"
        "download/v1.1.0/metrka_core-1.1.0-py3-none-any.whl"
    ]
