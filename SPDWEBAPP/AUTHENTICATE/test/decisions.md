# Decisions and defects

[Inventory](regression-spec.md) · [Cases](case-index.md)

Names are unresolved decisions or concrete source defects, not permission to
change application behavior. POLICY_BLOCKED takes precedence over associated
defects or missing facilities. Sources without a prefix below are under
`SPDWEBAPP/AUTHENTICATE/`; PARLEYPRO and core/demo paths retain their prefix.

### F-REDIR

Unchecked login next and role-gate Referer redirects can leave the trusted site. Source:
views.py:80–84 and PARLEYPRO/pp_decorators.py:26–48. Keep safe destination assertion separate from
chosen fallback.

### Q-REDIR

Choose allowed hosts/schemes, local relative destinations, encoding handling, rejection versus
fallback, and whether successful login identity is retained on rejected next.

### Q-LOGIN-SWITCH

Choose whether a logged-in user may submit another user's credentials: accepted switch with
session rotation, or rejection retaining the original identity. Fix response/redirect explicitly.

### Q-LOGIN-METHOD

Choose login GET-form handling for PUT/PATCH/DELETE versus HTTP 405. These methods cannot
authenticate submitted credentials or follow next.

### Q-LOGOUT-METHOD

Choose POST-only logout versus retained GET logout; choose rendering/redirect/status and repeat
behavior. Current navbar uses GET. Unsafe POST always requires CSRF.

### Q-PASSWORD-METHOD

Choose legacy non-POST HTTP 200 JSON false/error versus HTTP 405. Separate this transport decision
from password/session preservation.

### Q-MUTATION-METHOD

Choose PUT/PATCH/DELETE rejection for profile/photo/reset/major endpoints: existing
JSON-false/photo-redirect or HTTP 405. No implicit mutations.

### F-PARSE

Views parse JSON without schema/guard at 102,259,282; filtered missing profile fields call
None.lower. Typed/missing values can crash or set an unusable password.

### Q-PARSE

Define JSON object/type/required-field schemas and body-size boundary. Choose controlled
field/body error responses instead of incidental exceptions.

### Q-ERROR

Choose safe HTTP statuses/JSON field errors and infrastructure-failure responses. Do not return
raw exception details or claim success for partial failure.

### Q-PASSWORD

Choose validator use, password reuse, empty/unusable input rejection, whitespace semantics and
length limit. Template .trim() does not define backend semantics.

### F-VALID

Direct model save skips field/form validation; empty custom major is created; duplicate username
may raise a DB error. Sources: views.py:126–164,279–303.

### Q-VALID

Choose optional/required profile fields, email/PClass validation, length limits, Unicode/control
text and catalog name rules. Multipart 'null' is a literal string, not JSON null.

### F-PARTIAL

User.save precedes profile.save; major clear/add phases and file/database writes have no
encompassing transaction. Source: views.py:154–160,201–211,264–268.

### Q-ATOMIC

Choose transaction/compensation guarantees and explicit recoverable partial-result behavior. DB
rollback cannot restore deleted files. Inspect state before outer TestCase cleanup; use
TransactionTestCase for commit behavior.

### F-IMAGE-REWRITE

Brother_Profile.save reopens, re-encodes and rewraps any current image on every save; may
rename/orphan files on text-only/unchanged saves. Source: models.py:101–127.

### Q-IMAGE

Choose supported decode formats, MIME/name mismatch handling, byte/pixel bounds,
animation/alpha/metadata policy, filename collisions, replacement cleanup and unrelated-save
re-encoding.

### F-INVALID-IMAGE

Image decode errors are caught then super().save persists the original upload. Source:
models.py:103–127. Invalid bytes must not become a usable-photo replacement.

### F-FILE-LOSS

Old photo deletion precedes replacement storage, and reset deletes bytes before DB persistence.
Sources: views.py:201–211,243–247.

### F-ERROR-LEAK

Upload/reset/major failure responses include exception type/details; photo logging assumes .path.
Sources: views.py:213–233,251–252,273–274.

### Q-STORAGE

Choose supported local/remote backends, storage errors, absent bytes and transient URL failures.
Distinguish a generated URL from file existence; DB references and stored bytes need separate
assertions.

### F-PATH-DEPENDENCY

Photo endpoint calls .path for delete/logging despite storage APIs that need not expose a local
path. Source: views.py:204,213.

### Q-PROFILE

Choose missing-profile response/onboarding/explicit creation and nullable orphan lifecycle. Do not
infer a creation signal or bless current exceptions.

### F-DESTRUCTIVE-READ

Profile GET clears image pointer and saves profile on any URL exception. Source: views.py:171–177.
A transient read failure must not delete the saved reference.

### Q-MAJORS

Choose server maximum, explicit [] versus omitted key, permitted catalog creators, exact versus
normalized names, and concurrent replacement outcomes. UI-only max 2 is not an approved API rule.

### Q-NORMALIZE

Choose word.capitalize normalization versus acronym/Unicode-aware rules; selection endpoint
currently bypasses custom-major normalization.

### Q-UNIQUE

Choose unique normalized key, canonical row/conflict/remediation behavior for duplicates and
concurrent creation. Major.name is not unique (models.py:83). PostgreSQL races need independent
connections and bounded barriers.

### Q-VIS

Choose dashboard mixed-role precedence, roster audiences and fields, and public versus protected
media. Current login-only routes expose other profiles; UI visibility is not authorization
approval.

### Q-ORDER

Choose deterministic secondary ordering/null placement for equal or absent roster names and equal
dashboard-link order, or explicitly leave ties unordered.

### Q-FILTER

Choose blacklist/whitelist token or substring semantics, false-positive handling, helper
repair/removal and destructive global catalog cleanup versus retention/soft-delete. Preserve no
moderation loophole by accident.

### F-FILTER-BYPASS

Any whitelisted substring suppresses unrelated blacklist matches. Source: utils.py:35–39. Test
'biology fuck' separately from exact whitelist preservation.

### F-UNDEFINED-FILTER

Unused clean_profanity_from_user_fields refers to function-local inappropriate_words from another
function, causing NameError. Source: utils.py:43–66.

### Q-ROLE-EMPTY

Choose whether requires_role() means authenticated-only or retains profile requirement. Do not
conflate empty list policy with ALL versus ANY for actual requested roles.

### Q-ADMIN

Choose authorized role-assignment/legacy-role repair semantics, profile form support and
slashless/prefix admin boundary policy. Real Django model permissions, not app roles, gate core
admin.

### F-ADMIN-PROFILE

CustomUserAdmin.brother_profile dereferences absent profile without handling. Source:
admin.py:26–27.

### F-FORM-COMMIT

Unused Brother_ProfileForm creates a Major and adds M2M even for commit=False. Source:
admin.py:38–45. Retain ordinary deferred-save semantics if the helper is supported.

### F-FORM-UNSAVED

Unused Brother_ProfileForm adds majors before saving a new profile PK. Source: admin.py:39–44.
Repair or remove in a separately authorized code change.

### Q-DEMO

Choose trusted group membership/uniqueness, required persona username/profile/roles and accepted
content types. Current lookup is group .first(), then password check; JSON silently defaults
executive.

### F-ADMIN-PREFIX

Demo middleware blocks only literal /admin/ although core mount uses settings.ADMIN_URL. Source:
railway_demo/middleware.py:10–11 and SPDWEBAPP_CORE/urls.py:25. Actual public-demo admin must
remain unavailable.
