# Marks migration: legacy behavior and acceptance

Source baseline: `a492604` on `prototype/railway`. This document describes the
supported chapter workflows, defects to correct, and unresolved legacy policy.
It is the implementation/review contract; tests are evidence, not its definition.

## Source map

| Source | Responsibility |
| --- | --- |
| `models.py` | Requester, recipient, signed integer value, reason (100 characters), event/submission dates, requested/approved/denied state, decision and editor audit. No mark-category enumeration. |
| `urls.py` | `/newmember/` public resources, `marks/`, `request/`, `approve/`, `history/<user>/`, `edit/<mark>/`, `export-newmember-marks/`. |
| `views.py:newmember_request`, `views_functions.py:create_mark_requests` | ACTIVE submission, multi-recipient batch, session requester, board auto-approval. |
| `templates/newmember_marks_request.html` | Required recipient selector, signed whole number, date and reason; editing is single-recipient; explicit edit-deny confirmation. No future-date restriction or prescribed mark amounts. |
| `views.py:newmember_approve`, `views_functions.py:process_mark_approval` | NM_BOARD review; queue contains pending requests; approve and deny both available. |
| `views.py:newmember_edit_mark` | NM_BOARD edit/retarget; preserve requester, state and decision audit; record editor/time. Explicit deny additionally requires NME and updates both audits. |
| `views_functions.py:get_personal_stats`, `calculate_member_marks`, `get_active_member_analytics` | Approved-only signed totals, standing at zero, class average, global seven-day count and pending count. |
| `views_functions.py:get_user_submitted_marks` | Requester's pending and denied entries; denied entries older than 14 days by event date excluded. Old “month” comment is wrong. |
| `views.py:newmember_mark_history`, `templates/newmember_marks_history.html` | Current NEW_MEMBER recipient, approved history, requester/reason/value/date, edited marker and board edit link. |
| `views.py:export_approved_newmember_marks`, dashboard templates | Current-role or historical-class XLSX, approved rows, oldest first, signed totals. NEW_MEMBER cannot select historical classes, including dual-role board members. |
| `api.py`, `AUTHENTICATE/api_session.py` | Existing React dashboard read boundary/capabilities; NEW_MEMBER personal precedence over ACTIVE, board-only review mode, ALUMNI/roleless denial. |
| `test/regression-spec.md`, `test/cases/`, `test/test_*.py` | Frozen supported cases plus explicitly unapproved defects/policy questions; blocked cases are not passing coverage. |

All paths above are relative to `SPDWEBAPP/NEWMEMBER` unless otherwise noted.
No local Django Form exists at baseline: handlers parse raw POST. There are no
initiation thresholds, mark “types,” attendance rules or per-reason point tariffs.

## Roles and supported screens

Roles are independent; EXEC or NME alone does not imply ACTIVE or NM_BOARD.

| Actor | Dashboard/history | Create | Review | Edit/revoke | Export |
| --- | --- | --- | --- | --- | --- |
| Anonymous/missing profile | Denied safely | Denied | Denied | Denied | Denied |
| NEW_MEMBER | Own approved history/standing; class average | No, unless also ACTIVE | Only if also NM_BOARD | Only if NM_BOARD; explicit revoke also NME | Current class only, including dual roles |
| ACTIVE | Class approved totals, current-recipient history, own submissions | Yes; pending | Only if also NM_BOARD | Only if NM_BOARD; revoke also NME | Current and existing historical classes |
| NM_BOARD only | Existing limited review mode; current-recipient history for review | No without ACTIVE | Pending approve/deny | Edit; revoke additionally NME | Current/historical |
| ACTIVE + NM_BOARD | Active dashboard | Auto-approved, decision identity/time recorded | Pending approve/deny | Edit; revoke additionally NME | Current/historical unless NEW_MEMBER also present |
| ALUMNI, roleless, EXEC-only, NME-only | Current React marks boundary denies access | No | No | No | No new REST capability granted |

Legacy history/export handlers use login-only gates in places, exposing more than
the React domain boundary. That is a visibility ambiguity, not evidence that all
roles should gain a new REST disciplinary-record API. The migration keeps the
existing React role boundary; NEW_MEMBER personal history is self-only, ACTIVE
and board can inspect current new-member histories. The explicit legacy Current
class export for NEW_MEMBER is retained. Broader alumni/roleless access is not
introduced. The old public resources landing remains public.

## Submission and validation

1. ACTIVE selects one or more **current NEW_MEMBER** recipients, a signed integer,
   date and nonblank reason of at most 100 characters. These are the offered HTML
   controls and model contract. Zero, negative and positive values remain valid;
   no arbitrary point range, future-date prohibition or category is invented.
   Enforce the database-supported signed integer range and reject fractions.
2. New rows fix requester from session; client status, approver and editor fields
   cannot set audit/state. ACTIVE+NM_BOARD creates approved rows with real actor
   and time; other ACTIVE submissions are pending. No new self-review ban is
   invented: board creation explicitly auto-approves in the original code.
3. Validate every recipient and field before writing any row. Empty, duplicate,
   nonexistent or ineligible recipient IDs are invalid; the normal HTML multiple
   selector cannot produce duplicates. A failed batch writes nothing.
4. Each form keeps an operation UUID through timeout/retry. Reusing it with the
   same validated payload returns the original batch; changing the payload under
   that key conflicts. New intentional submissions use a new key. Do not use
   reason/date deduplication that could suppress legitimate repeated events.
