# Identity Admin cases

[Case index](../case-index.md) · [Inventory](../regression-spec.md) ·
[Shared fixtures](../../../../docs/testing/fixture-contract.md) · [Decisions](../decisions.md)

[Fresh actor/file fixture legend](../fixture-notes.md) applies independently to every case.

Use business settings for real admin, with explicit model permissions.
App roles never imply is_staff/is_superuser. Shared requires_role sentinel tests
are owned here; mounted-route integration is owned by PARLEYPRO/PHILANTHROPY.
CreateUserForm and Brother_ProfileForm are unmounted; the latter is not admin.form.

Every case is a design only. Refresh named rows/relations and check file bytes
separately. Unlisted fields on named A/B rows stay unchanged, including hashes,
User first_name/last_name and staff/superuser flags; admin LogEntry is asserted
only for admin writes. Compare session identity, not whole CSRF/session blobs.

<a id="auth-c03-01a"></a>

### AUTH-C03-01a — test_identity_role_and_profile_constraints

Parent: `AUTH-C03-01` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85; SPDWEBAPP/AUTHENTICATE/forms.py:6–10`

```text
GIVEN A has a profile and Role ACTIVE exists; B distinct
  AND variants: duplicate Role(name='ACTIVE'); second Brother_Profile(user=A)
WHEN attempt each direct ORM insert in an isolated transaction/savepoint
THEN database rejects duplicate unique role/user-one-to-one relation
  AND no extra Role or profile remains after savepoint rollback
  AND A/B User/profile/relations remain unchanged
```

<a id="auth-c03-01b"></a>

### AUTH-C03-01b — test_user_delete_profile_cascade

Parent: `AUTH-C03-01` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85; SPDWEBAPP/AUTHENTICATE/forms.py:6–10`

```text
GIVEN A profile links ACTIVE/Physics; B links same shared rows; A has no image
WHEN delete A User through ORM
THEN A User/profile and their M2M links are gone
  AND Role ACTIVE and Major Physics survive with B links
  AND B User/profile/role/major fields remain unchanged
```

<a id="auth-c03-01c"></a>

### AUTH-C03-01c — test_orphan_profile_database_semantics

Parent: `AUTH-C03-01` | Operation: `AUTH-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-PROFILE](../decisions.md#q-profile); database nullable-unique behavior
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85; SPDWEBAPP/AUTHENTICATE/forms.py:6–10`

```text
GIVEN A/B profiles exist; setup intentionally creates one Brother_Profile(user=None)
WHEN save a second Brother_Profile(user=None) using real ORM
THEN Q-PROFILE decides whether orphan profiles are supported or cleaned/rejected
  AND assert explicit chosen validation/DB behavior on intended backend
  AND A/B rows and shared Role/Major rows remain unchanged
```

<a id="auth-c03-01d"></a>

### AUTH-C03-01d — test_creation_form_hashes_without_privileges

Parent: `AUTH-C03-01` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85; SPDWEBAPP/AUTHENTICATE/forms.py:6–10`

```text
GIVEN CreateUserForm is unmounted; username='created-a' unused
  AND fields email='created@example.invalid', username='created-a'
  AND password1=password2='Distinct-Test-22!word'
WHEN validate then save CreateUserForm directly
THEN form is valid; saved User accepts the supplied password
  AND new User has no profile, roles, staff or superuser privilege
  AND B User/profile and catalog rows remain unchanged
```

<a id="auth-c03-01e"></a>

### AUTH-C03-01e — test_creation_form_validation

Parent: `AUTH-C03-01` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85; SPDWEBAPP/AUTHENTICATE/forms.py:6–10`

```text
GIVEN CreateUserForm payload uses username='created-a', email='created@example.invalid'
  AND password1=password2='Distinct-Test-22!word'
  AND variants: email='not-email'; username already B; password2='different'
WHEN validate each independent form without saving
THEN form is invalid with field error email, username or password2 respectively
  AND no new User/profile is persisted
  AND B and shared role/major rows remain unchanged
```

<a id="auth-c03-02a"></a>

