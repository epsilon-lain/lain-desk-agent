from __future__ import annotations

import unittest
from pathlib import Path

import _path  # noqa: F401


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE9_DOC = PROJECT_ROOT / "docs" / "PHASE_9_MINIMAL_SANDBOX_EXPERIMENT_DESIGN.md"
ROADMAP_DOC = PROJECT_ROOT / "docs" / "ROADMAP.md"
ARCHITECTURE_DOC = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
PHASE7_DOC = PROJECT_ROOT / "docs" / "PHASE_7_SANDBOX_ACTION_DESIGN.md"


class Phase9DesignDocTests(unittest.TestCase):
    def test_phase9_design_doc_exists_and_is_design_only(self) -> None:
        text = PHASE9_DOC.read_text(encoding="utf-8")

        for required in [
            "Phase 9 is a design-only specification",
            "dry-run simulation",
            "`dry_run = true` by default",
            "`real_action_enabled = false` by default",
            "`real_action_attempted = false`",
            "`real_desktop_actions = false`",
            "does not implement real desktop control",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_phase9_design_selects_minimal_sandbox_subset(self) -> None:
        text = PHASE9_DOC.read_text(encoding="utf-8")

        for scenario_id in [
            "dry_run_success_all_gates_pass",
            "real_action_disabled_skips_non_dry_run",
            "missing_user_approval_blocks",
            "stale_observation_blocks",
            "high_risk_target_blocks",
            "missing_audit_plan_blocks",
            "missing_action_contract_blocks",
        ]:
            with self.subTest(scenario_id=scenario_id):
                self.assertIn(scenario_id, text)

    def test_phase9_design_requires_phase7_gate_blockers(self) -> None:
        text = PHASE9_DOC.read_text(encoding="utf-8")

        for blocker in [
            "Missing audit plan blocks",
            "Missing action contract blocks",
            "High-risk target blocks",
            "Stale observation blocks",
            "Missing user approval blocks",
            "Missing post-action verification blocks",
            "Missing emergency stop blocks",
            "Invalid geometry blocks",
        ]:
            with self.subTest(blocker=blocker):
                self.assertIn(blocker, text)

    def test_phase9_design_preserves_phase8_report_fields(self) -> None:
        text = PHASE9_DOC.read_text(encoding="utf-8")

        for field in [
            "scenario_id",
            "scenario_name",
            "expected_outcome",
            "actual_outcome",
            "failure_reason_codes",
            "blocker_codes",
            "audit_event_names",
            "dry_run",
            "real_action_enabled",
            "real_action_skipped",
            "post_action_verification_planned",
            "target_risk_hint",
            "target_confidence",
            "readiness_ready",
            "action_type",
            "trace",
        ]:
            with self.subTest(field=field):
                self.assertIn(f"- `{field}`", text)

    def test_phase9_design_defines_mock_hooks_and_rollback(self) -> None:
        text = PHASE9_DOC.read_text(encoding="utf-8")

        for required in [
            "mock_user_approval",
            "mock_emergency_stop",
            "mock_post_action_verification",
            "Rollback And Emergency Stop",
            "Do not simulate an action completion",
            "Mock emergency stop active means block",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_phase9_design_forbids_real_action_paths(self) -> None:
        text = PHASE9_DOC.read_text(encoding="utf-8")

        for required in [
            "No OS mouse movement",
            "No OS click",
            "No typing",
            "No hotkey",
            "No scrolling",
            "No app switching",
            "No `/execute` call",
            "No actuation adapter call",
            "Do not modify Execution Policy, Permission Profile, Capability Registry",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_existing_docs_reference_phase9_design(self) -> None:
        docs = {
            "roadmap": ROADMAP_DOC.read_text(encoding="utf-8"),
            "architecture": ARCHITECTURE_DOC.read_text(encoding="utf-8"),
            "phase7": PHASE7_DOC.read_text(encoding="utf-8"),
        }

        for name, text in docs.items():
            with self.subTest(doc=name):
                self.assertIn("Phase 9", text)
                self.assertIn("dry-run", text)
                self.assertIn("real_action_enabled", text)
                self.assertIn("not execution permission", text)


if __name__ == "__main__":
    unittest.main()
