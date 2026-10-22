# AUTHENTICATE — identity and membership

Owns original authentication, profiles, rosters and dashboard views/models/forms.
Existing routes and writes remain intact; domain regression contracts live in
`test/` with their case map. New React presentation contracts are read-only.

- `api_session.py`: `GET /api/v1/session/` returns session/profile availability,
  demo availability, allowlisted landing path, and only the caller's display
  name, role labels/codes and navigation capabilities. It sets the normal CSRF
  cookie for native demo entry. It exposes no session keys, passwords, contact
  details or other members. Anonymous/missing-profile states are explicit.
- `api_dashboard.py`: authenticated `GET /api/v1/dashboard/` returns active
  announcements and safe configured links in original order. A missing profile
  is denied. NEW_MEMBER takes precedence over other roles and receives a separate
  landing path without the general feed, preserving the original redirect rule.
- Navigation capabilities describe current role gates; server endpoints must
  still enforce their own permissions. ACTIVE controls polls/service navigation.
  All authenticated reads use no-store and cookie SessionAuthentication.

The shared safe presentation-link guard belongs to CORE/api/links.py and is used
by public HOME and member read models. Frontend views and access handling live in
`frontend/src/domains/identity/`; `test/test_read_api.py` covers boundary contracts.
Run `manage.py test AUTHENTICATE.test.test_read_api` with standalone test settings;
full regression commands and unresolved policy cases are in docs/testing/README.
No new credentials or environment keys are introduced.