5. Show pending submission, prevent simultaneous duplicate clicks, retain fields
   on failure/interrupt and show success only after acknowledgement. Dirty forms
   require confirmation before leaving. Never auto-retry a mutation.

## Review and editing

- The review queue is NM_BOARD-only, not EXEC/ACTIVE-only. The legacy ACTIVE
  dashboard advertises Review Pending Marks to unauthorized users; fix that UI
  affordance instead of copying it into React.
- Queue actions accept only approve/deny and only pending records. Decision audit
  comes from the real reviewer. Repeating the same decision is an unchanged
  acknowledgement; a competing opposite decision conflicts and refreshes the
  queue. Crafted repeat/reverse POSTs are not an override workflow.
- NM_BOARD edits reason, signed value, date and one eligible recipient, including
  others' records. Keep requester, status and original decision audit; add editor
  identity/time. Validate before saving; missing/invalid resources do not mutate.
- Explicit **revoke/deny from edit** remains NM_BOARD **and** NME, distinct from
  denying a pending request. Preserve the existing warning/confirmation and both
  audit updates. This is the supported override route; other reversals remain
  unavailable. Do not silently unify the two deny permissions.
- Concurrent decisions must not overwrite each other's audit. Edits use an
  expected record revision so a stale form cannot silently replace a newer edit
  or review. Preserve unchanged fields; no delete workflow is introduced.

## Reads, history and export

- Count only approved records. A total >=0 is Good Standing; negative means
  Needs Improvement. Requested/denied never affect totals or approved history.
- Keep NEW_MEMBER personal precedence for dual roles. Active class totals keep
  the legacy ascending-total/roster ordering. Own pending
  and recent-denied submissions keep the actual 14-day event-date rule.
- Histories show actual recipient, requester, reason, signed value/date, reviewer
  and editor metadata where available. Do not synthesize old missing audit.
  Current-role eligibility matches legacy history; historical classes remain an
  export workflow rather than fabricated current recipients.
- Export approved marks for Current or a valid existing class. Preserve sheet
  name, four columns per member, signed numeric marks and totals, chronological
  rows, filename/MIME. Keep distinct people separate even if their names match;
  write names/reasons as literal strings so spreadsheet formulas never execute.
  Workbook failures return a clear error without saving a partial artifact.

## Architecture and acceptance

Shared domain operations own validation, role checks, atomic writes and audit.
HTML URL/view adapters retain `/newmember/...`; REST packages own
`/api/v1/new-members/...`; React owns `/app/new-members/...`. No duplicated
business implementation in serializers/components. Both interfaces use the same
records; every React workflow has a discreet contextual Legacy comparison link.
Submission, review, editing, history and export must work in React rather than
requiring a legacy handoff. Public resources may still link to the legacy page.

Browser acceptance uses fictional personas/records: ACTIVE batch submission ->
legacy pending queue -> board React decision -> new-member React/legacy totals;
board auto-approved signed submission; retarget/edit preserves audits; educator
revoke changes totals/history; current/historical export downloads; eligible and
denied direct routes; repeated/held/failed submissions; dirty cancel/back/reopen;
review conflicts and stale edit conflicts; desktop and 390px navigation/errors.
Verify stored values and both adapters, not only toasts or screenshots. Existing
poll/service flows must still work. Backend contracts cover forged identity,
invalid fields/targets/CSRF, atomicity, operation-key replay, audit preservation,
role conjunctions and parsed workbook cells. Record blocked/live checks honestly.

## Scope and unresolved legacy questions

This implementation preserves supported role workflows and adds integrity fixes;
it does not resolve all old Wave 1 policy questions. Unrestricted crafted history
URLs, arbitrary retargets, empty/duplicate batches, unknown action success, raw
exceptions/500s, formula exports, name-based merging and stale audit overwrites
are defects to harden, not promises to preserve. Broadening visibility, granting
new roles, general reverse decisions, changing point tariffs or changing
self-review/auto-approval policy requires an explicit chapter decision. Existing
Django admin permissions remain unchanged. Service-recipient assignment is a
separate unanswered question and does not block marks work.

## Verified local delivery

The completed implementation is verified locally, not yet independently verified
on Railway. Real browser workflows passed against both synthetic Django and the
built image, including poll/service regressions. The marks flows covered ACTIVE
batch -> legacy approval -> React denial/member totals; board auto-approval,
retarget/edit preserving decision audit, stale edit conflict/reload, educator
revocation, Current/historical workbook download and interrupted acknowledgement
replay without duplicate rows. A separate browser walkthrough inspected desktop
and390px pixels, real stored state and corresponding legacy history; no page errors
or overflow were observed. Manually downloaded workbooks excluded revoked records.

Backend audit:510passed,393/393READY mappings retained;13mutation probes caught
and restored;13demo checks and5file-tree checks passed. Type/build, formatting,
system checks, migration drift and schema validation passed. Browser suite:67
passed separately on Django and Docker. Logs/screenshots remain runtime-local in
`/workspace/work/marks-*`; screenshots and demo records are not repository data.
The built image serves index-CuIKHL9y.js and index-Dr7Nt-zZ.css.

Migration0004adds MarkSubmission and nullable event.submission; existing marks and
amounts are unchanged. Replay data is scoped by authenticated requester and key.
This is the existing disposable demo; no production database, service assignment
policy, credentials or Railway settings were changed. NM_BOARD-only and NME-only
role conjunctions are additionally covered by real HTTP/ORM tests; the browser
personas expose combined executive/board/educator Alex, ACTIVE Jordan, NEW_MEMBER
Cameron and ALUMNI Hayden. Live coordinator verification remains a separate gate.
