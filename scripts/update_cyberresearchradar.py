#!/usr/bin/env python3
"""Publish the CyberResearch Radar datasets into a GitHub Pages subdirectory.

The script is intentionally dependency-free. It validates the source JSON,
copies files atomically, and writes a dated manifest consumed by the static UI.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENT_FILES = (
    "opportunities.json",
    "crypto_opportunities.json",
    "cyber_opportunities.json",
    "catalogue_events.json",
)
JOURNAL_FILE = "journals.json"
OPTIONAL_REPORTS = ("watch_report.json", "journal_watch_report.json")
ALLOWED_EVENT_TYPES = {"conference", "workshop"}


class ValidationError(RuntimeError):
    """Raised when source data cannot safely be published."""


def read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValidationError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc


def validate_event_dataset(path: Path, payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValidationError(f"{path} must contain a JSON array")
    valid: list[dict[str, Any]] = []
    for index, record in enumerate(payload):
        if not isinstance(record, dict):
            raise ValidationError(f"{path}[{index}] must be an object")
        for key in ("id", "title", "type", "officialUrl", "evidenceUrl"):
            if not record.get(key):
                raise ValidationError(f"{path}[{index}] is missing required field {key!r}")
        if not isinstance(record.get("topics", []), list):
            raise ValidationError(f"{path}[{index}].topics must be an array")
        if not isinstance(record.get("rankings", []), list):
            raise ValidationError(f"{path}[{index}].rankings must be an array")
        valid.append(record)
    return valid


def validate_journals(path: Path, payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValidationError(f"{path} must contain a JSON array")
    valid: list[dict[str, Any]] = []
    for index, record in enumerate(payload):
        if not isinstance(record, dict):
            raise ValidationError(f"{path}[{index}] must be an object")
        for key in ("id", "title", "publisher", "officialUrl"):
            if not record.get(key):
                raise ValidationError(f"{path}[{index}] is missing required field {key!r}")
        if not isinstance(record.get("rankings", []), list):
            raise ValidationError(f"{path}[{index}].rankings must be an array")
        valid.append(record)
    return valid


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copyfile(source, temporary)
    os.replace(temporary, destination)


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")
    os.replace(temporary, path)


def git_head(repository: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def validate_static_shell(destination: Path) -> None:
    required = (
        destination / "index.html",
        destination / "assets" / "styles.css",
        destination / "assets" / "app.js",
    )
    for path in required:
        if not path.is_file() or path.stat().st_size < 100:
            raise ValidationError(f"Static site asset is missing or too small: {path}")

    index = (destination / "index.html").read_text(encoding="utf-8")
    javascript = (destination / "assets" / "app.js").read_text(encoding="utf-8")
    if './assets/styles.css' not in index or './assets/app.js' not in index:
        raise ValidationError("index.html must use relative asset paths for /cyberresearchradar")
    if "chatgpt.site" in index.lower() or "chatgpt.site" in javascript.lower():
        raise ValidationError("The GitHub Pages copy must not depend on chatgpt.site at runtime")
    for language in ("fr", "en", "kab"):
        if f"data-lang=\"{language}\"" not in index:
            raise ValidationError(f"Missing language selector for {language}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True, help="Checked-out cyber-research-radar repository")
    parser.add_argument("--destination", type=Path, required=True, help="GitHub Pages /cyberresearchradar directory")
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()
    source_data = source / "data"
    destination_data = destination / "data"

    validate_static_shell(destination)

    datasets: dict[str, list[dict[str, Any]]] = {}
    all_records: list[dict[str, Any]] = []
    for filename in EVENT_FILES:
        path = source_data / filename
        records = validate_event_dataset(path, read_json(path))
        datasets[filename] = records
        all_records.extend(records)

    journals_path = source_data / JOURNAL_FILE
    journals = validate_journals(journals_path, read_json(journals_path))

    event_records = [record for record in all_records if record.get("type") in ALLOWED_EVENT_TYPES]
    unique_events = {str(record["id"]): record for record in event_records}
    unique_journals = {str(record["id"]): record for record in journals}

    if len(unique_events) < 10:
        raise ValidationError(f"Refusing to publish only {len(unique_events)} unique conference/workshop records")
    if len(unique_journals) < 1:
        raise ValidationError("Refusing to publish an empty journal directory")

    for filename in EVENT_FILES:
        atomic_copy(source_data / filename, destination_data / filename)
    atomic_copy(journals_path, destination_data / JOURNAL_FILE)

    copied_reports: list[str] = []
    for filename in OPTIONAL_REPORTS:
        report_path = source_data / filename
        if not report_path.is_file():
            continue
        read_json(report_path)
        atomic_copy(report_path, destination_data / filename)
        copied_reports.append(filename)

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    manifest = {
        "generatedAt": generated_at,
        "sourceCommit": git_head(source),
        "sourceRepository": "yulliwasameur/cyber-research-radar",
        "recordCounts": {
            "eventsRaw": len(event_records),
            "eventsUnique": len(unique_events),
            "journals": len(unique_journals),
            "countries": len({str(record.get("country")) for record in unique_events.values() if record.get("country")}),
        },
        "files": [*EVENT_FILES, JOURNAL_FILE, *copied_reports],
        "languages": ["fr", "en", "kab"],
        "publicPath": "/cyberresearchradar/",
        "status": "ok",
    }
    write_json_atomic(destination_data / "manifest.json", manifest)

    print(
        "Published CyberResearch Radar: "
        f"{len(unique_events)} unique events, {len(unique_journals)} journals, "
        f"source commit {manifest['sourceCommit'] or 'unknown'}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
