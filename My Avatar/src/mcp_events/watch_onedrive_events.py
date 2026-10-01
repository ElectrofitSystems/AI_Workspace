"""Watch a OneDrive-synchronised queue and emit metadata-only MCP events."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def queue_root() -> Path:
    candidates: list[Path] = []
    commercial = os.environ.get("OneDriveCommercial")
    if commercial:
        candidates.append(Path(commercial))

    # Some OneDrive installations do not expose OneDriveCommercial even though
    # a business account is synchronised. Discover those folders explicitly and
    # prefer the queue that already exists.
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        candidates.extend(sorted(Path(user_profile).glob("OneDrive - *")))

    personal = os.environ.get("OneDrive")
    if personal:
        candidates.append(Path(personal))

    seen: set[Path] = set()
    roots: list[Path] = []
    for candidate in candidates:
        root = candidate / "My Avatar" / "MCP Events"
        if root not in seen:
            seen.add(root)
            roots.append(root)

    for root in roots:
        if (root / "Incoming").is_dir():
            return root
    if roots:
        return roots[0]
    raise RuntimeError("OneDrive is not configured")


def read_event(path: Path) -> tuple[str, str]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or set(data) != {"conversationId", "messageId"}:
        raise ValueError("Unexpected event schema")
    values = (data["conversationId"], data["messageId"])
    if any(not isinstance(value, str) or not 1 <= len(value) <= 512 for value in values):
        raise ValueError("Invalid event identifier")
    if any(any(ord(character) < 32 for character in value) for value in values):
        raise ValueError("Invalid event identifier")
    if any(any(character in value for character in "/?#") for value in values):
        raise ValueError("Invalid event identifier")
    return values


def process(path: Path, processed: Path, rejected: Path) -> None:
    try:
        conversation_id, message_id = read_event(path)
        helper = Path(__file__).with_name("emit_teams_event.py")
        result = subprocess.run(
            [
                sys.executable,
                str(helper),
                "--conversation-id",
                conversation_id,
                "--message-id",
                message_id,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        destination = processed if result.returncode == 0 else rejected
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError):
        destination = rejected

    destination.mkdir(parents=True, exist_ok=True)
    target = destination / path.name
    if target.exists():
        target = destination / f"{path.stem}-{time.time_ns()}{path.suffix}"
    shutil.move(str(path), str(target))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if not 0.5 <= args.interval <= 60:
        raise ValueError("Interval must be between 0.5 and 60 seconds")

    root = queue_root()
    incoming = root / "Incoming"
    processed = root / "Processed"
    rejected = root / "Rejected"
    incoming.mkdir(parents=True, exist_ok=True)

    while True:
        for path in sorted(incoming.glob("*.json")):
            if path.is_file():
                process(path, processed, rejected)
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
