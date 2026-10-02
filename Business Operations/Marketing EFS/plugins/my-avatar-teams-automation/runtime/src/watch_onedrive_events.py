from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def queue_root(install_root: Path, settings: dict) -> Path:
    configured = settings["oneDrive"].get("queueRoot", "auto")
    if configured != "auto":
        return Path(os.path.expandvars(configured)).expanduser()
    candidates = []
    for key in ("OneDriveCommercial", "OneDrive"):
        value = os.environ.get(key)
        if value:
            candidates.append(Path(value))
    profile = os.environ.get("USERPROFILE")
    if profile:
        candidates.extend(sorted(Path(profile).glob("OneDrive - *")))
    for candidate in candidates:
        root = candidate / "My Avatar" / "MCP Events"
        if (root / "Incoming").is_dir():
            return root
    if candidates:
        return candidates[0] / "My Avatar" / "MCP Events"
    raise RuntimeError("OneDrive is not configured")


def read_event(path: Path) -> tuple[str, str]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or set(data) != {"conversationId", "messageId"}:
        raise ValueError("Unexpected event schema")
    values = data["conversationId"], data["messageId"]
    if any(not isinstance(value, str) or not 1 <= len(value) <= 512 for value in values):
        raise ValueError("Invalid identifier")
    return values


def process(path: Path, processed: Path, rejected: Path, install_root: Path) -> None:
    try:
        conversation_id, message_id = read_event(path)
        helper = Path(__file__).with_name("emit_teams_event.py")
        result = subprocess.run([sys.executable, str(helper), "--root", str(install_root),
                                 "--conversation-id", conversation_id, "--message-id", message_id],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=30, check=False,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
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
    parser.add_argument("--root", required=True)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if not 0.5 <= args.interval <= 60:
        raise ValueError("Interval must be between 0.5 and 60 seconds")
    install_root = Path(args.root).resolve()
    settings = json.loads((install_root / "config" / "settings.json").read_text(encoding="utf-8-sig"))
    root = queue_root(install_root, settings)
    incoming, processed, rejected = root / "Incoming", root / "Processed", root / "Rejected"
    incoming.mkdir(parents=True, exist_ok=True)
    while True:
        for path in sorted(incoming.glob("*.json")):
            if path.is_file():
                process(path, processed, rejected, install_root)
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
