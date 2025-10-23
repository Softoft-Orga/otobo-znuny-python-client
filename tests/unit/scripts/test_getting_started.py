from __future__ import annotations

from pathlib import Path

import pytest

from otobo_znuny_python_client.cli.interface import OtoboCommandRunner
from otobo_znuny_python_client.setup import bootstrap as getting_started


class TestSystemEnvironment:
    @pytest.mark.unit
    def test_build_command_runner_creates_local_runner(self, tmp_path):
        console = tmp_path / "bin" / "console.pl"
        console.parent.mkdir(parents=True)
        console.touch()
        env = getting_started.SystemEnvironment(console_path=console, webservices_dir=tmp_path)

        runner = env.build_command_runner()

        assert isinstance(runner, OtoboCommandRunner)
        assert runner.prefix == []
        # Note: executable may be converted to string internally
        assert str(runner.executable) == str(console)


class TestDockerEnvironment:
    @pytest.mark.unit
    def test_build_command_runner_creates_docker_runner(self, tmp_path):
        console = Path("/bin/otobo.Console.pl")
        env = getting_started.DockerEnvironment(
            container_name="otobo-web-1",
            console_path=str(console),
            webservices_dir=tmp_path,
        )

        runner = env.build_command_runner()

        assert isinstance(runner, OtoboCommandRunner)
        assert runner.prefix == ["docker", "exec", "otobo-web-1"]
        # Note: executable may be converted to string internally
        assert str(runner.executable) == str(console)