### AUTH-C03-02a — test_all_role_gate_requires_each_role

Parent: `AUTH-C03-02` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52`

```text
GIVEN real middleware request wraps sentinel in requires_role('EXEC','ACTIVE')
  AND denied role sets: (), EXEC, ACTIVE, PHIL_CHAIR, NM_BOARD, NME
  AND also PHIL_CHAIR+ACTIVE and superuser with (); B distinct
WHEN call wrapped view without HTTP_REFERER for each actor
THEN response redirects to reverse('poll'); sentinel is not reached
  AND missing-role message lists precisely missing EXEC/ACTIVE in declared order
  AND A/B User/profile/role/major rows and session identity unchanged
```

<a id="auth-c03-02b"></a>

### AUTH-C03-02b — test_all_role_gate_accepts_complete_set

Parent: `AUTH-C03-02` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52`

```text
GIVEN A profile has EXEC+ACTIVE; B distinct
  AND sentinel returns HTTP 200 body 'reached' without writes
WHEN call sentinel wrapped in requires_role('EXEC','ACTIVE')
THEN response is 200 body 'reached'; sentinel invoked exactly once
  AND no error message is added
  AND A/B rows/relations and session identities remain unchanged
```

<a id="auth-c03-02c"></a>

### AUTH-C03-02c — test_role_gate_anonymous_and_missing_profile

Parent: `AUTH-C03-02` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52`

```text
GIVEN variants: anonymous request; authenticated no-profile user N
  AND wrapped sentinel requires EXEC+ACTIVE; no HTTP_REFERER
WHEN call wrapper using each listed actor
THEN anonymous redirects login with 'You must be logged in to access this page.'
  AND N redirects poll with 'User profile not found.'; sentinel never runs
  AND N has no new profile; B and all role/catalog state unchanged
```

<a id="auth-c03-02d"></a>

### AUTH-C03-02d — test_role_gate_local_referrer

Parent: `AUTH-C03-02` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52`

```text
GIVEN A profile has only ACTIVE; sentinel requires EXEC+ACTIVE
  AND HTTP_REFERER='/auth/dashboard/'
WHEN call wrapped sentinel
THEN response redirects to /auth/dashboard/ with missing EXEC message
  AND sentinel is not reached
  AND A/B rows, role/major links and session identity unchanged
```

<a id="auth-c03-02e"></a>

### AUTH-C03-02e — test_role_gate_external_referrer

Parent: `AUTH-C03-02` | Operation: `AUTH-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-REDIR](../decisions.md#f-redir); [Q-REDIR](../decisions.md#q-redir)
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52`

```text
GIVEN A has only ACTIVE or no profile; sentinel requires EXEC+ACTIVE
  AND referrers: https://other.invalid/x; //other.invalid/x
WHEN call wrapper for each referrer
THEN response must not direct browser to other.invalid; sentinel is not reached
  AND Q-REDIR chooses trusted fallback/rejection status and message policy
  AND A/B rows/roles and authenticated identity remain unchanged
```

<a id="auth-c03-02f"></a>

### AUTH-C03-02f — test_role_gate_empty_requirement_policy

Parent: `AUTH-C03-02` | Operation: `AUTH-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ROLE-EMPTY](../decisions.md#q-role-empty)
Source: `SPDWEBAPP/PARLEYPRO/pp_decorators.py:7–52`

```text
GIVEN sentinel wrapped in requires_role(); actors: profile-bearing A; no-profile N
WHEN call wrapper
THEN Q-ROLE-EMPTY decides whether empty requirements mean authenticated-only
  AND or retain source behavior requiring a profile even for no roles
  AND sentinel invocation/redirect follows decision; no A/B/N state changes
```

<a id="auth-c03-03a"></a>

### AUTH-C03-03a — test_admin_rejects_nonstaff_domain_executive

Parent: `AUTH-C03-03` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A has EXEC+ACTIVE, is_staff=False
  AND B profile and zero admin LogEntry changes captured
  AND models: User, Brother_Profile, Role, Major, DashboardLink
WHEN A GETs and CSRF-valid POSTs each model changelist/change URL
THEN Django admin redirects nonstaff A to configured admin login with next
  AND no model writes or admin LogEntry additions occur
  AND A flags/roles, B rows/files and session identity remain unchanged
```

