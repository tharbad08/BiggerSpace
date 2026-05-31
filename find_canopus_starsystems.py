#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

BASE_GAME_DATA = Path("/media/Various/Games/BattleTech/BATTLETECH root/BattleTech_Data/StreamingAssets/data/")
MODS_DIR = Path("/media/Various/Games/BattleTech/BATTLETECH root/Mods/")

# Destination folder
DEST_DIR = Path("/media/Various/Games/BattleTech/Dev/BiggerSpace/NewCanopus/")

TARGET_OWNER = "MagistracyOfCanopus"


def is_starsystemdef(path: Path, data: dict) -> bool:
    desc = data.get("Description", {})
    desc_id = ""

    if isinstance(desc, dict):
        desc_id = desc.get("Id", "") or desc.get("id", "")

    return (
        path.name.lower().startswith("starsystemdef_")
        or str(desc_id).lower().startswith("starsystemdef_")
    )


def scan_and_copy(root: Path):
    if not root.exists():
        print(f"[WARN] Missing path: {root}")
        return

    for path in root.rglob("*.json"):
        try:
            with path.open("r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        if not is_starsystemdef(path, data):
            continue

        if data.get("ownerID") != TARGET_OWNER:
            continue

        DEST_DIR.mkdir(parents=True, exist_ok=True)

        dest_file = DEST_DIR / path.name

        try:
            shutil.copy2(path, dest_file)

            desc = data.get("Description", {})
            name = desc.get("Name", path.stem) if isinstance(desc, dict) else path.stem

            print(f"[COPIED] {name}")
            print(f"  FROM: {path}")
            print(f"  TO:   {dest_file}")

        except Exception as e:
            print(f"[ERROR] Failed copying {path}")
            print(f"        {e}")


def main():
    print(f"[INFO] Copying all {TARGET_OWNER} starsystemdefs")
    print()

    scan_and_copy(BASE_GAME_DATA)
    scan_and_copy(MODS_DIR)

    print()
    print("[DONE]")


if __name__ == "__main__":
    main()
