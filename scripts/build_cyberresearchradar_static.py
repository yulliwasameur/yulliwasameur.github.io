#!/usr/bin/env python3
"""Rebuild the reviewed static CyberResearch Radar assets deterministically."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import lzma
import os
from pathlib import Path


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    asset_dir = script_dir / "cyberresearchradar_assets"
    manifest = json.loads((asset_dir / "assets.json").read_text(encoding="utf-8"))
    destination = args.destination.resolve()

    for relative_path, metadata in manifest.items():
        encoded = "".join((asset_dir / part).read_text(encoding="ascii").strip() for part in metadata["parts"])
        payload = lzma.decompress(base64.b64decode(encoded, validate=True))
        actual_sha256 = hashlib.sha256(payload).hexdigest()
        if actual_sha256 != metadata["sha256"]:
            raise RuntimeError(f"Integrity failure for {relative_path}: {actual_sha256}")
        if len(payload) != metadata["bytes"]:
            raise RuntimeError(f"Size mismatch for {relative_path}: {len(payload)}")
        output = destination / relative_path
        write_atomic(output, payload)
        print(f"Generated {output} ({len(payload)} bytes, sha256={actual_sha256[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