<a id="auth-c03-03b"></a>

### AUTH-C03-03b — test_admin_staff_without_model_permissions

Parent: `AUTH-C03-03` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A is_staff=True, no app roles/model permissions
  AND B target exists; models User, Brother_Profile, Role, Major, DashboardLink
WHEN A GETs change URL and POSTs change for each model
THEN response is 403, not a domain-role grant
  AND B and registered model rows remain unchanged; no LogEntry addition
  AND A staff/superuser flags and roles remain unchanged
```

<a id="auth-c03-03c"></a>

### AUTH-C03-03c — test_admin_forged_user_privilege_fields

Parent: `AUTH-C03-03` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A staff has auth.change_user permission
  AND B has profile, is_staff=False/is_superuser=False
  AND capture B roles and User password hash
WHEN A POSTs B user change form with username/email retained
  AND plus is_staff=true, is_superuser=true, brother_profile=another_profile
THEN accepted User form redirects to admin changelist
  AND readonly/omitted privilege fields do not change B flags/profile ownership
  AND B hash/roles and A rows remain unchanged; authorized change log may be added
```

<a id="auth-c03-03d"></a>

### AUTH-C03-03d — test_admin_user_missing_profile_display

Parent: `AUTH-C03-03` | Operation: `AUTH-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [F-ADMIN-PROFILE](../decisions.md#f-admin-profile); [Q-PROFILE](../decisions.md#q-profile); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A superuser has no app roles
  AND B has no profile
WHEN A GETs B User change page
THEN Q-PROFILE/Q-ERROR choose safe empty-profile display or controlled repair response
  AND CustomUserAdmin must not crash dereferencing B.brother_profile
  AND no new B profile or identity/role change and no LogEntry write
```

<a id="auth-c03-04a"></a>

### AUTH-C03-04a — test_admin_authorized_profile_image_roles

Parent: `AUTH-C03-04` | Operation: `AUTH-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ADMIN](../decisions.md#q-admin)
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A staff has explicit change_brother_profile permission
  AND B has image old.png and ACTIVE; replacement 900x450 PNG; A image separate
WHEN A POSTs B profile admin form setting image=new.png and roles=[ACTIVE,EXEC]
THEN Q-ADMIN decides whether this staff permission may assign listed app roles
  AND if allowed, redirect and change LogEntry; B new image decodes at 300x150
  AND only B selected fields/relations change; A, shared catalogs and B User flags unchanged
```

<a id="auth-c03-04b"></a>

### AUTH-C03-04b — test_admin_image_failure_consistency

Parent: `AUTH-C03-04` | Operation: `AUTH-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ADMIN](../decisions.md#q-admin); [Q-ATOMIC](../decisions.md#q-atomic); [Q-ERROR](../decisions.md#q-error)
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; permitted staff A changes B image/roles
  AND inject storage.save failure during profile save after any old-byte actions
WHEN A POSTs B profile admin form with new.png and roles=[ACTIVE,EXEC]
THEN Q-ERROR defines controlled failure; Q-ATOMIC defines DB/file compensation
  AND no unauthorized role escalation or falsely successful LogEntry
  AND A rows/files and unrelated B User/profile/major fields remain unchanged
```

<a id="auth-c03-04c"></a>

### AUTH-C03-04c — test_unused_profile_form_commit_false

