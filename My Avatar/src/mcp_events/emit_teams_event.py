"""Emit a metadata-only Teams wake event through an existing verified subscription.

This helper is intended to be launched by Power Automate Desktop.  It never
accepts message text and never prints the original Teams identifiers.
"""
import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit

from bridge import Bridge, Rejected


def pseudonym(kind: str, value: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 512:
        raise Rejected(f"Invalid {kind}")
    if any(ord(character) < 32 for character in value):
        raise Rejected(f"Invalid {kind}")
    digest = hashlib.sha256((kind + "\0" + value).encode("utf-8")).hexdigest()
    return f"TEST-TEAMS-{kind.upper()}-{digest}"


def verified_hosts(database: Path) -> set[str]:
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute("SELECT url FROM subscriptions").fetchall()
    finally:
        connection.close()
    hosts = set()
    for (url,) in rows:
        parts = urlsplit(url)
        if parts.scheme == "https" and parts.hostname:
            hosts.add(parts.hostname.lower())
    return hosts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conversation-id", required=True)
    parser.add_argument("--message-id", required=True)
    args = parser.parse_args()

    database = Path(os.environ["LOCALAPPDATA"]) / "MyAvatarMcpEvents" / "test-state.sqlite3"
    if not database.is_file():
        raise Rejected("MCP Events state is unavailable")

    payload = {
        "conversationId": pseudonym("conversation", args.conversation_id),
        "messageId": pseudonym("message", args.message_id),
    }
    connection = sqlite3.connect(database)
    try:
        connection.execute('''
          CREATE TABLE IF NOT EXISTS teams_events
            (conversation_key TEXT NOT NULL, message_key TEXT NOT NULL,
             conversation_id TEXT NOT NULL, message_id TEXT NOT NULL,
             created REAL NOT NULL, PRIMARY KEY(conversation_key,message_key))
        ''')
        connection.execute(
            'INSERT OR REPLACE INTO teams_events VALUES (?,?,?,?,strftime("%s","now"))',
            (payload["conversationId"], payload["messageId"],
             args.conversation_id, args.message_id),
        )
        connection.commit()
    finally:
        connection.close()
    bridge = Bridge(database, verified_hosts(database))
    try:
        code, result = bridge.ingest(payload)
    finally:
        bridge.db.close()

    safe_result = {
        "accepted": code == 200,
        "deliveryCount": len(result.get("deliveries", [])),
        "deliveryStates": result.get("deliveries", []),
    }
    print(json.dumps(safe_result, separators=(",", ":")))
    return 0 if code == 200 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Rejected, OSError, sqlite3.Error, ValueError, KeyError):
        print('{"accepted":false,"error":"local_bridge_unavailable"}')
        raise SystemExit(1)
