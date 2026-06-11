import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "validator" / "validate_receipts.py"
EXAMPLES = ROOT / "examples"


def load_validate_receipt():
    spec = importlib.util.spec_from_file_location("validate_receipts", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.validate_receipt


class ValidateReceiptsTest(unittest.TestCase):
    def test_examples_validate_cleanly(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_allowed_example_is_allowed(self):
        data = json.loads((EXAMPLES / "001_allowed_internal_draft.json").read_text(encoding="utf-8"))
        self.assertEqual(data["decision"], "allowed")
        self.assertFalse(data["external_effect"])

    def test_refused_publish_missing_approval(self):
        data = json.loads(
            (EXAMPLES / "002_refused_external_publish_missing_approval.json").read_text(encoding="utf-8")
        )
        self.assertEqual(data["decision"], "refused")
        self.assertTrue(data["human_approval_required"])
        self.assertFalse(data["human_approval_present"])
        self.assertFalse(data["external_effect"])

    def test_refused_missing_evidence(self):
        data = json.loads((EXAMPLES / "003_refused_missing_evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(data["decision"], "refused")
        missing = set(data["evidence_required"]) - set(data["evidence_present"])
        self.assertTrue(missing)

    def test_refused_with_external_effect_is_rejected(self):
        validate_receipt = load_validate_receipt()
        receipt = {
            "receipt_id": "ADR-EXAMPLE-099",
            "agent_intent": "Attempt an external publish without approval",
            "requested_action": "Post update to public status page",
            "permission_level": "external_publish",
            "blocked_surfaces": [],
            "evidence_required": ["source_note", "boundary_declaration", "human_approval_record"],
            "evidence_present": ["source_note", "boundary_declaration"],
            "human_approval_required": True,
            "human_approval_present": False,
            "decision": "refused",
            "decision_reason": "External publish requires human approval; approval not present",
            "external_effect": True,
            "closeout": "No publish attempted; agent may retry after approval is recorded",
        }
        errors = validate_receipt(receipt)
        self.assertTrue(
            any(
                "refused receipt must not have external_effect true in this teaching skeleton" in err
                for err in errors
            )
        )


if __name__ == "__main__":
    unittest.main()