# Inputs approvals — original export and repair

The immutable original package is `EFSMarketingApprovalReliability_1_0_0_3.zip`.
It was exported from Microsoft Power Apps and downloaded in Microsoft Edge on
15 October 2026. Its ZIP integrity check passed.

- SHA-256: `a651b8b238bad1d7bd3ed9d8c74b3dd0a7a4e91b34b6fcd5c8d84e4ebcf89e14`
- Solution: `EFSMarketingApprovalReliability`, unmanaged.
- Solution ID: `3c29e105-9cc8-f111-a059-e4fb1ef6bee7`.
- Power Automate flow ID: `d566e7c1-4941-77a4-abcc-752887b781dc`.
- Dataverse workflow ID: `90ba7edd-9fc0-f111-aaad-70a8a57edd59`.
- Existing connection reference: `new_sharedsharepointonline_d0d97`.

The original package preserves the two original workflow nodes and the actual
Microsoft approver configuration. It contains no access token or credential.
`configuration-before-repair.json` is a historical configuration snapshot,
not a replacement for the exported workflow package.

Corrective packages must preserve workflow identity and the existing connection,
approvers and response rule. Never overwrite this original ZIP. A rollback to
the original workflow definition must use a newer solution manifest version if
Microsoft rejects importing a lower version.

Current deployment status and live evidence are recorded in
`../../input-approval-reliability.md` and
`output/Linkedin/config/input-approval-automation.json` from the project root.
An exported or locally validated package does not prove a live correction.

## Verified deployment

Version `1.0.1.1` is active and completed controlled live tests on 15 October.
Run `08584095333550505814206822293CU02` succeeded in 90 seconds and created
native requests for NON-USARE items 656 and 657. Their IDs are
`bff107bd-64cf-423b-be3e-87c25e2f09ca` and
`7a57df33-ca4a-4683-8d88-2d8be4d3a4fa`; the second dispatch started 32.21 seconds
after the first completed. Rerun `08584095332359662866147049326CU00` succeeded in
5 seconds with the same two IDs, one attempt per item and cursor 657.

The flow polls Inputs every 5 minutes, persists events and processes at most
3 requests serially per run. No human decision was submitted. These test files
are excluded from editorial sources. Real 429 injection, crash recovery and a
forced cursor replay were not tested; ambiguous results remain quarantined for
reconciliation. The 34 historical failed-run outputs were not all reconstructed.

The live package SHA-256 is
`3394feb45ef669825d78bcacaabb187352dffebd62add70d75e4faefff86404e`.
The rollback package `1.0.1.9` retains the original workflow JSON and changes
only the solution version. Use it only for an authorized rollback.
