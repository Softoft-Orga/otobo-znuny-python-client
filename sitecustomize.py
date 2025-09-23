import typing

try:
    from typing_extensions import Generator as _CompatGenerator
except Exception:  # pragma: no cover
    _CompatGenerator = None  # type: ignore[assignment]

if _CompatGenerator is not None:
    typing.Generator = _CompatGenerator  # type: ignore[assignment]