Parent: `AUTH-C03-04` | Operation: `AUTH-C03` | Priority: P0
Status: `NEEDS_FIX` | Blockers: [F-FORM-COMMIT](../decisions.md#f-form-commit)
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN Brother_ProfileForm is not assigned to Brother_ProfileAdmin.form
  AND existing A profile with Physics; new_major='Astronomy', majors=[Physics]
WHEN validate form, then call save(commit=False), without save_m2m
THEN returned instance is A, but deferred save must not persist new catalog/M2M writes
  AND A major links/catalog remain as before; no premature Astronomy relation
  AND A/B User/profile/role rows and files remain unchanged
```

<a id="auth-c03-04d"></a>

### AUTH-C03-04d — test_unused_profile_form_unsaved_instance

Parent: `AUTH-C03-04` | Operation: `AUTH-C03` | Priority: P0
Status: `NEEDS_FIX` | Blockers: [F-FORM-UNSAVED](../decisions.md#f-form-unsaved)
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN unmounted Brother_ProfileForm uses unsaved profile instance
  AND new_major='Astronomy', majors=[]; A/B existing profiles unchanged
WHEN validate and call form.save(commit=True)
THEN retained form must save instance before adding its major relation, without ValueError
  AND saved new profile has its explicit intended major exactly once
  AND A/B rows/roles/links/files remain unchanged; no orphan catalog on failure
```

<a id="auth-c03-05a"></a>

### AUTH-C03-05a — test_admin_major_and_link_edit

Parent: `AUTH-C03-05` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A staff has change_major/change_dashboardlink
  AND B linked to Physics; links First(order=1), Second(order=2)
  AND variants: rename Physics to Applied Physics; change Second order to 0
WHEN A POSTs corresponding admin change form with other fields retained
THEN response redirects to model changelist with change LogEntry
  AND renamed Major keeps its PK/B link; link order edit places Second before First
  AND unselected model/identity/role/file fields remain unchanged
```

<a id="auth-c03-05b"></a>

### AUTH-C03-05b — test_admin_role_invalid_choice

Parent: `AUTH-C03-05` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A has AUTHENTICATE.change_role permission
  AND Role ACTIVE exists; B linked to it
WHEN A POSTs Role change name='UNDECLARED_ROLE'
THEN response is 200 form with name validation error
  AND Role remains ACTIVE and B relation unchanged; no change LogEntry
  AND A/B User/profile/files remain unchanged
```

<a id="auth-c03-05c"></a>

### AUTH-C03-05c — test_model_admin_display_labels

Parent: `AUTH-C03-05` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN Role ACTIVE, Major Physics; profile firstName=None,lastName=None
  AND profile has single ACTIVE role and Physics major; DashboardLink text='First'
WHEN call model __str__, ProfileAdmin.get_roles/get_majors directly
THEN Role displays 'Active Member'; Major 'Physics'; profile 'None None'; link 'First'
  AND admin helpers return 'Active Member' and 'Physics'
  AND no ORM, relation or file writes occur
```

<a id="auth-c03-05d"></a>

### AUTH-C03-05d — test_invalid_legacy_role_repair_policy

Parent: `AUTH-C03-05` | Operation: `AUTH-C03` | Priority: P0
Status: `POLICY_BLOCKED` | Blockers: [Q-ADMIN](../decisions.md#q-admin)
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN intentional local ORM setup bypasses choices: Role(name='UNDECLARED_ROLE')
  AND B linked to this row; A authorized administrator
WHEN invoke selected admin repair operation after Q-ADMIN defines it
THEN Q-ADMIN chooses rename/remap/delete/reject policy for invalid legacy roles
  AND assert documented relationship retention/removal and audit outcome
  AND B identity/files and unrelated role/major rows remain unchanged
```

<a id="auth-c03-03e"></a>

### AUTH-C03-03e — test_admin_superuser_without_domain_roles

Parent: `AUTH-C03-03` | Operation: `AUTH-C03` | Priority: P0
Status: `READY` | Blockers: none beyond shared harness
Source: `SPDWEBAPP/AUTHENTICATE/models.py:58–138; SPDWEBAPP/AUTHENTICATE/admin.py:8–85`

```text
GIVEN business settings; A is_staff=True/is_superuser=True with roles=()
  AND B has profile; actual admin model change URLs use configured admin prefix
  AND models: User, Brother_Profile, Role, Major, DashboardLink
WHEN A GETs existing change pages for each listed model
THEN responses are 200 admin forms without domain-role redirects
  AND A keeps zero app roles; no row or LogEntry changes on GET
  AND B and shared model rows/files remain unchanged
```
