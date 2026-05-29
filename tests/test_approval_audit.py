from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _path  # noqa: F401
from lain_desk_agent.main import append_approval_event, approval_event_from_payload


class ApprovalAuditTests(unittest.TestCase):
    def test_approval_event_includes_expected_fields(self) -> None:
        event = approval_event_from_payload(
            {
                "decision": "approved",
                "proposal_id": "proposal_0001",
                "proposal": {
                    "proposal_id": "proposal_0001",
                    "action": {"type": "target_hint"},
                },
                "safety_decision": {"decision": "needs_approval"},
                "task": "Search",
            }
        )

        self.assertEqual(event["type"], "proposal.approved")
        self.assertEqual(event["proposal_id"], "proposal_0001")
        self.assertEqual(event["task"], "Search")
        self.assertIn("timestamp", event)

    def test_reject_event_can_be_appended_to_jsonl(self) -> None:
        event = approval_event_from_payload(
            {
                "decision": "rejected",
                "proposal_id": "proposal_0002",
                "proposal": {
                    "proposal_id": "proposal_0002",
                    "action": {"type": "target_hint"},
                },
                "safety_decision": {"decision": "needs_approval"},
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            append_approval_event(event, run_dir=temp_dir)
            events_path = Path(temp_dir) / "events.jsonl"
            written = json.loads(events_path.read_text(encoding="utf-8").strip())

        self.assertEqual(written["type"], "proposal.rejected")
        self.assertEqual(written["proposal_id"], "proposal_0002")

    def test_invalid_decision_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            approval_event_from_payload(
                {
                    "decision": "clicked",
                    "proposal_id": "proposal_0003",
                    "proposal": {},
                    "safety_decision": {},
                }
            )


if __name__ == "__main__":
    unittest.main()
