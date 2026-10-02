"""Create a versioned approval manifest; upload it LAST, after all review files."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

WORKSPACE = Path(__file__).resolve().parents[2]
OUTPUTS = WORKSPACE / "output"
CLOUD = "https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Outputs/"
CATEGORIES = {"Linkedin": "LinkedIn", "Documentation": "Documentation", "Newsletter": "Newsletter", "Statistics": "Statistics"}

def prepare(title, revision, category, action, pairs, destination, authorization=None):
    target = Path(destination).resolve()
    target.relative_to(OUTPUTS.resolve())
    if not target.name.endswith("-approval-request.json"):
        raise ValueError("Use a versioned name ending in -approval-request.json")
    if action != "review_only" and not authorization:
        raise ValueError("Execution requires the user's explicit request recorded in --authorization")
    if action == "linkedin_publish" and category != "linkedin":
        raise ValueError("linkedin_publish requires category linkedin")
    files = []
    for local, cloud_relative in pairs:
        source = Path(local).resolve()
        source.relative_to(OUTPUTS.resolve())
        parts = Path(cloud_relative).parts
        if not parts or parts[0] not in CATEGORIES.values() or any(p in ("..", ".") for p in parts) or Path(cloud_relative).is_absolute():
            raise ValueError("Cloud files must be inside an existing Outputs category")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        files.append({"name": source.name, "url": CLOUD + quote(cloud_relative.replace("\\", "/"), safe="/"), "sha256": digest, "size": source.stat().st_size})
    if not files:
        raise ValueError("At least one review file is required")
    payload = {"schema_version": 1, "title": title, "revision": revision, "category": category, "requested_action": action, "execution_authorization": authorization, "files": files}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    payload.update({"created_at": datetime.now(timezone.utc).isoformat(), "package_sha256": digest, "review_url": files[0]["url"], "review_details": "\n\n".join(f"[{f['name']}]({f['url']})\nSHA256: {f['sha256']}" for f in files)})
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--category", choices=["linkedin", "documentation", "newsletter", "statistics"], required=True)
    parser.add_argument("--action", choices=["review_only", "linkedin_publish"], default="review_only")
    parser.add_argument("--authorization")
    parser.add_argument("--file", nargs=2, action="append", metavar=("LOCAL_PATH", "CLOUD_RELATIVE_PATH"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    print(prepare(args.title, args.revision, args.category, args.action, args.file, args.out, args.authorization))

if __name__ == "__main__":
    main()
