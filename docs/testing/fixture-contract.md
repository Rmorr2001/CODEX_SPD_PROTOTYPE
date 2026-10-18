# Shared fixture contract for Wave 2

Implemented under `SPDWEBAPP/SPDWEBAPP_CORE/testing/`, with 11 harness tests.
The coordinator owns these shared helpers; domains keep thin workflow-specific
constructors beside their tests. Business policy is not decided by fixtures.

## Identity and roles

```python
make_user(*, username, roles=(), with_profile=True, password=TEST_PASSWORD,
          is_active=True, is_staff=False, is_superuser=False,
          profile_fields=None) -> User
make_profile(user, *, roles=(), **profile_fields) -> Brother_Profile
```

- `username` is explicit and unique per test fixture. All data is synthetic.
- `make_user` returns a real saved Django User. Access its profile through the
  ORM. No real account, demo seed or network is needed.
- Roles are exact names, not an inferred hierarchy: EXEC never adds ACTIVE.
  A usable test-only password is the default; `password=None` means unusable.
- Staff and superuser flags default false and do not imply domain roles.
- `with_profile=False` creates no profile and rejects nonempty roles/profile
  fields rather than silently discarding them. `make_profile` creates the one
  missing profile; calling it for an already-profiled user is a fixture error.
- Defaults include no image or majors. Profile defaults must satisfy basic
  field types without implicitly selecting a class or granting privileges.
- Declared role names are validated; corruption/invalid-choice cases use explicit
  local ORM setup and name that intentional bypass in their setup.
- Admin fixtures attach actual Django model permissions explicitly. A domain
  role does not authorize admin access.

## Requests and isolation

Two standalone settings modes are available: `business` uses core routes and real admin
without demo blocking; `demo` uses actual demo URLs and middleware. Both use a
synthetic key, test-only database, temporary media, local hosts and no external
services or runtime secret imports. Keep real auth, session, message and CSRF
middleware. Demo secure-cookie cases use HTTPS test requests.

```python
login_actor(client, user)  # force_login for authorization tests only
csrf_client() -> Client   # enforce_csrf_checks=True; no automatic token bypass
temporary_media()         # context manager: isolated MEDIA_ROOT/storage
at_time(aware_datetime)   # context manager: patch the clocks consumed by case
```

`login_actor` must not be used as evidence of password-login behavior. Login
cases submit credentials. CSRF cases acquire a real cookie/token pair from the
appropriate rendered form and specify absent/bad/valid variants. `at_time`
patches `django.utils.timezone.now`; use its `targets=(...)` option for additional
fully qualified imported clock references. Local datetime/DST needs its own
aware clock boundary. Do not assume patching one module freezes all time.

Domain-local fixtures are thin real-ORM constructors with explicit owner,
status, dates and audit values. They live beside tests until truly shared.

## State and outputs

```python
before = snapshot_scope(named_rows, relations=(), files=())
assert_unchanged(before, except_fields={...})
```

These helpers capture selected state, not deep snapshots of the whole database.
Each case names affected rows/relations/files, then refreshes those records.
Denied requests may add a message or rotate CSRF metadata; compare session
identity rather than requiring an identical session blob. File assertions check
references and real synthetic bytes separately from database rollback.

Parse XLSX bytes with openpyxl and `data_only=False`; inspect cell types as well
as values. Concurrency requires separate database connections, synchronization
barriers and bounded timeouts on the intended PostgreSQL backend.

## Discovery and availability

Each domain has `test/__init__.py`, executable `test_*.py` files and an audited
`case-map.json`. Explicit-package and app-label discovery both passed; the empty
app-root `tests.py` placeholders were removed. Existing demo tests remain intact.

Use `SPDWEBAPP_CORE.testing.settings` for business/admin tests and
`SPDWEBAPP_CORE.testing.demo_settings` for the original demo suite. Both are
standalone; neither imports runtime settings or `secret_config`. Demo settings
copy the template configuration before adding the real demo context processor.
`RegressionTestCase` provides per-test temporary media; autocommit-dependent
error paths use `TransactionTestCase` and `temporary_media()` explicitly.

Run the full mapping/discovery/execution audit as documented in the
[root testing map](README.md). PostgreSQL concurrency, browser behavior and other
case-specific facilities remain explicitly blocked; SQLite success does not
verify them. See [actual Wave 2 results](wave-2-results.md).
