#!/usr/bin/env python3
"""Read-only local validator for public Agent Decision Receipt examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = [
    "receipt_id",
    "agent_intent",
    "requested_action",
    "permission_level",
    "blocked_surfaces",
    "evidence_required",
    "evidence_present",
    "human_approval_required",
    "human_approval_present",
    "decision",
    "decision_reason",
    "external_effect",
    "closeout",
]

PERMISSION_LEVELS = {"documentation_only", "internal_draft", "external_publish"}
DECISIONS = {"allowed", "refused"}
BLOCKED_SURFACES = {"external_publish", "credential_access", "filesystem_write"}
RECEIPT_ID_PREFIX = "ADR-EXAMPLE-"


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def validate_receipt(receipt: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(receipt, dict):
        return ["receipt must be a JSON object"]

    for field in REQUIRED_FIELDS:
        if field not in receipt:
            errors.append(f"missing required field: {field}")

    extra = set(receipt) - set(REQUIRED_FIELDS)
    if extra:
        errors.append(f"unexpected fields: {sorted(extra)}")

    receipt_id = receipt.get("receipt_id")
    if isinstance(receipt_id, str):
        suffix = receipt_id[len(RECEIPT_ID_PREFIX) :]
        if not receipt_id.startswith(RECEIPT_ID_PREFIX) or len(suffix) != 3 or not suffix.isdigit():
            errors.append("receipt_id must match ADR-EXAMPLE-NNN")

    permission_level = receipt.get("permission_level")
    if permission_level not in PERMISSION_LEVELS:
        errors.append("permission_level invalid")

    for list_name in ("blocked_surfaces", "evidence_required", "evidence_present"):
        if list_name in receipt and not _is_string_list(receipt[list_name]):
            errors.append(f"{list_name} must be a list of non-empty strings")
        elif list_name == "blocked_surfaces" and _is_string_list(receipt.get(list_name)):
            unknown = set(receipt[list_name]) - BLOCKED_SURFACES
            if unknown:
                errors.append(f"blocked_surfaces contains unknown values: {sorted(unknown)}")

    decision = receipt.get("decision")
    if decision not in DECISIONS:
        errors.append("decision must be allowed or refused")

    if "human_approval_required" in receipt and not isinstance(receipt["human_approval_required"], bool):
        errors.append("human_approval_required must be boolean")

    hap = receipt.get("human_approval_present")
    if hap is not None and not isinstance(hap, bool):
        errors.append("human_approval_present must be boolean or null")

    if "external_effect" in receipt and not isinstance(receipt["external_effect"], bool):
        errors.append("external_effect must be boolean")

    for text_field in ("agent_intent", "requested_action", "decision_reason", "closeout"):
        value = receipt.get(text_field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{text_field} must be a non-empty string")

    if (
        decision == "allowed"
        and receipt.get("human_approval_required")
        and receipt.get("human_approval_present") is not True
    ):
        errors.append("allowed receipt with human_approval_required must have human_approval_present true")

    if decision == "refused" and receipt.get("external_effect") is True:
        errors.append("refused receipt must not have external_effect true in this teaching skeleton")

    return errors


def validate_file(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            receipt = json.load(handle)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    prefix = f"{path.name}: "
    return [prefix + err for err in validate_receipt(receipt)]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    examples_dir = root / "examples"
    if not examples_dir.is_dir():
        print(f"examples directory not found: {examples_dir}", file=sys.stderr)
        return 1

    paths = sorted(examples_dir.glob("*.json"))
    if not paths:
        print("no example receipts found", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for path in paths:
        all_errors.extend(validate_file(path))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        print(f"FAIL: {len(paths)} checked, {len(all_errors)} error(s)", file=sys.stderr)
        return 1

    print(f"PASS: {len(paths)} example receipt(s) validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())