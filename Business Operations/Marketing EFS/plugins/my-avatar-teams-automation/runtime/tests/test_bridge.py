import base64
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bridge import Bridge, PENDING_TOOL, Rejected, STATUS_TOOL  # noqa: E402


class TestVault:
    def seal(self, value):
        return json.dumps(value).encode()

    def open(self, value):
        return json.loads(value)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        (self.root / "skills" / "sample").mkdir(parents=True)
        (self.root / "skills" / "sample" / "SKILL.md").write_text(
            "---\nname: sample\ndescription: Sample.\n---\n", encoding="utf-8")
        self.settings = {"bridge": {"eventName": "myavatar.message.ready",
                                     "callbackHosts": ["callback.example"]}}
        self.deliveries = []
        self.bridge = Bridge(self.root, self.settings, self.transport, TestVault(), lambda: 1000)
        os.environ["MYAVATAR_EVENT_SALT"] = "s" * 32

    def tearDown(self):
        self.bridge.db.close()
        self.temp.cleanup()
        os.environ.pop("MYAVATAR_EVENT_SALT", None)

    def transport(self, url, headers, body):
        payload = json.loads(body)
        if payload.get("type") == "verification":
            return 200, json.dumps({"challenge": payload["challenge"]}).encode()
        self.deliveries.append(payload)
        return 202, b"{}"

    def subscribe(self):
        secret = "whsec_" + base64.b64encode(b"a" * 32).decode()
        return self.bridge.subscribe({"name": "myavatar.message.ready",
            "arguments": {"queue": "verified_internal"},
            "delivery": {"mode": "webhook", "url": "https://callback.example/event", "secret": secret}})

    def test_status_and_skill_catalog(self):
        result = self.bridge.rpc("tools/call", {"name": STATUS_TOOL, "arguments": {}})
        self.assertFalse(result["structuredContent"]["autoReplyEnabled"])
        self.assertEqual(len(self.bridge.rpc("skills/list", {})["skills"]), 1)

    def test_ingress_requires_subscription_for_delivery(self):
        self.assertEqual(self.bridge.ingest({"conversationId": "c", "messageId": "m"}), 409)
        self.subscribe()
        self.assertEqual(self.bridge.ingest({"conversationId": "c2", "messageId": "m2"}), 202)
        self.assertEqual(len(self.deliveries), 1)
        arguments = self.deliveries[0]["arguments"]
        self.assertNotEqual(arguments["conversationId"], "c2")
        self.assertNotEqual(arguments["messageId"], "m2")

    def test_claim_requires_switch_and_is_once(self):
        self.subscribe()
        self.bridge.ingest({"conversationId": "conversation", "messageId": "message"})
        with self.assertRaises(Rejected):
            self.bridge.rpc("tools/call", {"name": PENDING_TOOL, "arguments": {}})
        (self.root / "config" / "auto-reply.enabled").touch()
        result = self.bridge.rpc("tools/call", {"name": PENDING_TOOL, "arguments": {}})
        payload = json.loads(result["content"][0]["text"])
        self.assertEqual(payload["claimState"], "claimed")
        with self.assertRaises(Rejected):
            self.bridge.rpc("tools/call", {"name": PENDING_TOOL, "arguments": {}})

    def test_rejects_message_content(self):
        with self.assertRaises(Rejected):
            self.bridge.ingest({"conversationId": "c", "messageId": "m", "text": "secret"})


if __name__ == "__main__":
    unittest.main()
