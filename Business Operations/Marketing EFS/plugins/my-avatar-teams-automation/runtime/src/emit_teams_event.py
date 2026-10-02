from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--conversation-id", required=True)
    parser.add_argument("--message-id", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    settings = json.loads((root / "config" / "settings.json").read_text(encoding="utf-8-sig"))
    token = os.environ.get("MYAVATAR_INGRESS_TOKEN", "")
    if len(token) < 32:
        raise SystemExit("MYAVATAR_INGRESS_TOKEN is not configured")
    url = f"http://{settings['bridge']['bindHost']}:{int(settings['bridge']['port'])}/ingress/teams"
    body = json.dumps({"conversationId": args.conversation_id, "messageId": args.message_id},
                      separators=(",", ":")).encode()
    request = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Authorization": "Bearer " + token,
                                              "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return 0 if response.status in (200, 202) else 1
    except urllib.error.HTTPError as error:
        return 0 if error.code == 409 else 1


if __name__ == "__main__":
    raise SystemExit(main())
