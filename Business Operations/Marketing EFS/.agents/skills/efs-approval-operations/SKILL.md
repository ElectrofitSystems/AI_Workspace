---
name: efs-approval-operations
description: Diagnose and maintain ElectroFit Marketing Inputs approval automation in Power Automate, including throttling, durable queues, duplicate prevention and recovery. Use for approval flow failures or reconciliation, not content approval or publishing.
---

# EFS approval operations

Use the canonical workspace
`C:/Users/Operations/Documents/AI_Workspace/Business Operations/Marketing EFS`.
Read `docs/maintenance/input-approval-reliability.md` for the current repair
procedure and deployment status, then `docs/company/marketing-input-folder.md`
and `docs/company/input-approvals.md` for revision and approval boundaries.
For derivative review packages read `docs/maintenance/teams-approvals.md`;
an Inputs failure does not authorize changes to the Outputs flow.

Diagnose from the actual Microsoft run and nested error body. Record observed
flow/run IDs, item and revision, service status and coverage. An outer 502 can
contain SharePoint 429. Never infer missing approvals from the email failure
count or a failed run alone.

For authorized repairs, preserve the current configuration and implement the
canonical durable-queue/serial-worker design. The installed design is one
five-minute Scheduled flow with serial acquisition and dispatch stages, not two
independent sending flows. Dispatch is bounded to three queued rows per run,
30-second spacing, a 15-minute lease and five attempts maximum. Expired
processing rows become `unknown`; unknown rows are never automatically resent.
Read current deployment/test status and evidence from the canonical procedure;
controlled success is not a promise that future failures cannot occur. Separate
live observations from structural tests and untested crash/429 recovery paths.
Do not provoke real throttling to demonstrate recovery. Check authoritative request state
before retries; use Retry-After/backoff and bounded recovery. A create timeout,
5xx or unreadable service remains `unknown` until reconciled. Do not blindly
resubmit or enable automatic retries on a non-idempotent create action.

Recover only verified missing requests for the exact relevant revision/scope.
Keep approvers and response rules in the existing Microsoft configuration;
do not copy identities from past receipts into code or choose new recipients.
Never approve as the agent or treat a queue/cache status as a human decision.

Verify saved/live configuration and observable request IDs before reporting a
cloud correction as active. Distinguish local validation, simulation and live
evidence. If access is missing, complete the reviewable local repair specification
and report `pending_verification` with the concrete remaining step. Preserve
originals, history and existing editorial schedules. This skill grants no extra
publication, messaging, access-management or deployment permissions.
