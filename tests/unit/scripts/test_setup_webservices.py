from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner

from otobo_znuny.setup.webservices import generator as sw

# Ensure the legacy scripts import resolves to the package under src/otobo/scripts.
scripts_pkg = sys.modules.get("scripts")
if scripts_pkg is None:
    scripts_pkg = ModuleType("scripts")
    scripts_pkg.__path__ = []  # type: ignore[attr-defined]
    sys.modules["scripts"] = scripts_pkg

webservice_util = importlib.import_module("otobo_znuny.scripts.webservice_util")
scripts_pkg.webservice_util = webservice_util
sys.modules["scripts.webservice_util"] = webservice_util

runner = CliRunner()


@pytest.mark.unit
def test_cli_generates_default_config(tmp_path: Path) -> None:
    """Test that CLI generates config with default parameters."""
    file_path = tmp_path / "config.yml"
    result = runner.invoke(
        sw.app,
        ["--output", str(file_path)],
    )

    # CLI should succeed with defaults
    assert result.exit_code == 0
    assert file_path.exists()
    assert "Web service configuration generated" in result.output


@pytest.mark.unit
def test_cli_generates_config_with_custom_params(tmp_path: Path) -> None:
    """Test that CLI generates config with custom parameters."""
    file_path = tmp_path / "custom.yml"
    result = runner.invoke(
        sw.app,
        [
            "--name", "CustomService",
            "--description", "Custom description",
            "--password", "secret123",
            "--operations", "create",
            "--operations", "update",
            "--output", str(file_path),
        ],
    )

    # CLI should succeed and create the file
    assert result.exit_code == 0
    assert file_path.exists()
    assert "Web service configuration generated" in result.output


@pytest.mark.unit
def test_cli_handles_single_operation(tmp_path: Path) -> None:
    """Test that CLI works with a single operation."""
    file_path = tmp_path / "single_op.yml"
    result = runner.invoke(
        sw.app,
        [
            "--name", "GetOnlyService",
            "--password", "pass123",
            "--operations", "get",
            "--output", str(file_path),
        ],
    )

    # CLI should succeed
    assert result.exit_code == 0
    assert file_path.exists()
