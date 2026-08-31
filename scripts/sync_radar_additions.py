#!/usr/bin/env python3
"""Publish supplementary Radar datasets and refresh the public manifest."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_EVENT_FILES = (
    "opportunities.json",
    "crypto_opportunities.json",
    "cyber_opportunities.json",
    "catalogue_events.json",
)
SUPPLEMENTAL_EVENT_FILES = (
    "publication_recommender_events.json",
    "community_opportunities.json",
)
OPTIONAL_FILES = (
    "publication_recommender_import_report.json",
    "publication_recommender_watch_report.json",
    "community_watch_report.json",
)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def copy_atomic(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copyfile(source, temporary)
    os.replace(temporary, destination)


def write_json_atomic(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)


def validate_events(payload: Any, filename: str) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValueError(f"{filename} must be a JSON array")
    ids: set[str] = set()
    for index, record in enumerate(payload):
        if not isinstance(record, dict):
            raise ValueError(f"{filename}[{index}] must be an object")
        for field in ("id", "title", "type", "officialUrl", "evidenceUrl"):
            if not record.get(field):
                raise ValueError(f"{filename}[{index}] is missing {field}")
        if record["id"] in ids:
            raise ValueError(f"Duplicate id in {filename}: {record['id']}")
        ids.add(record["id"])
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    source_data = args.source.resolve() / "data"
    destination_data = args.destination.resolve() / "data"

    supplemental_records: dict[str, list[dict[str, Any]]] = {}
    copied: list[str] = []
    for filename in SUPPLEMENTAL_EVENT_FILES:
        source = source_data / filename
        records = validate_events(read_json(source), filename)
        supplemental_records[filename] = records
        copy_atomic(source, destination_data / filename)
        copied.append(filename)

    for filename in OPTIONAL_FILES:
        source = source_data / filename
        if source.is_file():
            read_json(source)
            copy_atomic(source, destination_data / filename)
            copied.append(filename)

    manifest_path = destination_data / "manifest.json"
    manifest = read_json(manifest_path)
    event_files = (*BASE_EVENT_FILES, *SUPPLEMENTAL_EVENT_FILES)
    all_events: dict[str, dict[str, Any]] = {}
    raw_count = 0
    for filename in event_files:
        records = read_json(destination_data / filename)
        raw_count += len(records)
        for record in records:
            if record.get("type") in {"conference", "workshop"} and record.get("id"):
                all_events[str(record["id"])] = record

    countries = {str(record.get("country")) for record in all_events.values() if record.get("country")}
    manifest.setdefault("recordCounts", {})
    manifest["recordCounts"].update({
        "eventsRaw": raw_count,
        "eventsUnique": len(all_events),
        "countries": len(countries),
    })
    manifest["generatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    manifest["version"] = "3.2.0"
    files = list(manifest.get("files", []))
    for filename in copied:
        if filename not in files:
            files.append(filename)
    manifest["files"] = files
    write_json_atomic(manifest_path, manifest)

    supplemental_count = sum(len(records) for records in supplemental_records.values())
    print(f"Published {supplemental_count} supplementary events; {len(all_events)} unique events in manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
