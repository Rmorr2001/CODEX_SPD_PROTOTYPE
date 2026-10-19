# Read Models case designs

Use [the shared fixture contract](../../../../docs/testing/fixture-contract.md) and
[local fixture vocabulary and scope rules](../regression-spec.md#local-fixture-vocabulary).
All fixtures are created independently inside each case; none carry from earlier cases.
Non-admin relative routes in blocks are under `/newmember/`.
[Source, defects and decisions](../regression-spec.md) supply the linked policy gates.

### NM-05-01a — test_signed_class_totals_and_order_exclude_unapproved

Parent: `NM-05-01` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:9–43`

```text
GIVEN NEW_MEMBER T1/T2/T3 named Able/Baker/Zed and ALUMNI B
  AND T1 approved +5/-8 on Oct14/Oct16, T2 approved 0, T3 no marks
  AND requested/denied +99 for T1 and approved +90 for B
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN get_new_members() and calculate_member_marks(members) run
THEN source members are T1,T2,T3 by last name; progress totals are -3,0,0
  AND full_name values are exactly "T1 Able", "T2 Baker", "T3 Zed"
  AND is_negative is True,False,False and tie retains supplied member order
  AND no B progress or unapproved value appears
  AND all named marks/users/profiles/roles and mark count remain unchanged
  AND assert_unchanged(before)
```

### NM-05-01b — test_personal_stats_use_approved_signed_totals

Parent: `NM-05-01` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:70–97`

```text
GIVEN NEW_MEMBER T1 approved +5 on Oct14 and -8 on Oct16
  AND NEW_MEMBER T2 approved 0, NEW_MEMBER T3 no marks, T1 requested +99 on Oct17
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN get_personal_stats(T1) and get_personal_stats(T2) run
THEN T1 total=-3,class_average=-1.0,standing="Needs Improvement"
  AND T1 latest_mark is the approved Oct16 row
  AND T2 total=0,standing="Good Standing"
  AND requested/denied rows never affect latest, total or average
  AND all named marks/users/roles and mark count remain unchanged
  AND assert_unchanged(before)
```

Part 1 preservation extension, also mapped to `NM-05-01b`:

```text
GIVEN two NEW_MEMBER targets have approved signed totals [1,0]
WHEN get_personal_stats runs for either target
THEN class_average is exactly 0.5 and all captured rows/relations/files are unchanged
GIVEN a third NEW_MEMBER with zero marks joins the fixture
WHEN the first target's approved total is separately 1, -1 or 2
THEN every member's class_average is respectively 0.3, -0.3 or 0.7
  AND each read preserves the captured fixture state
```

### NM-05-02a — test_two_bound_date_ranges_are_inclusive

Parent: `NM-05-02` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:19–43,48–68`

```text
GIVEN NEW_MEMBER T1 approved values 1/2/4/8 on Oct09/Oct10/Oct12/Oct13 respectively
  AND ACTIVE A requested events on those dates; B requested one Oct11 event
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN calculate_member_marks([T1.profile],date(2026,10,10),date(2026,10,12))
  AND get_user_submitted_marks(A,date(2026,10,10),date(2026,10,12)) run
THEN T1 total is 6, and A submission IDs are Oct12 then Oct10
  AND B submissions and events outside inclusive range are absent
  AND all named mark fields/users/roles remain unchanged
  AND no files or authenticated identity are changed
  AND assert_unchanged(before)
```

### NM-05-02b — test_one_sided_reversed_and_tied_ranges_need_policy

Parent: `NM-05-02` | Operation: `NM-N05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q06 one-sided/reversed ranges and tie ordering
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:29–30,65–68,78`

```text
GIVEN NEW_MEMBER T1 and ACTIVE A have rows on Oct09,Oct10,Oct12,Oct13 and two tied Oct12 events
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN helpers receive (Oct10,None),(None,Oct12),(Oct12,Oct10),
  and both bounds Oct10/Oct12, parameterized separately
THEN Q06 chooses one-sided filtering versus ignore and reversed reject versus empty
  AND Q06 chooses deterministic tie order or explicitly unspecified tied set
  AND response/query values must follow that decision without including other owners
  AND snapshots of all named marks/users/roles remain unchanged
  AND no arbitrary tie order becomes a preservation requirement
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-05-02c — test_active_analytics_count_events_and_signed_standing

Parent: `NM-05-02` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:99–114`

```text
GIVEN progress totals [-3,0,6] with negative flags [True,False,False]
  AND approved events on Oct09,Oct10,Oct11 at_time(2026-10-17T12:00Z)
  AND one Oct11 event targets ALUMNI B, requested count=2, denied count=1
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN get_active_member_analytics(progress) runs
THEN total_new_members=3,members_in_good_standing=2,average_marks=1.0
  AND marks_this_week=2, counting Oct10/Oct11 approved events, not mark values
  AND pending_requests=2 across targets/requesters
  AND all named rows and relations remain unchanged
  AND assert_unchanged(before)
```

### NM-05-02d — test_future_week_events_and_timezone_cutoffs_need_policy

Parent: `NM-05-02` | Operation: `NM-N05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q06 future events and non-UTC date cutoff policy
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:51–62,101–109`

```text
GIVEN approved and denied rows on Oct09/Oct10/Oct11/Oct18
  AND at_time(2026-10-17T00:30Z), with timezone UTC or America/Chicago
  AND declare A using the linked local fixture vocabulary
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN active analytics and A submitted-mark queries run under each timezone
THEN Q06 chooses local-date versus UTC cutoff and whether future events count
  AND exact seven-day and fourteen-day boundary dates follow that decision
  AND counts use events, never signed value totals
  AND all named mark/user/role fields stay unchanged
  AND DateField datetime conversion is inspected on the selected backend
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-05-03a — test_own_denied_visibility_uses_actual_fourteen_days

Parent: `NM-05-03` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:48–68`

```text
GIVEN at_time(2026-10-17T12:00Z) with UTC active timezone
  AND ACTIVE A denied rows dated Oct02/Oct03/Oct04, requested Sep01/Oct16, approved Oct16
  AND B requested/denied Oct16; denial timestamps deliberately differ from event dates
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN get_user_submitted_marks(A) and ACTIVE A GET /newmember/marks/ run
THEN exact A IDs are requested Oct16, denied Oct04, denied Oct03, requested Sep01
  AND denied Oct02, A approved, and all B rows are excluded
  AND rendered values agree with context and event-date descending order
  AND all named mark fields/users/roles/session identity remain unchanged
  AND assert_unchanged(before)
```

### NM-05-04a — test_single_role_dashboard_selects_matching_context

Parent: `NM-05-04` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:17–44`

```text
GIVEN A has only ACTIVE and T1 has only NEW_MEMBER; approved marks total T1=-3
  AND A's requested M and B's requested Z exist
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN each actor GETs /newmember/marks/
THEN ACTIVE response uses ACTIVE_newmember_marks_dashboard.html with A's M only
  AND ACTIVE has analytics, personal_stats=None,is_active=True
  AND T1 response uses newmember_marks_dashboard.html with personal total=-3
  AND T1 has analytics=None,is_active=False; both responses are 200
  AND both progress contexts and rendered member labels include exactly the full names
      "T1 Able", "T2 Baker" and "T3 Zed" for the three fixture members
  AND M/Z/users/roles/mark count/session identities are unchanged
  AND assert_unchanged(before)
```

### NM-05-04b — test_mixed_roles_and_unprivileged_dashboard_need_visibility_policy

Parent: `NM-05-04` | Operation: `NM-N05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q06 mixed-role presentation; Q07 dashboard visibility
Source: `SPDWEBAPP/NEWMEMBER/views.py:17–44`

```text
GIVEN actors with roles (), (ALUMNI), (EXEC), (NM_BOARD), (ACTIVE,NEW_MEMBER)
  AND two NEW_MEMBER profiles and unrelated marks with explicit requester/target
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN each actor GETs /newmember/marks/
THEN Q07 chooses dashboard audience and Q06 chooses mixed-role template/context
  AND denied outcome reveals no protected marks; permitted output follows chosen role view
  AND mixed ACTIVE+NEW_MEMBER cannot silently lose its chosen personal/class metrics
  AND existing marks/users/profile roles remain unchanged
  AND authenticated identity remains each requesting actor
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-05-04c — test_class_choices_follow_reverse_enum_order

Parent: `NM-05-04` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views.py:29–39`

```text
GIVEN ACTIVE A and profiles pclass Alpha,Beta,Beta Gamma,Current
  AND Current value is intentional local ORM choice-validation bypass
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs /newmember/marks/
THEN response context pclasses is ["Beta Gamma","Beta","Alpha"]
  AND Current is absent and duplicate class values appear once
  AND response is 200 with matching export choices
  AND named users/profiles/class fields and marks stay unchanged
  AND authenticated identity remains A
  AND assert_unchanged(before)
```

### NM-05-04d — test_unknown_and_null_class_order_needs_policy

Parent: `NM-05-04` | Operation: `NM-N05` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q06 unknown/null class presentation
Source: `SPDWEBAPP/NEWMEMBER/views.py:29–31`

```text
GIVEN ACTIVE A and profiles with pclass None,"Unknown","Alpha"
  AND Unknown is intentional local ORM choice-validation bypass
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN A GETs marks dashboard and class choices are read
THEN Q06 chooses excluding, sorting or labeling null/unknown classes
  AND output must follow that choice without changing stored profile values
  AND no inferred enum position is assigned to unknown values
  AND all profile/user/role/mark snapshots remain unchanged
  AND authenticated identity remains A
  AND assert_unchanged(before, except_fields=fields_explicitly_allowed_by_selected_decision)
```

### NM-05-05a — test_empty_analytics_and_personal_totals_are_zero

Parent: `NM-05-05` | Operation: `NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:19–114`

```text
GIVEN ACTIVE A, no NEW_MEMBER profiles or marks; fresh variant adds NEW_MEMBER T1
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN calculate_member_marks, get_personal_stats(T1 in second variant),
  get_active_member_analytics and permitted single-role dashboards run
THEN empty class progress=[] and active totals/counts/average=0
  AND lone T1 total/class_average=0,latest_mark=None,standing="Good Standing"
  AND T1 progress contains total=0,is_negative=False
  AND no divide-by-zero occurs and permitted dashboard responses are 200
  AND users/profiles/roles and zero mark count remain unchanged
  AND assert_unchanged(before)
```

### NM-05-05b — test_pending_query_handles_missing_related_profiles

Parent: `NM-05-05` | Operation: `NM-N02,NM-N05` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:160–175`

```text
GIVEN requested M1 Oct15 and M2 Oct16; M1 requester lacks profile
  AND M2 target lacks profile; approved M3 and denied M4 exist; NM_BOARD R exists
  AND before = snapshot_scope(scope_rows, relations=scope_relations, files=scope_files)
WHEN get_pending_mark_requests() is fully evaluated and board R GETs approve/
THEN helper returns exactly M2,M1 in descending event order
  AND view is 200; missing profile labels do not remove the requested rows
  AND approved/denied rows never appear as pending
  AND all M1/M2/M3/M4 fields and related users/roles stay unchanged
  AND query evaluation, not merely lazy construction, is exercised
  AND assert_unchanged(before)
```
