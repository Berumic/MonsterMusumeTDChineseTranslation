from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "translations"
ASSETS = ROOT / "assets"

EXCLUDED_NAMES = {
    "manifest.json",
    "missing.json",
    "ui_snapshot.tsv",
    "subskill_scan.tsv",
}

def current_commit() -> str:
    github_sha = os.environ.get("GITHUB_SHA", "").strip()
    if github_sha:
        return github_sha
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def generate_manifest(
    source: Path,
    *,
    allowed_suffixes: set[str] | None = None,
    excluded_names: set[str] | None = None,
) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Manifest source directory does not exist: {source}")

    excluded_names = excluded_names or {"manifest.json"}
    files: dict[str, dict[str, str | int]] = {}
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.name in excluded_names:
            continue
        if allowed_suffixes is not None and path.suffix.lower() not in allowed_suffixes:
            continue

        content = path.read_bytes()
        files[path.relative_to(source).as_posix()] = {
            "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content),
        }

    output = source / "manifest.json"
    manifest = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "commit": current_commit(),
        "files": files,
    }
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {output} with {len(files)} files")


generate_manifest(
    TRANSLATIONS,
    allowed_suffixes={".json"},
    excluded_names=EXCLUDED_NAMES,
)
generate_manifest(ASSETS)
if (ASSETS / "android").is_dir():
    generate_manifest(ASSETS / "android")
