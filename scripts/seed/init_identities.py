from pathlib import Path
import json

ids = {
    "train_id": "tg-001",
    "ag_ids": ["ag1", "ag2"],
    "anchor_ids": ["anchor-main", "anchor-verify"],
}
Path("outputs/identities.json").write_text(json.dumps(ids, indent=2), encoding="utf-8")
print("seed identities written to outputs/identities.json")
