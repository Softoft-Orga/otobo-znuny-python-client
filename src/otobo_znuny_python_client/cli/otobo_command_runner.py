from __future__ import annotations

import subprocess
from pathlib import Path

from otobo_znuny_python_client.cli.command_models import CmdResult


class OtoboCommandRunner:
    def __init__(self, prefix: list[str], executable: Path | str, log_commands=True):
        self.prefix: list[str] = prefix
        self.executable: str = str(executable)
        self.log_commands: bool = log_commands

    @classmethod
    def from_docker(cls, container: str = "otobo-web-1",
                    console_path="./bin/otobo.Console.pl") -> OtoboCommandRunner:
        return cls(["docker", "exec", container], console_path)

    @classmethod
    def from_local(cls, console_path="/opt/otobo/bin/otobo.Console.pl") -> OtoboCommandRunner:
        return cls([], console_path)

    def run(self, operation: str, args: list[str]) -> CmdResult:
        cmd = [*self.prefix, self.executable, operation, *args]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        cmd_result = CmdResult(proc.returncode == 0, proc.returncode, proc.stdout.strip(), proc.stderr.strip())
        if self.log_commands:
            pass
        return cmd_result
