from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "translations"
OUTPUT = TRANSLATIONS / "manifest.json"

EXCLUDED_NAMES = {
    "manifest.json",
    "missing.json",
    "ui_snapshot.tsv",
    "subskill_scan.tsv",
}

ALLOWED_SUFFIXES = {".json"}

files: dict[str, dict[str, str | int]] = {}

for path in sorted(TRANSLATIONS.rglob("*")):
    if (
        not path.is_file()
        or path.name in EXCLUDED_NAMES
        or path.suffix.lower() not in ALLOWED_SUFFIXES
    ):
        continue

    relative_path = path.relative_to(TRANSLATIONS).as_posix()
    content = path.read_bytes()

    files[relative_path] = {
        "sha256": hashlib.sha256(content).hexdigest(),
        "size": len(content),
    }

manifest = {
    "schemaVersion": 1,
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "commit": "",
    "files": files,
}

OUTPUT.write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print(f"Generated {OUTPUT} with {len(files)} files")