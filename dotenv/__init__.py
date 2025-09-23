from __future__ import annotations

import os
from pathlib import Path
from typing import Any

__all__ = ["load_dotenv"]


def _parse_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "=" not in line:
        return None
    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip().strip('"').strip("'")
    return key, value


def load_dotenv(path: str | os.PathLike[str] | None = None, *args: Any, **kwargs: Any) -> bool:
    if path is None:
        return False
    file_path = Path(path)
    if not file_path.exists():
        return False
    updated = False
    with file_path.open() as handle:
        for line in handle:
            parsed = _parse_line(line)
            if parsed is None:
                continue
            key, value = parsed
            os.environ[key] = value
            updated = True
    return updated
