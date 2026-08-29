#!/usr/bin/env python3
"""Apply the persistent CyberResearch Radar v3.2 shell upgrade.

The static application is reconstructed from reviewed compressed assets every
Monday. This idempotent patch therefore runs after each reconstruction so the
version badge, visitor counter, cache busting and supplementary dataset survive.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

VERSION = "3.2.0"
SUPPLEMENTAL_DATASET = "publication_recommender_events.json"


def write_atomic(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def patch_index(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if 'name="cyberresearchradar-version"' not in text:
        text = text.replace(
            '<meta name="theme-color" content="#07151b">',
            '<meta name="theme-color" content="#07151b">\n  <meta name="cyberresearchradar-version" content="3.2.0">',
            1,
        )
    text = text.replace('./assets/styles.css"', f'./assets/styles.css?v={VERSION}"')
    text = text.replace('./assets/app.js"', f'./assets/app.js?v={VERSION}"')
    if 'radar-upgrade.css' not in text:
        text = text.replace(
            f'<link rel="stylesheet" href="./assets/styles.css?v={VERSION}">',
            f'<link rel="stylesheet" href="./assets/styles.css?v={VERSION}">\n  <link rel="stylesheet" href="./assets/radar-upgrade.css?v={VERSION}">',
            1,
        )
    if 'radar-upgrade.js' not in text:
        text = text.replace(
            f'<script defer src="./assets/app.js?v={VERSION}"></script>',
            f'<script defer src="./assets/app.js?v={VERSION}"></script>\n  <script defer src="./assets/radar-upgrade.js?v={VERSION}"></script>',
            1,
        )
    write_atomic(path, text)


def patch_javascript(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if SUPPLEMENTAL_DATASET not in text:
        old = "const DATA_FILES = ['opportunities.json', 'crypto_opportunities.json', 'cyber_opportunities.json', 'catalogue_events.json'];"
        new = "const DATA_FILES = ['opportunities.json', 'crypto_opportunities.json', 'cyber_opportunities.json', 'catalogue_events.json', 'publication_recommender_events.json'];"
        if old not in text:
            raise RuntimeError("Could not locate the CyberResearch Radar dataset declaration")
        text = text.replace(old, new, 1)
    write_atomic(path, text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    destination = args.destination.resolve()
    index = destination / "index.html"
    javascript = destination / "assets" / "app.js"
    if not index.is_file() or not javascript.is_file():
        raise FileNotFoundError("CyberResearch Radar static shell is incomplete")
    patch_index(index)
    patch_javascript(javascript)
    print(f"Applied CyberResearch Radar v{VERSION} shell upgrade")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
