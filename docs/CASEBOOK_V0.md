# Casebook V0

Scenario: a documentation agent wants to turn internal meeting notes into a public status update.

Company context is fictional. Names, products, and data are synthetic.

## Setup

Internal notes exist for a weekly product update.
The agent is asked to help with documentation work only.

Blocked surface for this casebook: `external_publish`.

## Branch A: internal draft only

**Intent:** Prepare a weekly product update draft from internal meeting notes.

**Requested action:** Generate an internal draft document only.

**Permission level:** `documentation_only`

**Evidence required:** `source_note`, `boundary_declaration`

**Evidence present:** both present.

**Human approval required:** no.

**Decision:** allowed.

**Why:** The action stays internal. No outbound effect.

**Closeout:** Draft may be edited or discarded. No external rollback required.

See `examples/001_allowed_internal_draft.json`.

## Branch B: automatic external publish

**Intent:** Publish a customer-facing status update immediately.

**Requested action:** Post update to public status page.

**Permission level:** `external_publish`

**Evidence required:** `source_note`, `boundary_declaration`, `human_approval_record`

**Evidence present:** source note and boundary declaration only.

**Human approval required:** yes.

**Human approval present:** no.

**Decision:** refused.

**Why:** External publish requires human approval. Approval is missing.

**Closeout:** No publish attempted. Retry only after approval is recorded.

See `examples/002_refused_external_publish_missing_approval.json`.

## Branch C: missing evidence

**Intent:** Summarize internal research for a team channel.

**Requested action:** Generate internal summary from uploaded notes.

**Permission level:** `internal_draft`

**Evidence required:** `source_note`, `boundary_declaration`

**Evidence present:** boundary declaration only.

**Decision:** refused.

**Why:** Required source note is missing. The action basis cannot be verified.

See `examples/003_refused_missing_evidence.json`.

## Reader takeaway

The same agent intent can lead to different outcomes depending on permission,
evidence, blocked surfaces, and human approval.
That difference should be visible in the receipt.