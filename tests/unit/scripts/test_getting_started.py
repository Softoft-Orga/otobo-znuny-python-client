from __future__ import annotations

import string
from pathlib import Path
from types import SimpleNamespace

import pytest

from otobo_znuny.scripts.cli_interface import CommandRunner

from otobo_znuny.scripts import getting_started


class TestSlug:
    def test_replaces_special_characters_and_normalises_case(self) -> None:
        assert getting_started._slug("Hello, World! Welcome") == "hello-world-welcome"


class TestGeneratePassword:
    def test_generated_password_has_expected_length_and_charset(self) -> None:
        password = getting_started._gen_password(16)

        assert len(password) == 16
        allowed = set(string.ascii_letters + string.digits)
        assert set(password).issubset(allowed)


class TestGenerateRandomDomain:
    def test_uses_generated_password_lowercased_for_domain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(getting_started, "_gen_password", lambda n=32: "AbC12345")

        assert getting_started._gen_random_domain() == "abc12345.com"


class TestWriteText:
    def test_writes_file_and_creates_parent_directories(self, tmp_path: Path) -> None:
        target = tmp_path / "nested" / "file.txt"

        getting_started._write_text(target, "content", force=False)

        assert target.read_text(encoding="utf-8") == "content"

    def test_raises_when_exists_and_force_is_false(self, tmp_path: Path) -> None:
        target = tmp_path / "file.txt"
        target.write_text("existing", encoding="utf-8")

        with pytest.raises(FileExistsError):
            getting_started._write_text(target, "new", force=False)

    def test_overwrites_when_force_is_true(self, tmp_path: Path) -> None:
        target = tmp_path / "file.txt"
        target.write_text("existing", encoding="utf-8")

        getting_started._write_text(target, "new", force=True)

        assert target.read_text(encoding="utf-8") == "new"


class TestGetRunningContainer:
    def test_returns_matching_pattern_when_docker_list_contains_it(self, monkeypatch: pytest.MonkeyPatch) -> None:
        result = SimpleNamespace(returncode=0, stdout="otobo-web-1\nother")
        monkeypatch.setattr(
            getting_started.subprocess,
            "run",
            lambda *args, **kwargs: result,
        )

        assert getting_started._get_running_container(["otobo-web-1"]) == "otobo-web-1"

    def test_returns_none_when_command_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        result = SimpleNamespace(returncode=1, stdout="")
        monkeypatch.setattr(
            getting_started.subprocess,
            "run",
            lambda *args, **kwargs: result,
        )

        assert getting_started._get_running_container(["otobo-web-1"]) is None


class TestSystemEnvironment:
    def test_is_valid_environment_checks_path_existence(self, tmp_path: Path) -> None:
        console = tmp_path / "bin" / "console.pl"
        webservices = tmp_path / "var" / "webservices"
        console.parent.mkdir(parents=True)
        console.touch()
        webservices.mkdir(parents=True)

        env = getting_started.SystemEnvironment(console_path=console, webservices_dir=webservices)

        assert env.is_valid_environment()

    def test_ticket_system_name_resolution(self) -> None:
        env_otobo = getting_started.SystemEnvironment(Path("/opt/otobo/bin/otobo.Console.pl"), Path("/ws"))
        env_znuny = getting_started.SystemEnvironment(Path("/opt/znuny/bin/otrs.Console.pl"), Path("/ws"))
        env_unknown = getting_started.SystemEnvironment(Path("/opt/custom/bin/console.pl"), Path("/ws"))

        assert env_otobo.ticket_system_name == "otobo"
        assert env_znuny.ticket_system_name == "znuny"
        assert env_unknown.ticket_system_name == "Unknown"

    def test_build_command_runner_creates_local_runner(self, tmp_path: Path) -> None:
        console = tmp_path / "bin" / "console.pl"
        console.parent.mkdir(parents=True)
        console.touch()
        env = getting_started.SystemEnvironment(console_path=console, webservices_dir=tmp_path)

        runner = env.build_command_runner()

        assert isinstance(runner, CommandRunner)
        assert runner.prefix == []
        assert runner.executable == console


class TestDockerEnvironment:
    def test_build_command_runner_creates_docker_runner(self, tmp_path: Path) -> None:
        console = Path("/bin/otobo.Console.pl")
        env = getting_started.DockerEnvironment(
            container_name="otobo-web-1",
            console_path=console,
            webservices_dir=tmp_path,
        )

        runner = env.build_command_runner()

        assert isinstance(runner, CommandRunner)
        assert runner.prefix == ["docker", "exec", "otobo-web-1"]
        assert runner.executable == console

    def test_is_valid_environment_requires_webservices_path(self, tmp_path: Path) -> None:
        env = getting_started.DockerEnvironment(
            container_name="otobo-web-1",
            console_path=Path("/bin/otobo.Console.pl"),
            webservices_dir=tmp_path,
        )

        assert env.is_valid_environment()


class TestBuildSystemEnvironment:
    def test_returns_docker_environment_when_container_name_provided(self, tmp_path: Path) -> None:
        env = getting_started._build_system_environment(
            console_path=Path("/bin/otobo.Console.pl"),
            webservices_dir=tmp_path,
            container_name="otobo-web-1",
        )

        assert isinstance(env, getting_started.DockerEnvironment)

    def test_returns_system_environment_when_no_container(self, tmp_path: Path) -> None:
        env = getting_started._build_system_environment(
            console_path=tmp_path / "console.pl",
            webservices_dir=tmp_path,
            container_name=None,
        )

        assert isinstance(env, getting_started.SystemEnvironment)


class TestDetectEnvironment:
    def test_prefers_docker_environment_when_container_detected(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(getting_started, "_get_running_container", lambda patterns: "otobo-web-1")

        env = getting_started._detect_environment()

        assert isinstance(env, getting_started.DockerEnvironment)
        assert env.container_name == "otobo-web-1"
        assert env.console_path == Path("/bin/otobo.Console.pl")
        assert env.webservices_dir == getting_started.OTOBO_DOCKER_WEBSERVICE_PATH

    def test_returns_system_environment_when_single_local_paths_exist(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(getting_started, "_get_running_container", lambda patterns: None)

        existing = {
            str(path): True
            for path in (
                Path("/opt/otobo/bin/otobo.Console.pl"),
                Path("/opt/otobo/var/webservices"),
            )
        }

        def fake_exists(self: Path) -> bool:  # noqa: ANN001
            return existing.get(str(self), False)

        monkeypatch.setattr(Path, "exists", fake_exists, raising=False)

        env = getting_started._detect_environment()

        assert isinstance(env, getting_started.SystemEnvironment)
        assert env.console_path == Path("/opt/otobo/bin/otobo.Console.pl")
        assert env.webservices_dir == Path("/opt/otobo/var/webservices")

    def test_returns_none_when_no_environment_detected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(getting_started, "_get_running_container", lambda patterns: None)

        monkeypatch.setattr(Path, "exists", lambda self: False, raising=False)

        assert getting_started._detect_environment() is None
