#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path.cwd()
DRY_RUN = False
MAKE_BACKUP = True

FROM_TAG = "map_travel_3"
TO_TAG = "map_travel_2"


def is_starsystemdef(path: Path, data: dict) -> bool:
    desc = data.get("Description", {})
    desc_id = ""

    if isinstance(desc, dict):
        desc_id = desc.get("Id", "") or desc.get("id", "")

    return (
        path.name.lower().startswith("starsystemdef_")
        or str(desc_id).lower().startswith("starsystemdef_")
    )


def replace_tag(obj):
    if isinstance(obj, dict):
        return {k: replace_tag(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [replace_tag(v) for v in obj]

    if obj == FROM_TAG:
        return TO_TAG

    return obj


def process_file(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[SKIP] Invalid JSON: {path} ({e})")
        return False

    if not isinstance(data, dict):
        return False

    if not is_starsystemdef(path, data):
        return False

    if "TravelRequirements" not in data:
        print(f"[SKIP] No TravelRequirements: {path}")
        return False

    new_data = {
        "TravelRequirements": replace_tag(data["TravelRequirements"])
    }

    if DRY_RUN:
        print(f"[DRY] Would rewrite: {path}")
        return True

    if MAKE_BACKUP:
        backup_path = path.with_suffix(path.suffix + ".bak")
        if not backup_path.exists():
            backup_path.write_bytes(path.read_bytes())

    with path.open("w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4)
        f.write("\n")

    print(f"[OK] Rewritten: {path}")
    return True


def main():
    scanned = 0
    changed = 0

    for path in ROOT.rglob("*.json"):
        if path.name.endswith(".bak"):
            continue

        scanned += 1
        if process_file(path):
            changed += 1

    print()
    print(f"[DONE] Scanned JSON files: {scanned}")
    print(f"[DONE] Rewritten starsystemdefs: {changed}")


if __name__ == "__main__":
    main()
