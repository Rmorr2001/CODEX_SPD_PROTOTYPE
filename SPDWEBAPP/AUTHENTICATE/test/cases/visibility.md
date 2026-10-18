# Visibility cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Use explicit role sets, not the demo executive. Freeze consumed clocks with at_time.
MISC owns announcements; HOME owns daylight helpers. Roster visibility is not
approved merely because the current route returns 200.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-a09-01a"></a>

### AUTH-A09-01a — test_dashboard_non_newmember_render

Parent: `AUTH-A09-01` | Operation: `AUTH-A09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN A has profile; role variants: (), ACTIVE, EXEC, PHIL_CHAIR, NM_BOARD, NME
  AND also EXEC+ACTIVE, PHIL_CHAIR+ACTIVE, ALUMNI and ALUMNI+ACTIVE; B distinct
WHEN A GETs /auth/dashboard/
THEN response is 200 using AUTHENTICATE/dashboard.html
  AND no /newmember/ redirect occurs for any listed role set
  AND A/B User/profile/role/major state and files remain unchanged
```

<a id="auth-a09-01b"></a>

### AUTH-A09-01b — test_dashboard_newmember_precedence

Parent: `AUTH-A09-01` | Operation: `AUTH-A09` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-VIS](../decisions.md#q-vis)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN A profile role sets: NEW_MEMBER; NEW_MEMBER+ACTIVE; NEW_MEMBER+EXEC+ACTIVE
  AND B distinct; do not follow destination redirect
WHEN A GETs /auth/dashboard/
THEN Q-VIS confirms NEW_MEMBER precedence or selects mixed-role routing
  AND current source redirects each listed set to /newmember/
  AND assert selected Location without exercising destination; A/B rows unchanged
```

<a id="auth-a09-01c"></a>

### AUTH-A09-01c — test_dashboard_missing_profile

Parent: `AUTH-A09-01` | Operation: `AUTH-A09` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: [Q-PROFILE](../decisions.md#q-profile); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN make_user(username='no-profile', with_profile=False); B has profile
WHEN no-profile user GETs /auth/dashboard/
THEN Q-PROFILE/Q-ERROR choose onboarding or controlled missing-profile rejection
  AND no incidental profile/role/User creation
  AND B rows/relations/files remain unchanged
```

<a id="auth-a09-02a"></a>

### AUTH-A09-02a — test_dashboard_links_and_active_announcements

Parent: `AUTH-A09-02` | Operation: `AUTH-A09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN A ACTIVE; links Second(order=2), First(order=1)
  AND announcements Active(is_active=True), Hidden(is_active=False)
  AND at_time is aware 2026-10-01T12:00:00Z; B distinct
WHEN A GETs /auth/dashboard/
THEN response is 200; dashboard_links ordered First then Second with stored hrefs
  AND active announcement rendered, Hidden absent from announcement context/render
  AND A/B rows, links/announcements and files remain unchanged
```

<a id="auth-a09-02b"></a>

### AUTH-A09-02b — test_dashboard_empty_content

Parent: `AUTH-A09-02` | Operation: `AUTH-A09` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN A ACTIVE; no DashboardLink or AnnouncementAlert rows
  AND at_time is aware 2026-10-01T12:00:00Z; B distinct
WHEN A GETs /auth/dashboard/
THEN response is 200; dashboard_links/announcements are empty
  AND built-in roster/philanthropy/poll links still render
  AND no rows, relationships or files change
```

<a id="auth-a09-03a"></a>

### AUTH-A09-03a — test_roster_partition_order_and_class_policy

Parent: `AUTH-A09-03` | Operation: `AUTH-A09` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-VIS](../decisions.md#q-vis)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN profiles: Adams ACTIVE, Brown ALUMNI+ACTIVE, Clark ALUMNI, Davis roles=()
  AND also Evans NEW_MEMBER and orphan Fox(user=None); each has distinct lastName
  AND requesters: roleless, ACTIVE, NEW_MEMBER, ALUMNI, no-profile user
WHEN each requester GETs /auth/roster/ and /auth/alumni_roster/
THEN Q-VIS first approves audience/field policy; if current audience retained, both return 200
  AND active query has Adams/Davis/Evans/Fox, alumni has Brown/Clark, once each
  AND rows lastName ordered; pclass_order matches PClass choices; no writes
```

<a id="auth-a09-03b"></a>

### AUTH-A09-03b — test_roster_ties_and_missing_names

Parent: `AUTH-A09-03` | Operation: `AUTH-A09` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-VIS](../decisions.md#q-vis); [Q-ORDER](../decisions.md#q-order)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN A may read rosters under Q-VIS
  AND profiles have equal lastName='Adams', lastName=None and lastName=''
WHEN A GETs both roster routes
THEN Q-ORDER chooses secondary/null ordering or explicitly leaves ties unordered
  AND assert exact ordering only if that decision defines it
  AND Q-VIS determines inclusion; profile/User/roles/majors/files remain unchanged
```

<a id="auth-a09-04a"></a>

### AUTH-A09-04a — test_roster_sensitive_field_visibility

Parent: `AUTH-A09-04` | Operation: `AUTH-A09` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-VIS](../decisions.md#q-vis)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN B fields: firstName='SecretName', hometown='SecretTown', class='Alpha'
  AND B has photo/major/role; actors roleless, NEW_MEMBER, ALUMNI
WHEN each actor directly GETs both rosters and dashboard without relying on links
THEN Q-VIS decides allowed audience and name/photo/class/major/hometown/role fields
  AND denied response must not contain B protected values/image links
  AND email column remains absent; A/B data and file bytes unchanged
```

<a id="auth-a09-04b"></a>

### AUTH-A09-04b — test_roster_literal_text_escaping

Parent: `AUTH-A09-04` | Operation: `AUTH-A09` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-VIS](../decisions.md#q-vis)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN B firstName='<tag>', hometown='<script>bad()</script>'; A visibility awaits Q-VIS
WHEN A GETs an allowed roster under the selected visibility rule
THEN response escapes synthetic tags rather than executing/rendering raw markup
  AND assert literal text and named columns, not full HTML snapshot
  AND A/B rows/relations and files remain unchanged
```

<a id="auth-a09-04c"></a>

### AUTH-A09-04c — test_media_access_policy

Parent: `AUTH-A09-04` | Operation: `AUTH-A09` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-VIS](../decisions.md#q-vis); [Q-STORAGE](../decisions.md#q-storage)
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–69; SPDWEBAPP/AUTHENTICATE/templates/AUTHENTICATE/roster.html:30–45`

```text
GIVEN B has synthetic profile_images/other.png under temporary_media
  AND anonymous and roleless A know the media URL
WHEN each actor GETs /media/profile_images/other.png
THEN Q-VIS/Q-STORAGE decide public image bytes versus protected serving
  AND assert allowed readable bytes or denied response under that rule
  AND no profile reference, file bytes or role/identity state changes
```
