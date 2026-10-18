# Mounted integration and unmounted direct view

Use [shared fixtures](../../../../docs/testing/fixture-contract.md).
AUTHENTICATE owns full login/session policy; HOME owns public page composition.
No case introduces a public MISC route.

<a id="misc-t17a"></a>

### MISC-T17a — test_resolver_contains_no_misc_view

Parent: `MISC-T17` | Operation: `MISC-O12` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/SPDWEBAPP_CORE/urls.py:23–34`

```text
GIVEN shared settings separately business and demo with actual core URL includes
WHEN traversing resolver callbacks and named routes without making network calls
THEN daylight_savings_alert is not a mounted callback
  AND MISC.urls has no patterns and no root include
  AND dashboard resolves at /auth/dashboard/ and home resolves at /
  AND no request to an invented /misc/ route is used as a contract
  AND database/session/files/admin audit remain unchanged
```

<a id="misc-t17b"></a>

### MISC-T17b — test_direct_view_context_messages_without_public_endpoint

Parent: `MISC-T17` | Operation: `MISC-O06` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/MISC/views.py:4–20`

```text
GIVEN RequestFactory requests separately GET and POST with empty payload
  AND inactive setting S={name:"Ignored"}; before=snapshot_scope([S])
  AND utility boundary separately returns March 8 2026, November 1 2026 or None
  AND render boundary is captured solely to inspect arguments of this unmounted callable
WHEN daylight_savings_alert(request) is invoked directly
THEN template argument is dls_alert.html and show_alert=True regardless of S
  AND message is "Daylight Saving Time is on March 08, 2026. Clocks will move forward one hour!"
  AND fall variant replaces date with November 01, 2026 and direction with back
  AND None variant is "No upcoming Daylight Saving Time changes found."
  AND assert_unchanged(before); no session/file/LogEntry effect
```

<a id="misc-t17c"></a>

### MISC-T17c — test_unused_view_lifecycle_needs_decision

Parent: `MISC-T17` | Operation: `MISC-O06` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q7 retire/repair/mount policy; D3 wrong template path
Source: `SPDWEBAPP/MISC/views.py:20`

```text
GIVEN only MISC/dls_alert.html exists in the inspected template tree
  AND RequestFactory GET request invokes the unmounted view with a computed date
WHEN deciding whether to retain daylight_savings_alert
THEN Q7 must choose removal or namespaced-template repair
  AND any route mounting additionally needs explicit authentication/method policy
  AND if retained the template must resolve without TemplateDoesNotExist (D3)
  AND no option may mutate settings or announcements on a read
```

<a id="misc-t18a"></a>

### MISC-T18a — test_eligible_roles_receive_global_active_content

Parent: `MISC-T18` | Operation: `MISC-O12` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–35`

```text
GIVEN make_user(username="reader-a",roles=R), R separately (), (ACTIVE,), (ALUMNI,), (PRESIDENT,)
  AND make_user(username="reader-b",roles=())
  AND active A={title:"Global",content:"Everyone eligible"}; inactive B={title:"Hidden",content:"No"}
  AND before=snapshot_scope([A,B], relations=[reader-a.brother_profile.roles])
WHEN each actor is login_actor-authenticated and GETs /auth/dashboard/
THEN each response is 200 with announcement PK set exactly {A.pk}
  AND content is not filtered by actor or creator; neither model has owner field
  AND assert_unchanged(before); each request preserves its session identity
```

<a id="misc-t19a"></a>

### MISC-T19a — test_anonymous_dashboard_redirect_discloses_no_fragment

Parent: `MISC-T19` | Operation: `MISC-O12` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–35`

```text
GIVEN anonymous client; active A={title:"Member-only notice",content:"Text"}
  AND S={is_active:True,name:"Clock"}; before=snapshot_scope([A,S])
WHEN client GETs /auth/dashboard/ without following redirects
THEN response is 302 to the configured login URL with next=/auth/dashboard/
  AND response body has no Member-only notice, clockButton or announcement-row
  AND assert_unchanged(before); no authenticated session identity is created
```

<a id="misc-t19b"></a>

### MISC-T19b — test_any_new_member_combination_redirects_before_alert_render

Parent: `MISC-T19` | Operation: `MISC-O12` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–35`

```text
GIVEN make_user(username="new-reader",roles=R) where R separately
  AND (NEW_MEMBER,), (NEW_MEMBER,ACTIVE), (NEW_MEMBER,PRESIDENT)
  AND active A={title:"No redirect disclosure",content:"Text"}
  AND before=snapshot_scope([A],relations=[new-reader.brother_profile.roles])
WHEN login_actor(client,new-reader) then GET /auth/dashboard/ without following
THEN response is 302 with Location=/newmember/
  AND response body contains no announcement fragment or clockButton
  AND assert_unchanged(before); session identity remains new-reader
```

<a id="misc-t20a"></a>

### MISC-T20a — test_missing_profile_dashboard_needs_response_policy

Parent: `MISC-T20` | Operation: `MISC-O12` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q8 AUTHENTICATE response policy; D4 missing-profile exception
Source: `SPDWEBAPP/NEWMEMBER/views_functions.py:190–192`

```text
GIVEN make_user(username="no-profile",with_profile=False) logged in
  AND A={title:"Keep",content:"Text"}; before=snapshot_scope([A])
WHEN client GETs /auth/dashboard/
THEN current check_user_role dereferences absent brother_profile (D4)
  AND Q8 must choose controlled denial, profile setup redirect or restricted dashboard
  AND chosen outcome must not leak a related-object traceback or create implicit privileges
  AND assert_unchanged(before); user, session identity and missing-profile state stay unchanged
```

<a id="misc-t20b"></a>

### MISC-T20b — test_home_has_no_announcement_or_clock_integration

Parent: `MISC-T20` | Operation: `MISC-O12` | Priority: P1
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/HOME/views.py:8–12`

```text
GIVEN client separately anonymous and login_actor-authenticated reader with roles=()
  AND active A={title:"Do not show on home",content:"Text"}
  AND S={is_active:True,name:"Do not show clock"}; before=snapshot_scope([A,S])
WHEN client GETs /
THEN response is 200 with no announcement-row or clockButton
  AND neither MISC sentinel text is present
  AND assert_unchanged(before); no implicit MISC setting/default is created
```

<a id="misc-t30a"></a>

### MISC-T30a — test_dashboard_read_failure_requires_fragment_isolation_rule

Parent: `MISC-T30` | Operation: `MISC-O01` | Priority: P1
Status: `POLICY_BLOCKED` | Blockers: Q6 shared rendering failure response/logging
Source: `SPDWEBAPP/AUTHENTICATE/views.py:26–35`

```text
GIVEN logged-in make_user(username="reader",roles=())
  AND A={title:"Recoverable",content:"Text"}; S={is_active:True,name:"Clock"}
  AND before=snapshot_scope([A,S,reader],relations=[reader.brother_profile.roles])
  AND inject OperationalError during announcement evaluation, separately setting lookup
WHEN client GETs /auth/dashboard/
THEN Q6 chooses partial safe page with 200 or controlled error response
  AND no outcome exposes raw exception details or writes fallback rows
  AND assert_unchanged(before); reader session identity remains unchanged
WHEN injection is removed and reader GETs /auth/dashboard/ again
THEN response is 200 with Recoverable and Clock; no cached failure is persisted
```
