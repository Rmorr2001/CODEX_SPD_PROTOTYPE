# Workflow fixture legend

This is a precise fixture design layered on the
[shared contract](../../../docs/testing/fixture-contract.md), not another factory API.
Every case starts fresh; no fixture or state comes from the preceding case.
Only actors mentioned by that case need to be constructed.

- A means `make_user(username="actor-a", roles=())`.
- B means `make_user(username="actor-b", roles=())`, distinct from A by PK and username.
- Z means `make_user(username="roleless-z", roles=())`.
- N or the no-profile user means
  `make_user(username="no-profile", roles=(), with_profile=False)`.
- Inactive A uses username `inactive-a`, `is_active=False`, otherwise A defaults.

These fixtures have TEST_PASSWORD, a profile except N, no major/image, and false
staff/superuser flags, as defined by the shared contract. Each GIVEN explicitly
overrides these defaults when it names roles, images, flags, username or missing
profile. Role variants **replace** roles; they never add an implied ACTIVE role.
A GIVEN that spells out make_user describes that actor's construction, not a
second User with the same username. No-profile variants omit nonempty roles and
profile_fields, following the shared factory guard.

An authenticated A/B means `login_actor(client, actor)` only for authorization
cases. Password/session-evidence cases explicitly submit TEST_PASSWORD credentials.
A mentioned second B client gets its own Client and login_actor(B). An anonymous
client has no authenticated identity. A session marker, where asserted, is
explicitly set to `marker="before"` before the action.

An administrator actor uses A's username and only the flags/permissions stated in
GIVEN. Permission names refer to real content types: e.g.
`auth.change_user`, `AUTHENTICATE.change_brother_profile`,
`AUTHENTICATE.change_role`, `AUTHENTICATE.change_major`, and
`AUTHENTICATE.change_dashboardlink`. Staff alone grants no model permission.

Named Major rows (Old, Other, New, Physics, Chemistry, Biology, Astronomy) are thin
local ORM fixtures with exactly those names. A case stating a link creates that
row and relation explicitly; it never infers majors from roles. Duplicate-name
and invalid-role cases intentionally bypass factory validation through local ORM.

Named image fixtures use temporary_media and real synthetic Pillow bytes:
old.png is a 40×40 red PNG, other.png a 40×40 blue PNG, and new.png a 40×40 green PNG,
unless GIVEN specifies different dimensions/format. Each belongs only to the
named profile. Snapshot file references and actual bytes separately. No default
fixture opens an existing upload or reads production/member data.

Demo E users use explicit usernames `demo-executive`, `demo-active`,
`demo-newmember`, `demo-alumni`, password=None, is_active=True,
is_staff=False/is_superuser=False, plus only the profile roles named in GIVEN.
Each joins exactly its named `railway-demo:demo-<persona>` group through real ORM.
Corrupt/multiple-member setups use distinct `extra-persona` usernames and explicit
flags/profile differences. This does not call the demo seed command.
