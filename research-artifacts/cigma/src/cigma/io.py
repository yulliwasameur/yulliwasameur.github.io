"""Deterministic artifact input/output helpers."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration and reject a non-mapping document."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"configuration must be a mapping: {config_path}")
    return payload


def canonical_json_bytes(payload: Any) -> bytes:
    """Return stable UTF-8 JSON bytes for hashing and result export."""

    return (
        json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_json_bytes(payload))


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(
    path: str | Path,
    rows: Iterable[Mapping[str, Any]],
    *,
    fieldnames: list[str] | None = None,
) -> None:
    """Write a stable CSV with Unix newlines and an explicit column order."""

    materialized = [dict(row) for row in rows]
    if fieldnames is None:
        fieldnames = sorted({key for row in materialized for key in row})
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def artifact_files(root: str | Path) -> list[Path]:
    base = Path(root)
    return sorted(
        path
        for path in base.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    )


def safe_clean_output(path: str | Path) -> None:
    """Remove only files below a campaign directory carrying our marker."""

    target = Path(path).resolve()
    marker = target / ".cigma-results"
    if not target.exists():
        return
    if not target.is_dir() or not marker.is_file():
        raise ValueError(f"refusing to clean unmarked output directory: {target}")
    # Avoid broad targets even if a marker is accidentally placed there.
    if target == Path(target.anchor) or len(target.parts) < 4:
        raise ValueError(f"refusing to clean broad output directory: {target}")
    for child in sorted(target.rglob("*"), reverse=True):
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            child.rmdir()
    target.rmdir()


def mark_output(path: str | Path) -> None:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    (target / ".cigma-results").write_text(
        "CIGMA deterministic campaign output\n", encoding="utf-8"
    )


def _csv_value(value: Any) -> Any:
    if isinstance(value, float):
        return f"{value:.10g}"
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    if value is None:
        return ""
    return value


def deterministic_environment() -> dict[str, str]:
    """Return only stable, non-secret execution metadata."""

    import platform

    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.system().lower(),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "not-set"),
    }
