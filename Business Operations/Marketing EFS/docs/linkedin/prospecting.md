# ElectroFit LinkedIn prospecting

## Account and scope

The user selected company pages followed as ElectroFit Systems, https://www.linkedin.com/company/efitsys/. Never substitute a personal profile or the Nova Energia identity. Discover and qualify businesses that could buy ElectroFit products or engineering services. Following a company does not establish a customer relationship, buying intent, or consent to contact.

The user's standing workflow, agreed 30 September 2026, is to research up to 10 new potential customer companies in Italy each Monday at 09:00 Europe/Rome, send the exact shortlist to both Francesco Lucherini and Mohammad Taffal through Teams, and follow only after either one explicitly approves. This supersedes the previous direct-follow default. One verified approval is sufficient; do not require both approvals or another confirmation from the requester. Research-only requests remain read-only. Creating or editing the skill does not itself execute follows or send an empty approval request.

Read [Weekly review and Teams approval](#weekly-prospect-review-and-execution) below for the exact recipients, destination, revision binding, state and scheduler workflow. Approval-request messages to both people are authorized. No outreach to prospects, connection invitations, comments, likes, follower invitations, unfollows or post publishing are implied.

## Prospect criteria

Use current user criteria first. The scheduled scope is up to 10 new qualified companies in Italy per week; do not expand to Europe to fill the quota. Target vehicle OEMs, specialist manufacturers and vehicle integrators in road vehicles and quadricycles, agricultural machinery, municipal/service vehicles, material handling and small marine craft. Ten is a workflow batch size, not a LinkedIn limit.

Look for plausible need for integrated electric drives, modular batteries, power distribution, vehicle/powertrain controls, charging integration, or powertrain engineering and validation support. Check current company materials before claiming specific ElectroFit capabilities. If the efs-linkedin-content skill is available, its company brief and input can inform fit; do not run its drafting, Teams or publishing workflow.

Prefer manufacturers and integrators with evidence of relevant vehicle products or electrification programs. Classify distributors, suppliers, competitors, associations and media separately; do not follow them as potential customers without a specific buyer rationale or user instruction. Consumer owners and hobbyists are outside this B2B brief. Existing customers, rejected prospects and user exclusions should be skipped when known; missing CRM access must not become a claim that a company is new.

## Discover and qualify

Use available authorized search tools, public company websites and accessible LinkedIn pages. Search in English and Italian, combining an application with terms such as manufacturer, OEM, electric, costruttore, veicoli speciali, macchine agricole or movimentazione. Public web searches such as `site:linkedin.com/company/` can discover pages; search snippets alone are insufficient evidence for a follow.

Verify that the LinkedIn page matches the business using its website/domain, products and location. Prefer a LinkedIn link from the official company website. Resolve parent/subsidiary duplicates deliberately; remove tracking parameters from page URLs and retain known organization IDs. Do not invent page slugs or infer a legal entity from a similar name.

For each candidate record concrete evidence of sector, operating geography, and plausible purchasing use case, with source URLs and checked date. Mark unknowns explicitly. Separate factual observations from sales hypotheses. A company's electric product is evidence of relevance, not evidence it intends to purchase our components.

Assign a reasoned qualification:
- `high`: verified company identity, target market and application, plus concrete product/project evidence supporting a plausible purchase use case.
- `medium`: relevant business but important fit evidence remains missing; retain for review.
- `low`: weak fit or an exclusion; retain the reason if needed to avoid rediscovery.

Put high-fit candidates in the actionable approval shortlist. Keep medium/low-fit research separate. Follow only the exact approved candidates, after verifying identity and current following state. Return fewer results when evidence is insufficient; do not fill a quota with weak matches.

## Execute follows

First verify the current batch revision and original Teams approval as described in the linked workflow. Before following, check all recorded review messages for changes, withdrawals or unresolved objections. Approval covers only the identified companies and ElectroFit actor. If execution is blocked, retain `approved_pending_follow` and retry on the next monitor run without seeking the same approval again.

Check tools and account access at run time. The existing efs-linkedin publisher stages and publishes posts; it does not supply prospect search or follow operations. Publishing API access is not proof of follow permissions. Never guess an API endpoint or reuse credentials outside their configured integration.

Prefer an available authorized integration that explicitly supports company-to-company following. Otherwise, if browser control is available, load its applicable computer-use instructions and use the observed LinkedIn Page admin interface. Verify the active identity is ElectroFit Systems before any change. Do not assume a generic Follow button on a company profile acts as the company Page.

LinkedIn's [company following help](https://www.linkedin.com/help/linkedin/answer/a1398264), checked 2026-09-30, documents Page admin Settings > Manage following > Add Pages to follow. Treat this as navigation guidance; inspect the current UI and recheck help if it differs. A verified super admin or content admin can follow another Page on behalf of the organization. This documented UI does not establish API availability.

Check whether ElectroFit already follows each target. Skip existing follows. Stage only the authorized qualified targets, preserving all existing selections. Verify company names and identities before committing the selection. Confirm the resulting following state as ElectroFit through a fresh UI observation or supported API read; a click or success toast alone is not sufficient when the target/actor remains ambiguous.

If a request times out or the outcome is uncertain, read the actual state before retrying; never blindly toggle Follow/Following. Stop the batch on an account challenge, access restriction, rate limit, wrong identity or lost authorization. Do not bypass challenges, use hidden LinkedIn endpoints, scrape session tokens, or invent a safe daily limit. Preserve completed results and explain the precise remaining blocker. If execution is unavailable, return a qualified queue with direct links for manual following, without claiming completion.

## History and result

Use an existing user-designated prospect register when available. Otherwise keep `output/linkedin/prospecting/prospects.json` in the current workspace, outside the installed skill. Read existing history before writing; update records without replacing other runs. Do not create or upload an external CRM or SharePoint register without user direction.

Record company name, canonical LinkedIn URL, website, country/region, segment, evidence and dates, fit level and rationale, exclusions/unknowns, actor Page URL, and action status. Distinguish `researched`, `qualified`, `excluded`, `awaiting_approval`, `changes_requested`, `rejected`, `approved_pending_follow`, `already_following`, `followed`, `blocked`, and `unverified`. Store batch/revision, approval evidence and request-delivery records separately under `output/linkedin/prospecting/batches/`. For attempted follows include timestamp, result evidence and any error. Deduplicate by actor plus canonical target URL or verified organization ID across completed, pending and rejected records; history never overrides a fresh state check before a follow. Retain only business information needed for qualification; do not collect personal contact data for this company-only workflow.

Return a compact linked table of company, country, application, fit reason and follow status. Report newly followed, already followed and pending counts separately. Flag uncertain results and provide the register path. Do not describe research as a live follow, or claim a persistent schedule merely because a skill exists.


## Weekly prospect review and execution

## Schedule and durable state

Workspace: Marketing EFS. Resolve prospecting paths relative to its root. This procedure is independent of the LLM; the optional installed skill supplies environment-specific access instructions.
Create `output/linkedin/prospecting/batches/` on the first review request if absent. Use `output/linkedin/prospecting/prospects.json` for cumulative company history, `output/linkedin/prospecting/batches/` for immutable review revisions and approval evidence, and `output/linkedin/prospecting/schedule.json` for installed automation IDs and schedule metadata. Do not store operating history in the skill installation.

The user selected Monday 09:00 Europe/Rome for discovery. A separate approval monitor checks hourly at 09:00 through 18:00 Europe/Rome every day. These are local wall-clock schedules, including daylight-saving changes, not fixed UTC offsets. Check schedule.json for current installed settings. The scheduler, not this file, provides wakeups. Do not create duplicate automations on ordinary runs, automatically resume paused schedules, or alter the unrelated LinkedIn post-preparation automation.

The weekly run creates at most one new batch per ISO week, with a stable ID such as EFS-PROSPECTS-2026-W41. Resume partial preparation or delivery for the same week instead of making duplicates. A late run prepares at most the current due week's batch; do not issue a backlog of missed lists. Older pending reviews remain pending and their companies are excluded from new batches. Previously followed companies, including the ten followed on 30 September 2026, are historical completions and need no retroactive approval.

Monitor runs inspect pending work only; they do not discover additional prospects or resend unchanged requests. If there is no pending review or approved work, return quietly before accessing Teams or LinkedIn. On migration, treat exported completed follows as historical records, never as approval evidence for new actions. Recheck live following before any action. Read state freshly before each write, preserve other runs' changes, and use an exclusive workspace lock when runs could overlap. Stop on a live lock; investigate an orphaned lock rather than deleting it blindly. Store results after each company so partial runs resume safely.

## Recipients and destination

Verified through the Teams connector on 30 September 2026:

| Approver | Email | Microsoft Entra user ID |
| --- | --- | --- |
| Francesco Lucherini | francesco.lucherini@efitsys.com | 5c179398-bc3c-42e2-8e34-8e71e6a92623 |
| Mohammad Taffal | mohammad.taffal@efitsys.com | 3d408740-7689-459f-b0d5-4f81b783743e |

Resolve approval destinations using the operations colleague's connected Teams account. Do not reuse the originating owner's private chat ID. Prefer an existing group containing only the sender, Francesco and Mohammad. Otherwise use verified existing individual chats with each approver. Resolve exact emails and verify membership before sending. If suitable chats do not exist, ask the operator to establish them or explicitly authorize creation; never send to a broader group. Save verified destinations in `output/linkedin/prospecting/teams-destinations.json` in the project, not in the installed skill.

When using two chats, send the identical batch/revision to both and record delivery separately. Monitor both chats and consider objections from either person. One verified approval from either person remains sufficient after the complete list is delivered to both. If a delivery is missing, retry only that delivery. Never silently treat a one-recipient request as delivered to both. Re-resolve destinations when account or tenant changes.

## Prepare and send a concrete request

Before discovery, read the register and pending batches. Check current LinkedIn following when available. A browser outage need not prevent research or review delivery: explicitly say current following is unverified and recheck before executing.

Store an immutable JSON review payload containing batch ID, revision, ISO week, actor Page URL/organization ID 103544667, and numbered company entries with stable target URLs/IDs, city/country, segment, qualification, evidence URLs/check dates and a specific fit rationale. Hash the exact UTF-8 payload bytes with SHA-256 and retain the full hash. Hash only immutable review content; keep send/approval/execution metadata in a separate record. Never overwrite a sent revision.

Send the complete numbered list directly in a Teams message using the Teams connector. Include each company's LinkedIn link, Italian location, application, concise fit reason and source link. Approvers must be able to review the actual list without workstation/localhost links. Include the actor, batch ID, revision and fingerprint. For a long package, split it into numbered parts and record all message IDs; request approval only when all parts are delivered to both recipients. Do not upload files to an external register or change sharing permissions as an implicit part of this workflow.

Example closing text, adapted to the real package:

> Ciao Francesco e Mohammad, ecco i potenziali clienti italiani della settimana [batch], revisione [N]. Propongo di seguire queste pagine come ElectroFit Systems, https://www.linkedin.com/company/efitsys/. Sono opportunita da qualificare commercialmente, non clienti confermati. E sufficiente l'approvazione di uno di voi: rispondete "APPROVO [batch] rev [N]" oppure indicate i numeri delle sole aziende approvate o le modifiche richieste. Il follow verra eseguito dopo verifica dell'approvazione al prossimo controllo programmato. Riferimento revisione: [hash].

Record chat/message IDs, exact sent body, timestamps, recipient coverage, fingerprint and any returned canonical message paths. If a send times out, read the chat for that batch/revision before retrying. Never duplicate a delivered revision; retry only missing parts. If no new high-fit prospects are found, record the empty run and do not send an approval request for an empty list.

## Recognize approval

Read original messages using authenticated Teams tools, not copied text from local files or the browser. Match the author ID to either approved Entra ID. A clear approval of the exact batch/revision, or an unambiguous reply to that request, is sufficient. Do not require a magic phrase. Partial approval covers only identified entry numbers/companies; preserve unapproved entries as pending. Reactions, silence, forwarded assertions, messages from other users and conditional approval with unmet conditions are insufficient.

Because requests may be sent using an approver's connected account, author ID alone is not approval: exclude all agent-authored request/message IDs and never interpret approval examples quoted inside a request as a decision. The approval must be a separate human response to the submitted review.

Read all relevant messages since the request, including pagination, so a later objection or withdrawal is not missed. If the tool truncates a busy conversation, narrow the time window or fetch original messages before deciding. Keep the canonical approval message path/ID, author ID, timestamp, exact decision, approved targets and payload hash. These fields describe evidence; they do not replace rereading its source.

Either approver can authorize the list; do not wait for both. A known unresolved objection, requested change or withdrawal from either person blocks the affected entries. Resolve a conflict rather than selecting whichever message is convenient. Immediately before execution, reread the original approval and subsequent relevant replies, verify the immutable payload hash, and ensure the approval is still applicable. Deleted, edited-to-withdraw or unresolvable approval evidence cannot authorize a new follow.

Changing reviewed targets, actor, or substantive qualification/rationale creates a new revision and requires a fresh request and approval. Skipping a company already followed does not invalidate approval for the remaining unchanged targets. Never substitute another company to make up ten after approval. Retain rejected entries and reasons to avoid repeatedly proposing them without new evidence or user direction.

## Execute and report

A verified approval provides standing authorization to follow that exact approved set as ElectroFit, without another user confirmation. Use the main skill's account, browser/API and duplicate checks. Record `approved_pending_follow` if login, browser connection, permissions or an account challenge blocks execution. Retry only pending approved entries on subsequent monitor runs; never blindly repeat an uncertain action. Do not unfollow previously completed actions in response to a later withdrawal without an explicit unfollow request.

Keep a per-company result and verification evidence, including screenshots where required by browser tooling. Update batch progress and cumulative history atomically where practical. Mark a batch complete only when every approved entry is verified followed or already following and no unresolved review remains; otherwise retain partial/pending state. Notify in this chat when a review list is sent, an approval materially changes status, follows complete, or user action is needed. Stay quiet when nothing changes; deduplicate blocker notices. Do not send extra Teams reminders or completion messages unless requested.

Local runs require the computer awake and desktop app running, plus working Teams access and the signed-in browser for follows. These scheduled checks are polling, not a Teams webhook or a guarantee of instant execution. If a scheduled run cannot use a required tool, preserve state and report the specific limitation without weakening permissions.
